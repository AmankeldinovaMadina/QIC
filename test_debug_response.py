"""Debug test to see full response structure."""

import json

import requests

BASE_URL = "http://localhost:8001"

hotels_data = [
    {
        "id": "hotel_1",
        "name": "Test Hotel",
        "location": "Tokyo",
        "price_per_night": 100.0,
        "total_price": 700.0,
        "currency": "USD",
        "rating": 4.5,
        "reviews_count": 100,
        "hotel_class": 4,
        "amenities": ["WiFi"],
        "link": "https://example.com/hotel1",
    }
]

rank_request = {
    "search_id": "test",
    "hotels": hotels_data,
    "preferences_prompt": "Good hotel",
}

response = requests.post(f"{BASE_URL}/api/v1/hotels/rank", json=rank_request)

print("Status:", response.status_code)
print("\nFull Response:")
print(json.dumps(response.json(), indent=2))
