from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import os
import json

from agents import (
    HitlerAgent, GandhiAgent, JinnahAgent,
    RationalAgent, EmpatheticAgent, JudgeAgent,
)
from debates import DebateSimulator
from debates.experiment_runner import (
    get_experiment_configs, run_experiment, run_all_experiments,
    EXPERIMENT_TOPICS,
)
from utils.ollama_client import OllamaClient
from utils.gemini_client import GeminiClient
from utils.conversation_state import InMemoryConversationStore, load_state
from utils.memory_clients import SuperMemoryClient, ExaContextClient

app = FastAPI(title="AI Political Agents Frontend")
conversation_store = InMemoryConversationStore()

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


AGENT_REGISTRY: Dict[str, Any] = {
    "hitler": HitlerAgent,
    "gandhi": GandhiAgent,
    "jinnah": JinnahAgent,
    "rational": lambda **kw: RationalAgent(**kw),
    "empathetic": lambda **kw: EmpatheticAgent(**kw),
}


def create_agent(
    agent_name: str,
    llm_client: Optional[OllamaClient] = None,
    memory_client: Optional[SuperMemoryClient] = None,
):
    key = agent_name.lower()
    if key in ("rational", "empathetic"):
        return AGENT_REGISTRY[key](llm_client=llm_client, memory_client=memory_client)
    if key not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(AGENT_REGISTRY.keys())}")
    return AGENT_REGISTRY[key](llm_client=llm_client, memory_client=memory_client)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/simulate")
async def simulate(request: Request) -> JSONResponse:
    body = await request.json()
    agent_names: List[str] = body.get("agents", [])
    topic: str = body.get("topic", "")
    rounds: int = int(body.get("rounds", 12))
    summary_only: bool = bool(body.get("summaryOnly", True))
    use_ollama: bool = bool(body.get("useOllama", False))
    use_gemini: bool = bool(body.get("useGemini", False))
    model: Optional[str] = body.get("model")
    base_url: Optional[str] = body.get("baseUrl")
    session_id: Optional[str] = body.get("sessionId")

    if len(agent_names) < 2:
        return JSONResponse({"error": "Select at least two agents"}, status_code=400)
    if not topic:
        return JSONResponse({"error": "Topic is required"}, status_code=400)

    llm_client = None
    memory_client = SuperMemoryClient()
    exa_client = ExaContextClient()
    if use_gemini:
        llm_client = GeminiClient(model=model)
    elif use_ollama:
        llm_client = OllamaClient(base_url=base_url, model=model)

    # Build agents
    conversation_state = load_state(session_id=session_id, store=conversation_store)
    if not conversation_state.turns:
        conversation_state.append_turn("user", f"Run a debate on: {topic}")
    agents = [create_agent(name, llm_client=llm_client, memory_client=memory_client) for name in agent_names]

    # Run debate
    simulator = DebateSimulator(max_rounds=rounds, consensus_threshold=0.7)
    result = simulator.debate(
        agents=agents,
        topic=topic,
        initial_context={
            "historical_period": "1940s",
            "context": "High-stakes political negotiation",
            "stakes": "Critical - involves national interests and survival",
            "use_llm": llm_client is not None,
            "memory_provider": "supermemory",
            "context_provider": "exa",
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

    # Build transcript with chat messages
    chat_messages = []
    for rd in result.rounds:
        chat_messages.append({
            "round": rd.round_number,
            "speaker": rd.speaker,
            "content": rd.response.strip(),
        })

    payload: Dict[str, Any] = {
        "agents": agent_names,
        "topic": topic,
        "status": result.status.value,
        "consensusScore": round(result.consensus_score, 4),
        "rounds": len(result.rounds),
        "durationMinutes": round(result.duration_minutes, 2),
        "agreements": result.key_agreements,
        "disagreements": result.key_disagreements,
        "usedLLM": llm_client is not None,
        "llmBackend": "gemini" if use_gemini else ("ollama" if use_ollama else None),
        "model": model or (os.environ.get("GEMINI_MODEL") if use_gemini else os.environ.get("OLLAMA_MODEL")),
        "sessionId": conversation_state.session_id,
        "chatMessages": chat_messages,
        "policyScores": {a.name: a.scorecard.as_dict() for a in agents},
        "empathyRatios": {a.name: round(a.empathy_ratio, 3) for a in agents},
        "oceanTraits": {a.name: a.ocean.as_dict() for a in agents},
    }
    payload["majorityVote"] = result.majority_vote
    payload["finalResolution"] = result.final_resolution
    if not summary_only:
        payload["transcript"] = simulator.get_debate_transcript()

    return JSONResponse(payload)


@app.post("/experiment")
async def run_experiment_endpoint(request: Request) -> JSONResponse:
    """Run one of the 8 pre-configured experiments."""
    body = await request.json()
    experiment_id: int = int(body.get("experimentId", 1))
    topic: str = body.get("topic", "war")
    max_rounds: int = int(body.get("maxRounds", 15))

    # Build historical agents if needed (for experiments 5-8)
    historical_agents = None
    hist_names = body.get("historicalAgents", [])
    if len(hist_names) >= 2:
        historical_agents = [create_agent(n) for n in hist_names[:2]]

    configs = get_experiment_configs(
        topic=topic,
        historical_agents=historical_agents,
        max_rounds=max_rounds,
    )

    # Select the requested experiment (1-indexed)
    idx = max(0, min(experiment_id - 1, len(configs) - 1))
    if idx >= len(configs):
        return JSONResponse({"error": f"Experiment {experiment_id} not available"}, status_code=400)

    result = run_experiment(configs[idx])
    return JSONResponse(result.as_dict())


@app.get("/experiments/list")
async def list_experiments() -> JSONResponse:
    """List available experiments and topics."""
    return JSONResponse({
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
        "agents": list(AGENT_REGISTRY.keys()),
    })
