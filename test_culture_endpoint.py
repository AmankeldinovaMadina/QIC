"""
Test script for the culture guide endpoint.
Tests the /culture-guide endpoint with various destinations.
"""

import json

import requests

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

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


def print_response(data):
    """Print formatted JSON response."""
    print(f"{YELLOW}Response:{RESET}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ============================================================================
# Test 1: Culture Guide for Tokyo
# ============================================================================


def test_tokyo_culture():
    """Test culture guide for Tokyo, Japan."""
    print_test("Culture Guide - Tokyo")

    try:
        payload = {"destination": "Tokyo, Japan", "language": "en"}

        response = requests.post(f"{API_BASE}/culture-guide", json=payload)

        print(f"Status: {response.status_code}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        print_response(data)

        # Validate structure
        assert "destination" in data, "Missing destination"
        assert "summary" in data, "Missing summary"
        assert "tips" in data, "Missing tips"
        assert (
            len(data["tips"]) >= 3
        ), f"Expected at least 3 tips, got {len(data['tips'])}"
        assert (
            len(data["tips"]) <= 4
        ), f"Expected at most 4 tips, got {len(data['tips'])}"

        # Validate each tip
        for i, tip in enumerate(data["tips"], 1):
            assert "category" in tip, f"Tip {i} missing category"
            assert "title" in tip, f"Tip {i} missing title"
            assert "tip" in tip, f"Tip {i} missing tip"
            assert "do" in tip, f"Tip {i} missing do"
            assert "avoid" in tip, f"Tip {i} missing avoid"
            assert "emoji" in tip, f"Tip {i} missing emoji"

            print_info(f"Tip {i}: {tip['emoji']} {tip['title']} ({tip['category']})")

        print_success(f"Culture guide generated for {data['destination']}!")
        print_info(f"Summary: {data['summary']}")
        return True

    except Exception as e:
        print_error(f"Tokyo culture test failed: {e}")
        return False


# ============================================================================
# Test 2: Culture Guide for Dubai
# ============================================================================


def test_dubai_culture():
    """Test culture guide for Dubai, UAE."""
    print_test("Culture Guide - Dubai")

    try:
        payload = {"destination": "Dubai, UAE"}

        response = requests.post(f"{API_BASE}/culture-guide", json=payload)

        print(f"Status: {response.status_code}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        print_response(data)

        # Validate structure
        assert len(data["tips"]) >= 3, f"Expected at least 3 tips"

        # Print tips
        for i, tip in enumerate(data["tips"], 1):
            print_info(f"Tip {i}: {tip['emoji']} {tip['title']}")
            print_info(f"  Do: {tip['do'][:60]}...")
            print_info(f"  Avoid: {tip['avoid'][:60]}...")

        print_success(f"Culture guide generated for {data['destination']}!")
        return True

    except Exception as e:
        print_error(f"Dubai culture test failed: {e}")
        return False


# ============================================================================
# Test 3: Culture Guide for Paris
# ============================================================================


def test_paris_culture():
    """Test culture guide for Paris, France."""
    print_test("Culture Guide - Paris")

    try:
        payload = {"destination": "Paris"}

        response = requests.post(f"{API_BASE}/culture-guide", json=payload)

        print(f"Status: {response.status_code}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # Validate tips count
        assert len(data["tips"]) >= 3, f"Expected at least 3 tips"

        print_success(f"Culture guide generated for {data['destination']}!")
        print_info(f"Summary: {data['summary']}")

        # Print categories
        categories = [tip["category"] for tip in data["tips"]]
        print_info(f"Categories covered: {', '.join(categories)}")

        return True

    except Exception as e:
        print_error(f"Paris culture test failed: {e}")
        return False


# ============================================================================
# Main Test Runner
# ============================================================================


def run_culture_tests():
    """Run all culture guide tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}CULTURE GUIDE ENDPOINT TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Base URL: {BASE_URL}{RESET}")
    print(f"{YELLOW}API Base: {API_BASE}{RESET}")

    tests = [
        ("Tokyo Culture Guide", test_tokyo_culture),
        ("Dubai Culture Guide", test_dubai_culture),
        ("Paris Culture Guide", test_paris_culture),
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
        success = run_culture_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
