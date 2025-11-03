"""Google Hotels service using SerpApi."""

from typing import Any, Dict, Optional
import httpx
from app.core.settings import settings

SERP_ENGINE = "google_hotels"


def _csv(val: Optional[list[int]]) -> Optional[str]:
    """Convert list of integers to CSV string."""
    if not val:
        return None
    return ",".join(str(x) for x in val)


def _bool(val: Optional[bool]) -> Optional[str]:
    """Convert boolean to string for SerpApi."""
    if val is None:
        return None
    return "true" if val else "false"


class GoogleHotelsService:
    """Service for fetching hotel data from SerpApi Google Hotels."""
    
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "https://serpapi.com/search.json"
        self.api_key = settings.serpapi_key
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY is not configured in settings")

    async def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for hotels using Google Hotels via SerpApi."""
        
        query: Dict[str, Any] = {
            "engine": SERP_ENGINE,
            "api_key": self.api_key,

            # Required
            "q": params["q"],
            "check_in_date": params["check_in_date"],
            "check_out_date": params["check_out_date"],

            # Optional localization
            "gl": params.get("gl"),
            "hl": params.get("hl"),
            "currency": params.get("currency"),

            # Occupancy
            "adults": params.get("adults"),
            "children": params.get("children"),
            "children_ages": _csv(params.get("children_ages")),

            # Filters
            "sort_by": params.get("sort_by"),
            "min_price": params.get("min_price"),
            "max_price": params.get("max_price"),
            "property_types": _csv(params.get("property_types")),
            "amenities": _csv(params.get("amenities")),
            "rating": params.get("rating"),
            "brands": _csv(params.get("brands")),
            "hotel_class": _csv(params.get("hotel_class")),
            "free_cancellation": _bool(params.get("free_cancellation")),
            "special_offers": _bool(params.get("special_offers")),
            "eco_certified": _bool(params.get("eco_certified")),

            # Vacation rentals
            "vacation_rentals": _bool(params.get("vacation_rentals")),
            "bedrooms": params.get("bedrooms"),
            "bathrooms": params.get("bathrooms"),

            # Pagination
            "next_page_token": params.get("next_page_token"),

            # SerpApi parameters
            "no_cache": _bool(params.get("no_cache")),
            "output": params.get("output") or "json",
            "json_restrictor": params.get("json_restrictor"),
        }

        # Drop None values
        query = {k: v for k, v in query.items() if v is not None}

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(self.base_url, params=query)
            r.raise_for_status()
            data = r.json()

        # Check for errors from SerpApi
        status = data.get("search_metadata", {}).get("status")
        if status == "Error":
            msg = data.get("error") or "SerpApi returned an error"
            raise RuntimeError(msg)

        return data

    async def property_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information for a specific property."""
        
        query: Dict[str, Any] = {
            "engine": SERP_ENGINE,
            "api_key": self.api_key,
            "property_token": params["property_token"],

            # Context parameters
            "q": params.get("q"),
            "check_in_date": params["check_in_date"],
            "check_out_date": params["check_out_date"],
            "gl": params.get("gl"),
            "hl": params.get("hl"),
            "currency": params.get("currency"),
            "adults": params.get("adults", 2),
            "children": params.get("children", 0),
            "children_ages": _csv(params.get("children_ages")),
        }
        
        # Drop None values
        query = {k: v for k, v in query.items() if v is not None}

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(self.base_url, params=query)
            r.raise_for_status()
            data = r.json()

        # Check for errors
        status = data.get("search_metadata", {}).get("status")
        if status == "Error":
            msg = data.get("error") or "SerpApi returned an error"
            raise RuntimeError(msg)

        return data
