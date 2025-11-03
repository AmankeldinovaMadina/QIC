"""OpenAI client for flight ranking and analysis."""

import json
import asyncio
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI

from app.core.settings import settings
from app.flights.schemas import RankRequest, RankResponse, RankItem, RankMeta, Itinerary


class OpenAIFlightRanker:
    """OpenAI client for ranking flights with pros/cons analysis."""
    
    def __init__(self):
        from app.core.settings import settings
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY missing. Ensure .env is loaded in the app process.")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, "OPENAI_MODEL", None) or "gpt-4o-mini"
        
    async def rank_flights(self, request: RankRequest) -> RankResponse:
        """Rank flights using OpenAI with structured output."""
        limited_flights = request.flights[:30]
        try:
            response = await self._call_openai(request, limited_flights)
            return self._parse_openai_response(response, request.search_id)
        except Exception as e:
            import traceback, sys
            print("OpenAI ranking failed:", repr(e), file=sys.stderr)
            traceback.print_exc()
            return self._heuristic_ranking(request)
    
    async def _call_openai(self, request: RankRequest, flights: List[Itinerary]) -> Dict[str, Any]:
        """Call OpenAI API with structured JSON schema using Responses API."""
        
        response_schema = {
            "type": "object",
            "required": ["ordered_ids", "items", "meta"],
            "additionalProperties": False,
            "properties": {
                "ordered_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        # --- FIX #1: Added "tags" to this 'required' list ---
                        "required": ["id","score","title","rationale_short","pros_keywords","cons_keywords","tags"],
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string"},
                            "score": {"type": "number", "minimum": 0, "maximum": 1},
                            "title": {"type": "string", "maxLength": 140},
                            "rationale_short": {"type": "string", "maxLength": 240},
                            "pros_keywords": {"type": "array","items":{"type":"string"},"maxItems":8},
                            "cons_keywords": {"type": "array","items":{"type":"string"},"maxItems":8},
                            "tags": {"type":["array","null"],"items":{"type":"string"},"maxItems":5}
                        }
                    }
                },
                "meta": {
                    "type": "object",
                    # --- FIX #2: Added "notes" to this 'required' list ---
                    "required": ["used_model", "deterministic", "notes"],
                    "additionalProperties": False,
                    "properties": {
                        "used_model": {"type": "string"},
                        "deterministic": {"type": "boolean"},
                        "notes": {"type":["array","null"],"items":{"type":"string"}}
                    }
                }
            }
        }

        system_prompt = self._build_system_prompt()
        user_prompt   = self._build_user_prompt(request, flights)

        try:
            # Use Chat Completions API with structured outputs (response_format)
            completion = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "FlightRankResult",
                        "schema": response_schema,
                        "strict": True
                    }
                }
            )
        except Exception as e:
            # Bubble a clear error so rank_flights() fallback logs it
            raise RuntimeError(f"OpenAI Chat Completions API call failed: {e}")

        # Check for refusal
        message = completion.choices[0].message
        if hasattr(message, 'refusal') and message.refusal:
            raise RuntimeError(f"OpenAI refused the request: {message.refusal}")
        
        # Extract content
        content = message.content
        
        if not content:
            raise RuntimeError("OpenAI returned empty content (no text to parse)")

        try:
            return json.loads(content)
        except Exception as parse_err:
            # Log first 500 chars for diagnosis
            snippet = content[:500].replace("\n", "\\n")
            raise ValueError(f"Model returned non-JSON or schema-invalid text: {snippet}") from parse_err
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for flight ranking."""
        return """You are a flight concierge expert. Rank flight itineraries based on user preferences.

Rules:
1. Obey hard constraints (budget, max stops, date/time windows)
2. Optimize for user's stated priorities (price, time, comfort, etc.)
3. Penalize risky connections (<70 min domestic, <90 min international unless same terminal)
4. Consider overnight flights (red-eyes) negatively unless user specifically wants them
5. Add concise, relevant pros/cons keywords
6. Never invent prices, durations, or flight details
7. Score from 0.0 to 1.0 where 1.0 is perfect match for user preferences

For each flight, provide:
- Accurate score based on how well it matches user preferences
- Concise title summarizing key details
- Short rationale explaining the ranking
- Relevant pros/cons keywords (not generic)
- Optional tags for special categories

