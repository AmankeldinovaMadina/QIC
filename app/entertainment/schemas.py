"""Entertainment schemas for Google Maps venues and AI ranking."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GPSCoordinates(BaseModel):
    """GPS coordinates for a venue."""

    latitude: float
    longitude: float


class OperatingHours(BaseModel):
    """Operating hours for a venue."""

    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None


class GoogleMapsVenue(BaseModel):
    """Venue information from Google Maps API."""

    position: int
    place_id: str
    data_id: Optional[str] = None
    data_cid: Optional[str] = None
    title: str
    rating: Optional[float] = None
    reviews: Optional[int] = None
    price: Optional[str] = None  # $, $$, $$$, $$$$
    type: Optional[str] = None
    types: Optional[List[str]] = None
    type_id: Optional[str] = None
    type_ids: Optional[List[str]] = None
    address: Optional[str] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    open_state: Optional[str] = None
    hours: Optional[str] = None
    operating_hours: Optional[OperatingHours] = None
    thumbnail: Optional[str] = None
    service_options: Optional[Dict[str, Any]] = None


class EntertainmentSearchRequest(BaseModel):
    """Request for searching entertainment venues."""

    trip_id: str
    destination: str  # City name
    query: Optional[str] = None  # Optional custom query, otherwise uses entertainment_tags
    latitude: Optional[float] = None  # For GPS-based search
    longitude: Optional[float] = None
    zoom: Optional[str] = "14z"  # Map zoom level


class EntertainmentSearchResponse(BaseModel):
    """Response containing Google Maps search results."""

    search_id: str
    trip_id: str
    query: str
    destination: str
    venues: List[GoogleMapsVenue]
    total_results: int


class EntertainmentRankRequest(BaseModel):
    """Request for ranking entertainment venues using AI."""

    trip_id: str
    search_id: str
    venues: List[GoogleMapsVenue]
    preferences_prompt: Optional[str] = None  # Custom preferences, or uses entertainment_tags
    entertainment_tags: Optional[List[str]] = None  # From trip


class EntertainmentRankItem(BaseModel):
    """Individual ranked entertainment venue."""

    place_id: str
    score: float = Field(ge=0.0, le=1.0)
    title: str = Field(max_length=140)
    rationale_short: str = Field(max_length=240)
    pros_keywords: List[str] = Field(max_items=8)
    cons_keywords: List[str] = Field(max_items=8)
    tags: Optional[List[str]] = None


class EntertainmentRankMeta(BaseModel):
    """Metadata about the ranking process."""

    used_model: str
    deterministic: bool
    notes: Optional[List[str]] = None


class EntertainmentRankResponse(BaseModel):
    """Response containing ranked entertainment venues."""

    trip_id: str
    search_id: str
    ordered_place_ids: List[str]
    items: List[EntertainmentRankItem]
    meta: EntertainmentRankMeta


class EntertainmentSelectionRequest(BaseModel):
    """Request to select one or more entertainment venues for a trip."""

    trip_id: str
    selections: List[Dict[str, Any]]  # Array of venue data with AI ranking info


class EntertainmentSelectionResponse(BaseModel):
    """Response after selecting entertainment venues."""

    success: bool
    message: str
    trip_id: str
    selected_count: int
    selections: List[Dict[str, Any]]
