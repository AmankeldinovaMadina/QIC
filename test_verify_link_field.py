"""Test to verify server has updated code with link field."""

import json

import requests

print("Testing if server has updated hotel ranking code...")
print("=" * 60)

# Test with heuristic ranking (no OpenAI) to avoid delays
hotels_data = [
    {
        "id": "test_hotel",
        "name": "Test Hotel",
        "location": "Tokyo",
        "price_per_night": 100.0,
        "total_price": 700.0,
        "currency": "USD",
        "rating": 4.0,
        "link": "https://example.com/hotel",
    }
]

response = requests.post(
    "http://localhost:8001/api/v1/hotels/rank",
    json={"search_id": "test", "hotels": hotels_data, "preferences_prompt": "test"},
)

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    item = data["items"][0]

    print("Response item keys:", list(item.keys()))
    print("\nHas 'link' key:", "link" in item)

    if "link" in item:
        print(f"Link value: {item['link']}")
        if item["link"] == "https://example.com/hotel":
            print("\n✅ SUCCESS: Link field is working correctly!")
        elif item["link"] is None:
            print("\n⚠️  Link field exists but is None - check server logs")
        else:
            print(f"\n⚠️  Link field has unexpected value: {item['link']}")
    else:
        print("\n❌ FAILED: Link field is missing from response")
        print("\n⚠️  Server may need to be restarted to pick up code changes")
        print("   Run: python -m app.main")
else:
    print(f"❌ Request failed: {response.text}")