Return ONLY valid JSON matching the exact schema."""
    
    def _build_user_prompt(self, request: RankRequest, flights: List[Itinerary]) -> str:
        """Build user prompt with preferences and flight data."""
        locale = request.locale or {}
        
        # Prepare compact flight data for the model
        flight_data = []
        for flight in flights:
            flight_summary = {
                "id": flight.id,
                "price": {
                    "amount": float(flight.price.amount),
                    "currency": flight.price.currency
                },
                "total_duration_min": flight.total_duration_min,
                "stops": flight.stops,
                "emissions_kg": flight.emissions_kg,
                "layovers_min": flight.layovers_min,
                "legs": [
                    {
                        "dep_iata": leg.dep_iata,
                        "dep_time": leg.dep_time.isoformat(),
                        "arr_iata": leg.arr_iata,
                        "arr_time": leg.arr_time.isoformat(),
                        "marketing": leg.marketing,
                        "flight_no": leg.flight_no,
                        "duration_min": leg.duration_min
                    }
                    for leg in flight.legs
                ]
            }
            flight_data.append(flight_summary)
        
        prompt_data = {
            "preferences_prompt": request.preferences_prompt,
            "locale": {
                "hl": locale.hl or "en",
                "currency": locale.currency or "USD",
                "tz": locale.tz
            },
            "flights": flight_data
        }
        
        return json.dumps(prompt_data, indent=2)
    
    def _parse_openai_response(self, response: Dict[str, Any], search_id: str) -> RankResponse:
        """Parse and validate OpenAI response."""
        ordered_ids = response.get("ordered_ids", [])
        items_data = response.get("items", [])
        meta_data = response.get("meta", {})
        
        # Parse items
        items = []
        for item_data in items_data:
            item = RankItem(
                id=item_data["id"],
                score=item_data["score"],
                title=item_data["title"],
                rationale_short=item_data["rationale_short"],
                pros_keywords=item_data["pros_keywords"],
                cons_keywords=item_data["cons_keywords"],
                tags=item_data.get("tags")
            )
            items.append(item)
        
        # Parse metadata
        meta = RankMeta(
            used_model=meta_data.get("used_model", self.model),
            deterministic=meta_data.get("deterministic", True),
            notes=meta_data.get("notes")
        )
        
        return RankResponse(
            search_id=search_id,
            ordered_ids=ordered_ids,
            items=items,
            meta=meta
        )
    
    def _heuristic_ranking(self, request: RankRequest) -> RankResponse:
        """Fallback heuristic ranking when OpenAI is unavailable."""
        flights = request.flights[:30]  # Limit for consistency
        
        # Sort by: price asc -> stops asc -> duration asc
        sorted_flights = sorted(
            flights,
            key=lambda f: (float(f.price.amount), f.stops, f.total_duration_min)
        )
        
        ordered_ids = [f.id for f in sorted_flights]
        items = []
        
        for i, flight in enumerate(sorted_flights):
            # Generate basic pros/cons
            pros = self._generate_heuristic_pros(flight, i == 0)
            cons = self._generate_heuristic_cons(flight)
            
            # Simple scoring (best to worst)
            score = max(0.1, 1.0 - (i * 0.1))
            
            # Generate title
            title = self._generate_heuristic_title(flight)
            
            item = RankItem(
                id=flight.id,
                score=score,
                title=title,
                rationale_short=f"Ranked #{i+1} by price, stops, and duration",
                pros_keywords=pros,
                cons_keywords=cons,
                tags=["heuristic"] if i == 0 else None
            )
            items.append(item)
        
        meta = RankMeta(
            used_model="heuristic_fallback",
            deterministic=True,
            notes=["OpenAI unavailable, used heuristic ranking"]
        )
        
        return RankResponse(
            search_id=request.search_id,
            ordered_ids=ordered_ids,
            items=items,
            meta=meta
        )
    
    def _generate_heuristic_pros(self, flight: Itinerary, is_best: bool) -> List[str]:
        """Generate heuristic pros keywords."""
        pros = []
        
        if is_best:
            pros.append("lowest price")
        
        if flight.stops == 0:
            pros.append("nonstop")
        elif flight.stops == 1:
            pros.append("1 stop")
            
        if flight.layovers_min:
            if all(layover >= 60 and layover <= 120 for layover in flight.layovers_min):
                pros.append("reasonable layovers")
        
        if flight.total_duration_min < 360:  # Less than 6 hours
            pros.append("short flight")
            
        if flight.emissions_kg and flight.emissions_kg < 500:
            pros.append("low emissions")
        
        # Check for good departure/arrival times
        for leg in flight.legs:
            if 6 <= leg.dep_time.hour <= 10:
                pros.append("morning departure")
                break
            elif 14 <= leg.dep_time.hour <= 18:
                pros.append("afternoon departure")
                break
        
        return pros[:5]  # Limit to 5
    
    def _generate_heuristic_cons(self, flight: Itinerary) -> List[str]:
        """Generate heuristic cons keywords."""
        cons = []
        
        if flight.stops >= 2:
            cons.append("multiple stops")
        
        if flight.layovers_min:
            if any(layover < 60 for layover in flight.layovers_min):
                cons.append("tight connection")
            elif any(layover > 300 for layover in flight.layovers_min):
                cons.append("long layover")
        
        if flight.total_duration_min > 720:  # More than 12 hours
            cons.append("long flight")
        
        # Check for red-eye flights
        for leg in flight.legs:
            if leg.dep_time.hour >= 22 or leg.dep_time.hour <= 5:
                cons.append("red-eye")
                break
        
        return cons[:5]  # Limit to 5
    
    def _generate_heuristic_title(self, flight: Itinerary) -> str:
        """Generate heuristic title."""
        stops_text = "Nonstop" if flight.stops == 0 else f"{flight.stops} stop{'s' if flight.stops > 1 else ''}"
        duration_hours = flight.total_duration_min // 60
        duration_mins = flight.total_duration_min % 60
        duration_text = f"{duration_hours}h{duration_mins:02d}m"
        
        airlines = list(set(leg.marketing for leg in flight.legs if leg.marketing))
        airline_text = airlines[0] if airlines else "Multi"
        
        price_text = f"${int(flight.price.amount)}"
        
        return f"{stops_text} • {duration_text} • {airline_text} • {price_text}"


# Global instance
openai_flight_ranker = OpenAIFlightRanker()