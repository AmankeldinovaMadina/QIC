"""Flight domain models and schemas."""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class FlightLeg(BaseModel):
    """Individual flight leg."""
    dep_iata: str = Field(..., description="Departure airport IATA code")
    dep_time: datetime = Field(..., description="Departure time in ISO format")
    arr_iata: str = Field(..., description="Arrival airport IATA code") 
    arr_time: datetime = Field(..., description="Arrival time in ISO format")
    marketing: str = Field(..., description="Marketing airline code (e.g., 'DL')")
    operating: Optional[str] = Field(None, description="Operating airline if different")
    flight_no: str = Field(..., description="Full flight number (e.g., 'DL 1384')")
    duration_min: int = Field(..., description="Flight duration in minutes")


class Price(BaseModel):
    """Price information."""
    amount: Decimal = Field(..., description="Price amount")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")


class Itinerary(BaseModel):
    """Complete flight itinerary."""
    id: str = Field(..., description="Stable hash of legs + carrier + times")
    type: Literal['ONE_WAY', 'ROUND_TRIP'] = Field(..., description="Trip type")
    price: Price = Field(..., description="Total price")
    total_duration_min: int = Field(..., description="Total travel duration")
    stops: int = Field(..., description="Number of stops (0=nonstop)")
    emissions_kg: Optional[int] = Field(None, description="CO2 emissions in kg")
    layovers_min: Optional[List[int]] = Field(None, description="Layover durations in minutes")
    legs: List[FlightLeg] = Field(..., description="Flight legs")
    
    # Internal tokens (not exposed to client)
    tokens: Optional[Dict[str, str]] = Field(None, description="Booking/departure tokens")


class SearchInsights(BaseModel):
    """Search insights from provider."""
    lowest: Decimal = Field(..., description="Lowest price found")
    typical_range: Optional[List[Decimal]] = Field(None, description="Typical price range [min, max]")
    level: Optional[Literal['low', 'typical', 'high']] = Field(None, description="Price level")


class SearchResult(BaseModel):
    """Flight search result."""
    search_id: str = Field(..., description="Unique search identifier")
    currency: str = Field(..., description="Currency for all prices")
    insights: Optional[SearchInsights] = Field(None, description="Price insights")
    itineraries: List[Itinerary] = Field(..., description="Found itineraries")


# Search request schemas
class FlightSearchParams(BaseModel):
    """Flight search parameters."""
    type: Literal[1, 2] = Field(..., description="1=round-trip, 2=one-way")
    departure_id: str = Field(..., description="Departure airport/city code")
    arrival_id: str = Field(..., description="Arrival airport/city code") 
    outbound_date: str = Field(..., description="Outbound date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date for round-trip")
    currency: str = Field(default="USD", description="Currency code")
    hl: str = Field(default="en", description="Language")
    gl: str = Field(default="us", description="Country")
    sort_by: Optional[Literal['best', 'price', 'duration', 'emissions']] = Field(None)
    travel_class: Optional[Literal[1, 2, 3, 4]] = Field(None, description="1=economy, 2=premium, 3=business, 4=first")
    adults: int = Field(default=1, ge=1, le=9, description="Number of adults")
    children: int = Field(default=0, ge=0, le=8, description="Number of children")
    infants_in_seat: int = Field(default=0, ge=0, le=8)
    infants_on_lap: int = Field(default=0, ge=0, le=8)
    max_stops: Optional[int] = Field(None, ge=0, le=2, description="Maximum stops")
    include_airlines: Optional[str] = Field(None, description="Comma-separated airline codes")
    exclude_airlines: Optional[str] = Field(None, description="Comma-separated airline codes to exclude")
    exclude_basic: Optional[bool] = Field(None, description="Exclude basic economy (US only)")
    deep_search: Optional[bool] = Field(None, description="Enable deep search")


# AI ranking schemas
class LocalePrefs(BaseModel):
    """Locale preferences for AI ranking."""
    hl: str = Field(default="en", description="Language")
    currency: str = Field(default="USD", description="Currency")
    tz: Optional[str] = Field(None, description="Timezone")


class RankRequest(BaseModel):
    """Request to rank flights with AI."""
    search_id: str = Field(..., description="Search ID from flight search")
    preferences_prompt: str = Field(..., description="User preferences in natural language")
    flights: List[Itinerary] = Field(..., description="Flights to rank")
    locale: Optional[LocalePrefs] = Field(default_factory=LocalePrefs)


class RankItem(BaseModel):
    """Individual ranked flight item."""
    id: str = Field(..., description="Flight itinerary ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score")
    title: str = Field(..., max_length=140, description="Short title/summary")
    rationale_short: str = Field(..., max_length=240, description="Brief explanation")
    pros_keywords: List[str] = Field(..., max_items=8, description="Positive keywords")
    cons_keywords: List[str] = Field(..., max_items=8, description="Negative keywords")
    tags: Optional[List[str]] = Field(None, max_items=5, description="Additional tags")


class RankMeta(BaseModel):
    """Ranking metadata."""
    used_model: str = Field(..., description="AI model used")
    deterministic: bool = Field(..., description="Whether result is deterministic")
    notes: Optional[List[str]] = Field(None, description="Additional notes")


class RankResponse(BaseModel):
    """Response from AI ranking."""
    search_id: str = Field(..., description="Original search ID")
    ordered_ids: List[str] = Field(..., description="Flight IDs in ranked order")
    items: List[RankItem] = Field(..., description="Ranked items with details")
    meta: RankMeta = Field(..., description="Ranking metadata")