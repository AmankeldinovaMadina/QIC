"""
Test suite for hotel endpoints: search, AI ranking, and selection.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
test_data = {
    "username": f"hotel_test_user_{datetime.now().timestamp()}",
    "access_token": None,
    "trip_id": None
}

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        # Truncate large responses
        if isinstance(data, dict) and "data" in data:
            print(f"Response: {{data: <truncated {len(str(data['data']))} chars>}}")
        else:
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    except:
        print(f"Response: {response.text[:200]}")


# ============================================================================
# Setup: Register and Create Trip
# ============================================================================

def test_setup():
    """Register user and create a trip."""
    print_test("Setup: Register User and Create Trip")
    
    # Register
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={"username": test_data["username"]}
    )
    assert response.status_code == 200
    data = response.json()
    test_data["access_token"] = data["access_token"]
    print_success(f"User registered: {test_data['username']}")
    
    # Create trip
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(days=5)
    
    response = requests.post(
        f"{API_BASE}/trips",
        json={
            "from_city": "New York",
            "to_city": "Tokyo",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "transport": "flight",
            "adults": 2,
            "budget_max": 5000.00
        },
        headers={"Authorization": f"Bearer {test_data['access_token']}"}
    )
    assert response.status_code == 200
    test_data["trip_id"] = response.json()["id"]
    print_success(f"Trip created: {test_data['trip_id']}")
    
    return True


# ============================================================================
# Test 1: Hotel AI Ranking
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
                    "free_cancellation": True
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
                    "free_cancellation": False
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
                    "amenities": ["WiFi", "Breakfast", "Gym", "Pool", "Spa", "Restaurant", "Bar", "Concierge"],
                    "free_cancellation": True
                }
            ]
        }
        
        response = requests.post(
            f"{API_BASE}/hotels/rank",
            json=payload
        )
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
# Test 2: Select Hotel for Trip
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
            "cons_keywords": test_data["ranked_hotel"]["cons_keywords"]
        }
        
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(
            f"{API_BASE}/hotels/select",
            json=payload,
            headers=headers
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
# Test 3: Verify Hotel Saved to Trip
# ============================================================================

def test_verify_hotel_saved():
    """Test that the selected hotel is saved in the trip."""
    print_test("Verify Hotel Saved to Trip")
    
    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}",
            headers=headers
        )
        print_response(response)
        
        assert response.status_code == 200, "Get trip failed"
        data = response.json()
        assert "selected_hotel" in data, "No selected_hotel in response"
        assert data["selected_hotel"] is not None, "selected_hotel is null"
        assert data["selected_hotel"]["hotel_name"] == "Tokyo Grand Hotel", "Hotel name mismatch"
        
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
# Main Test Runner
# ============================================================================

def run_hotel_tests():
    """Run all hotel tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}HOTEL ENDPOINTS TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Base URL: {BASE_URL}{RESET}")
    print(f"{YELLOW}API Base: {API_BASE}{RESET}")
    
    tests = [
        ("Setup", test_setup),
        ("Hotel AI Ranking", test_hotel_ranking),
        ("Select Hotel", test_select_hotel),
        ("Verify Hotel Saved", test_verify_hotel_saved),
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
        success = run_hotel_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
