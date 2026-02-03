# AI Political Agents Project

A system for simulating political debates and negotiations between AI agents modeled after historical figures with opposing ideologies.

## Research Question
Can political AI agents of historical figures who opposed each other reach a consensus in a simulated setting?

## Example Scenarios
- **Hitler vs Gandhi vs Jinnah**: Exploring ideological conflicts and potential common ground
- **US vs Japan**: Could the atomic bomb have been prevented? How?
- **Trump vs Mao**: Trade and tariff negotiations
- **Winston Churchill vs Karl Marx vs Niccolò Machiavelli**: Different political ideologies

## Key Features
- Historical figure personality modeling
- Multi-agent debate system
- Consensus detection and analysis
- Real-time negotiation simulation
- Optional Ollama LLM integration (local)
- Minimal FastAPI web UI

## Project Structure
```
├── agents/           # Historical figure AI agents
├── debates/          # Debate simulation system
├── frontend/         # FastAPI + HTML minimal frontend
├── utils/            # Utilities (Ollama client)
├── consensus/        # Consensus detection algorithms
├── data/             # Historical data and context
└── examples/         # Example scenarios and outputs
```

## Quick Start (CLI)
```bash
python3 main.py --agents hitler gandhi jinnah --topic territorial_disputes --rounds 10 --format json --summary-only
```

## Optional: Use Ollama for LLM Responses
- Install Ollama: see `https://ollama.com`
- Start server (macOS): `ollama serve`
- Pull a model (example): `ollama pull llama3.1:8b`
- Configure (optional):
  - `export OLLAMA_BASE_URL=http://localhost:11434`
  - `export OLLAMA_MODEL=llama3.1:8b`
- In FastAPI UI, check "Use Ollama" and optionally set base URL/model.

## Chat API (Serverless)
- Vercel route: `POST /api/chat`
- Recommended env (Gemini): `GOOGLE_CLOUD_API_KEY`
- Legacy env (xAI/Grok, no longer default): `XAI_API_KEY` or `GROK_API_KEY`
- Optional tuning:
  - `XAI_BASE_URL` (default `https://api.x.ai/v1`)
  - `CHAT_CACHE_TTL_S` (default 120 seconds)
  - `CHAT_CACHE_MAX_ITEMS` (default 256)

## Conversation Memory (Chat Continuity)
- The simulator keeps a short-term memory window (default: 8 turns) plus a rolling summary.
- It tracks salient user preferences, open loops, and consensus metrics to keep replies coherent.
- Tuning knobs (see `utils/conversation_state.py`):
  - `memory_window` (default 8)
  - `compromise_threshold` (default 0.7)
  - `weights` for consensus scoring

## Run Local Frontend (FastAPI)
```bash
uvicorn frontend.server:app --reload
```
Then open `http://127.0.0.1:8000`.

## Streamlit UI (Alternative)
```bash
pip3 install -r requirements.txt
streamlit run web_app.py
```

## License
MIT
