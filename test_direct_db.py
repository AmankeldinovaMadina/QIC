#!/usr/bin/env python3
"""
Direct database test to verify we can save flight information
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from datetime import datetime

from app.db.models import Trip

async def test_flight_save():
    """Test saving flight information directly to database"""
    
    # Create engine
    engine = create_async_engine("sqlite+aiosqlite:///./travel_db.sqlite")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get the trip
        trip_id = "856ab99f-ec37-4ea2-be53-de94026fba3a"
        stmt = select(Trip).where(Trip.id == trip_id)
        result = await session.execute(stmt)
        trip = result.scalar_one_or_none()
        
        if not trip:
            print(f"❌ Trip {trip_id} not found")
            return
        
        print(f"✅ Trip found: {trip.from_city} → {trip.to_city}")
        print(f"   User ID: {trip.user_id}")
        
        # Update with flight info
        trip.selected_flight_id = "test_flight_123"
        trip.selected_flight_airline = "Delta"
        trip.selected_flight_number = "DL999"
        trip.selected_flight_departure_airport = "JFK"
        trip.selected_flight_arrival_airport = "LAX"
        trip.selected_flight_departure_time = datetime.fromisoformat("2025-12-01T08:00:00")
        trip.selected_flight_arrival_time = datetime.fromisoformat("2025-12-01T11:30:00")
        trip.selected_flight_price = 450.0
        trip.selected_flight_currency = "USD"
        trip.selected_flight_duration_min = 210
        trip.selected_flight_stops = 0
        trip.selected_flight_score = 0.9
        trip.selected_flight_title = "Test Flight"
        trip.selected_flight_pros = ["direct", "cheap"]
        trip.selected_flight_cons = ["busy"]
        
        # Commit
        await session.commit()
        print("✅ Flight information saved to database!")
        
        # Verify
        await session.refresh(trip)
        print(f"✅ Verified: {trip.selected_flight_airline} {trip.selected_flight_number}")

if __name__ == "__main__":
    asyncio.run(test_flight_save())
