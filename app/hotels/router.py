"""Hotels router with search, AI ranking, and selection endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.schemas import (
    HotelSearchQuery,
    HotelPropertyDetailsQuery,
    SerpApiRaw,
    HotelRankRequest,
    HotelRankResponse,
    HotelSelectionRequest
)
from app.hotels.service import GoogleHotelsService
from app.hotels.ai_ranker import OpenAIHotelRanker
from app.trips.service import trips_service
from app.db import get_async_session, User
from app.auth import get_current_user

router = APIRouter(prefix="/hotels", tags=["hotels"])


def _svc() -> GoogleHotelsService:
    """Dependency to get Google Hotels service."""
    return GoogleHotelsService()


# ============================================================================
# Google Hotels Search Endpoints
# ============================================================================

@router.get("/search", response_model=SerpApiRaw)
async def hotels_search(
    q: HotelSearchQuery = Depends(),
    svc: GoogleHotelsService = Depends(_svc)
):
    """
    Search for hotels using Google Hotels via SerpApi.
    
    Returns raw SerpApi response with hotel listings, prices, and details.
    """
    try:
        data = await svc.search(q.model_dump())
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Hotels search failed: {e}")


@router.get("/property", response_model=SerpApiRaw)
async def hotel_property_details(
    q: HotelPropertyDetailsQuery = Depends(),
    svc: GoogleHotelsService = Depends(_svc)
):
    """
    Get detailed information for a specific hotel property.
    
    Requires a property_token from a search result.
    """
    try:
        data = await svc.property_details(q.model_dump())
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Property details failed: {e}")


# ============================================================================
# AI Hotel Ranking Endpoint
# ============================================================================

@router.post("/rank", response_model=HotelRankResponse)
async def rank_hotels(req: HotelRankRequest):
    """
    Rank hotels using AI-powered analysis.
    
    Analyzes hotels based on user preferences and returns ranked results
    with scores, pros/cons keywords, and detailed rationale.
    
    Uses OpenAI for intelligent ranking with heuristic fallback.
    """
    try:
        ranker = OpenAIHotelRanker()
        result = await ranker.rank_hotels(req)
        return result
    except Exception as e:
        print(f"ERROR in rank_hotels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-rank", response_model=HotelRankResponse)
async def rank_hotels_alias(req: HotelRankRequest):
    """Legacy alias: /ai-rank -> /rank"""
    return await rank_hotels(req)


# ============================================================================
# Hotel Selection Endpoint (Save to Trip)
# ============================================================================

@router.post("/select")
async def select_hotel_for_trip(
    req: HotelSelectionRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Select a hotel and save it to a trip.
    
    This endpoint takes a trip ID and complete hotel information,
    and stores it in the trip's database record.
    """
    try:
        print(f"🏨 Hotel selection for trip {req.trip_id}")
        
        # Get the trip and verify ownership
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        print(f"✅ Trip found: {trip.from_city} → {trip.to_city}")
        
        # Update trip with hotel information
        trip.selected_hotel_id = req.hotel_id
        trip.selected_hotel_name = req.hotel_name
        trip.selected_hotel_location = req.location
        trip.selected_hotel_price_per_night = req.price_per_night
        trip.selected_hotel_total_price = req.total_price
        trip.selected_hotel_currency = req.currency
        trip.selected_hotel_check_in = req.check_in_date
        trip.selected_hotel_check_out = req.check_out_date
        trip.selected_hotel_rating = req.rating
        trip.selected_hotel_reviews_count = req.reviews_count
        trip.selected_hotel_class = req.hotel_class
        trip.selected_hotel_amenities = req.amenities
        trip.selected_hotel_free_cancellation = req.free_cancellation
        trip.selected_hotel_score = req.score
        trip.selected_hotel_title = req.title
        trip.selected_hotel_pros = req.pros_keywords
        trip.selected_hotel_cons = req.cons_keywords
        trip.selected_hotel_thumbnail = req.thumbnail
        
        # Save to database
        await session.commit()
        await session.refresh(trip)
        
        print(f"✅ Hotel {req.hotel_name} saved successfully!")
        
        # Return success response
        return {
            "success": True,
            "message": f"Hotel {req.hotel_name} successfully added to your trip",
            "trip_id": str(trip.id),
            "trip": {
                "destination": f"{trip.from_city} → {trip.to_city}",
                "dates": f"{trip.start_date.date()} to {trip.end_date.date()}"
            },
            "hotel": {
                "name": req.hotel_name,
                "location": req.location,
                "price": f"${req.total_price} {req.currency} (${req.price_per_night}/night)",
                "rating": f"{req.rating}/5" if req.rating else "N/A",
                "check_in": req.check_in_date,
                "check_out": req.check_out_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
