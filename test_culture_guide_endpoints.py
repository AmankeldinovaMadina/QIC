"""Test script for culture guide endpoints."""

import json

import requests

BASE_URL = "http://localhost:8001"


def test_culture_guide_endpoints():
    """Test POST and GET culture guide endpoints."""

    print("Testing Culture Guide Endpoints\n" + "=" * 50)

    # Test data
    trip_id = "test-trip-id-123"

    # Test POST - Create culture guide
    print("\n1. Testing POST /api/v1/culture/guide")
    print("-" * 50)

    post_data = {"trip_id": trip_id, "destination": "Tokyo, Japan", "language": "en"}

    print(f"Request: POST {BASE_URL}/api/v1/culture/guide")
    print(f"Body: {json.dumps(post_data, indent=2)}")

    try:
        response = requests.post(f"{BASE_URL}/api/v1/culture/guide", json=post_data)

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Culture guide generated and saved successfully!")
            result = response.json()
            print(f"\nDestination: {result['destination']}")
            print(f"Summary: {result['summary']}")
            print(f"\nTips ({len(result['tips'])}):")
            for i, tip in enumerate(result["tips"], 1):
                print(f"\n  {i}. {tip['emoji']} {tip['title']}")
                print(f"     Category: {tip['category']}")
                print(f"     Tip: {tip['tip']}")
        else:
            print(f"❌ Failed: {response.text}")
            return

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the server is running.")
        return
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    # Test GET - Retrieve culture guide
    print("\n\n2. Testing GET /api/v1/culture/guide/{trip_id}")
    print("-" * 50)

    print(f"Request: GET {BASE_URL}/api/v1/culture/guide/{trip_id}")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/culture/guide/{trip_id}")

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Culture guide retrieved successfully!")
            result = response.json()
            print(f"\nDestination: {result['destination']}")
            print(f"Summary: {result['summary']}")
            print(f"\nTips ({len(result['tips'])}):")
            for i, tip in enumerate(result["tips"], 1):
                print(f"\n  {i}. {tip['emoji']} {tip['title']}")
                print(f"     Category: {tip['category']}")
        elif response.status_code == 404:
            print("❌ Culture guide not found for this trip")
        else:
            print(f"❌ Failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test GET with non-existent trip_id
    print("\n\n3. Testing GET /api/v1/culture/guide/{non_existent_trip_id}")
    print("-" * 50)

    non_existent_trip_id = "non-existent-trip-999"
    print(f"Request: GET {BASE_URL}/api/v1/culture/guide/{non_existent_trip_id}")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/culture/guide/{non_existent_trip_id}"
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 404:
            print("✅ Correctly returns 404 for non-existent culture guide")
            print(f"Message: {response.json()['detail']}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 50)
    print("Testing completed!")


if __name__ == "__main__":
    test_culture_guide_endpoints()
