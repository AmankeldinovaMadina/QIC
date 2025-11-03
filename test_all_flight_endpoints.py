"""Comprehensive test for all flight endpoints."""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"


def test_all_flight_endpoints():
    """Test the complete flight workflow: search, rank, select, retrieve."""
    print("\n" + "=" * 70)
    print("TESTING ALL FLIGHT ENDPOINTS")
    print("=" * 70)

    # Step 1: Register/Login
    print("\n1️⃣  AUTHENTICATION")
    print("-" * 70)
    login_data = {"username": "testuser_flights_all"}

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    if response.status_code == 401:
        print("   User doesn't exist, registering...")
        register_data = {"username": "testuser_flights_all"}
        requests.post(f"{BASE_URL}/auth/register", json=register_data)
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Logged in successfully as {login_data['username']}")

    # Step 2: Create a trip
    print("\n2️⃣  CREATE TRIP")
    print("-" * 70)
    trip_data = {
        "from_city": "New York",
        "to_city": "Los Angeles",
        "start_date": "2025-12-15",
        "end_date": "2025-12-20",
        "transport": "flight",
        "adults": 2,
        "children": 1,
        "budget_min": 800,
        "budget_max": 2000,
        "notes": "Prefer direct flights with morning departures. Comfortable seating is important.",
    }

    response = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=headers)
    assert response.status_code == 200, f"Trip creation failed: {response.text}"
    trip = response.json()
    trip_id = trip["id"]
    print(f"   ✅ Trip created:")
    print(f"      Trip ID: {trip_id}")
    print(f"      Route: {trip['from_city']} → {trip['to_city']}")
    print(f"      Dates: {trip['start_date']} to {trip['end_date']}")
    print(f"      Passengers: {trip['adults']} adults, {trip['children']} children")

    # Step 3: Search flights using backend API
    print("\n3️⃣  SEARCH FLIGHTS (Backend API → SerpAPI)")
    print("-" * 70)
    search_request = {
        "trip_id": trip_id,
        # Let backend auto-fill from trip data
    }

    response = requests.post(
        f"{BASE_URL}/flights/search", json=search_request, headers=headers
    )
    assert response.status_code == 200, f"Flight search failed: {response.text}"
    search_result = response.json()

    print(f"   ✅ Flight search successful!")
    print(f"      Search ID: {search_result['search_id']}")
    print(f"      Total results: {search_result['total_results']}")
    print(f"      Search params: {json.dumps(search_result['search_params'], indent=6)}")

    flights = search_result["flights"]
    assert len(flights) > 0, "No flights found"
    print(f"\n   📋 Found {len(flights)} flights:")

    for i, flight in enumerate(flights[:5], 1):  # Show first 5
        print(f"\n      Flight {i}:")
        print(f"         ID: {flight['id']}")
        print(f"         Price: ${flight['price']['amount']} {flight['price']['currency']}")
        print(f"         Duration: {flight['total_duration_min']} minutes")
        print(f"         Stops: {flight['stops']}")
        if flight.get("emissions_kg"):
            print(f"         Emissions: {flight['emissions_kg']} kg CO2")

        # Show legs
        for j, leg in enumerate(flight["legs"], 1):
            print(
                f"         Leg {j}: {leg['marketing']} {leg['flight_no']} | "
                f"{leg['dep_iata']} → {leg['arr_iata']}"
            )

    # Step 4: Rank flights with AI
    print("\n4️⃣  RANK FLIGHTS WITH AI")
    print("-" * 70)
    rank_request = {
        "search_id": search_result["search_id"],
        "flights": flights,
        "preferences_prompt": trip_data["notes"],
        "locale": {"hl": "en", "currency": "USD", "tz": "America/New_York"},
    }

    response = requests.post(f"{BASE_URL}/flights/rank", json=rank_request)
    assert response.status_code == 200, f"Flight ranking failed: {response.text}"
    rank_result = response.json()

    print(f"   ✅ Flights ranked successfully!")
    print(f"      Search ID: {rank_result['search_id']}")
    print(f"      Model used: {rank_result['meta']['used_model']}")
    print(f"      Deterministic: {rank_result['meta']['deterministic']}")
    if rank_result["meta"].get("notes"):
        for note in rank_result["meta"]["notes"]:
            print(f"      Note: {note}")

    print(f"\n   🏆 Top 5 Ranked Flights:")
    for i, flight_id in enumerate(rank_result["ordered_ids"][:5], 1):
        rank_item = next((item for item in rank_result["items"] if item["id"] == flight_id), None)
        original_flight = next((f for f in flights if f["id"] == flight_id), None)

        if rank_item and original_flight:
            print(f"\n      #{i} - AI Score: {rank_item['score']:.2f}")
            print(f"         Title: {rank_item['title']}")
            print(f"         Rationale: {rank_item['rationale_short']}")
            print(f"         Pros: {', '.join(rank_item['pros_keywords'])}")
            print(f"         Cons: {', '.join(rank_item['cons_keywords'])}")
            print(
                f"         Price: ${original_flight['price']['amount']} | "
                f"Duration: {original_flight['total_duration_min']}min | "
                f"Stops: {original_flight['stops']}"
            )

    # Step 5: Select the best flight
    print("\n5️⃣  SELECT FLIGHT")
    print("-" * 70)
    
    # Get the top-ranked flight
    best_flight_id = rank_result["ordered_ids"][0]
    best_rank_item = next(item for item in rank_result["items"] if item["id"] == best_flight_id)
    best_flight = next(f for f in flights if f["id"] == best_flight_id)

    # Prepare selection request
    first_leg = best_flight["legs"][0]
    last_leg = best_flight["legs"][-1]

    selection_request = {
        "trip_id": trip_id,
        "flight_id": best_flight["id"],
        "airline": first_leg["marketing"],
        "flight_number": first_leg["flight_no"],
        "departure_airport": first_leg["dep_iata"],
        "arrival_airport": last_leg["arr_iata"],
        "departure_time": first_leg["dep_time"],
        "arrival_time": last_leg["arr_time"],
        "price": best_flight["price"]["amount"],
        "currency": best_flight["price"]["currency"],
        "total_duration_min": best_flight["total_duration_min"],
        "stops": best_flight["stops"],
        "score": best_rank_item["score"],
        "title": best_rank_item["title"],
        "pros_keywords": best_rank_item["pros_keywords"],
        "cons_keywords": best_rank_item["cons_keywords"],
    }

    response = requests.post(
        f"{BASE_URL}/flights/select", json=selection_request, headers=headers
    )
    assert response.status_code == 200, f"Flight selection failed: {response.text}"
    selection_result = response.json()

    print(f"   ✅ Flight selected successfully!")
    print(f"      Message: {selection_result['message']}")
    print(f"      Trip ID: {selection_result['trip_id']}")
    print(f"      Selected Flight:")
    print(f"         Airline: {selection_result['flight']['airline']}")
    print(f"         Flight Number: {selection_result['flight']['flight_number']}")
    print(f"         Route: {selection_result['flight']['route']}")
    print(f"         Price: {selection_result['flight']['price']}")
    print(f"         Departure: {selection_result['flight']['departure']}")

    # Step 6: Retrieve selected flight (dedicated endpoint)
    print("\n6️⃣  GET SELECTED FLIGHT (Dedicated Endpoint)")
    print("-" * 70)
    
    response = requests.get(
        f"{BASE_URL}/flights/{trip_id}/selection", headers=headers
    )
    assert response.status_code == 200, f"GET flight selection failed: {response.text}"
    flight_selection = response.json()

    print(f"   ✅ Flight selection retrieved!")
    selected = flight_selection["selected_flight"]
    print(f"      Flight ID: {selected['flight_id']}")
    print(f"      Airline: {selected['airline']} {selected['flight_number']}")
    print(f"      Route: {selected['departure_airport']} → {selected['arrival_airport']}")
    print(f"      Departure: {selected['departure_time']}")
    print(f"      Arrival: {selected['arrival_time']}")
    print(f"      Price: ${selected['price']} {selected['currency']}")
    print(f"      Duration: {selected['total_duration_min']} minutes")
    print(f"      Stops: {selected['stops']}")
    print(f"      AI Score: {selected['score']}")
    print(f"      Title: {selected['title']}")
    print(f"      Pros: {', '.join(selected['pros_keywords'])}")
    print(f"      Cons: {', '.join(selected['cons_keywords'])}")

    # Step 7: Verify in trip details
    print("\n7️⃣  VERIFY IN TRIP DETAILS")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers)
    assert response.status_code == 200, f"GET trip failed: {response.text}"
    trip_details = response.json()

    assert trip_details["selected_flight"] is not None, "Flight not in trip!"
    trip_flight = trip_details["selected_flight"]

    print(f"   ✅ Flight verified in trip details!")
    print(f"      Trip Status: {trip_details['status']}")
    print(f"      Selected Flight:")
    print(f"         {trip_flight['airline']} {trip_flight['flight_number']}")
    print(f"         {trip_flight['departure_airport']} → {trip_flight['arrival_airport']}")
    print(f"         ${trip_flight['price']} {trip_flight['currency']}")
    print(f"         AI Score: {trip_flight['score']}")

    # Verify data consistency
    assert selected["flight_id"] == trip_flight["flight_id"]
    assert selected["airline"] == trip_flight["airline"]
    assert selected["flight_number"] == trip_flight["flight_number"]
    assert selected["price"] == trip_flight["price"]

    print("\n" + "=" * 70)
    print("✅ ALL FLIGHT ENDPOINT TESTS PASSED!")
    print("=" * 70)
    print("\nTested Endpoints:")
    print("   1. POST /api/v1/auth/login")
    print("   2. POST /api/v1/trips")
    print("   3. POST /api/v1/flights/search ⭐ NEW")
    print("   4. POST /api/v1/flights/rank")
    print("   5. POST /api/v1/flights/select")
    print("   6. GET  /api/v1/flights/{trip_id}/selection ⭐ NEW")
    print("   7. GET  /api/v1/trips/{trip_id}")
    print("\n✨ Complete flight workflow validated!")


if __name__ == "__main__":
    try:
        test_all_flight_endpoints()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
