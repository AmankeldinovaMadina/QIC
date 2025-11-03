"""SerpApi Google Flights provider."""

import hashlib
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app.core.settings import settings
from app.flights.schemas import (
    Itinerary, FlightLeg, Price, SearchResult, SearchInsights, 
    FlightSearchParams
)


class SerpApiError(Exception):
    """SerpApi specific error."""
    pass


class GoogleFlightsProvider:
    """Google Flights provider using SerpApi."""
    
    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
        
    async def search_flights(self, params: FlightSearchParams) -> SearchResult:
        """Search flights using SerpApi Google Flights engine."""
        if not self.api_key:
            raise SerpApiError("SerpApi key not configured")
            
        # Build SerpApi parameters
        serp_params = self._build_serp_params(params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=serp_params)
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise SerpApiError(f"SerpApi error: {data['error']}")
                
            # Transform to our domain model
            return self._transform_response(data, params)
    
    def _build_serp_params(self, params: FlightSearchParams) -> Dict[str, Any]:
        """Build SerpApi parameters from search params."""
        serp_params = {
            "engine": "google_flights",
            "api_key": self.api_key,
            "type": params.type,
            "departure_id": params.departure_id,
            "arrival_id": params.arrival_id,
            "outbound_date": params.outbound_date,
            "currency": params.currency,
            "hl": params.hl,
            "gl": params.gl,
            "adults": params.adults,
            "children": params.children,
            "infants_in_seat": params.infants_in_seat,
            "infants_on_lap": params.infants_on_lap,
        }
        
        # Optional parameters
        if params.return_date:
            serp_params["return_date"] = params.return_date
        if params.sort_by:
            serp_params["sort_by"] = params.sort_by
        if params.travel_class:
            serp_params["travel_class"] = params.travel_class
        if params.max_stops is not None:
            serp_params["max_stops"] = params.max_stops
        if params.include_airlines:
            serp_params["include_airlines"] = params.include_airlines
        if params.exclude_airlines:
            serp_params["exclude_airlines"] = params.exclude_airlines
        if params.exclude_basic:
            serp_params["exclude_basic"] = params.exclude_basic
        if params.deep_search:
            serp_params["deep_search"] = params.deep_search
            
        return serp_params
    
    def _transform_response(self, data: Dict[str, Any], params: FlightSearchParams) -> SearchResult:
        """Transform SerpApi response to our domain model."""
        search_id = self._generate_search_id(params)
        
        # Extract best flights
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        all_flights = best_flights + other_flights
        
        itineraries = []
        for flight_data in all_flights:
            try:
                itinerary = self._transform_flight(flight_data, params)
                if itinerary:
                    itineraries.append(itinerary)
            except Exception as e:
                # Log error but continue with other flights
                print(f"Error transforming flight: {e}")
                continue
        
        # Extract insights
        insights = None
        if "search_metadata" in data:
            insights = self._extract_insights(data, params.currency)
        
        return SearchResult(
            search_id=search_id,
            currency=params.currency,
            insights=insights,
            itineraries=itineraries
        )
    
    def _transform_flight(self, flight_data: Dict[str, Any], params: FlightSearchParams) -> Optional[Itinerary]:
        """Transform individual flight data."""
        flights = flight_data.get("flights", [])
        if not flights:
            return None
            
        # Build legs
        legs = []
        total_duration = 0
        layovers = []
        
        for i, leg_data in enumerate(flights):
            leg = self._transform_leg(leg_data)
            if leg:
                legs.append(leg)
                total_duration += leg.duration_min
                
                # Calculate layover if not the last leg
                if i < len(flights) - 1:
                    next_leg = flights[i + 1]
                    layover_min = self._calculate_layover(leg_data, next_leg)
                    if layover_min:
                        layovers.append(layover_min)
        
        if not legs:
            return None
            
        # Calculate stops
        stops = len(legs) - 1
        
        # Extract price
        price_info = flight_data.get("price", 0)
        if isinstance(price_info, dict):
            price_amount = price_info.get("value", 0)
        else:
            price_amount = price_info
            
        price = Price(amount=Decimal(str(price_amount)), currency=params.currency)
        
        # Generate stable ID
        flight_id = self._generate_flight_id(legs, price)
        
        # Extract emissions
        emissions_kg = None
        if "carbon_emissions" in flight_data:
            emissions_kg = flight_data["carbon_emissions"].get("this_flight")
        
        # Extract tokens for booking
        tokens = {}
        if "departure_token" in flight_data:
            tokens["departure_token"] = flight_data["departure_token"]
        if "booking_token" in flight_data:
            tokens["booking_token"] = flight_data["booking_token"]
            
        trip_type = "ROUND_TRIP" if params.type == 1 else "ONE_WAY"
        
        return Itinerary(
            id=flight_id,
            type=trip_type,
            price=price,
            total_duration_min=total_duration,
            stops=stops,
            emissions_kg=emissions_kg,
            layovers_min=layovers if layovers else None,
            legs=legs,
            tokens=tokens if tokens else None
        )
    
    def _transform_leg(self, leg_data: Dict[str, Any]) -> Optional[FlightLeg]:
        """Transform individual leg data."""
        try:
            departure = leg_data.get("departure_airport", {})
            arrival = leg_data.get("arrival_airport", {})
            
            # Parse times
            dep_time_str = leg_data.get("departure_time")
            arr_time_str = leg_data.get("arrival_time")
            
            if not dep_time_str or not arr_time_str:
                return None
                
            dep_time = datetime.fromisoformat(dep_time_str.replace('Z', '+00:00'))
            arr_time = datetime.fromisoformat(arr_time_str.replace('Z', '+00:00'))
            
            # Calculate duration in minutes
            duration_str = leg_data.get("duration")
            duration_min = self._parse_duration(duration_str)
            
            # Extract airline info
            airline = leg_data.get("airline", "")
            flight_number = leg_data.get("flight_number", "")
            flight_no = f"{airline} {flight_number}" if airline and flight_number else flight_number
            
            return FlightLeg(
                dep_iata=departure.get("id", ""),
                dep_time=dep_time,
                arr_iata=arrival.get("id", ""),
                arr_time=arr_time,
                marketing=airline,
                flight_no=flight_no,
                duration_min=duration_min
            )
        except Exception as e:
            print(f"Error parsing leg: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to minutes."""
        if not duration_str:
            return 0
            
        # Handle formats like "3h 15m", "1h 30m", "45m"
        duration_str = duration_str.lower().strip()
        total_minutes = 0
        
        if 'h' in duration_str:
            parts = duration_str.split('h')
            hours = int(parts[0].strip())
            total_minutes += hours * 60
            
            if len(parts) > 1 and parts[1].strip():
                minutes_part = parts[1].replace('m', '').strip()
                if minutes_part:
                    total_minutes += int(minutes_part)
        elif 'm' in duration_str:
            minutes = int(duration_str.replace('m', '').strip())
            total_minutes = minutes
            
        return total_minutes
    
    def _calculate_layover(self, current_leg: Dict[str, Any], next_leg: Dict[str, Any]) -> Optional[int]:
        """Calculate layover duration between legs."""
        try:
            arr_time_str = current_leg.get("arrival_time")
            dep_time_str = next_leg.get("departure_time")
            
            if not arr_time_str or not dep_time_str:
                return None
                
            arr_time = datetime.fromisoformat(arr_time_str.replace('Z', '+00:00'))
            dep_time = datetime.fromisoformat(dep_time_str.replace('Z', '+00:00'))
            
            layover_delta = dep_time - arr_time
            return int(layover_delta.total_seconds() / 60)
        except Exception:
            return None
    
    def _extract_insights(self, data: Dict[str, Any], currency: str) -> Optional[SearchInsights]:
        """Extract price insights from search results."""
        try:
            price_insights = data.get("price_insights", {})
            if not price_insights:
                return None
                
            lowest_price = price_insights.get("lowest_price")
            if lowest_price is None:
                return None
                
            insights = SearchInsights(
                lowest=Decimal(str(lowest_price)),
                level=price_insights.get("price_level")
            )
            
            # Extract typical range if available
            if "typical_price_range" in price_insights:
                range_data = price_insights["typical_price_range"]
                if isinstance(range_data, list) and len(range_data) == 2:
                    insights.typical_range = [Decimal(str(range_data[0])), Decimal(str(range_data[1]))]
            
            return insights
        except Exception:
            return None
    
    def _generate_search_id(self, params: FlightSearchParams) -> str:
        """Generate stable search ID from parameters."""
        param_str = f"{params.departure_id}_{params.arrival_id}_{params.outbound_date}_{params.return_date or ''}_{params.adults}_{params.children}"
        return hashlib.md5(param_str.encode()).hexdigest()[:12]
    
    def _generate_flight_id(self, legs: List[FlightLeg], price: Price) -> str:
        """Generate stable flight ID."""
        leg_str = "_".join([f"{leg.dep_iata}{leg.arr_iata}{leg.flight_no}{leg.dep_time.isoformat()}" for leg in legs])
        flight_str = f"{leg_str}_{price.amount}_{price.currency}"
        return hashlib.md5(flight_str.encode()).hexdigest()[:16]


# Global provider instance
google_flights_provider = GoogleFlightsProvider()