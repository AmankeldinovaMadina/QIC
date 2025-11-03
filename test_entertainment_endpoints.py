#!/usr/bin/env python3
"""Test entertainment endpoints: search, rank, and select multiple venues."""

import requests

# Configuration
BASE_URL = "http://localhost:8001/api/v1"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Test data will be stored here
test_data = {}


def print_test(test_name):
    """Print test header."""
    print(f"\n{BLUE}{'=' * 60}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 60}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


# ============================================================================
# TEST 1: Setup - Register and Create Trip
# ============================================================================
def test_setup():
    """Setup: Register user and create trip with entertainment tags."""
    print_test("1. Setup - Register & Create Trip")

    # Register
    username = f"entertainment_user_{__import__('time').time()}"
    resp = requests.post(f"{BASE_URL}/auth/register", json={"username": username})

    if resp.status_code != 200:
        print_error(f"Registration failed: {resp.text}")
        return False

    data = resp.json()
    test_data["token"] = data["access_token"]
    test_data["user_id"] = data["user_id"]
    print_success(f"Registered user: {username}")

    # Create trip with entertainment tags
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    trip_payload = {
        "from_city": "San Francisco",
        "to_city": "Tokyo",
        "start_date": "2024-12-15T09:00:00Z",
        "end_date": "2024-12-21T18:00:00Z",
        "transport": "flight",
        "adults": 2,
        "children": 0,
        "entertainment_tags": ["culture", "food", "sightseeing", "museums", "shopping"],
        "budget_max": 5000,
        "notes": "First time in Tokyo, interested in traditional and modern culture",
    }

    resp = requests.post(f"{BASE_URL}/trips", json=trip_payload, headers=headers)

    if resp.status_code != 200:
        print_error(f"Trip creation failed: {resp.text}")
        return False

    trip = resp.json()
    test_data["trip_id"] = trip["id"]
    print_success(f"Created trip: {trip['from_city']} → {trip['to_city']}")
    print_info(f"Entertainment tags: {', '.join(trip['entertainment_tags'])}")

    return True


# ============================================================================
# TEST 2: Search Entertainment Venues
# ============================================================================
def test_search_venues():
    """Search for entertainment venues using Google Maps."""
    print_test("2. Search Entertainment Venues")

    headers = {"Authorization": f"Bearer {test_data['token']}"}
    search_payload = {
        "trip_id": test_data["trip_id"],
        "destination": "Tokyo",
        # Let it use entertainment_tags from trip
    }

    resp = requests.post(
        f"{BASE_URL}/entertainment/search", json=search_payload, headers=headers
    )

    if resp.status_code != 200:
        print_error(f"Entertainment search failed: {resp.text}")
        return False

    result = resp.json()
    test_data["search_id"] = result["search_id"]
    test_data["venues"] = result["venues"]

    print_success(f"Found {result['total_results']} venues")
    print_info(f"Query: {result['query']}")

    # Show first 5 venues
    print(f"\n{YELLOW}Sample venues:{RESET}")
    for venue in result["venues"][:5]:
        rating_str = f"{venue['rating']}★" if venue.get("rating") else "No rating"
        price_str = venue.get("price", "")
        print(f"  • {venue['title']}")
        print(
            f"    Type: {venue.get('type', 'N/A')} | {rating_str} ({venue.get('reviews', 0)} reviews) {price_str}"
        )
        if venue.get("address"):
            print(f"    Address: {venue['address']}")

    return True


# ============================================================================
# TEST 3: Rank Entertainment Venues with AI
# ============================================================================
def test_rank_venues():
    """Rank entertainment venues using OpenAI."""
    print_test("3. Rank Entertainment Venues with AI")

    headers = {"Authorization": f"Bearer {test_data['token']}"}
    rank_payload = {
        "trip_id": test_data["trip_id"],
        "search_id": test_data["search_id"],
        "venues": test_data["venues"],
        "preferences_prompt": "Looking for authentic cultural experiences and great food. Budget-conscious but willing to pay for quality.",
    }

    resp = requests.post(
        f"{BASE_URL}/entertainment/rank", json=rank_payload, headers=headers
    )

    if resp.status_code != 200:
        print_error(f"Entertainment ranking failed: {resp.text}")
        return False

    result = resp.json()
    test_data["ranked_items"] = result["items"]

    print_success(f"Ranked {len(result['items'])} venues")
    print_info(f"Model used: {result['meta']['used_model']}")

    # Show top 10 ranked venues
    print(f"\n{YELLOW}Top 10 Recommendations:{RESET}")
    for i, item in enumerate(result["items"][:10], 1):
        # Find original venue data
        venue = next(
            (v for v in test_data["venues"] if v["place_id"] == item["place_id"]), None
        )

        print(f"\n{i}. {item['title']} (Score: {item['score']:.2f})")
        if venue:
            print(f"   Name: {venue['title']}")
            rating_str = f"{venue['rating']}★" if venue.get("rating") else "No rating"
            print(
                f"   {venue.get('type', 'N/A')} | {rating_str} ({venue.get('reviews', 0)} reviews)"
            )
        print(f"   Why: {item['rationale_short']}")
        print(f"   Pros: {', '.join(item['pros_keywords'])}")
        print(f"   Cons: {', '.join(item['cons_keywords'])}")

    return True


# ============================================================================
# TEST 4: Select Multiple Entertainment Venues
# ============================================================================
def test_select_venues():
    """Select top 5 entertainment venues and save to trip."""
    print_test("4. Select Multiple Entertainment Venues")

    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # Prepare selections: top 5 venues with their ranking data
    selections = []
    for i, item in enumerate(test_data["ranked_items"][:5]):
        # Find original venue data
        venue = next(
            (v for v in test_data["venues"] if v["place_id"] == item["place_id"]), None
        )
        if venue:
            selections.append(
                {
                    "venue": venue,
                    "ranking": item,
                }
            )

    select_payload = {
        "trip_id": test_data["trip_id"],
        "selections": selections,
    }

    resp = requests.post(
        f"{BASE_URL}/entertainment/select", json=select_payload, headers=headers
    )

    if resp.status_code != 200:
        print_error(f"Entertainment selection failed: {resp.text}")
        return False

    result = resp.json()
    print_success(result["message"])
    print_info(f"Selected {result['selected_count']} venues")

    # Show selected venues
    print(f"\n{YELLOW}Selected Venues:{RESET}")
    for sel in result["selections"]:
        rating_str = f"{sel['rating']}★" if sel.get("rating") else "No rating"
        score_str = f"(AI Score: {sel['score']:.2f})" if sel.get("score") else ""
        print(f"  • {sel['venue_name']}")
        print(f"    Type: {sel.get('venue_type', 'N/A')} | {rating_str} {score_str}")
        print(f"    {sel.get('title', '')}")

    return True


# ============================================================================
# TEST 5: Retrieve Entertainment Selections
# ============================================================================
def test_get_selections():
    """Retrieve all entertainment selections for the trip."""
    print_test("5. Retrieve Entertainment Selections")

    headers = {"Authorization": f"Bearer {test_data['token']}"}

    resp = requests.get(
        f"{BASE_URL}/entertainment/{test_data['trip_id']}/selections", headers=headers
    )

    if resp.status_code != 200:
        print_error(f"Failed to retrieve selections: {resp.text}")
        return False

    result = resp.json()
    print_success(f"Retrieved {result['total_selections']} selections")

    # Show details
    print(f"\n{YELLOW}Entertainment Selections Details:{RESET}")
    for sel in result["selections"]:
        print(f"\n  • {sel['venue_name']}")
        print(f"    ID: {sel['venue_id']}")
        print(f"    Type: {sel.get('venue_type', 'N/A')}")
        if sel.get("address"):
            print(f"    Address: {sel['address']}")
        if sel.get("rating"):
            print(
                f"    Rating: {sel['rating']}★ ({sel.get('reviews_count', 0)} reviews)"
            )
        if sel.get("price_level"):
            print(f"    Price: {sel['price_level']}")
        if sel.get("website"):
            print(f"    Website: {sel['website']}")
        if sel.get("phone"):
            print(f"    Phone: {sel['phone']}")
        print(f"    AI Title: {sel.get('title', 'N/A')}")
        if sel.get("pros_keywords"):
            print(f"    Pros: {', '.join(sel['pros_keywords'])}")
        if sel.get("cons_keywords"):
            print(f"    Cons: {', '.join(sel['cons_keywords'])}")

    return True


# ============================================================================
# TEST 6: Verify Trip Contains Selections
# ============================================================================
def test_verify_trip():
    """Verify the trip contains entertainment selections."""
    print_test("6. Verify Trip Contains Selections")

    headers = {"Authorization": f"Bearer {test_data['token']}"}

    resp = requests.get(f"{BASE_URL}/trips/{test_data['trip_id']}", headers=headers)

    if resp.status_code != 200:
        print_error(f"Failed to retrieve trip: {resp.text}")
        return False

    trip = resp.json()

    # Check selected_entertainments field
    if trip.get("selected_entertainments"):
        print_success(
            f"Trip has {len(trip['selected_entertainments'])} entertainment venues"
        )
        print_info("Entertainment data is stored in trip for AI planning")
    else:
        print_error("Trip does not have selected_entertainments field")
        return False

    return True


# ============================================================================
# Run All Tests
# ============================================================================
def run_all_tests():
    """Run all entertainment endpoint tests."""
    tests = [
        ("Setup - Register & Create Trip", test_setup),
        ("Search Entertainment Venues", test_search_venues),
        ("Rank Venues with AI", test_rank_venues),
        ("Select Multiple Venues", test_select_venues),
        ("Retrieve Selections", test_get_selections),
        ("Verify Trip Data", test_verify_trip),
    ]

    print(f"\n{BLUE}{'=' * 60}")
    print("ENTERTAINMENT ENDPOINTS TEST SUITE")
    print(f"{'=' * 60}{RESET}\n")

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            if not success:
                print_error(f"Test failed: {test_name}")
                break
        except Exception as e:
            print_error(f"Test exception: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))
            break

    # Print summary
    print(f"\n{BLUE}{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}{RESET}\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"{status}  {test_name}")

    print(f"\n{YELLOW}Results: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"{GREEN}All tests passed! ✓{RESET}\n")
    else:
        print(f"{RED}Some tests failed. ✗{RESET}\n")


if __name__ == "__main__":
    run_all_tests()
