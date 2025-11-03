#!/usr/bin/env python3
"""
Test script for flight selection endpoints
Tests the complete workflow: AI ranking -> Flight selection -> Trip update
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8001/api/v1"

# Authentication token from user registration
ACCESS_TOKEN = "e920fee0-9317-46a8-b13c-5229cdf95fe5"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def register_test_user():
    """Register a test user and get access token"""
    global ACCESS_TOKEN, HEADERS
    
    print("🔐 Registering test user...")
    
    registration_data = {
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)
        if response.status_code == 200:
            result = response.json()
            ACCESS_TOKEN = result["access_token"]
            HEADERS["Authorization"] = f"Bearer {ACCESS_TOKEN}"
            print(f"✅ User registered successfully!")
            print(f"Username: {result['username']}")
            print(f"User ID: {result['user_id']}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_complete_workflow():
    """Test the complete flight workflow with authentication"""
    
    print("🚀 Testing Complete Flight Workflow\n")
    
    # Step 1: Create a real trip
    print("1️⃣ Creating a test trip...")
    
    trip_payload = {
        "from_city": "New York",
        "to_city": "Los Angeles",
        "start_date": "2025-12-01T00:00:00",
        "end_date": "2025-12-05T00:00:00", 
        "transport": "flight",
        "adults": 1,
        "children": 0,
        "budget_min": 300,
        "budget_max": 1000,
        "notes": "Business trip"
    }
    
    try:
        trip_response = requests.post(f"{BASE_URL}/trips", json=trip_payload, headers=HEADERS)
        print(f"Trip creation status: {trip_response.status_code}")
        
        if trip_response.status_code == 200:
            trip_data = trip_response.json()
            trip_id = trip_data['id']
            print(f"✅ Trip created successfully!")
            print(f"Trip ID: {trip_id}")
            print(f"From: {trip_data['from_city']} To: {trip_data['to_city']}")
            
            # Step 2: Test AI ranking
            print("\n2️⃣ Testing AI Flight Ranking...")
            
            ranking_payload = {
                "search_id": f"search_{trip_id}",
                "preferences_prompt": "I prefer direct flights with good value for money, departing in the morning",
                "flights": [
                    {
                        "id": "flight1", 
                        "price": {
                            "amount": 450.0,
                            "currency": "USD"
                        },
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
                                "duration_min": 330
                            }
                        ]
                    },
                    {
                        "id": "flight2",
                        "price": {
                            "amount": 380.0,
                            "currency": "USD"
                        },
                        "total_duration_min": 330,
                        "stops": 0,
                        "legs": [
                            {
                                "dep_iata": "JFK",
                                "dep_time": "2025-12-01T14:15:00",
                                "arr_iata": "LAX",
                                "arr_time": "2025-12-01T17:45:00", 
                                "marketing": "United",
                                "flight_no": "UA456",
                                "duration_min": 330
                            }
                        ]
                    },
                    {
                        "id": "flight3",
                        "price": {
                            "amount": 420.0,
                            "currency": "USD"
                        },
                        "total_duration_min": 345,
                        "stops": 1,
                        "legs": [
                            {
                                "dep_iata": "JFK",
                                "dep_time": "2025-12-01T10:30:00",
                                "arr_iata": "LAX",
                                "arr_time": "2025-12-01T14:15:00",
                                "marketing": "American",
                                "flight_no": "AA789", 
                                "duration_min": 345
                            }
                        ]
                    }
                ]
            }
            
            ranking_response = requests.post(f"{BASE_URL}/flights/ai-rank", json=ranking_payload, headers=HEADERS)
            print(f"AI Ranking status: {ranking_response.status_code}")
            
            if ranking_response.status_code == 200:
                ranking_result = ranking_response.json()
                print("✅ AI Ranking successful!")
                print(f"Ranked {len(ranking_result.get('items', []))} flights")
                
                # Get the top ranked flight
                if ranking_result.get('items'):
                    top_flight_item = ranking_result['items'][0]
                    top_flight_id = top_flight_item['id']
                    
                    print(f"Top flight: {top_flight_item.get('title')}")
                    print(f"Score: {top_flight_item.get('score')}")
                    print(f"Pros: {top_flight_item.get('pros_keywords')}")
                    
                    # Find the original flight data
                    original_flight = None
                    for flight in ranking_payload['flights']:
                        if flight['id'] == top_flight_id:
                            original_flight = flight
                            break
                    
                    if original_flight:
                        # Step 3: Test flight selection
                        print("\n3️⃣ Testing Flight Selection...")
                        
                        # Convert the flight data to the selection format (flattened)
                        selection_payload = {
                            "trip_id": trip_id,
                            "flight_id": original_flight['id'],
                            "airline": original_flight['legs'][0]['marketing'],
                            "flight_number": original_flight['legs'][0]['flight_no'],
                            "departure_airport": original_flight['legs'][0]['dep_iata'],
                            "arrival_airport": original_flight['legs'][0]['arr_iata'],
                            "departure_time": original_flight['legs'][0]['dep_time'],
                            "arrival_time": original_flight['legs'][0]['arr_time'],
                            "price": original_flight['price']['amount'],
                            "currency": original_flight['price']['currency'],
                            "total_duration_min": original_flight['total_duration_min'],
                            "stops": original_flight['stops'],
                            "score": top_flight_item['score'],
                            "title": top_flight_item['title'],
                            "pros_keywords": top_flight_item['pros_keywords'],
                            "cons_keywords": top_flight_item['cons_keywords']
                        }
                        
                        selection_response = requests.post(f"{BASE_URL}/flights/select", json=selection_payload, headers=HEADERS)
                        print(f"Flight selection status: {selection_response.status_code}")
                        
                        if selection_response.status_code == 200:
                            selection_result = selection_response.json()
                            print("✅ Flight selection successful!")
                            print(f"Success: {selection_result.get('success')}")
                            print(f"Message: {selection_result.get('message')}")
                            
                            # Display selected flight info from trip
                            if selection_result.get('trip', {}).get('selected_flight'):
                                selected = selection_result['trip']['selected_flight']
                                print(f"Selected flight: {selected.get('airline')} {selected.get('flight_number')}")
                                print(f"Route: {selected.get('departure_airport')} → {selected.get('arrival_airport')}")
                                print(f"Price: ${selected.get('price')} {selected.get('currency')}")
                                print(f"Departure: {selected.get('departure_time')}")
                                
                            # Step 4: Verify the trip was updated
                            print("\n4️⃣ Verifying trip update...")
                            
                            trip_get_response = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=HEADERS)
                            if trip_get_response.status_code == 200:
                                updated_trip = trip_get_response.json()
                                if updated_trip.get('selected_flight'):
                                    print("✅ Flight successfully saved to trip!")
                                    trip_flight = updated_trip['selected_flight']
                                    print(f"Trip has flight: {trip_flight.get('airline')} {trip_flight.get('flight_number')}")
                                else:
                                    print("❌ Flight not found in updated trip")
                            else:
                                print(f"❌ Failed to retrieve updated trip: {trip_get_response.status_code}")
                                
                        else:
                            print(f"❌ Flight selection failed: {selection_response.status_code}")
                            print(f"Error: {selection_response.text}")
                    else:
                        print("❌ Could not find original flight data")
                else:
                    print("❌ No ranked flights returned")
            else:
                print(f"❌ AI Ranking failed: {ranking_response.status_code}")
                print(f"Error: {ranking_response.text}")
        else:
            print(f"❌ Trip creation failed: {trip_response.status_code}")
            print(f"Error: {trip_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_flight_selection_endpoint():
    """Test the flight selection endpoint directly with mock data"""
    
    print("🎯 Testing Flight Selection Endpoint Only\n")
    
    # Create a trip first
    print("Creating test trip...")
    trip_payload = {
        "from_city": "Miami", 
        "to_city": "Boston",
        "start_date": "2025-12-15T00:00:00",
        "end_date": "2025-12-18T00:00:00",
        "transport": "flight",
        "adults": 2,
        "budget_max": 800
    }
    
    try:
        trip_response = requests.post(f"{BASE_URL}/trips", json=trip_payload, headers=HEADERS)
        if trip_response.status_code == 200:
            trip_data = trip_response.json()
            trip_id = trip_data['id']
            print(f"✅ Test trip created: {trip_id}")
            
            # Test flight selection with correct flattened format
            print("Selecting flight for trip...")
            
            selection_payload = {
                "trip_id": trip_id,
                "flight_id": "flight_test_123",
                "airline": "JetBlue",
                "flight_number": "B6789",
                "departure_airport": "MIA",
                "arrival_airport": "BOS",
                "departure_time": "2025-12-15T09:15:00",
                "arrival_time": "2025-12-15T12:45:00", 
                "price": 299.0,
                "currency": "USD",
                "total_duration_min": 210,
                "stops": 0,
                "score": 0.85,
                "title": "Great value direct flight",
                "pros_keywords": ["direct", "affordable", "good timing"],
                "cons_keywords": ["basic service"]
            }
            
            response = requests.post(f"{BASE_URL}/flights/select", json=selection_payload, headers=HEADERS)
            print(f"Selection status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Flight selection successful!")
                print(f"Success: {result.get('success')}")
                print(f"Message: {result.get('message')}")
                if result.get('trip', {}).get('selected_flight'):
                    flight = result['trip']['selected_flight']
                    print(f"Selected: {flight['airline']} {flight['flight_number']}")
            else:
                print(f"❌ Selection failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        else:
            print(f"❌ Trip creation failed: {trip_response.status_code}")
            print(f"Error: {trip_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_ai_ranking_endpoint():
    """Test AI ranking endpoint with correct schema"""
    
    print("🤖 Testing AI Flight Ranking Endpoint\n")
    
    # Create properly formatted flight data matching the schema
    ranking_payload = {
        "search_id": "search123",
        "preferences_prompt": "I prefer direct flights with good value for money, departing in the morning",
        "flights": [
            {
                "id": "flight1", 
                "price": {
                    "amount": 450.0,
                    "currency": "USD"
                },
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
                        "duration_min": 330
                    }
                ]
            },
            {
                "id": "flight2",
                "price": {
                    "amount": 380.0,
                    "currency": "USD"
                },
                "total_duration_min": 330,
                "stops": 0,
                "legs": [
                    {
                        "dep_iata": "JFK",
                        "dep_time": "2025-12-01T14:15:00",
                        "arr_iata": "LAX",
                        "arr_time": "2025-12-01T17:45:00", 
                        "marketing": "United",
                        "flight_no": "UA456",
                        "duration_min": 330
                    }
                ]
            },
            {
                "id": "flight3",
                "price": {
                    "amount": 420.0,
                    "currency": "USD"
                },
                "total_duration_min": 345,
                "stops": 1,
                "legs": [
                    {
                        "dep_iata": "JFK",
                        "dep_time": "2025-12-01T10:30:00",
                        "arr_iata": "LAX",
                        "arr_time": "2025-12-01T14:15:00",
                        "marketing": "American",
                        "flight_no": "AA789", 
                        "duration_min": 345
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/flights/ai-rank", json=ranking_payload, headers=HEADERS)
        print(f"AI Ranking status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Ranking successful!")
            print(f"Ranked {len(result.get('items', []))} flights")
            
            # Show top ranked flight
            if result.get('items'):
                top_flight = result['items'][0]
                print(f"Top flight: {top_flight.get('title')}")
                print(f"Score: {top_flight.get('score')}")
                print(f"Pros: {top_flight.get('pros_keywords')}")
        else:
            print(f"❌ AI Ranking failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_health_endpoint():
    """Test the health endpoint to verify API is working"""
    
    print("❤️ Testing Health Endpoint\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API is healthy!")
            print(f"Status: {result.get('status')}")
            print(f"Version: {result.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8001")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("FLIGHT SELECTION ENDPOINT TESTING WITH AUTH")
    print("=" * 60)
    
    # Test health first
    test_health_endpoint()
    
    print("\n" + "=" * 60)
    
    # Test AI ranking
    test_ai_ranking_endpoint()
    
    print("\n" + "=" * 60)
    
    # Test flight selection only
    test_flight_selection_endpoint()
    
    print("\n" + "=" * 60)
    
    # Test complete workflow
    test_complete_workflow()
    
    print("\n✨ All tests complete!")