from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import os
import json

from agents import HitlerAgent, GandhiAgent, JinnahAgent
from debates import DebateSimulator
from utils.ollama_client import OllamaClient
from utils.conversation_state import InMemoryConversationStore, load_state
from utils.memory_clients import SuperMemoryClient, ExaContextClient

app = FastAPI(title="AI Political Agents Frontend")
conversation_store = InMemoryConversationStore()

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def create_agent(
    agent_name: str,
    llm_client: Optional[OllamaClient] = None,
    memory_client: Optional[SuperMemoryClient] = None,
):
    agents = {
        "hitler": HitlerAgent,
        "gandhi": GandhiAgent,
        "jinnah": JinnahAgent,
    }
    key = agent_name.lower()
    if key not in agents:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(agents.keys())}")
    return agents[key](llm_client=llm_client, memory_client=memory_client)


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
    model: Optional[str] = body.get("model")
    base_url: Optional[str] = body.get("baseUrl")
    session_id: Optional[str] = body.get("sessionId")

    if len(agent_names) < 2:
        return JSONResponse({"error": "Select at least two agents"}, status_code=400)
    if not topic:
        return JSONResponse({"error": "Topic is required"}, status_code=400)

    ollama_client: Optional[OllamaClient] = None
    memory_client = SuperMemoryClient()
    exa_client = ExaContextClient()
    if use_ollama:
        ollama_client = OllamaClient(base_url=base_url, model=model)

    # Build agents
    conversation_state = load_state(session_id=session_id, store=conversation_store)
    if not conversation_state.turns:
        conversation_state.append_turn("user", f"Run a debate on: {topic}")
    agents = [create_agent(name, llm_client=ollama_client, memory_client=memory_client) for name in agent_names]

    # Run debate
    simulator = DebateSimulator(max_rounds=rounds, consensus_threshold=0.7)
    result = simulator.debate(
        agents=agents,
        topic=topic,
        initial_context={
            "historical_period": "1940s",
            "context": "High-stakes political negotiation",
            "stakes": "Critical - involves national interests and survival",
            "use_llm": bool(ollama_client is not None),
            "memory_provider": "supermemory",
            "context_provider": "exa",
            "context_briefing": exa_client.fetch_context(topic),
            "conversation_state": conversation_state,
        }
    )

    payload: Dict[str, Any] = {
        "agents": agent_names,
        "topic": topic,
        "status": result.status.value,
        "consensusScore": round(result.consensus_score, 4),
        "rounds": len(result.rounds),
        "durationMinutes": round(result.duration_minutes, 2),
        "agreements": result.key_agreements,
        "disagreements": result.key_disagreements,
        "usedOllama": bool(ollama_client is not None),
        "model": model or os.environ.get("OLLAMA_MODEL"),
        "sessionId": conversation_state.session_id,
    }
    payload["majorityVote"] = result.majority_vote
    payload["finalResolution"] = result.final_resolution
    if not summary_only:
        payload["transcript"] = simulator.get_debate_transcript()

    return JSONResponse(payload)
