"""
Vercel serverless function for running debate simulations.

Handles POST /api/simulate with the same interface as the FastAPI endpoint.
Self-contained: adds project root to sys.path so all imports resolve.
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

# Ensure project root is on the path so agents/debates/scoring/utils resolve
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

_boot_error = ""
try:
    from agents import HitlerAgent, GandhiAgent, JinnahAgent, RationalAgent, EmpatheticAgent
    from debates import DebateSimulator
    from utils.conversation_state import InMemoryConversationStore, load_state
    from utils.memory_clients import SuperMemoryClient, ExaContextClient
    from utils.gemini_client import GeminiClient
except ImportError:
    _boot_error = traceback.format_exc()

_conversation_store: Any = None

AGENT_MAP: Dict[str, Any] = {}
if not _boot_error:
    _conversation_store = InMemoryConversationStore()
    AGENT_MAP = {
        "hitler": HitlerAgent,
        "gandhi": GandhiAgent,
        "jinnah": JinnahAgent,
        "rational": lambda **kw: RationalAgent(**{k: v for k, v in kw.items() if k in ("llm_client", "memory_client")}),
        "empathetic": lambda **kw: EmpatheticAgent(**{k: v for k, v in kw.items() if k in ("llm_client", "memory_client")}),
    }


def _create_agent(name: str, llm_client: Any = None, memory_client: Any = None) -> Any:
    key = name.lower()
    if key in ("rational", "empathetic"):
        return AGENT_MAP[key](llm_client=llm_client, memory_client=memory_client)
    if key not in AGENT_MAP:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENT_MAP.keys())}")
    return AGENT_MAP[key](llm_client=llm_client, memory_client=memory_client)


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if _boot_error:
            self._send(500, {"error": "Boot failed", "detail": _boot_error})
            return
        self._send(200, {
            "status": "ok",
            "service": "simulate",
            "agents": list(AGENT_MAP.keys()),
            "python": sys.version,
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

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON body"})
            return

        agent_names: List[str] = body.get("agents", [])
        topic: str = body.get("topic", "")
        rounds: int = int(body.get("rounds", 12))
        use_gemini: bool = bool(body.get("useGemini", False))
        model: Optional[str] = body.get("model")
        session_id: Optional[str] = body.get("sessionId")

        if len(agent_names) < 2:
            self._send(400, {"error": "Select at least two agents"})
            return
        if not topic:
            self._send(400, {"error": "Topic is required"})
            return

        llm_client = None
        if use_gemini:
            llm_client = GeminiClient(model=model)

        memory_client = SuperMemoryClient()
        exa_client = ExaContextClient()

        conversation_state = load_state(session_id=session_id, store=_conversation_store)
        if not conversation_state.turns:
            conversation_state.append_turn("user", f"Run a debate on: {topic}")

        try:
            agents = [_create_agent(name, llm_client=llm_client, memory_client=memory_client) for name in agent_names]
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
            return

        simulator = DebateSimulator(max_rounds=rounds, consensus_threshold=0.7)
        result = simulator.debate(
            agents=agents,
            topic=topic,
            initial_context={
                "historical_period": "1940s",
                "context": "High-stakes political negotiation",
                "stakes": "Critical - involves national interests and survival",
                "use_llm": llm_client is not None,
                "context_briefing": exa_client.fetch_context(topic),
                "conversation_state": conversation_state,
                "policy_scoring": True,
            }
        )

        # Score each round
        for round_num, rd in enumerate(result.rounds):
            speaker = next((a for a in agents if a.name == rd.speaker), None)
            if speaker:
                opponent_obj = 0.0
                for other in agents:
                    if other.name != speaker.name and other.scorecard.objective_values:
                        opponent_obj = other.scorecard.objective_values[-1]
                speaker.score_round(
                    topic=topic,
                    round_number=round_num + 1,
                    max_rounds=rounds,
                    opponent_objective=opponent_obj,
                )

        chat_messages = [
            {"round": rd.round_number, "speaker": rd.speaker, "content": rd.response.strip()}
            for rd in result.rounds
        ]

        payload: Dict[str, Any] = {
            "agents": agent_names,
            "topic": topic,
            "status": result.status.value,
            "consensusScore": round(result.consensus_score, 4),
            "rounds": len(result.rounds),
            "durationMinutes": round(result.duration_minutes, 2),
            "agreements": result.key_agreements,
            "disagreements": result.key_disagreements,
            "sessionId": conversation_state.session_id,
            "chatMessages": chat_messages,
            "policyScores": {a.name: a.scorecard.as_dict() for a in agents},
            "empathyRatios": {a.name: round(a.empathy_ratio, 3) for a in agents},
            "oceanTraits": {a.name: a.ocean.as_dict() for a in agents},
            "majorityVote": result.majority_vote,
            "finalResolution": result.final_resolution,
        }

        self._send(200, payload)
