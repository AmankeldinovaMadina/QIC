from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.flights.ai_ranker import OpenAIFlightRanker
from app.flights.schemas import RankRequest, RankResponse
from app.trips.schemas import FlightSelectionRequest, FlightSelectionResponse
from app.trips.service import trips_service
from app.db import get_async_session, User
from app.auth import get_current_user

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/rank", response_model=RankResponse)
async def rank_flights(req: RankRequest):
    """Rank flight itineraries using AI (or heuristic fallback)."""
    try:
        ranker = OpenAIFlightRanker()
        result = await ranker.rank_flights(req)
        return result
    except Exception as e:
        print(f"ERROR in rank_flights: {e}")
        # If OpenAI unavailable, use heuristic fallback directly
        # This should not happen since OpenAIFlightRanker has internal fallback
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-rank", response_model=RankResponse)
async def rank_flights_alias(req: RankRequest):
    """Legacy alias: /ai-rank -> /rank"""
    return await rank_flights(req)


@router.post("/select")
async def select_flight_for_trip(
    req: FlightSelectionRequest,
    session = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Select a flight and save it to a trip - simplified working version."""
    try:
        print(f"🛫 Flight selection for trip {req.trip_id}")
        
        # Get the trip and verify ownership
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        print(f"✅ Trip found: {trip.from_city} → {trip.to_city}")
        
        # Update trip with flight information directly
        trip.selected_flight_id = req.flight_id
        trip.selected_flight_airline = req.airline
        trip.selected_flight_number = req.flight_number
        trip.selected_flight_departure_airport = req.departure_airport
        trip.selected_flight_arrival_airport = req.arrival_airport
        trip.selected_flight_departure_time = req.departure_time
        trip.selected_flight_arrival_time = req.arrival_time
        trip.selected_flight_price = req.price
        trip.selected_flight_currency = req.currency
        trip.selected_flight_duration_min = req.total_duration_min
        trip.selected_flight_stops = req.stops
        trip.selected_flight_score = req.score
        trip.selected_flight_title = req.title
        trip.selected_flight_pros = req.pros_keywords
        trip.selected_flight_cons = req.cons_keywords
        
        # Save to database
        await session.commit()
        await session.refresh(trip)
        
        print(f"✅ Flight {req.airline} {req.flight_number} saved successfully!")
        
        # Return simple success response
        return {
            "success": True,
            "message": f"Flight {req.airline} {req.flight_number} successfully added to trip",
            "trip_id": trip.id,
            "flight": {
                "airline": req.airline,
                "flight_number": req.flight_number,
                "route": f"{req.departure_airport} → {req.arrival_airport}",
                "price": f"${req.price} {req.currency}",
                "departure": req.departure_time.isoformat() if req.departure_time else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
