"""Flights module exports."""

from .ai_ranker import OpenAIFlightRanker
from .router import router as flights_router
from .schemas import (
    FlightLeg,
    Itinerary,
    Locale,
    Price,
    RankItem,
    RankMeta,
    RankRequest,
    RankResponse,
)

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
