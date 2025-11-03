"""Test script to check if the AI ranker is working."""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.flights.ai_ranker import OpenAIFlightRanker
from app.flights.schemas import RankRequest, Itinerary, Segment, Price, FlightLeg

async def test_ai_ranker():
    """Test the AI ranker with sample flight data."""

    # Create sample flight data
    sample_flights = [
        Itinerary(
            id="flight1",
            price=Price(amount=500.0, currency="USD"),
            total_duration_min=855,  # 14h 15m
            stops=0,
            emissions_kg=450.0,
            legs=[
                FlightLeg(
                    dep_iata="JFK",
                    dep_time=datetime.fromisoformat("2024-12-15T14:30:00"),
                    arr_iata="DXB",
                    arr_time=datetime.fromisoformat("2024-12-16T06:45:00"),
                    marketing="Emirates",
                    flight_no="EK201",
                    duration_min=855
                )
            ]
        ),
        Itinerary(
            id="flight2",
            price=Price(amount=450.0, currency="USD"),
            total_duration_min=1275,  # 21h 15m
            stops=1,
            emissions_kg=380.0,
            layovers_min=205,  # 3h 25m layover in DOH
            legs=[
                FlightLeg(
                    dep_iata="JFK",
                    dep_time=datetime.fromisoformat("2024-12-15T18:20:00"),
                    arr_iata="DOH",
                    arr_time=datetime.fromisoformat("2024-12-16T10:35:00"),
                    marketing="Qatar Airways",
                    flight_no="QR701",
                    duration_min=735
                ),
                FlightLeg(
                    dep_iata="DOH",
                    dep_time=datetime.fromisoformat("2024-12-16T14:00:00"),
                    arr_iata="DXB",
                    arr_time=datetime.fromisoformat("2024-12-16T15:30:00"),
                    marketing="Qatar Airways",
                    flight_no="QR418",
                    duration_min=90
                )
            ]
        )
    ]

    # Create rank request
    request = RankRequest(
        search_id="test-search-123",
        flights=sample_flights,
        preferences={
            "budget_priority": 0.7,
            "comfort_priority": 0.8,
            "speed_priority": 0.6,
            "stops_penalty": 0.5
        }
    )

    try:
        # Initialize ranker
        ranker = OpenAIFlightRanker()
        print("✅ AI Ranker initialized successfully")

        # Test ranking
        print("🔄 Testing flight ranking...")
        response = await ranker.rank_flights(request)

        print("✅ AI ranking completed successfully!")
        print(f"📊 Ranked {len(response.items)} flights")
        print(f"🏆 Top flight: {response.items[0].flight_id} (score: {response.items[0].score})")

        # Print details of top flight
        top_flight = response.items[0]
        print(f"✈️  Airline: {top_flight.airline}")
        print(f"💰 Price: ${top_flight.price}")
        print(f"⭐ Score: {top_flight.score}")
        print(f"👍 Pros: {', '.join(top_flight.pros[:3])}")
        print(f"👎 Cons: {', '.join(top_flight.cons[:3])}")

        return True

    except Exception as e:
        print(f"❌ AI Ranker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_ai_ranker())
        if result:
            print("\n🎉 AI Ranker test passed!")
        else:
            print("\n❌ AI Ranker test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)