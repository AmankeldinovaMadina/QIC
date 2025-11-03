#!/usr/bin/env python3
"""
Test to check if trip loads flight data from database
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.db.models import Trip
from app.trips.service import trips_service

async def test_trip_loading():
    """Test if trip properly loads flight data"""
    
    # Create engine
    engine = create_async_engine("sqlite+aiosqlite:///./travel_db.sqlite")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get the trip
        trip_id = "856ab99f-ec37-4ea2-be53-de94026fba3a"
        user_id = "869f80df-faee-4eee-b602-70360b563bcd"
        
        trip = await trips_service.get_trip_by_id(session, trip_id, user_id)
        
        if not trip:
            print(f"❌ Trip not found")
            return
        
        print(f"✅ Trip loaded: {trip.from_city} → {trip.to_city}")
        print(f"   selected_flight_id: {trip.selected_flight_id}")
        print(f"   selected_flight_airline: {trip.selected_flight_airline}")
        print(f"   selected_flight_number: {trip.selected_flight_number}")
        
        # Try to build selected flight info
        selected_flight = trips_service._build_selected_flight_info(trip)
        
        if selected_flight:
            print(f"✅ Selected flight built successfully!")
            print(f"   Flight: {selected_flight.airline} {selected_flight.flight_number}")
            print(f"   Route: {selected_flight.departure_airport} → {selected_flight.arrival_airport}")
        else:
            print(f"❌ Selected flight is None")

if __name__ == "__main__":
    asyncio.run(test_trip_loading())
