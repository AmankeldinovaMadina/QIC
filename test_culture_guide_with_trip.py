"""Test script for culture guide endpoints with trip creation."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def test_culture_guide_with_trip():
    """Test culture guide endpoints with proper trip creation."""
    
    print("Testing Culture Guide Endpoints (with Trip Creation)")
    print("="*60)
    
    # Step 1: Create a test trip
    print("\n1. Creating a test trip...")
    print("-" * 60)
    
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(days=7)
    
    trip_data = {
        "from_city": "New York",
        "to_city": "Tokyo",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "transport": "flight",
        "adults": 2,
        "children": 0,
        "budget_min": 2000,
        "budget_max": 5000,
        "notes": "Test trip for culture guide"
    }
    
    try:
        # Note: You may need authentication. If so, you'll need to login first
        response = requests.post(
            f"{BASE_URL}/api/v1/trips",
            json=trip_data
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201 or response.status_code == 200:
            trip = response.json()
            trip_id = trip.get("id")
            print(f"✅ Trip created successfully!")
            print(f"   Trip ID: {trip_id}")
            print(f"   Destination: {trip['to_city']}")
        elif response.status_code == 401 or response.status_code == 403:
            print("⚠️  Authentication required. Testing with manual trip_id instead...")
            print("\nPlease create a trip first and use its ID for testing.")
            print("Or, let's try with a test trip_id that might exist...")
            trip_id = input("\nEnter a valid trip_id (or press Enter to exit): ").strip()
            if not trip_id:
                print("Exiting test.")
                return
        else:
            print(f"❌ Failed to create trip: {response.text}")
            print("\nTrying with a manual trip_id instead...")
            trip_id = input("Enter a valid trip_id (or press Enter to exit): ").strip()
            if not trip_id:
                print("Exiting test.")
                return
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the server is running.")
        return
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Step 2: Generate culture guide
    print("\n\n2. Testing POST /api/v1/culture/guide")
    print("-" * 60)
    
    culture_data = {
        "trip_id": trip_id,
        "destination": "Tokyo, Japan",
        "language": "en"
    }
    
    print(f"Request: POST {BASE_URL}/api/v1/culture/guide")
    print(f"Body: {json.dumps(culture_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/culture/guide",
            json=culture_data
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Culture guide generated and saved successfully!")
            result = response.json()
            print(f"\nDestination: {result['destination']}")
            print(f"Summary: {result['summary']}")
            print(f"\nTips ({len(result['tips'])}):")
            for i, tip in enumerate(result['tips'], 1):
                print(f"\n  {i}. {tip['emoji']} {tip['title']}")
                print(f"     Category: {tip['category']}")
                print(f"     Tip: {tip['tip'][:100]}...")
        else:
            print(f"❌ Failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Step 3: Retrieve culture guide
    print("\n\n3. Testing GET /api/v1/culture/guide/{trip_id}")
    print("-" * 60)
    
    print(f"Request: GET {BASE_URL}/api/v1/culture/guide/{trip_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/culture/guide/{trip_id}")
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Culture guide retrieved successfully!")
            result = response.json()
            print(f"\nDestination: {result['destination']}")
            print(f"Summary: {result['summary']}")
            print(f"\nNumber of tips: {len(result['tips'])}")
        elif response.status_code == 404:
            print("❌ Culture guide not found for this trip")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Step 4: POST again - should return cached
    print("\n\n4. Testing POST again (should return cached version)")
    print("-" * 60)
    
    print(f"Request: POST {BASE_URL}/api/v1/culture/guide")
    print("This should be fast (no OpenAI call)...")
    
    try:
        import time
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/culture/guide",
            json=culture_data
        )
        
        elapsed = time.time() - start_time
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Cached culture guide returned!")
            if elapsed < 1.0:
                print("   ⚡ Very fast response - definitely cached!")
            else:
                print("   ⚠️  Slower response - may have regenerated")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Step 5: Test 404 for non-existent trip
    print("\n\n5. Testing GET with non-existent trip_id")
    print("-" * 60)
    
    non_existent_trip_id = "non-existent-trip-999"
    print(f"Request: GET {BASE_URL}/api/v1/culture/guide/{non_existent_trip_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/culture/guide/{non_existent_trip_id}")
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly returns 404 for non-existent culture guide")
            print(f"Message: {response.json()['detail']}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Testing completed!")
    print(f"\nTest Trip ID used: {trip_id}")


if __name__ == "__main__":
    test_culture_guide_with_trip()
