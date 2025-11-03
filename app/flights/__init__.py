"""Flights module exports."""

from .router import router as flights_router
from .schemas import (
    RankRequest,
    RankResponse,
    RankItem,
    RankMeta,
    Itinerary,
    FlightLeg,
    Price,
    Locale
)
from .ai_ranker import OpenAIFlightRanker

__all__ = [
    "flights_router",
    "RankRequest",
    "RankResponse", 
    "RankItem",
    "RankMeta",
    "Itinerary",
    "FlightLeg",
    "Price",
    "Locale",
    "OpenAIFlightRanker",
]