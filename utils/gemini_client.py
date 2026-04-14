import os
from typing import Optional, Dict, Any

import requests


class GeminiClient:
    """LLM client that uses the Gemini API for generating agent responses.

    Exposes the same ``generate()`` interface as ``OllamaClient`` so it can be
    used as a drop-in replacement when passed as ``llm_client`` to agents.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.base_url = (
            base_url
            or os.getenv(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta",
            )
        ).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        contents = []
        if system:
            contents.append(
                {"role": "user", "parts": [{"text": f"[System instructions]\n{system}"}]}
            )
            contents.append(
                {"role": "model", "parts": [{"text": "Understood. I will follow those instructions."}]}
            )
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        temperature = 0.9
        max_tokens = 256
        if options:
            temperature = options.get("temperature", temperature)
            max_tokens = options.get("max_tokens", max_tokens)

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = f"{self.base_url}/models/{self.model}:generateContent"
        resp = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=self.timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates") or []
        if candidates and isinstance(candidates[0], dict):
            content = candidates[0].get("content") or {}
            parts = content.get("parts") or []
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            return "".join(texts)
        return ""
