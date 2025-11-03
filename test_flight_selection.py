"""Test script for flight selection functionality."""

import asyncio
import json
from datetime import datetime


async def test_flight_selection():
    """Test the flight selection endpoint with sample data."""

    # Sample flight selection request data
    flight_selection_data = {
        "trip_id": "test-trip-123",
        "flight_id": "flight_aa_nonstop",
        "airline": "American Airlines",
        "flight_number": "AA100",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "departure_time": "2025-12-15T08:00:00",
        "arrival_time": "2025-12-15T11:00:00",
        "price": 250.0,
        "currency": "USD",
        "total_duration_min": 360,
        "stops": 0,
        "score": 0.9,
        "title": "Non-stop Flight AA100: JFK to LAX",
        "pros_keywords": ["non-stop", "short duration", "direct flight"],
        "cons_keywords": ["higher price than 1-stop"],
    }

    print("Flight Selection Test Data:")
    print(json.dumps(flight_selection_data, indent=2, default=str))

    print("\nCURL command to test the endpoint:")
    curl_command = f"""curl -X POST "http://localhost:8001/api/v1/flights/select" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(flight_selection_data)}'"""

    print(curl_command)

    print("\nExpected workflow:")
    print("1. User gets flight rankings from /api/v1/flights/ai-rank")
    print("2. User selects a flight from the ranking results")
    print("3. User posts to /api/v1/flights/select with trip_id and flight details")
    print("4. Flight information is saved to the trip in the database")
    print("5. Updated trip information is returned with selected_flight details")


if __name__ == "__main__":
    asyncio.run(test_flight_selection())
