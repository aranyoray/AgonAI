import os
import requests
from typing import Optional, Dict, Any


class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout_seconds: int = 60):
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or "llama3.1:8b"
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str, system: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options
        resp = requests.post(url, json=payload, timeout=self.timeout_seconds)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
