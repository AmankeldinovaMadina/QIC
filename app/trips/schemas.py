"""Trip schemas and DTOs."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator

from app.db.models import TransportType, TripStatus


class SelectedFlightInfo(BaseModel):
    """Selected flight information for a trip."""

    flight_id: str
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str
    total_duration_min: int
    stops: int
    score: Optional[float] = None
    title: Optional[str] = None
    pros_keywords: Optional[List[str]] = None
    cons_keywords: Optional[List[str]] = None


# Import SelectedHotelInfo from hotels module at the top level for use in TripResponse
# This will be set after hotels module is loaded
SelectedHotelInfo = None


class TripCreateRequest(BaseModel):
    """Trip creation request."""

    from_city: str = Field(..., min_length=1, max_length=100)
    to_city: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    transport: TransportType
    adults: int = Field(default=1, ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)
    budget_min: Optional[Decimal] = Field(default=None, ge=0)
    budget_max: Optional[Decimal] = Field(default=None, ge=0)
    entertainment_tags: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=5000)
    timezone: Optional[str] = Field(default=None, max_length=50)

    @validator("end_date")
    def end_date_after_start_date(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    @validator("budget_max")
    def budget_max_greater_than_min(cls, v, values):
        if (
            v is not None
            and "budget_min" in values
            and values["budget_min"] is not None
        ):
            if v < values["budget_min"]:
                raise ValueError(
                    "budget_max must be greater than or equal to budget_min"
                )
        return v


class TripUpdateRequest(BaseModel):
    """Trip update request (partial updates)."""

    from_city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    to_city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transport: Optional[TransportType] = None
    adults: Optional[int] = Field(default=None, ge=1, le=20)
    children: Optional[int] = Field(default=None, ge=0, le=20)
    budget_min: Optional[Decimal] = Field(default=None, ge=0)
    budget_max: Optional[Decimal] = Field(default=None, ge=0)
    entertainment_tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=5000)
    timezone: Optional[str] = Field(default=None, max_length=50)
    status: Optional[TripStatus] = None


class TripResponse(BaseModel):
    """Trip response model."""

    id: str  # Changed from UUID to str for SQLite compatibility
    user_id: str
    from_city: str
    to_city: str
    start_date: datetime
    end_date: datetime
    transport: TransportType
    adults: int
    children: int
    budget_min: Optional[Decimal]
    budget_max: Optional[Decimal]
    entertainment_tags: Optional[List[str]]
    notes: Optional[str]
    status: TripStatus
    timezone: Optional[str]
    ics_token: str
    created_at: datetime
    updated_at: Optional[datetime]

    # Selected flight information
    selected_flight: Optional[SelectedFlightInfo] = None

    # Selected hotel information (will be Optional[SelectedHotelInfo])
    selected_hotel: Optional[dict] = None  # Using dict for now to avoid circular import

    # Selected entertainment venues
    selected_entertainments: Optional[List[dict]] = None  # Array of venue objects

    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    """Trip list response."""

    trips: List[TripResponse]
    total: int
    page: int
    per_page: int


class TripPlanResponse(BaseModel):
    """Trip plan response."""

    id: str
    trip_id: str
    plan_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class TripChecklistResponse(BaseModel):
    """Trip checklist response."""

    id: str
    trip_id: str
    checklist_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class FlightSelectionRequest(BaseModel):
    """Request to select a flight for a trip."""

    trip_id: str
    flight_id: str
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str
    total_duration_min: int
    stops: int
    score: Optional[float] = None
    title: Optional[str] = None
    pros_keywords: Optional[List[str]] = None
    cons_keywords: Optional[List[str]] = None


class FlightSelectionResponse(BaseModel):
    """Response after selecting a flight for a trip."""

    success: bool
    message: str
    trip: TripResponse
