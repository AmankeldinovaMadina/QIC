"""Direct test of entertainment AI ranker with link field (no API call)."""

import asyncio
from app.entertainment.ai_ranker import OpenAIEntertainmentRanker
from app.entertainment.schemas import EntertainmentRankRequest, GoogleMapsVenue


async def test_ranker_directly():
    """Test the AI ranker directly without going through the API."""
    
    print("Testing Entertainment AI Ranker with Link Field (Direct)")
    print("="*60)
    
    # Sample venue data with links
    venues = [
        GoogleMapsVenue(
            position=1,
            place_id="ChIJ_test_venue_1",
            title="Tokyo Skytree",
            rating=4.6,
            reviews=50000,
            price="$$$",
            type="tourist_attraction",
            types=["tourist_attraction", "point_of_interest"],
            address="1 Chome-1-2 Oshiage, Sumida City, Tokyo",
            phone="+81-3-1234-5678",
            website="https://www.tokyo-skytree.jp",
            description="Tokyo's tallest structure with observation decks",
            thumbnail="https://example.com/skytree.jpg",
            link="https://www.google.com/maps/place/Tokyo+Skytree"
        ),
        GoogleMapsVenue(
            position=2,
            place_id="ChIJ_test_venue_2",
            title="Senso-ji Temple",
            rating=4.5,
            reviews=35000,
            price="$",
            type="buddhist_temple",
            types=["buddhist_temple", "place_of_worship", "tourist_attraction"],
            address="2 Chome-3-1 Asakusa, Taito City, Tokyo",
            phone="+81-3-9876-5432",
            description="Tokyo's oldest temple, founded in 628 AD",
            thumbnail="https://example.com/sensoji.jpg",
            link="https://www.google.com/maps/place/Senso-ji+Temple"
        ),
        GoogleMapsVenue(
            position=3,
            place_id="ChIJ_test_venue_3",
            title="Tsukiji Outer Market",
            rating=4.3,
            reviews=15000,
            price="$$",
            type="market",
            types=["market", "food", "shopping"],
            address="4 Chome Tsukiji, Chuo City, Tokyo",
            website="https://www.tsukiji.or.jp",
            description="Famous fish market with fresh seafood and sushi",
            thumbnail="https://example.com/tsukiji.jpg",
            link="https://www.google.com/maps/place/Tsukiji+Outer+Market"
        )
    ]
    
    # Create ranking request
    request = EntertainmentRankRequest(
        trip_id="test_trip_123",
        search_id="test_search_456",
        venues=venues,
        preferences_prompt="I want to visit iconic cultural landmarks and experience local food culture in Tokyo.",
        entertainment_tags=["culture", "food", "sightseeing"]
    )
    
    print(f"\nVenues count: {len(venues)}")
    print(f"All venues have links: {all(v.link is not None for v in venues)}")
    
    try:
        # Initialize ranker
        ranker = OpenAIEntertainmentRanker()
        
        # Rank venues
        print("\nRanking venues...")
        result = await ranker.rank_venues(request)
        
        print(f"✅ Ranking successful!")
        print(f"\nModel used: {result.meta.used_model}")
        print(f"Number of ranked venues: {len(result.items)}")
        
        print("\n" + "="*60)
        print("Ranked Venues with Links:")
        print("="*60)
        
        for i, item in enumerate(result.items, 1):
            print(f"\n{i}. Place ID: {item.place_id}")
            print(f"   Score: {item.score}")
            print(f"   Title: {item.title}")
            print(f"   Pros: {', '.join(item.pros_keywords[:3])}")
            print(f"   Cons: {', '.join(item.cons_keywords[:3]) if item.cons_keywords else 'None'}")
            
            # Check if link is present
            if item.link:
                print(f"   ✅ Link: {item.link}")
            else:
                print(f"   ❌ Link: MISSING")
        
        # Verify all items have links
        links_present = [item.link for item in result.items]
        all_have_links = all(link is not None for link in links_present)
        
        print("\n" + "="*60)
        if all_have_links:
            print("✅ SUCCESS: All ranked venues have links!")
            return True
        else:
            missing_count = sum(1 for link in links_present if link is None)
            print(f"⚠️  WARNING: {missing_count} venue(s) missing link field")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_ranker_directly())
    
    if success:
        print("\n" + "="*60)
        print("✅ Test completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Test failed")
        print("="*60)
