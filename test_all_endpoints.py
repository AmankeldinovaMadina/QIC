"""
Comprehensive test suite for all API endpoints.
Tests authentication, trips, flights, hotels, and full workflow.
"""

import json
from datetime import datetime, timedelta

import requests

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

# Test data storage
test_data = {
    "username": f"test_user_{datetime.now().timestamp()}",
    "access_token": None,
    "trip_id": None,
    "flight_id": "test_flight_001",
}

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(name):
    """Print test name."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def print_response(response):
    """Print formatted response."""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


# ============================================================================
# TEST 1: Root Endpoint
# ============================================================================
def test_root():
    """Test root endpoint."""
    print_test("Root Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)

        assert response.status_code == 200, "Root endpoint failed"
        data = response.json()
        assert "message" in data, "No message in response"

        print_success("Root endpoint working!")
        return True
    except Exception as e:
        print_error(f"Root endpoint failed: {e}")
        return False


# ============================================================================
# TEST 2: Health Check
# ============================================================================
def test_health():
    """Test health check endpoint."""
    print_test("Health Check")

    try:
        response = requests.get(f"{API_BASE}/health")
        print_response(response)

        assert response.status_code == 200, "Health check failed"
        data = response.json()
        assert data["status"] == "ok", "Health status not ok"

        print_success("Health check passed!")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


# ============================================================================
# TEST 3: User Registration
# ============================================================================
def test_register():
    """Test user registration."""
    print_test("User Registration")

    try:
        payload = {"username": test_data["username"]}
        response = requests.post(f"{API_BASE}/auth/register", json=payload)
        print_response(response)

        assert response.status_code == 200, "Registration failed"
        data = response.json()
        assert "access_token" in data, "No access token in response"
        assert "user_id" in data, "No user_id in response"

        # Store the access token
        test_data["access_token"] = data["access_token"]
        test_data["user_id"] = data["user_id"]

        print_success(f"User registered! Token: {test_data['access_token'][:20]}...")
        print_success(f"User ID: {test_data['user_id']}")
        return True
    except Exception as e:
        print_error(f"Registration failed: {e}")
        return False


# ============================================================================
# TEST 4: User Login
# ============================================================================
def test_login():
    """Test user login."""
    print_test("User Login")

    try:
        payload = {"username": test_data["username"]}
        response = requests.post(f"{API_BASE}/auth/login", json=payload)
        print_response(response)

        assert response.status_code == 200, "Login failed"
        data = response.json()
        assert "access_token" in data, "No access token in response"

        print_success("Login successful!")
        return True
    except Exception as e:
        print_error(f"Login failed: {e}")
        return False


# ============================================================================
# TEST 5: Get Current User
# ============================================================================
def test_get_me():
    """Test getting current user info."""
    print_test("Get Current User Info")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        print_response(response)

        assert response.status_code == 200, "Get user info failed"
        data = response.json()
        assert data["username"] == test_data["username"], "Username mismatch"

        print_success("User info retrieved successfully!")
        return True
    except Exception as e:
        print_error(f"Get user info failed: {e}")
        return False


# ============================================================================
# TEST 6: Create Trip
# ============================================================================
def test_create_trip():
    """Test creating a trip."""
    print_test("Create Trip")

    try:
        start_date = datetime.now() + timedelta(days=30)
        end_date = start_date + timedelta(days=5)

        payload = {
            "from_city": "New York",
            "to_city": "Los Angeles",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "transport": "flight",
            "adults": 2,
            "children": 0,
            "budget_max": 2000.00,
            "notes": "Test trip for comprehensive testing",
        }

        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(f"{API_BASE}/trips", json=payload, headers=headers)
        print_response(response)

        assert response.status_code == 200, "Create trip failed"
        data = response.json()
        assert "id" in data, "No trip ID in response"

        # Store the trip ID
        test_data["trip_id"] = data["id"]

        print_success(f"Trip created! ID: {test_data['trip_id']}")
        return True
    except Exception as e:
        print_error(f"Create trip failed: {e}")
        return False


# ============================================================================
# TEST 7: Get All Trips
# ============================================================================
def test_get_trips():
    """Test getting all user trips."""
    print_test("Get All Trips")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(f"{API_BASE}/trips", headers=headers)
        print_response(response)

        assert response.status_code == 200, "Get trips failed"
        data = response.json()
        assert "trips" in data, "No trips array in response"
        assert data["total"] >= 1, "No trips found"

        print_success(f"Found {data['total']} trip(s)!")
        return True
    except Exception as e:
        print_error(f"Get trips failed: {e}")
        return False


# ============================================================================
# TEST 8: Get Single Trip
# ============================================================================
def test_get_trip():
    """Test getting a single trip."""
    print_test("Get Single Trip")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Get trip failed"
        data = response.json()
        assert data["id"] == test_data["trip_id"], "Trip ID mismatch"

        print_success("Trip retrieved successfully!")
        return True
    except Exception as e:
        print_error(f"Get trip failed: {e}")
        return False


# ============================================================================
# TEST 9: Update Trip
# ============================================================================
def test_update_trip():
    """Test updating a trip."""
    print_test("Update Trip")

    try:
        payload = {
            "notes": "Updated test notes - trip looks great!",
            "budget_max": 2500.00,
        }

        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.patch(
            f"{API_BASE}/trips/{test_data['trip_id']}", json=payload, headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Update trip failed"
        data = response.json()
        assert data["notes"] == payload["notes"], "Notes not updated"

        print_success("Trip updated successfully!")
        return True
    except Exception as e:
        print_error(f"Update trip failed: {e}")
        return False


# ============================================================================
# TEST 10: Flight AI Ranking
# ============================================================================
def test_flight_ranking():
    """Test AI flight ranking."""
    print_test("Flight AI Ranking")

    try:
        payload = {
            "search_id": "test_jfk_lax",
            "preferences_prompt": "I prefer direct flights in the morning, price is important",
            "locale": {"currency": "USD", "hl": "en"},
            "flights": [
                {
                    "id": "flight_1",
                    "price": {"amount": 350, "currency": "USD"},
                    "total_duration_min": 330,
                    "stops": 0,
                    "legs": [
                        {
                            "dep_iata": "JFK",
                            "dep_time": "2025-12-01T08:00:00",
                            "arr_iata": "LAX",
                            "arr_time": "2025-12-01T11:30:00",
                            "marketing": "Delta",
                            "flight_no": "DL123",
                            "duration_min": 330,
                        }
                    ],
                },
                {
                    "id": "flight_2",
                    "price": {"amount": 280, "currency": "USD"},
                    "total_duration_min": 480,
                    "stops": 1,
                    "layovers_min": 95,
                    "legs": [
                        {
                            "dep_iata": "JFK",
                            "dep_time": "2025-12-01T14:00:00",
                            "arr_iata": "ORD",
                            "arr_time": "2025-12-01T16:00:00",
                            "marketing": "United",
                            "flight_no": "UA100",
                            "duration_min": 120,
                        },
                        {
                            "dep_iata": "ORD",
                            "dep_time": "2025-12-01T17:35:00",
                            "arr_iata": "LAX",
                            "arr_time": "2025-12-01T20:00:00",
                            "marketing": "United",
                            "flight_no": "UA200",
                            "duration_min": 145,
                        },
                    ],
                },
            ],
        }

        response = requests.post(f"{API_BASE}/flights/rank", json=payload)
        print_response(response)

        assert response.status_code == 200, "Flight ranking failed"
        data = response.json()
        assert "items" in data, "No ranked items in response"
        assert len(data["items"]) == 2, "Expected 2 ranked flights"

        # Store the top flight for selection test
        test_data["ranked_flight"] = data["items"][0]

        print_success(f"Flights ranked! Top choice: {data['items'][0]['title']}")
        print_info(f"Score: {data['items'][0]['score']}")
        return True
    except Exception as e:
        print_error(f"Flight ranking failed: {e}")
        return False


# ============================================================================
# TEST 11: Select Flight for Trip
# ============================================================================
def test_select_flight():
    """Test selecting a flight for a trip."""
    print_test("Select Flight for Trip")

    try:
        # Use data from the ranked flight
        payload = {
            "trip_id": test_data["trip_id"],
            "flight_id": test_data["flight_id"],
            "airline": "Delta",
            "flight_number": "DL123",
            "departure_airport": "JFK",
            "arrival_airport": "LAX",
            "departure_time": "2025-12-01T08:00:00",
            "arrival_time": "2025-12-01T11:30:00",
            "price": 350.00,
            "currency": "USD",
            "total_duration_min": 330,
            "stops": 0,
            "score": test_data["ranked_flight"]["score"],
            "title": test_data["ranked_flight"]["title"],
            "pros_keywords": test_data["ranked_flight"]["pros_keywords"],
            "cons_keywords": test_data["ranked_flight"]["cons_keywords"],
        }

        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(
            f"{API_BASE}/flights/select", json=payload, headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Flight selection failed"
        data = response.json()
        assert data["success"] == True, "Selection not successful"
        assert data["trip_id"] == test_data["trip_id"], "Trip ID mismatch"

        print_success("Flight selected and saved to trip!")
        return True
    except Exception as e:
        print_error(f"Flight selection failed: {e}")
        return False


# ============================================================================
# TEST 12: Verify Flight Saved to Trip
# ============================================================================
def test_verify_flight_saved():
    """Test that the selected flight is saved in the trip."""
    print_test("Verify Flight Saved to Trip")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Get trip failed"
        data = response.json()
        assert "selected_flight" in data, "No selected_flight in response"
        assert data["selected_flight"] is not None, "selected_flight is null"
        assert data["selected_flight"]["airline"] == "Delta", "Airline mismatch"
        assert (
            data["selected_flight"]["flight_number"] == "DL123"
        ), "Flight number mismatch"

        print_success("Flight data verified in trip!")
        print_info(
            f"Flight: {data['selected_flight']['airline']} {data['selected_flight']['flight_number']}"
        )
        print_info(
            f"Route: {data['selected_flight']['departure_airport']} → {data['selected_flight']['arrival_airport']}"
        )
        return True
    except Exception as e:
        print_error(f"Flight verification failed: {e}")
        return False


# ============================================================================
# TEST 13: Hotel AI Ranking
# ============================================================================
def test_hotel_ranking():
    """Test AI hotel ranking endpoint."""
    print_test("Hotel AI Ranking")

    try:
        # Sample hotels data
        payload = {
            "search_id": "test_tokyo_hotels",
            "preferences_prompt": "I prefer hotels near tourist attractions with good breakfast, free WiFi is important",
            "hotels": [
                {
                    "id": "hotel_1",
                    "name": "Tokyo Grand Hotel",
                    "location": "Shinjuku, Tokyo",
                    "price_per_night": 180.00,
                    "total_price": 900.00,
                    "currency": "USD",
                    "rating": 4.5,
                    "reviews_count": 1250,
                    "hotel_class": 4,
                    "property_type": "Hotel",
                    "amenities": ["WiFi", "Breakfast", "Gym", "Pool", "Restaurant"],
                    "free_cancellation": True,
                },
                {
                    "id": "hotel_2",
                    "name": "Budget Stay Tokyo",
                    "location": "Asakusa, Tokyo",
                    "price_per_night": 80.00,
                    "total_price": 400.00,
                    "currency": "USD",
                    "rating": 3.8,
                    "reviews_count": 456,
                    "hotel_class": 2,
                    "property_type": "Hotel",
                    "amenities": ["WiFi", "Breakfast"],
                    "free_cancellation": False,
                },
                {
                    "id": "hotel_3",
                    "name": "Luxury Palace Tokyo",
                    "location": "Ginza, Tokyo",
                    "price_per_night": 450.00,
                    "total_price": 2250.00,
                    "currency": "USD",
                    "rating": 4.9,
                    "reviews_count": 2890,
                    "hotel_class": 5,
                    "property_type": "Luxury Hotel",
                    "amenities": [
                        "WiFi",
                        "Breakfast",
                        "Gym",
                        "Pool",
                        "Spa",
                        "Restaurant",
                        "Bar",
                        "Concierge",
                    ],
                    "free_cancellation": True,
                },
            ],
        }

        response = requests.post(f"{API_BASE}/hotels/rank", json=payload)
        print_response(response)

        assert response.status_code == 200, "Hotel ranking failed"
        data = response.json()
        assert "items" in data, "No ranked items in response"
        assert len(data["items"]) == 3, "Expected 3 ranked hotels"

        # Store top hotel for selection test
        test_data["ranked_hotel"] = data["items"][0]

        print_success(f"Hotels ranked! Top choice: {data['items'][0]['title']}")
        print_info(f"Score: {data['items'][0]['score']}")
        print_info(f"Pros: {', '.join(data['items'][0]['pros_keywords'][:3])}")

        return True
    except Exception as e:
        print_error(f"Hotel ranking failed: {e}")
        return False


# ============================================================================
# TEST 14: Select Hotel for Trip
# ============================================================================
def test_select_hotel():
    """Test selecting a hotel and saving it to a trip."""
    print_test("Select Hotel for Trip")

    try:
        check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")

        payload = {
            "trip_id": test_data["trip_id"],
            "hotel_id": "hotel_1",
            "hotel_name": "Tokyo Grand Hotel",
            "location": "Shinjuku, Tokyo",
            "price_per_night": 180.00,
            "total_price": 900.00,
            "currency": "USD",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "rating": 4.5,
            "reviews_count": 1250,
            "hotel_class": 4,
            "amenities": ["WiFi", "Breakfast", "Gym", "Pool", "Restaurant"],
            "free_cancellation": True,
            "score": test_data["ranked_hotel"]["score"],
            "title": test_data["ranked_hotel"]["title"],
            "pros_keywords": test_data["ranked_hotel"]["pros_keywords"],
            "cons_keywords": test_data["ranked_hotel"]["cons_keywords"],
        }

        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(
            f"{API_BASE}/hotels/select", json=payload, headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Hotel selection failed"
        data = response.json()
        assert data["success"] == True, "Selection not successful"
        assert data["trip_id"] == test_data["trip_id"], "Trip ID mismatch"

        print_success("Hotel selected and saved to trip!")
        return True
    except Exception as e:
        print_error(f"Hotel selection failed: {e}")
        return False


# ============================================================================
# TEST 15: Verify Hotel Saved to Trip
# ============================================================================
def test_verify_hotel_saved():
    """Test that the selected hotel is saved in the trip."""
    print_test("Verify Hotel Saved to Trip")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Get trip failed"
        data = response.json()
        assert "selected_hotel" in data, "No selected_hotel in response"
        assert data["selected_hotel"] is not None, "selected_hotel is null"
        assert (
            data["selected_hotel"]["hotel_name"] == "Tokyo Grand Hotel"
        ), "Hotel name mismatch"

        hotel = data["selected_hotel"]
        print_success("Hotel data verified in trip!")
        print_info(f"Hotel: {hotel['hotel_name']}")
        print_info(f"Location: {hotel['location']}")
        print_info(f"Price: ${hotel['total_price']} ({hotel['currency']})")
        print_info(f"Rating: {hotel['rating']}/5")

        return True
    except Exception as e:
        print_error(f"Hotel verification failed: {e}")
        return False


# ============================================================================
# TEST 16: Finalize Trip
# ============================================================================
def test_finalize_trip():
    """Test finalizing a trip."""
    print_test("Finalize Trip")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(
            f"{API_BASE}/trips/{test_data['trip_id']}/finalize", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Finalize trip failed"
        data = response.json()
        assert data["status"] == "planned", "Trip status not planned"

        print_success("Trip finalized!")
        return True
    except Exception as e:
        print_error(f"Finalize trip failed: {e}")
        return False


# ============================================================================
# TEST 17: Get Trip Plan
# ============================================================================
def test_get_trip_plan():
    """Test getting trip plan."""
    print_test("Get Trip Plan")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}/plan", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Get trip plan failed"
        data = response.json()
        assert "plan_json" in data, "No plan_json in response"

        print_success("Trip plan retrieved!")
        return True
    except Exception as e:
        print_error(f"Get trip plan failed: {e}")
        return False


# ============================================================================
# TEST 18: Get Trip Checklist
# ============================================================================
def test_get_trip_checklist():
    """Test getting trip checklist."""
    print_test("Get Trip Checklist")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}/checklist", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Get trip checklist failed"
        data = response.json()
        assert "checklist_json" in data, "No checklist_json in response"

        print_success("Trip checklist retrieved!")
        return True
    except Exception as e:
        print_error(f"Get trip checklist failed: {e}")
        return False


# ============================================================================
# TEST 19: Delete Trip (Optional - cleanup)
# ============================================================================
def test_delete_trip():
    """Test deleting a trip."""
    print_test("Delete Trip (Cleanup)")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.delete(
            f"{API_BASE}/trips/{test_data['trip_id']}", headers=headers
        )
        print_response(response)

        assert response.status_code == 200, "Delete trip failed"

        print_success("Trip deleted successfully!")
        return True
    except Exception as e:
        print_error(f"Delete trip failed: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def run_all_tests():
    """Run all tests in sequence."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}COMPREHENSIVE API ENDPOINT TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Base URL: {BASE_URL}{RESET}")
    print(f"{YELLOW}API Base: {API_BASE}{RESET}")

    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("User Registration", test_register),
        ("User Login", test_login),
        ("Get Current User", test_get_me),
        ("Create Trip", test_create_trip),
        ("Get All Trips", test_get_trips),
        ("Get Single Trip", test_get_trip),
        ("Update Trip", test_update_trip),
        ("Flight AI Ranking", test_flight_ranking),
        ("Select Flight", test_select_flight),
        ("Verify Flight Saved", test_verify_flight_saved),
        ("Hotel AI Ranking", test_hotel_ranking),
        ("Select Hotel", test_select_hotel),
        ("Verify Hotel Saved", test_verify_hotel_saved),
        ("Finalize Trip", test_finalize_trip),
        ("Get Trip Plan", test_get_trip_plan),
        ("Get Trip Checklist", test_get_trip_checklist),
        ("Delete Trip", test_delete_trip),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
        print(f"{name:.<40} {status}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Total Tests: {len(results)}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"{BLUE}{'='*60}{RESET}\n")

    return passed == len(results)


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        exit(1)
