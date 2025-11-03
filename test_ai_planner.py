"""
Test script for AI trip planning functionality.
Tests the finalize trip endpoint with AI plan generation.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
test_data = {
    "username": f"ai_planner_test_{datetime.now().timestamp()}",
    "access_token": None,
    "trip_id": None,
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


def print_json(data, max_lines=50):
    """Print JSON with optional truncation."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    lines = json_str.split("\n")
    if len(lines) > max_lines:
        print("\n".join(lines[:max_lines]))
        print(f"{YELLOW}... ({len(lines) - max_lines} more lines){RESET}")
    else:
        print(json_str)


# ============================================================================
# Test 1: Setup - Register and Create Trip
# ============================================================================


def test_setup():
    """Register user and create a trip for planning."""
    print_test("Setup: Register User and Create Trip")

    # Register
    response = requests.post(
        f"{API_BASE}/auth/register", json={"username": test_data["username"]}
    )
    assert response.status_code == 200
    data = response.json()
    test_data["access_token"] = data["access_token"]
    print_success(f"User registered: {test_data['username']}")

    # Create trip with more details for better AI planning
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
            "children": 0,
            "budget_max": 3000.00,
            "entertainment_tags": ["culture", "food", "sightseeing", "museums"],
            "notes": "First time visiting Japan. Interested in traditional culture, amazing food, and modern technology.",
            "timezone": "Asia/Tokyo",
        },
        headers={"Authorization": f"Bearer {test_data['access_token']}"},
    )
    assert response.status_code == 200
    test_data["trip_id"] = response.json()["id"]
    print_success(f"Trip created: {test_data['trip_id']}")

    return True


# ============================================================================
# Test 2: Add Flight to Trip (Optional but improves plan quality)
# ============================================================================


def test_add_flight():
    """Add a sample flight to the trip for better AI planning."""
    print_test("Add Flight to Trip")

    try:
        start_date = datetime.now() + timedelta(days=30)

        payload = {
            "trip_id": test_data["trip_id"],
            "flight_id": "ai_test_flight_001",
            "airline": "JAL",
            "flight_number": "JL006",
            "departure_airport": "JFK",
            "arrival_airport": "NRT",
            "departure_time": start_date.replace(hour=13, minute=0).isoformat(),
            "arrival_time": (start_date + timedelta(hours=14)).replace(hour=17, minute=0).isoformat(),
            "price": 1200.00,
            "currency": "USD",
            "total_duration_min": 840,  # 14 hours
            "stops": 0,
            "score": 0.95,
            "title": "Direct Flight to Tokyo",
            "pros_keywords": ["direct", "good timing", "reliable airline"],
            "cons_keywords": ["long flight"],
        }

        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(f"{API_BASE}/flights/select", json=payload, headers=headers)

        assert response.status_code == 200
        print_success("Flight added to trip!")
        return True
    except Exception as e:
        print_error(f"Failed to add flight: {e}")
        return False


# ============================================================================
# Test 3: Finalize Trip with AI Planning
# ============================================================================


def test_finalize_with_ai():
    """Finalize trip and generate AI-powered daily plan."""
    print_test("Finalize Trip with AI Planning")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.post(
            f"{API_BASE}/trips/{test_data['trip_id']}/finalize", headers=headers
        )

        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print_error(f"Failed: {response.text}")
            return False

        data = response.json()
        assert data["status"] == "planned", "Trip status should be 'planned'"

        print_success("Trip finalized with AI-generated plan!")
        print_info(f"Trip ID: {data['id']}")
        print_info(f"Status: {data['status']}")

        return True
    except Exception as e:
        print_error(f"Finalize failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# ============================================================================
# Test 4: Retrieve and Validate AI-Generated Plan
# ============================================================================


def test_retrieve_plan():
    """Retrieve the AI-generated trip plan and validate structure."""
    print_test("Retrieve AI-Generated Trip Plan")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}/plan", headers=headers
        )

        print(f"Status: {response.status_code}")
        assert response.status_code == 200

        data = response.json()
        plan = data["plan_json"]

        # Validate plan structure
        assert "title" in plan, "Plan missing title"
        assert "days" in plan, "Plan missing days"
        assert "timezone" in plan, "Plan missing timezone"
        assert "start_date" in plan, "Plan missing start_date"
        assert "end_date" in plan, "Plan missing end_date"

        print_success("Plan retrieved successfully!")
        print_info(f"Plan Title: {plan['title']}")
        print_info(f"Timezone: {plan['timezone']}")
        print_info(f"Duration: {plan['start_date']} to {plan['end_date']}")
        print_info(f"Number of days: {len(plan['days'])}")

        # Show day summaries
        print(f"\n{YELLOW}Daily Itinerary:{RESET}")
        for i, day in enumerate(plan["days"], 1):
            print(f"\n{BLUE}Day {i} - {day['date']}{RESET}")
            if day.get("city"):
                print(f"  Location: {day['city']}")
            if day.get("summary"):
                print(f"  Summary: {day['summary']}")
            if day.get("events"):
                print(f"  Events: {len(day['events'])}")
                for j, event in enumerate(day["events"][:3], 1):  # Show first 3 events
                    print(f"    {j}. {event['title']} ({event.get('priority', 'N/A')})")
                if len(day["events"]) > 3:
                    print(f"    ... and {len(day['events']) - 3} more events")

        # Optional: Print full plan (truncated)
        print(f"\n{YELLOW}Full Plan JSON (first 30 lines):{RESET}")
        print_json(plan, max_lines=30)

        return True
    except Exception as e:
        print_error(f"Retrieve plan failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# ============================================================================
# Test 5: Retrieve Checklist
# ============================================================================


def test_retrieve_checklist():
    """Retrieve the trip checklist."""
    print_test("Retrieve Trip Checklist")

    try:
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(
            f"{API_BASE}/trips/{test_data['trip_id']}/checklist", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        checklist = data["checklist_json"]

        print_success("Checklist retrieved!")
        print_info(f"Pre-trip items: {len(checklist.get('pre_trip', []))}")
        print_info(f"Packing items: {len(checklist.get('packing', []))}")
        print_info(f"Documents: {len(checklist.get('documents', []))}")

        return True
    except Exception as e:
        print_error(f"Retrieve checklist failed: {e}")
        return False


# ============================================================================
# Main Test Runner
# ============================================================================


def run_ai_planner_tests():
    """Run all AI planner tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}AI TRIP PLANNER TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Base URL: {BASE_URL}{RESET}")

    tests = [
        ("Setup", test_setup),
        ("Add Flight", test_add_flight),
        ("Finalize with AI", test_finalize_with_ai),
        ("Retrieve Plan", test_retrieve_plan),
        ("Retrieve Checklist", test_retrieve_checklist),
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
        success = run_ai_planner_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
