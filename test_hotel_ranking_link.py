"""Test script for hotel ranking with link field."""

import json

import requests

BASE_URL = "http://localhost:8001"


def test_hotel_ranking_with_link():
    """Test that hotel ranking returns the link field."""

    print("Testing Hotel Ranking with Link Field")
    print("=" * 60)

    # Sample hotel data with links
    hotels_data = [
        {
            "id": "hotel_1",
            "name": "Grand Hotel Tokyo",
            "location": "Shibuya, Tokyo",
            "price_per_night": 200.0,
            "total_price": 1400.0,
            "currency": "USD",
            "rating": 4.5,
            "reviews_count": 1250,
            "hotel_class": 5,
            "property_type": "Hotel",
            "amenities": ["WiFi", "Pool", "Gym", "Spa", "Restaurant"],
            "free_cancellation": True,
            "thumbnail": "https://example.com/hotel1.jpg",
            "link": "https://www.google.com/travel/hotels/s/booking/hotel1",
        },
        {
            "id": "hotel_2",
            "name": "Budget Inn Tokyo",
            "location": "Asakusa, Tokyo",
            "price_per_night": 80.0,
            "total_price": 560.0,
            "currency": "USD",
            "rating": 3.8,
            "reviews_count": 450,
            "hotel_class": 3,
            "property_type": "Hotel",
            "amenities": ["WiFi", "Breakfast"],
            "free_cancellation": False,
            "thumbnail": "https://example.com/hotel2.jpg",
            "link": "https://www.google.com/travel/hotels/s/booking/hotel2",
        },
        {
            "id": "hotel_3",
            "name": "Modern Apartment Shinjuku",
            "location": "Shinjuku, Tokyo",
            "price_per_night": 150.0,
            "total_price": 1050.0,
            "currency": "USD",
            "rating": 4.2,
            "reviews_count": 320,
            "hotel_class": 4,
            "property_type": "Apartment",
            "amenities": ["WiFi", "Kitchen", "Washer"],
            "free_cancellation": True,
            "thumbnail": "https://example.com/hotel3.jpg",
            "link": "https://www.google.com/travel/hotels/s/booking/hotel3",
        },
    ]

    # Ranking request
    rank_request = {
        "search_id": "test_search_123",
        "hotels": hotels_data,
        "preferences_prompt": "I want a highly-rated hotel with good amenities and free cancellation, close to tourist attractions.",
    }

    print("\n1. Testing POST /api/v1/hotels/rank")
    print("-" * 60)
    print(f"Request: POST {BASE_URL}/api/v1/hotels/rank")
    print(f"Hotels count: {len(hotels_data)}")
    print(f"All hotels have links: {all('link' in h for h in hotels_data)}")

    try:
        response = requests.post(f"{BASE_URL}/api/v1/hotels/rank", json=rank_request)

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Ranking successful!")

            print(f"\nSearch ID: {result['search_id']}")
            print(f"Number of ranked hotels: {len(result['items'])}")
            print(f"Model used: {result['meta']['used_model']}")

            print("\n" + "=" * 60)
            print("Ranked Hotels with Links:")
            print("=" * 60)

            for i, item in enumerate(result["items"], 1):
                print(f"\n{i}. Hotel ID: {item['id']}")
                print(f"   Score: {item['score']}")
                print(f"   Title: {item['title']}")
                print(f"   Pros: {', '.join(item['pros_keywords'][:3])}")
                print(
                    f"   Cons: {', '.join(item['cons_keywords'][:3]) if item['cons_keywords'] else 'None'}"
                )

                # Check if link is present
                if "link" in item and item["link"]:
                    print(f"   ✅ Link: {item['link']}")
                else:
                    print(f"   ❌ Link: MISSING")

            # Verify all items have links
            links_present = [item.get("link") for item in result["items"]]
            all_have_links = all(link is not None for link in links_present)

            print("\n" + "=" * 60)
            if all_have_links:
                print("✅ SUCCESS: All ranked hotels have links!")
            else:
                missing_count = sum(1 for link in links_present if link is None)
                print(f"⚠️  WARNING: {missing_count} hotel(s) missing link field")

            return result

        else:
            print(f"❌ FAILED: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(
            "❌ Error: Could not connect to server. Make sure the server is running on port 8001."
        )
        print("Run: python -m app.main")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    result = test_hotel_ranking_with_link()

    if result:
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Test failed - check server and try again")
        print("=" * 60)
