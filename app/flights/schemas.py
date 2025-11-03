"""Flight-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Price information."""

    amount: float
    currency: str


class FlightLeg(BaseModel):
    """Individual flight leg information."""

    dep_iata: str
    dep_time: datetime
    arr_iata: str
    arr_time: datetime
    marketing: str
    flight_no: str
    duration_min: int


class Itinerary(BaseModel):
    """Flight itinerary information."""

    id: str
    price: Price
    total_duration_min: int
    stops: int
    emissions_kg: Optional[float] = None
    layovers_min: Optional[int] = None
    legs: List[FlightLeg]


class Locale(BaseModel):
    """Locale preferences."""

    hl: Optional[str] = "en"
    currency: Optional[str] = "USD"
    tz: Optional[str] = None


class RankRequest(BaseModel):
    """Request for flight ranking."""

    search_id: str
    flights: List[Itinerary]
    preferences_prompt: str
    locale: Optional[Locale] = None


class RankItem(BaseModel):
    """Individual ranked flight item."""

    id: str
    score: float = Field(ge=0.0, le=1.0)
    title: str = Field(max_length=140)
    rationale_short: str = Field(max_length=240)
    pros_keywords: List[str] = Field(max_items=8)
    cons_keywords: List[str] = Field(max_items=8)
    tags: Optional[List[str]] = None


class RankMeta(BaseModel):
    """Metadata about the ranking process."""

    used_model: str
    deterministic: bool
    notes: Optional[List[str]] = None


class RankResponse(BaseModel):
    """Response containing ranked flights."""

    search_id: str
    ordered_ids: List[str]
    items: List[RankItem]
    meta: RankMeta


# Additional schemas for the test
class Segment(BaseModel):
    """Flight segment for testing."""

    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
