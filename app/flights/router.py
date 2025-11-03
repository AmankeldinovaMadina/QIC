"""Flight search and ranking router."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.db import User
from app.auth import get_current_user
from app.flights.schemas import (
    FlightSearchParams, SearchResult, RankRequest, RankResponse
)
from app.flights.providers import google_flights_provider
from app.flights.ai_ranker import openai_flight_ranker


router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search", response_model=SearchResult)
async def search_flights(
    type: int = Query(..., description="1=round-trip, 2=one-way"),
    departure_id: str = Query(..., description="Departure airport/city code"),
    arrival_id: str = Query(..., description="Arrival airport/city code"),
    outbound_date: str = Query(..., description="Outbound date (YYYY-MM-DD)"),
    return_date: Optional[str] = Query(None, description="Return date for round-trip"),
    currency: str = Query("USD", description="Currency code"),
    hl: str = Query("en", description="Language"),
    gl: str = Query("us", description="Country"),
    sort_by: Optional[str] = Query(None, description="Sort by: best, price, duration, emissions"),
    travel_class: Optional[int] = Query(None, description="1=economy, 2=premium, 3=business, 4=first"),
    adults: int = Query(1, ge=1, le=9, description="Number of adults"),
    children: int = Query(0, ge=0, le=8, description="Number of children"),
    infants_in_seat: int = Query(0, ge=0, le=8),
    infants_on_lap: int = Query(0, ge=0, le=8),
    max_stops: Optional[int] = Query(None, ge=0, le=2, description="Maximum stops"),
    include_airlines: Optional[str] = Query(None, description="Comma-separated airline codes"),
    exclude_airlines: Optional[str] = Query(None, description="Comma-separated airline codes to exclude"),
    exclude_basic: Optional[bool] = Query(None, description="Exclude basic economy (US only)"),
    deep_search: Optional[bool] = Query(None, description="Enable deep search"),
    current_user: User = Depends(get_current_user)
):
    """Search flights using Google Flights via SerpApi."""
    
    # Validate business rules
    if type == 1 and not return_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="return_date is required for round-trip flights"
        )
    
    if include_airlines and exclude_airlines:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot specify both include_airlines and exclude_airlines"
        )
    
    if exclude_basic and (gl != "us" or travel_class != 1):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="exclude_basic is only valid for US searches with economy class"
        )
    
    # Build search parameters
    search_params = FlightSearchParams(
        type=type,
        departure_id=departure_id,
        arrival_id=arrival_id,
        outbound_date=outbound_date,
        return_date=return_date,
        currency=currency,
        hl=hl,
        gl=gl,
        sort_by=sort_by,
        travel_class=travel_class,
        adults=adults,
        children=children,
        infants_in_seat=infants_in_seat,
        infants_on_lap=infants_on_lap,
        max_stops=max_stops,
        include_airlines=include_airlines,
        exclude_airlines=exclude_airlines,
        exclude_basic=exclude_basic,
        deep_search=deep_search
    )
    
    try:
        # Search flights using SerpApi
        result = await google_flights_provider.search_flights(search_params)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Flight search failed: {str(e)}"
        )


@router.post("/ai-rank", response_model=RankResponse)
async def rank_flights_with_ai(
    request: RankRequest,
    current_user: User = Depends(get_current_user)
):
    """Rank flights using AI with pros/cons analysis."""
    
    # Validate request
    if not request.flights:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No flights provided for ranking"
        )
    
    if len(request.preferences_prompt.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Preferences prompt too short - please provide more details"
        )
    
    try:
        # Rank flights using OpenAI
        result = await openai_flight_ranker.rank_flights(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Flight ranking failed: {str(e)}"
        )