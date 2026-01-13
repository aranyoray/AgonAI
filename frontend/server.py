from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import os
import json

from agents import HitlerAgent, GandhiAgent, JinnahAgent
from debates import DebateSimulator
from utils.ollama_client import OllamaClient

app = FastAPI(title="AI Political Agents Frontend")

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def create_agent(agent_name: str, llm_client: Optional[OllamaClient] = None):
    agents = {
        "hitler": HitlerAgent,
        "gandhi": GandhiAgent,
        "jinnah": JinnahAgent,
    }
    key = agent_name.lower()
    if key not in agents:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(agents.keys())}")
    return agents[key](llm_client=llm_client)


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

    if len(agent_names) < 2:
        return JSONResponse({"error": "Select at least two agents"}, status_code=400)
    if not topic:
        return JSONResponse({"error": "Topic is required"}, status_code=400)

    ollama_client: Optional[OllamaClient] = None
    if use_ollama:
        ollama_client = OllamaClient(base_url=base_url, model=model)

    # Build agents
    agents = [create_agent(name, llm_client=ollama_client) for name in agent_names]

    # Run debate
    simulator = DebateSimulator(max_rounds=rounds, consensus_threshold=0.7)
    result = simulator.debate(
        agents=agents,
        topic=topic,
        initial_context={
            "historical_period": "1940s",
            "context": "High-stakes political negotiation",
            "stakes": "Critical - involves national interests and survival",
            "use_llm": bool(ollama_client is not None)
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
        "model": model or os.environ.get("OLLAMA_MODEL")
    }
    if not summary_only:
        payload["transcript"] = simulator.get_debate_transcript()

    return JSONResponse(payload)
