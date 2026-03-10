"""
FastAPI entrypoint for hosting platforms.

Vercel (and similar platforms) scan for an `app` object in files like
server.py, main.py, app.py. This module tries to load the full app from
frontend/server.py.  If that fails (e.g. heavy deps not installed), it
falls back to a minimal FastAPI stub so the deploy doesn't crash.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

try:
    from frontend.server import app  # noqa: F401
except Exception:
    # Minimal stub so Vercel always finds a valid ASGI app.
    app = FastAPI(title="AgonAI")

    @app.get("/")
    async def root():
        return JSONResponse({
            "status": "ok",
            "service": "AgonAI",
            "note": "Full app unavailable — use /api/chat or /api/simulate",
        })

__all__ = ["app"]
