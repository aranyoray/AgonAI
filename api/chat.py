import hashlib
import json
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Tuple, Optional

# Ensure project root is on sys.path so sibling packages resolve
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    import requests
except ImportError as e:
    requests = None
    _import_error = str(e)
else:
    _import_error = ""

# Gemini / Google Generative Language API configuration
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta",
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
        cleaned: List[Dict[str, str]] = []
        for m in messages:
            if not isinstance(m, dict):
                continue
            cleaned.append(
                {
                    "role": str(m.get("role", "user")),
                    "content": "" if m.get("content") is None else str(m.get("content", "")),
                }
            )
        return cleaned
    prompt = body.get("prompt") or body.get("message")
    if prompt:
        return [{"role": "user", "content": str(prompt)}]
    return []


class handler(BaseHTTPRequestHandler):
    def _send_cors(self) -> None:
        # Allow browser-based clients (and simple local frontends) to call this endpoint.
        self.send_header("Access-Control-Allow-Origin", os.getenv("CHAT_CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_GET(self) -> None:
        """Health check endpoint."""
        if requests is None:
            self._send(500, {"error": "requests library not available", "detail": _import_error})
            return
        self._send(200, {
            "status": "ok",
            "service": "chat",
            "api": "gemini",
            "python": sys.version,
            "has_api_key": bool(GEMINI_API_KEY),
        })

    def do_POST(self) -> None:
        # Never crash the function — always return a JSON error.
        try:
            if requests is None:
                self._send(500, {"error": "requests library not available", "detail": _import_error})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0

            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": "Invalid JSON body"})
                return

            if not isinstance(body, dict):
                self._send(400, {"error": "JSON body must be an object"})
                return

            if not GEMINI_API_KEY:
                self._send(500, {"error": "GEMINI_API_KEY is not configured"})
                return

            messages = _extract_messages(body)
            if not messages:
                self._send(400, {"error": "messages or prompt is required"})
                return

            # Default to a Gemini model; allow override via body["model"]
            model = body.get("model") or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            if not isinstance(model, str):
                model = str(model)

            def _safe_float(value: Any, default: float) -> float:
                try:
                    if value is None or value == "":
                        return default
                    return float(value)
                except (TypeError, ValueError):
                    return default

            def _safe_int(value: Any, default: int) -> int:
                try:
                    if value is None or value == "":
                        return default
                    return int(value)
                except (TypeError, ValueError):
                    return default

            temperature = _safe_float(body.get("temperature", 0.2), 0.2)
            max_tokens = _safe_int(body.get("max_tokens", 512), 512)

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

            try:
                data = response.json()
            except ValueError:
                self._send(502, {"error": "Gemini returned non-JSON response", "detail": response.text})
                return

            # Extract text from Gemini response: candidates[0].content.parts[*].text
            reply = ""
            if isinstance(data, dict):
                candidates = data.get("candidates") or []
                if candidates and isinstance(candidates, list) and isinstance(candidates[0], dict):
                    content = candidates[0].get("content") or {}
                    parts = content.get("parts") or []
                    if isinstance(parts, list):
                        texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
                        reply = "".join(texts)

            result = {"reply": reply, "model": model}
            _cache_set(cache_key, result)
            self._send(200, result)
        except Exception as exc:
            self._send(500, {"error": "Unhandled server error", "detail": str(exc)})
