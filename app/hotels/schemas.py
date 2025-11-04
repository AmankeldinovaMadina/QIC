"""Hotel search and property schemas for SerpApi Google Hotels."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class HotelSearchQuery(BaseModel):
    """Query parameters for hotel search via SerpApi."""

    # Required by Google Hotels via SerpApi
    q: str = Field(..., description="Search query, e.g. 'Bali Resorts' or 'Paris'")
    check_in_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")

    # Localization
    gl: Optional[str] = Field(
        None, min_length=2, max_length=2, description="Country code, e.g. 'us'"
    )
    hl: Optional[str] = Field(
        None, min_length=2, max_length=2, description="Language code, e.g. 'en'"
    )
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code, e.g. 'USD'"
    )

    # Occupancy
    adults: Optional[int] = Field(2, ge=1, le=20)
    children: Optional[int] = Field(0, ge=0, le=10)
    children_ages: Optional[List[int]] = None

    # Advanced filters
    sort_by: Optional[Literal[3, 8, 13]] = (
        None  # 3=Lowest price, 8=Highest rating, 13=Most reviewed
    )
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    property_types: Optional[List[int]] = None
    amenities: Optional[List[int]] = None
    rating: Optional[Literal[7, 8, 9]] = None  # 3.5+, 4.0+, 4.5+
    brands: Optional[List[int]] = None
    hotel_class: Optional[List[Literal[2, 3, 4, 5]]] = None
    free_cancellation: Optional[bool] = None
    special_offers: Optional[bool] = None
    eco_certified: Optional[bool] = None

    # Vacation rentals specific
    vacation_rentals: Optional[bool] = None
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)

    # Pagination
    next_page_token: Optional[str] = None

    # SerpApi parameters
    no_cache: Optional[bool] = None
    output: Optional[Literal["json", "html"]] = "json"
    json_restrictor: Optional[str] = None

    @field_validator("children_ages")
    @classmethod
    def validate_children_ages(cls, v, info):
        children = info.data.get("children", 0)
        if v is None:
            if children and children > 0:
                pass
            return v
        if children != len(v):
            raise ValueError("children_ages length must match children count")
        for age in v:
            if not (1 <= age <= 17):
                raise ValueError("child age must be between 1 and 17")
        return v


class HotelPropertyDetailsQuery(BaseModel):
    """Query for specific hotel property details."""

    property_token: str
    q: Optional[str] = None
    check_in_date: str
    check_out_date: str
    gl: Optional[str] = None
    hl: Optional[str] = None
    currency: Optional[str] = None
    adults: Optional[int] = 2
    children: Optional[int] = 0
    children_ages: Optional[List[int]] = None


class SerpApiRaw(BaseModel):
    """Wrapper for raw SerpApi response."""

    data: dict


# ============================================================================
# AI Ranking Schemas (similar to flights)
# ============================================================================


class HotelForRanking(BaseModel):
    """Individual hotel data for AI ranking."""

    id: str = Field(..., description="Unique hotel identifier (property_token)")
    name: str
    location: str = Field(..., description="Hotel address or area")

    # Pricing
    price_per_night: float = Field(..., description="Price per night")
    total_price: float = Field(..., description="Total price for the stay")
    currency: str = Field(default="USD")

    # Ratings and reviews
    rating: Optional[float] = Field(None, ge=0, le=5, description="Hotel rating (0-5)")
    reviews_count: Optional[int] = Field(None, ge=0)

    # Property details
    hotel_class: Optional[int] = Field(None, ge=1, le=5, description="Star rating")
    property_type: Optional[str] = None  # "Hotel", "Resort", "Apartment", etc.

    # Amenities
    amenities: Optional[List[str]] = Field(default_factory=list)

    # Policies
    free_cancellation: Optional[bool] = None

    # Images
    thumbnail: Optional[str] = None
    
    # Booking link
    link: Optional[str] = Field(None, description="Booking URL for the hotel")


class HotelRankRequest(BaseModel):
    """Request to rank hotels using AI."""

    search_id: str
    hotels: List[HotelForRanking]
    preferences_prompt: str = Field(
        ..., description="User preferences for hotel selection"
    )
    locale: Optional[dict] = None


class HotelRankItem(BaseModel):
    """Individual ranked hotel result."""

    id: str
    score: float = Field(..., ge=0.0, le=1.0)
    title: str = Field(..., max_length=140)
    rationale_short: str = Field(..., max_length=240)
    pros_keywords: List[str] = Field(default_factory=list, max_items=8)
    cons_keywords: List[str] = Field(default_factory=list, max_items=8)
    tags: Optional[List[str]] = None
    link: Optional[str] = Field(None, description="Booking URL for the hotel")


class HotelRankMeta(BaseModel):
    """Metadata about the ranking process."""

    used_model: str
    deterministic: bool
    notes: Optional[List[str]] = None


class HotelRankResponse(BaseModel):
    """Response containing ranked hotels."""

    search_id: str
    ordered_ids: List[str]
    items: List[HotelRankItem]
    meta: HotelRankMeta


# ============================================================================
# Hotel Selection Schemas (for saving to trip)
# ============================================================================


class HotelSelectionRequest(BaseModel):
    """Request to select a hotel and save it to a trip."""

    trip_id: str

    # Hotel identification
    hotel_id: str = Field(..., description="Property token or unique hotel ID")
    hotel_name: str

    # Location
    location: str = Field(..., description="Hotel address or area")

    # Pricing
    price_per_night: float
    total_price: float
    currency: str = Field(default="USD")

    # Dates
    check_in_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")

    # Ratings
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews_count: Optional[int] = None
    hotel_class: Optional[int] = Field(None, ge=1, le=5)

    # Amenities
    amenities: Optional[List[str]] = None

    # Policies
    free_cancellation: Optional[bool] = None

    # AI ranking data
    score: Optional[float] = Field(None, ge=0.0, le=1.0)
    title: Optional[str] = None
    pros_keywords: Optional[List[str]] = None
    cons_keywords: Optional[List[str]] = None

    # Images
    thumbnail: Optional[str] = None
    
    # Booking link
    link: Optional[str] = Field(None, description="Booking URL for the hotel")


class HotelSelectionResponse(BaseModel):
    """Response after selecting a hotel."""

    success: bool
    message: str
    trip_id: str
    hotel: dict


class SelectedHotelInfo(BaseModel):
    """Selected hotel information for a trip."""

    hotel_id: str
    hotel_name: str
    location: str

    price_per_night: float
    total_price: float
    currency: str

    check_in_date: str
    check_out_date: str

    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    hotel_class: Optional[int] = None

    amenities: Optional[List[str]] = None
    free_cancellation: Optional[bool] = None

    score: Optional[float] = None
    title: Optional[str] = None
    pros_keywords: Optional[List[str]] = None
    cons_keywords: Optional[List[str]] = None

    thumbnail: Optional[str] = None
    link: Optional[str] = None
