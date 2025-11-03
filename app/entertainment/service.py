"""Service for fetching entertainment venues from Google Maps via SerpAPI."""

import uuid
from typing import List, Optional

import httpx

from app.core.settings import settings
from app.entertainment.schemas import (
    EntertainmentSearchRequest,
    EntertainmentSearchResponse,
    GoogleMapsVenue,
    GPSCoordinates,
    OperatingHours,
)


class GoogleMapsService:
    """Service for interacting with Google Maps API via SerpAPI."""

    def __init__(self):
        if not settings.serpapi_key:
            raise RuntimeError("SERPAPI_KEY missing. Cannot fetch Google Maps data.")
        self.api_key = settings.serpapi_key
        self.base_url = "https://serpapi.com/search.json"

    async def search_venues(
        self, request: EntertainmentSearchRequest, entertainment_tags: Optional[List[str]] = None
    ) -> EntertainmentSearchResponse:
        """Search for entertainment venues using Google Maps API."""
        
        # Build search query based on entertainment_tags or custom query
        if request.query:
            search_query = request.query
        elif entertainment_tags:
            # Convert entertainment tags to search query
            search_query = self._build_query_from_tags(entertainment_tags, request.destination)
        else:
            search_query = f"entertainment in {request.destination}"

        # Build location parameter
        if request.latitude and request.longitude:
            ll_param = f"@{request.latitude},{request.longitude},{request.zoom}"
        else:
            # Use destination name (SerpAPI will geocode it)
            ll_param = None

        # Build API parameters
        params = {
            "engine": "google_maps",
            "q": search_query,
            "type": "search",
            "api_key": self.api_key,
        }

        if ll_param:
            params["ll"] = ll_param
        else:
            # Add destination to query for better results
            params["q"] = f"{search_query} near {request.destination}"

        print(f"🗺️  Searching Google Maps: {params['q']}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

            # Parse venues from response
            venues = self._parse_venues(data.get("local_results", []))

            search_id = str(uuid.uuid4())

            return EntertainmentSearchResponse(
                search_id=search_id,
                trip_id=request.trip_id,
                query=search_query,
                destination=request.destination,
                venues=venues,
                total_results=len(venues),
            )

        except httpx.HTTPError as e:
            print(f"❌ Google Maps API error: {e}")
            raise RuntimeError(f"Failed to fetch Google Maps data: {e}")

    def _build_query_from_tags(self, tags: List[str], destination: str) -> str:
        """Build search query from entertainment tags."""
        # Map common tags to search queries
        tag_queries = {
            "culture": "museums, art galleries, cultural centers",
            "food": "restaurants, food markets, culinary experiences",
            "nightlife": "bars, clubs, night entertainment",
            "sightseeing": "landmarks, attractions, viewpoints",
            "museums": "museums, exhibitions, galleries",
            "shopping": "shopping centers, markets, boutiques",
            "outdoor": "parks, outdoor activities, nature",
            "sports": "sports venues, stadiums, activities",
            "theater": "theaters, shows, performances",
            "family": "family attractions, kids activities",
            "adventure": "adventure activities, experiences",
            "relaxation": "spas, wellness centers, relaxation",
        }

        # Get queries for user's tags
        queries = []
        for tag in tags[:3]:  # Limit to 3 tags to keep query focused
            tag_lower = tag.lower()
            if tag_lower in tag_queries:
                queries.append(tag_queries[tag_lower])
            else:
                queries.append(tag_lower)

        if queries:
            return f"{', '.join(queries)} in {destination}"
        else:
            return f"entertainment attractions in {destination}"

    def _parse_venues(self, local_results: List[dict]) -> List[GoogleMapsVenue]:
        """Parse venue data from SerpAPI response."""
        venues = []

        for idx, result in enumerate(local_results):
            # Parse GPS coordinates
            gps = None
            if "gps_coordinates" in result:
                gps_data = result["gps_coordinates"]
                gps = GPSCoordinates(
                    latitude=gps_data.get("latitude", 0.0),
                    longitude=gps_data.get("longitude", 0.0),
                )

            # Parse operating hours
            operating_hours = None
            if "operating_hours" in result:
                hours_data = result["operating_hours"]
                operating_hours = OperatingHours(
                    monday=hours_data.get("monday"),
                    tuesday=hours_data.get("tuesday"),
                    wednesday=hours_data.get("wednesday"),
                    thursday=hours_data.get("thursday"),
                    friday=hours_data.get("friday"),
                    saturday=hours_data.get("saturday"),
                    sunday=hours_data.get("sunday"),
                )

            venue = GoogleMapsVenue(
                position=result.get("position", idx + 1),
                place_id=result.get("place_id", ""),
                data_id=result.get("data_id"),
                data_cid=result.get("data_cid"),
                title=result.get("title", "Unknown Venue"),
                rating=result.get("rating"),
                reviews=result.get("reviews"),
                price=result.get("price"),
                type=result.get("type"),
                types=result.get("types"),
                type_id=result.get("type_id"),
                type_ids=result.get("type_ids"),
                address=result.get("address"),
                gps_coordinates=gps,
                phone=result.get("phone"),
                website=result.get("website"),
                description=result.get("description"),
                open_state=result.get("open_state"),
                hours=result.get("hours"),
                operating_hours=operating_hours,
                thumbnail=result.get("thumbnail"),
                service_options=result.get("service_options"),
            )
            venues.append(venue)

        return venues


# Singleton instance
google_maps_service = GoogleMapsService()
