#!/usr/bin/env python3
"""
Simple test for flight selection debugging
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"
ACCESS_TOKEN = "e920fee0-9317-46a8-b13c-5229cdf95fe5"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def test_simple_flight_selection():
    print("🧪 Simple Flight Selection Test")
    
    # First, create a trip
    print("\n1. Creating a trip...")
    trip_payload = {
        "from_city": "New York", 
        "to_city": "Miami",
        "start_date": "2025-12-20T00:00:00",
        "end_date": "2025-12-23T00:00:00",
        "transport": "flight",
        "adults": 1
    }
    
    trip_response = requests.post(f"{BASE_URL}/trips", json=trip_payload, headers=HEADERS)
    print(f"Trip creation: {trip_response.status_code}")
    
    if trip_response.status_code == 200:
        trip_data = trip_response.json()
        trip_id = trip_data['id']
        print(f"✅ Trip created: {trip_id}")
        
        # Now test flight selection
        print("\n2. Selecting flight...")
        
        flight_payload = {
            "trip_id": trip_id,
            "flight_id": "simple_test_flight",
            "airline": "American",
            "flight_number": "AA1234",
            "departure_airport": "JFK",
            "arrival_airport": "MIA",
            "departure_time": "2025-12-20T08:00:00",
            "arrival_time": "2025-12-20T11:30:00",
            "price": 350.0,
            "currency": "USD",
            "total_duration_min": 210,
            "stops": 0
        }
        
        print("Request payload:")
        print(json.dumps(flight_payload, indent=2))
        
        flight_response = requests.post(f"{BASE_URL}/flights/select", json=flight_payload, headers=HEADERS)
        print(f"\nFlight selection: {flight_response.status_code}")
        print(f"Response headers: {dict(flight_response.headers)}")
        print(f"Response text: '{flight_response.text}'")
        
        if flight_response.status_code == 200:
            result = flight_response.json()
            print("✅ Flight selection successful!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Flight selection failed")
    else:
        print(f"❌ Trip creation failed: {trip_response.text}")

if __name__ == "__main__":
    test_simple_flight_selection()