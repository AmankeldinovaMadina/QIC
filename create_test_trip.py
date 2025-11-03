"""Create a test trip directly in the database for testing."""

import asyncio
import uuid
from datetime import datetime, timedelta
from app.db.database import async_session_factory
from app.db.models import Trip, User, TransportType, TripStatus


async def create_test_trip():
    """Create a test trip and user in the database."""
    
    async with async_session_factory() as session:
        # Check if test user exists, create if not
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.username == "test_user_for_culture_guide")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            user_id = existing_user.id
            print(f"ℹ️  Using existing test user: {user_id}")
        else:
            user_id = str(uuid.uuid4())
            test_user = User(
                id=user_id,
                username="test_user_for_culture_guide"
            )
            session.add(test_user)
            print(f"✅ Created new test user: {user_id}")
        
        # Create test trip
        trip_id = str(uuid.uuid4())
        start_date = datetime.now() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        test_trip = Trip(
            id=trip_id,
            user_id=user_id,
            from_city="New York",
            to_city="Tokyo",
            start_date=start_date,
            end_date=end_date,
            transport=TransportType.FLIGHT,
            adults=2,
            children=0,
            budget_min=2000,
            budget_max=5000,
            notes="Test trip for culture guide testing",
            status=TripStatus.DRAFT
        )
        
        try:
            if not existing_user:
                session.add(test_user)
            session.add(test_trip)
            await session.commit()
            
            print("✅ Test trip created successfully!")
            print(f"\nUser ID: {user_id}")
            print(f"Trip ID: {trip_id}")
            print(f"From: {test_trip.from_city}")
            print(f"To: {test_trip.to_city}")
            print(f"Dates: {test_trip.start_date.date()} to {test_trip.end_date.date()}")
            print(f"\n📝 Use this trip_id for testing: {trip_id}")
            print(f"\nTest command:")
            print(f'curl -X POST http://localhost:8001/api/v1/culture/guide \\')
            print(f'  -H "Content-Type: application/json" \\')
            print(f"  -d '{{\"trip_id\": \"{trip_id}\", \"destination\": \"Tokyo, Japan\", \"language\": \"en\"}}'")
            
            return trip_id
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating test trip: {str(e)}")
            raise


if __name__ == "__main__":
    trip_id = asyncio.run(create_test_trip())
