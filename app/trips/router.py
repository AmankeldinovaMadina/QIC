"""Trip router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.planner import generate_trip_plan
from app.auth import get_current_user
from app.db import User, get_async_session
from app.db.models import TripStatus
from app.trips.schemas import (
    TripChecklistResponse,
    TripCreateRequest,
    TripListResponse,
    TripPlanResponse,
    TripResponse,
    TripUpdateRequest,
)
from app.trips.service import trips_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripResponse)
async def create_trip(
    trip_data: TripCreateRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new trip."""
    trip = await trips_service.create_trip(session, current_user.id, trip_data)
    return trip


@router.get("", response_model=TripListResponse)
async def get_trips(
    status: Optional[TripStatus] = Query(None, description="Filter by trip status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get user's trips with pagination."""
    trips, total = await trips_service.get_user_trips(
        session, current_user.id, status, page, per_page
    )

    return TripListResponse(trips=trips, total=total, page=page, per_page=per_page)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific trip."""
    trip = await trips_service.get_trip_by_id(session, trip_id, current_user.id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    # Build the selected flight info if it exists
    selected_flight = trips_service._build_selected_flight_info(trip)

    # Build the selected hotel info if it exists (returns dict directly)
    selected_hotel = trips_service._build_selected_hotel_info(trip)

    # Parse selected_entertainments JSON if it exists
    selected_entertainments = None
    if trip.selected_entertainments:
        if isinstance(trip.selected_entertainments, str):
            import json
            try:
                selected_entertainments = json.loads(trip.selected_entertainments)
            except:
                selected_entertainments = []
        elif isinstance(trip.selected_entertainments, list):
            selected_entertainments = trip.selected_entertainments

    # Create response with selected flight and hotel
    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        from_city=trip.from_city,
        to_city=trip.to_city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        transport=trip.transport,
        adults=trip.adults,
        children=trip.children,
        budget_min=trip.budget_min,
        budget_max=trip.budget_max,
        entertainment_tags=trip.entertainment_tags,
        notes=trip.notes,
        status=trip.status,
        timezone=trip.timezone,
        ics_token=trip.ics_token,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
        selected_flight=selected_flight,
        selected_hotel=selected_hotel,
        selected_entertainments=selected_entertainments,
    )


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    update_data: TripUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update a trip."""
    trip = await trips_service.update_trip(
        session, trip_id, current_user.id, update_data
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    return trip


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a trip."""
    success = await trips_service.delete_trip(session, trip_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    return {"message": "Trip deleted successfully"}


@router.post("/{trip_id}/finalize", response_model=TripResponse)
async def finalize_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Finalize a trip and generate AI-powered daily plan.

    This endpoint:
    1. Validates the trip belongs to the user
    2. Generates a detailed daily itinerary using OpenAI Structured Outputs
    3. Considers selected flight, hotel, and user preferences
    4. Stores the generated plan in the database
    5. Updates trip status to 'planned'
    """
    # First, get the trip to pass to AI planner
    trip = await trips_service.get_trip_by_id(session, trip_id, current_user.id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    if trip.status == TripStatus.PLANNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip is already finalized",
        )

    try:
        # Generate AI-powered trip plan using OpenAI Structured Outputs
        print(f"Generating AI plan for trip {trip_id}...")
        plan_json = generate_trip_plan(trip)
        print(f"Plan generated successfully. Keys: {list(plan_json.keys())}")

        # Generate a simple checklist (can be enhanced with AI later)
        checklist_json = {
            "pre_trip": [
                "Check passport validity (6 months minimum)",
                "Apply for visa if required",
                "Book transportation and accommodation",
                "Arrange travel insurance",
                "Notify bank of travel dates",
            ],
            "packing": [
                "Travel documents (passport, visa, tickets)",
                "Clothing appropriate for destination weather",
                "Toiletries and medications",
                "Electronics and chargers",
                "Emergency contact information",
            ],
            "documents": [
                "Passport",
                "Visa",
                "Flight tickets",
                "Hotel confirmations",
                "Travel insurance documents",
            ],
            "during_trip": [
                "Keep important documents secure",
                "Stay aware of local customs",
                "Keep emergency contacts handy",
                "Monitor weather and local news",
            ],
        }

        # Save plan and finalize trip
        finalized_trip = await trips_service.finalize_trip(
            session, trip_id, current_user.id, plan_json, checklist_json
        )

        if not finalized_trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or cannot be finalized",
            )

        return finalized_trip

    except Exception as e:
        # Log the error and return a helpful message
        import traceback

        print(f"Error generating trip plan: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate trip plan: {str(e)}",
        )


@router.get("/{trip_id}/plan", response_model=TripPlanResponse)
async def get_trip_plan(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get trip plan."""
    plan = await trips_service.get_trip_plan(session, trip_id, current_user.id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip plan not found"
        )

    return plan


@router.get("/{trip_id}/checklist", response_model=TripChecklistResponse)
async def get_trip_checklist(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get trip checklist."""
    checklist = await trips_service.get_trip_checklist(
        session, trip_id, current_user.id
    )

    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip checklist not found"
        )

    return checklist
