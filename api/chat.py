import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Tuple, Optional

import requests

# Gemini / Google Generative Language API configuration
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta",
)
GEMINI_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
CACHE_TTL_S = int(os.getenv("CHAT_CACHE_TTL_S", "120"))
CACHE_MAX_ITEMS = int(os.getenv("CHAT_CACHE_MAX_ITEMS", "256"))

_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _cache_key(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    now = time.time()
    entry = _CACHE.get(key)
    if not entry:
        return None
    created_at, value = entry
    if now - created_at > CACHE_TTL_S:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: Dict[str, Any]) -> None:
    if len(_CACHE) >= CACHE_MAX_ITEMS:
        oldest_key = min(_CACHE.items(), key=lambda item: item[1][0])[0]
        _CACHE.pop(oldest_key, None)
    _CACHE[key] = (time.time(), value)


def _to_gemini_contents(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Convert internal chat message format into Gemini 'contents' format."""
    contents: List[Dict[str, Any]] = []
    for m in messages:
        text = m.get("content", "")
        if not text:
            continue
        role = m.get("role", "user").lower()
        gem_role = "model" if role in ("assistant", "model") else "user"
        contents.append(
            {
                "role": gem_role,
                "parts": [{"text": text}],
            }
        )
    return contents


def _extract_messages(body: Dict[str, Any]) -> List[Dict[str, str]]:
    messages = body.get("messages")
    if isinstance(messages, list) and messages:
        return [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
    prompt = body.get("prompt") or body.get("message")
    if prompt:
        return [{"role": "user", "content": str(prompt)}]
    return []


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON body"})
            return

        if not GEMINI_API_KEY:
            self._send(500, {"error": "GOOGLE_CLOUD_API_KEY is not configured"})
            return

        messages = _extract_messages(body)
        if not messages:
            self._send(400, {"error": "messages or prompt is required"})
            return

        # Default to a Gemini model; allow override via body["model"]
        model = body.get("model", "gemini-1.5-flash")
        temperature = float(body.get("temperature", 0.2))
        max_tokens = int(body.get("max_tokens", 512))

        # Build Gemini generateContent payload
        payload = {
            "contents": _to_gemini_contents(messages),
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        cache_key = _cache_key(payload)
        cached = _cache_get(cache_key)
        if cached:
            self._send(200, {**cached, "cached": True})
            return

        try:
            response = requests.post(
                f"{GEMINI_BASE_URL}/models/{model}:generateContent",
                params={"key": GEMINI_API_KEY},
                json=payload,
                timeout=30,
            )
        except requests.RequestException as exc:
            self._send(502, {"error": "Upstream request failed", "detail": str(exc)})
            return

        if response.status_code >= 400:
            self._send(
                response.status_code,
                {"error": "Gemini API error", "detail": response.text},
            )
            return

        data = response.json()
        # Extract text from Gemini response: candidates[0].content.parts[*].text
        reply = ""
        candidates = data.get("candidates") or []
        if candidates:
            content = candidates[0].get("content") or {}
            parts = content.get("parts") or []
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            reply = "".join(texts)
        result = {"reply": reply, "model": model}
        _cache_set(cache_key, result)
        self._send(200, result)
