"""
Vercel serverless function for running experiments.

Handles POST /api/experiment (rewritten from /experiment).
Also handles GET /api/experiment (rewritten from /experiments/list).
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

_boot_error = ""
try:
    from agents import HitlerAgent, GandhiAgent, JinnahAgent
    from debates.experiment_runner import (
        get_experiment_configs,
        run_experiment,
        EXPERIMENT_TOPICS,
    )
except ImportError:
    _boot_error = traceback.format_exc()

AGENT_MAP: Dict[str, Any] = {}
if not _boot_error:
    AGENT_MAP = {
        "hitler": HitlerAgent,
        "gandhi": GandhiAgent,
        "jinnah": JinnahAgent,
    }


def _create_agent(name: str) -> Any:
    key = name.lower()
    if key not in AGENT_MAP:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENT_MAP.keys())}")
    return AGENT_MAP[key]()


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """List available experiments and topics."""
        if _boot_error:
            self._send(500, {"error": "Boot failed", "detail": _boot_error})
            return
        self._send(200, {
            "experiments": [
                {"id": 1, "name": "Rational vs Rational", "needsHistorical": False},
                {"id": 2, "name": "Empathetic vs Empathetic", "needsHistorical": False},
                {"id": 3, "name": "Rational vs Empathetic", "needsHistorical": False},
                {"id": 4, "name": "Low Empathy vs High Empathy", "needsHistorical": False},
                {"id": 5, "name": "Historical Conflict", "needsHistorical": True},
                {"id": 6, "name": "Historical + Empathy Injection", "needsHistorical": True},
                {"id": 7, "name": "Historical + Judge", "needsHistorical": True},
                {"id": 8, "name": "Full Pipeline", "needsHistorical": True},
            ],
            "topics": EXPERIMENT_TOPICS,
            "agents": list(AGENT_MAP.keys()),
        })

    def do_POST(self) -> None:
        try:
            self._handle_post()
        except Exception:
            self._send(500, {"error": "Internal server error", "detail": traceback.format_exc()})

    def _handle_post(self) -> None:
        if _boot_error:
            self._send(500, {"error": "Boot failed", "detail": _boot_error})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(raw or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON body"})
            return

        experiment_id: int = int(body.get("experimentId", 1))
        topic: str = body.get("topic", "war")
        max_rounds: int = int(body.get("maxRounds", 15))

        # Build historical agents if needed (for experiments 5-8)
        historical_agents = None
        hist_names: List[str] = body.get("historicalAgents", [])
        if len(hist_names) >= 2:
            try:
                historical_agents = [_create_agent(n) for n in hist_names[:2]]
            except ValueError as exc:
                self._send(400, {"error": str(exc)})
                return

        configs = get_experiment_configs(
            topic=topic,
            historical_agents=historical_agents,
            max_rounds=max_rounds,
        )

        idx = experiment_id - 1
        if idx < 0 or idx >= len(configs):
            self._send(400, {"error": f"Experiment {experiment_id} not available"})
            return

        result = run_experiment(configs[idx])
        raw_dict = result.as_dict()

        # Map keys to match what the frontend expects
        raw_dict["key_agreements"] = raw_dict.pop("agreements", [])
        raw_dict["key_disagreements"] = raw_dict.pop("disagreements", [])
        raw_dict["policy_scores"] = raw_dict.pop("scorecards", {})

        # Build transcript for the chat display
        raw_dict["transcript"] = [
            {
                "round_number": rd.round_number,
                "speaker": rd.speaker,
                "response": rd.response,
            }
            for rd in result.debate_result.rounds
        ]

        self._send(200, raw_dict)
