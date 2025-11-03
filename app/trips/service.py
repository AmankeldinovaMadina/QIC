"""Trip service layer."""

import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Trip, TripChecklist, TripPlan, TripStatus, User
from app.trips.schemas import SelectedFlightInfo, TripCreateRequest, TripUpdateRequest


class TripsService:
    """Service for trip management."""

    def _build_selected_flight_info(self, trip: Trip) -> Optional[SelectedFlightInfo]:
        """Build SelectedFlightInfo from trip model."""
        if not trip.selected_flight_id:
            return None

        return SelectedFlightInfo(
            flight_id=trip.selected_flight_id,
            airline=trip.selected_flight_airline,
            flight_number=trip.selected_flight_number,
            departure_airport=trip.selected_flight_departure_airport,
            arrival_airport=trip.selected_flight_arrival_airport,
            departure_time=trip.selected_flight_departure_time,
            arrival_time=trip.selected_flight_arrival_time,
            price=(
                float(trip.selected_flight_price) if trip.selected_flight_price else 0.0
            ),
            currency=trip.selected_flight_currency or "USD",
            total_duration_min=trip.selected_flight_duration_min or 0,
            stops=trip.selected_flight_stops or 0,
            score=(
                float(trip.selected_flight_score)
                if trip.selected_flight_score
                else None
            ),
            title=trip.selected_flight_title,
            pros_keywords=trip.selected_flight_pros,
            cons_keywords=trip.selected_flight_cons,
        )

    def _build_selected_hotel_info(self, trip: Trip) -> Optional[dict]:
        """Build selected hotel info dict from trip model."""
        if not trip.selected_hotel_id:
            return None

        # Return as dict to avoid circular import
        return {
            "hotel_id": trip.selected_hotel_id,
            "hotel_name": trip.selected_hotel_name,
            "location": trip.selected_hotel_location,
            "price_per_night": (
                float(trip.selected_hotel_price_per_night)
                if trip.selected_hotel_price_per_night
                else 0.0
            ),
            "total_price": (
                float(trip.selected_hotel_total_price)
                if trip.selected_hotel_total_price
                else 0.0
            ),
            "currency": trip.selected_hotel_currency or "USD",
            "check_in_date": trip.selected_hotel_check_in,
            "check_out_date": trip.selected_hotel_check_out,
            "rating": (
                float(trip.selected_hotel_rating)
                if trip.selected_hotel_rating
                else None
            ),
            "reviews_count": trip.selected_hotel_reviews_count,
            "hotel_class": trip.selected_hotel_class,
            "amenities": trip.selected_hotel_amenities,
            "free_cancellation": trip.selected_hotel_free_cancellation,
            "score": (
                float(trip.selected_hotel_score) if trip.selected_hotel_score else None
            ),
            "title": trip.selected_hotel_title,
            "pros_keywords": trip.selected_hotel_pros,
            "cons_keywords": trip.selected_hotel_cons,
            "thumbnail": trip.selected_hotel_thumbnail,
        }

    async def create_trip(
        self,
        session: AsyncSession,
        user_id: str,  # Changed from UUID to str
        trip_data: TripCreateRequest,
    ) -> Trip:
        """Create a new trip."""
        trip = Trip(user_id=user_id, **trip_data.dict(exclude_unset=True))

        session.add(trip)
        await session.commit()
        await session.refresh(trip)
        return trip

    async def get_trip_by_id(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
    ) -> Optional[Trip]:
        """Get a trip by ID for a specific user."""
        stmt = select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_trips(
        self,
        session: AsyncSession,
        user_id: str,  # Changed from UUID to str
        status: Optional[TripStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[Trip], int]:
        """Get trips for a user with pagination."""
        # Build query
        stmt = select(Trip).where(Trip.user_id == user_id)

        if status:
            stmt = stmt.where(Trip.status == status)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()

        # Apply pagination and ordering
        stmt = stmt.order_by(Trip.created_at.desc())
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)

        result = await session.execute(stmt)
        trips = result.scalars().all()

        return list(trips), total

    async def update_trip(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
        update_data: TripUpdateRequest,
    ) -> Optional[Trip]:
        """Update a trip."""
        trip = await self.get_trip_by_id(session, trip_id, user_id)

        if not trip:
            return None

        # Apply updates
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(trip, field, value)

        await session.commit()
        await session.refresh(trip)
        return trip

    async def delete_trip(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
    ) -> bool:
        """Delete a trip (soft delete by setting status)."""
        trip = await self.get_trip_by_id(session, trip_id, user_id)

        if not trip:
            return False

        trip.status = TripStatus.CANCELLED
        await session.commit()
        return True

    async def finalize_trip(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
        plan_json: dict,
        checklist_json: dict,
    ) -> Optional[Trip]:
        """Finalize a trip and save plan/checklist."""
        trip = await self.get_trip_by_id(session, trip_id, user_id)

        if not trip or trip.status != TripStatus.DRAFT:
            return None

        # Save plan
        trip_plan = TripPlan(trip_id=trip_id, plan_json=plan_json)
        session.add(trip_plan)

        # Save checklist
        trip_checklist = TripChecklist(trip_id=trip_id, checklist_json=checklist_json)
        session.add(trip_checklist)

        # Update trip status
        trip.status = TripStatus.PLANNED

        await session.commit()
        await session.refresh(trip)
        return trip

    async def get_trip_plan(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
    ) -> Optional[TripPlan]:
        """Get the plan for a trip."""
        # Verify user owns the trip
        trip = await self.get_trip_by_id(session, trip_id, user_id)
        if not trip:
            return None

        stmt = select(TripPlan).where(TripPlan.trip_id == trip_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_trip_checklist(
        self,
        session: AsyncSession,
        trip_id: str,  # Changed from UUID to str
        user_id: str,  # Changed from UUID to str
    ) -> Optional[TripChecklist]:
        """Get the checklist for a trip."""
        # Verify user owns the trip
        trip = await self.get_trip_by_id(session, trip_id, user_id)
        if not trip:
            return None

        stmt = select(TripChecklist).where(TripChecklist.trip_id == trip_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def select_flight_for_trip(
        self, session: AsyncSession, trip_id: str, user_id: str, flight_data: dict
    ) -> Optional[Trip]:
        """Select and save flight information for a trip."""
        trip = await self.get_trip_by_id(session, trip_id, user_id)

        if not trip:
            return None

        # Update trip with selected flight information
        trip.selected_flight_id = flight_data.get("flight_id")
        trip.selected_flight_airline = flight_data.get("airline")
        trip.selected_flight_number = flight_data.get("flight_number")
        trip.selected_flight_departure_airport = flight_data.get("departure_airport")
        trip.selected_flight_arrival_airport = flight_data.get("arrival_airport")
        trip.selected_flight_departure_time = flight_data.get("departure_time")
        trip.selected_flight_arrival_time = flight_data.get("arrival_time")
        trip.selected_flight_price = flight_data.get("price")
        trip.selected_flight_currency = flight_data.get("currency")
        trip.selected_flight_duration_min = flight_data.get("total_duration_min")
        trip.selected_flight_stops = flight_data.get("stops")
        trip.selected_flight_score = flight_data.get("score")
        trip.selected_flight_title = flight_data.get("title")
        trip.selected_flight_pros = flight_data.get("pros_keywords")
        trip.selected_flight_cons = flight_data.get("cons_keywords")

        await session.commit()
        await session.refresh(trip)
        return trip


# Global service instance
trips_service = TripsService()
