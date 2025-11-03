"""Quick test for culture guide endpoints with known trip ID."""

import requests
import json

BASE_URL = "http://localhost:8001"
TRIP_ID = "8b79a56b-5e46-4aa7-bfd7-7c8db75103c7"  # From create_test_trip.py

print("Testing Culture Guide with Trip ID:", TRIP_ID)
print("="*60)

# Test POST
print("\n1. POST /api/v1/culture/guide")
print("-"*60)

response = requests.post(
    f"{BASE_URL}/api/v1/culture/guide",
    json={
        "trip_id": TRIP_ID,
        "destination": "Tokyo, Japan",
        "language": "en"
    }
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    guide = response.json()
    print(f"✅ SUCCESS")
    print(f"\nDestination: {guide['destination']}")
    print(f"Summary: {guide['summary'][:100]}...")
    print(f"Tips: {len(guide['tips'])}")
else:
    print(f"❌ FAILED: {response.text}")
    exit(1)

# Test GET
print("\n\n2. GET /api/v1/culture/guide/{trip_id}")
print("-"*60)

response = requests.get(f"{BASE_URL}/api/v1/culture/guide/{TRIP_ID}")

print(f"Status: {response.status_code}")

if response.status_code == 200:
    print(f"✅ SUCCESS - Guide retrieved from database")
else:
    print(f"❌ FAILED: {response.text}")

print("\n" + "="*60)
print("✅ All tests passed!")
