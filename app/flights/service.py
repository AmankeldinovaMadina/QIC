"""Flight search service using SerpAPI."""

import uuid
from datetime import datetime
from typing import List, Optional

import httpx

from app.core.settings import settings
from app.flights.schemas import FlightLeg, Itinerary, Price


class FlightSearchService:
    """Service for searching flights via SerpAPI Google Flights."""

    def __init__(self):
        self.api_key = settings.serpapi_key
        self.base_url = "https://serpapi.com/search"

    async def search_flights(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        currency: str = "USD",
        hl: str = "en",
    ) -> tuple[List[Itinerary], Optional[str]]:
        """
        Search for flights using SerpAPI.

        Args:
            departure_id: IATA code for departure airport (e.g., "JFK")
            arrival_id: IATA code for arrival airport (e.g., "NRT")
            outbound_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional for one-way)
            adults: Number of adult passengers
            children: Number of child passengers
            currency: Currency code (e.g., "USD")
            hl: Language code (e.g., "en")

        Returns:
            List of Itinerary objects
        """
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": currency,
            "hl": hl,
            "api_key": self.api_key,
        }

        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way

        if adults > 1:
            params["adults"] = adults

        if children > 0:
            params["children"] = children

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Debug: Check what we got from SerpAPI
                print(f"📊 SerpAPI Response keys: {list(data.keys())}")
                if "search_information" in data:
                    print(f"📋 Search info: {data['search_information']}")
                if "error" in data:
                    print(f"⚠️  SerpAPI error: {data['error']}")

                # Parse flights from response
                flights = []

                # Get best flights
                if "best_flights" in data:
                    print(f"✈️  Found {len(data['best_flights'])} best_flights")
                    for idx, flight_data in enumerate(data["best_flights"][:2]):  # Debug first 2
                        print(f"📋 Sample flight {idx}: {flight_data.get('flights', [])} legs")
                    for flight_data in data["best_flights"]:
                        itinerary = self._parse_flight(flight_data)
                        if itinerary:
                            flights.append(itinerary)

                # Get other flights
                if "other_flights" in data:
                    print(f"✈️  Found {len(data['other_flights'])} other_flights")
                    for flight_data in data["other_flights"]:
                        itinerary = self._parse_flight(flight_data)
                        if itinerary:
                            flights.append(itinerary)

                print(f"✅ Successfully parsed {len(flights)} itineraries")
                
                # Get the Google Flights URL from search metadata
                google_flights_url = data.get("search_metadata", {}).get("google_flights_url")
                
                # Limit to 20 flights
                return flights[:20], google_flights_url

        except httpx.HTTPError as e:
            print(f"❌ SerpAPI HTTP Error: {e}")
            raise Exception(f"Failed to search flights: {str(e)}")
        except Exception as e:
            print(f"❌ Flight search error: {e}")
            raise Exception(f"Flight search failed: {str(e)}")

    def _parse_flight(self, flight_data: dict) -> Optional[Itinerary]:
        """Parse a single flight from SerpAPI response."""
        try:
            # Generate unique ID for this flight
            flight_id = str(uuid.uuid4())

            # Parse price
            price = Price(
                amount=float(flight_data.get("price", 0)),
                currency=flight_data.get("currency", "USD"),
            )

            # Parse flights (legs)
            legs = []
            flights_list = flight_data.get("flights", [])

            for leg_data in flights_list:
                dep_airport = leg_data.get("departure_airport", {})
                arr_airport = leg_data.get("arrival_airport", {})

                # Parse datetime
                dep_time_str = dep_airport.get("time")
                arr_time_str = arr_airport.get("time")

                # Convert to ISO format datetime
                dep_time = self._parse_datetime(dep_time_str)
                arr_time = self._parse_datetime(arr_time_str)

                if not dep_time or not arr_time:
                    continue

                leg = FlightLeg(
                    dep_iata=dep_airport.get("id", ""),
                    dep_time=dep_time,
                    arr_iata=arr_airport.get("id", ""),
                    arr_time=arr_time,
                    marketing=leg_data.get("airline", ""),
                    flight_no=leg_data.get("flight_number", ""),
                    duration_min=leg_data.get("duration", 0),
                )
                legs.append(leg)

            if not legs:
                return None

            print(f"🔍 Parsed {len(legs)} legs for flight")
            if len(legs) > 0:
                print(f"   First leg: {legs[0].dep_iata} → {legs[0].arr_iata} ({legs[0].dep_time})")
            if len(legs) > 1:
                print(f"   Last leg: {legs[-1].dep_iata} → {legs[-1].arr_iata} ({legs[-1].dep_time})")

            # Calculate total duration and layovers
            total_duration = flight_data.get("total_duration", 0)
            stops = len(legs) - 1

            # Calculate layover time
            layovers_min = 0
            if stops > 0:
                for i in range(len(legs) - 1):
                    # Time between arrival and next departure
                    layover = (
                        legs[i + 1].dep_time - legs[i].arr_time
                    ).total_seconds() / 60
                    layovers_min += int(layover)

            # Create itinerary
            itinerary = Itinerary(
                id=flight_id,
                price=price,
                total_duration_min=total_duration,
                stops=stops,
                emissions_kg=flight_data.get("carbon_emissions", {}).get("this_flight"),
                layovers_min=layovers_min if stops > 0 else None,
                legs=legs,
            )

            return itinerary

        except Exception as e:
            print(f"⚠️  Failed to parse flight: {e}")
            return None

    def _parse_datetime(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from SerpAPI."""
        if not time_str:
            return None

        try:
            # SerpAPI returns datetime like "2025-06-01 10:00"
            # Try to parse it
            return datetime.fromisoformat(time_str.replace(" ", "T"))
        except Exception:
            try:
                # Try parsing with format
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            except Exception as e:
                print(f"⚠️  Failed to parse datetime '{time_str}': {e}")
                return None


# Singleton instance
flight_search_service = FlightSearchService()
