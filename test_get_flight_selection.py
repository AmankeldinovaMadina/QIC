"""Test the GET /flights/{trip_id}/selection endpoint."""

import requests

BASE_URL = "http://localhost:8001/api/v1"


def test_get_flight_selection():
    """Test retrieving the selected flight for a trip."""
    print("\n" + "=" * 60)
    print("Testing GET Flight Selection Endpoint")
    print("=" * 60)

    # Step 1: Register/Login
    print("\n1️⃣  Logging in...")
    login_data = {"username": "testuser_flights"}

    response = requests.post(
        f"{BASE_URL}/auth/login", json=login_data, allow_redirects=False
    )

    if response.status_code == 401:
        print("   User doesn't exist, registering...")
        register_data = {"username": "testuser_flights"}
        requests.post(f"{BASE_URL}/auth/register", json=register_data)
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Logged in successfully")

    # Step 2: Create a trip
    print("\n2️⃣  Creating a test trip...")
    trip_data = {
        "from_city": "New York",
        "to_city": "Tokyo",
        "start_date": "2025-06-01",
        "end_date": "2025-06-10",
        "transport": "flight",
        "adults": 2,
        "children": 0,
        "notes": "Prefer direct flights",
    }

    response = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=headers)
    assert response.status_code == 200, f"Trip creation failed: {response.text}"
    trip = response.json()
    trip_id = trip["id"]
    print(f"   ✅ Trip created: {trip_id}")

    # Step 3: Check flight selection (should be empty)
    print("\n3️⃣  Checking flight selection (should be empty)...")
    response = requests.get(
        f"{BASE_URL}/flights/{trip_id}/selection", headers=headers
    )
    assert response.status_code == 200, f"GET failed: {response.text}"
    data = response.json()
    assert data["trip_id"] == trip_id
    assert data["selected_flight"] is None
    print(f"   ✅ No flight selected yet: {data['message']}")

    # Step 4: Select a flight
    print("\n4️⃣  Selecting a flight...")
    flight_data = {
        "trip_id": trip_id,
        "flight_id": "test-flight-123",
        "airline": "American Airlines",
        "flight_number": "AA154",
        "departure_airport": "JFK",
        "arrival_airport": "NRT",
        "departure_time": "2025-06-01T10:00:00Z",
        "arrival_time": "2025-06-02T14:00:00Z",
        "price": 1200,
        "currency": "USD",
        "total_duration_min": 780,
        "stops": 0,
        "score": 0.95,
        "title": "Direct flight, morning departure",
        "pros_keywords": ["direct", "morning", "fast"],
        "cons_keywords": ["pricey"],
    }

    response = requests.post(
        f"{BASE_URL}/flights/select", json=flight_data, headers=headers
    )
    assert response.status_code == 200, f"Flight selection failed: {response.text}"
    print(f"   ✅ Flight selected: {response.json()['message']}")

    # Step 5: Get flight selection (should have data)
    print("\n5️⃣  Retrieving flight selection...")
    response = requests.get(
        f"{BASE_URL}/flights/{trip_id}/selection", headers=headers
    )
    assert response.status_code == 200, f"GET failed: {response.text}"
    data = response.json()
    assert data["trip_id"] == trip_id
    assert data["selected_flight"] is not None
    flight = data["selected_flight"]
    
    print(f"\n   ✅ Flight retrieved successfully!")
    print(f"      Flight ID: {flight['flight_id']}")
    print(f"      Airline: {flight['airline']} {flight['flight_number']}")
    print(f"      Route: {flight['departure_airport']} → {flight['arrival_airport']}")
    print(f"      Departure: {flight['departure_time']}")
    print(f"      Arrival: {flight['arrival_time']}")
    print(f"      Price: ${flight['price']} {flight['currency']}")
    print(f"      Duration: {flight['total_duration_min']} minutes")
    print(f"      Stops: {flight['stops']}")
    print(f"      AI Score: {flight['score']}")
    print(f"      Title: {flight['title']}")
    print(f"      Pros: {', '.join(flight['pros_keywords'])}")
    print(f"      Cons: {', '.join(flight['cons_keywords'])}")

    # Verify all fields
    assert flight["flight_id"] == "test-flight-123"
    assert flight["airline"] == "American Airlines"
    assert flight["flight_number"] == "AA154"
    assert flight["departure_airport"] == "JFK"
    assert flight["arrival_airport"] == "NRT"
    assert flight["price"] == 1200
    assert flight["currency"] == "USD"
    assert flight["total_duration_min"] == 780
    assert flight["stops"] == 0
    assert flight["score"] == 0.95
    assert flight["title"] == "Direct flight, morning departure"
    assert flight["pros_keywords"] == ["direct", "morning", "fast"]
    assert flight["cons_keywords"] == ["pricey"]

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    test_get_flight_selection()
