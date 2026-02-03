"""
FastAPI entrypoint for hosting platforms.

Many platforms scan for an `app` object in common filenames like
`server.py`, `main.py`, or `app.py`. This thin wrapper simply exposes
the existing FastAPI instance defined in `frontend/server.py`.
"""

from frontend.server import app  # noqa: F401

__all__ = ["app"]

