from fastapi import APIRouter, Depends
from helpers.config import Settings, get_settings

base_router = APIRouter(prefix="/api", tags=["health"])


@base_router.get("/")
async def welcome(settings: Settings = Depends(get_settings)):
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}!"
    }
