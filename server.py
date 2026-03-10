"""
FastAPI entrypoint for hosting platforms (local / Railway / Render / etc).

Many platforms scan for an `app` object in common filenames like
`server.py`, `main.py`, or `app.py`. This thin wrapper simply exposes
the existing FastAPI instance defined in `frontend/server.py`.

NOTE: For Vercel serverless deployment, use the api/ directory instead.
This file imports from agents/debates/utils/scoring which are only
available when the full project is installed (not on Vercel).
"""

try:
    from frontend.server import app  # noqa: F401
except ImportError:
    # Graceful fallback when running in environments where the full
    # project dependencies are not installed (e.g., Vercel build step).
    app = None

__all__ = ["app"]
