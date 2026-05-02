# =============================================================================
# routes/base.py — Health Check Endpoint
# =============================================================================
# PURPOSE:
#   Provides a simple GET endpoint to confirm the API is alive.
#   Also demonstrates the basic FastAPI router pattern used throughout.
#
# ENDPOINT: GET /api/
# CALLED BY: Anything that wants to verify the server is running.
#            (docker healthcheck, Streamlit UI on startup, Postman tests)
#
# TEAM NOTE (Pair B — Member 4):
#   This is the simplest route — implement it first to validate that
#   FastAPI is wired up correctly before touching the complex routes.
# =============================================================================

from fastapi import APIRouter, Depends
from helpers.config import Settings, get_settings

base_router = APIRouter(prefix="/api", tags=["health"])


@base_router.get("/")
async def welcome(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint.
    Returns the app name and version from config.

    Response:
        {"message": "Welcome to Mini-RAG v0.1.0!"}
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}!"
    }
