"""Test script for entertainment ranking with link field."""

import requests
import json

BASE_URL = "http://localhost:8001"


def test_entertainment_ranking_with_link():
    """Test that entertainment ranking returns the link field."""
    
    print("Testing Entertainment Ranking with Link Field")
    print("="*60)
    
    # Sample venue data with links
    venues_data = [
        {
            "position": 1,
            "place_id": "ChIJ_test_venue_1",
            "title": "Tokyo Skytree",
            "rating": 4.6,
            "reviews": 50000,
            "price": "$$$",
            "type": "tourist_attraction",
            "types": ["tourist_attraction", "point_of_interest"],
            "address": "1 Chome-1-2 Oshiage, Sumida City, Tokyo",
            "phone": "+81-3-1234-5678",
            "website": "https://www.tokyo-skytree.jp",
            "description": "Tokyo's tallest structure with observation decks",
            "thumbnail": "https://example.com/skytree.jpg",
            "link": "https://www.google.com/maps/place/Tokyo+Skytree"
        },
        {
            "position": 2,
            "place_id": "ChIJ_test_venue_2",
            "title": "Senso-ji Temple",
            "rating": 4.5,
            "reviews": 35000,
            "price": "$",
            "type": "buddhist_temple",
            "types": ["buddhist_temple", "place_of_worship", "tourist_attraction"],
            "address": "2 Chome-3-1 Asakusa, Taito City, Tokyo",
            "phone": "+81-3-9876-5432",
            "description": "Tokyo's oldest temple, founded in 628 AD",
            "thumbnail": "https://example.com/sensoji.jpg",
            "link": "https://www.google.com/maps/place/Senso-ji+Temple"
        },
        {
            "position": 3,
            "place_id": "ChIJ_test_venue_3",
            "title": "Tsukiji Outer Market",
            "rating": 4.3,
            "reviews": 15000,
            "price": "$$",
            "type": "market",
            "types": ["market", "food", "shopping"],
            "address": "4 Chome Tsukiji, Chuo City, Tokyo",
            "website": "https://www.tsukiji.or.jp",
            "description": "Famous fish market with fresh seafood and sushi",
            "thumbnail": "https://example.com/tsukiji.jpg",
            "link": "https://www.google.com/maps/place/Tsukiji+Outer+Market"
        }
    ]
    
    # Ranking request
    rank_request = {
        "trip_id": "test_trip_123",
        "search_id": "test_search_456",
        "venues": venues_data,
        "preferences_prompt": "I want to visit iconic cultural landmarks and experience local food culture in Tokyo.",
        "entertainment_tags": ["culture", "food", "sightseeing"]
    }
    
    print("\n1. Testing POST /api/v1/entertainment/rank")
    print("-" * 60)
    print(f"Request: POST {BASE_URL}/api/v1/entertainment/rank")
    print(f"Venues count: {len(venues_data)}")
    print(f"All venues have links: {all('link' in v for v in venues_data)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/entertainment/rank",
            json=rank_request
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ranking successful!")
            
            print(f"\nTrip ID: {result['trip_id']}")
            print(f"Search ID: {result['search_id']}")
            print(f"Number of ranked venues: {len(result['items'])}")
            print(f"Model used: {result['meta']['used_model']}")
            
            print("\n" + "="*60)
            print("Ranked Venues with Links:")
            print("="*60)
            
            for i, item in enumerate(result['items'], 1):
                print(f"\n{i}. Place ID: {item['place_id']}")
                print(f"   Score: {item['score']}")
                print(f"   Title: {item['title']}")
                print(f"   Pros: {', '.join(item['pros_keywords'][:3])}")
                print(f"   Cons: {', '.join(item['cons_keywords'][:3]) if item['cons_keywords'] else 'None'}")
                
                # Check if link is present
                if 'link' in item and item['link']:
                    print(f"   ✅ Link: {item['link']}")
                else:
                    print(f"   ❌ Link: MISSING")
            
            # Verify all items have links
            links_present = [item.get('link') for item in result['items']]
            all_have_links = all(link is not None for link in links_present)
            
            print("\n" + "="*60)
            if all_have_links:
                print("✅ SUCCESS: All ranked venues have links!")
            else:
                missing_count = sum(1 for link in links_present if link is None)
                print(f"⚠️  WARNING: {missing_count} venue(s) missing link field")
            
            return result
            
        else:
            print(f"❌ FAILED: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the server is running on port 8001.")
        print("Run: python -m app.main")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = test_entertainment_ranking_with_link()
    
    if result:
        print("\n" + "="*60)
        print("Test completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Test failed - check server and try again")
        print("="*60)
