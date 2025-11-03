"""Main API router aggregating all module endpoints."""

from fastapi import APIRouter

from app.auth import auth_router
from app.trips import trips_router
from app.flights import flights_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all module routers
api_router.include_router(auth_router)
api_router.include_router(trips_router)
api_router.include_router(flights_router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}