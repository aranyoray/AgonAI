"""
Memory and context clients for debate simulations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import os
import requests


@dataclass
class MemoryEvent:
    speaker: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SuperMemoryClient:
    """
    Placeholder memory service client.

    Falls back to in-memory summaries when remote access is unavailable.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: float = 3.0,
    ) -> None:
        self.api_key = api_key or os.getenv(
            "SUPERMEMORY_API_KEY",
            "sm_ytv7FS5jkifRGCuZvBWyhz_GAptVZLTQweosUiPuogXSGmwLucudgCWilbxXszxqepfvbDMGwtPioWYOXcZkCuF",
        )
        self.base_url = base_url or os.getenv("SUPERMEMORY_BASE_URL")
        self.timeout_s = timeout_s
        self._events: Dict[str, List[MemoryEvent]] = {}

    def record_event(self, agent_name: str, speaker: str, content: str, metadata: Dict[str, Any]) -> None:
        self._events.setdefault(agent_name, []).append(
            MemoryEvent(speaker=speaker, content=content, metadata=metadata)
        )
        if not self.base_url:
            return
        try:
            requests.post(
                f"{self.base_url.rstrip('/')}/memory",
                json={
                    "agent": agent_name,
                    "speaker": speaker,
                    "content": content,
                    "metadata": metadata,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout_s,
            )
        except requests.RequestException:
            return

    def summarize_recent(self, agent_name: str, window: int = 8) -> str:
        events = self._events.get(agent_name, [])[-window:]
        if not events:
            return "No recent memory available."
        summary_lines = []
        for event in events:
            snippet = event.content.replace("\n", " ").strip()
            if len(snippet) > 140:
                snippet = snippet[:137].rstrip() + "..."
            summary_lines.append(f"- {event.speaker}: {snippet}")
        return "\n".join(summary_lines)


class ExaContextClient:
    """
    Placeholder context client to fetch background or summaries.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: float = 3.0,
    ) -> None:
        self.api_key = api_key or os.getenv("EXA_API_KEY", "7557a88a-52af-4489-8e5b-7c3a9e9b77a4")
        self.base_url = base_url or os.getenv("EXA_BASE_URL")
        self.timeout_s = timeout_s

    def fetch_context(self, query: str) -> Optional[str]:
        if not self.base_url:
            return None
        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/search",
                json={"query": query},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("summary")
        except (requests.RequestException, ValueError):
            return None
