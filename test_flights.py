"""Test script for flight search and AI ranking."""

import asyncio
import json
from app.flights.schemas import FlightSearchParams, RankRequest, LocalePrefs
from app.flights.providers import google_flights_provider
from app.flights.ai_ranker import openai_flight_ranker


async def test_flight_search():
    """Test flight search functionality."""
    print("Testing flight search...")
    
    # Test search parameters
    params = FlightSearchParams(
        type=2,  # One way
        departure_id="JFK",
        arrival_id="LAX", 
        outbound_date="2025-12-15",
        currency="USD",
        adults=1
    )
    
    try:
        # This will fail without SerpApi key, but let's test the structure
        print(f"Search params: {params.model_dump()}")
        print("✓ Search parameters validation passed")
        
        # Test heuristic ranking (doesn't need API keys)
        mock_flights = []  # Empty for now
        
        rank_request = RankRequest(
            search_id="test_123",
            preferences_prompt="I want cheap flights, prefer morning departures, no red-eyes",
            flights=mock_flights,
            locale=LocalePrefs(hl="en", currency="USD")
        )
        
        print(f"Rank request: {rank_request.model_dump()}")
        print("✓ Rank request validation passed")
        
    except Exception as e:
        print(f"✗ Error: {e}")


async def test_ai_ranker_heuristic():
    """Test AI ranker with heuristic fallback."""
    print("\nTesting AI ranker heuristic...")
    
    # Create mock request with no flights (will trigger heuristic)
    request = RankRequest(
        search_id="test_heuristic", 
        preferences_prompt="Test preferences",
        flights=[]
    )
    
    try:
        result = await openai_flight_ranker.rank_flights(request)
        print(f"Heuristic result: {result.model_dump()}")
        print("✓ Heuristic ranking passed")
        
    except Exception as e:
        print(f"✗ Error: {e}")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Flight Search & AI Ranking Tests")
    print("=" * 50)
    
    await test_flight_search()
    await test_ai_ranker_heuristic()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("Note: Full functionality requires API keys in .env:")
    print("- SERPAPI_KEY for flight search")
    print("- OPENAI_API_KEY for AI ranking")


if __name__ == "__main__":
    asyncio.run(main())