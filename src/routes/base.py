from fastapi import APIRouter, Depends
from helpers.config import Settings, get_settings

base_router = APIRouter(tags=["health"])


@base_router.get("/health")
async def welcome(settings: Settings = Depends(get_settings)):
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status":  "healthy"
    }
