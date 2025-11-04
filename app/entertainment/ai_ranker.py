"""OpenAI client for entertainment venue ranking and analysis."""

import json
from typing import Any, Dict, List

from openai import AsyncOpenAI

from app.core.settings import settings
from app.entertainment.schemas import (
    EntertainmentRankItem,
    EntertainmentRankMeta,
    EntertainmentRankRequest,
    EntertainmentRankResponse,
    GoogleMapsVenue,
)


class OpenAIEntertainmentRanker:
    """OpenAI client for ranking entertainment venues with pros/cons analysis."""

    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY missing. Ensure .env is loaded in the app process."
            )
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = getattr(settings, "OPENAI_MODEL", None) or "gpt-4o-mini"
        print(f"DEBUG: Entertainment OpenAI client initialized successfully")

    async def rank_venues(
        self, request: EntertainmentRankRequest
    ) -> EntertainmentRankResponse:
        """Rank entertainment venues using OpenAI with structured output."""
        # Limit to 15 venues for cost control
        limited_venues = request.venues[:15]

        try:
            print(f"DEBUG: Attempting to call OpenAI for {len(limited_venues)} venues")
            # Call OpenAI with JSON schema
            response = await self._call_openai(request, limited_venues)

            print(f"DEBUG: OpenAI call successful")
            # Validate and return
            return self._parse_openai_response(response, request)

        except Exception as e:
            print(f"OpenAI venue ranking failed: {e}")
            # Fallback to heuristic ranking
            return self._heuristic_ranking(request, limited_venues)

    async def _call_openai(
        self, request: EntertainmentRankRequest, venues: List[GoogleMapsVenue]
    ) -> Dict[str, Any]:
        """Call OpenAI API with structured JSON schema."""

        # Define the JSON schema for response
        response_schema = {
            "type": "object",
            "required": ["ordered_place_ids", "items", "meta"],
            "properties": {
                "ordered_place_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "place_id",
                            "score",
                            "title",
                            "rationale_short",
                            "pros_keywords",
                            "cons_keywords",
                        ],
                        "properties": {
                            "place_id": {"type": "string"},
                            "score": {"type": "number", "minimum": 0, "maximum": 1},
                            "title": {"type": "string", "maxLength": 140},
                            "rationale_short": {"type": "string", "maxLength": 240},
                            "pros_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "maxItems": 8,
                            },
                            "cons_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "maxItems": 8,
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "maxItems": 8,
                            },
                        },
                    },
                },
                "meta": {
                    "type": "object",
                    "required": ["used_model", "deterministic"],
                    "properties": {
                        "used_model": {"type": "string"},
                        "deterministic": {"type": "boolean"},
                        "notes": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        }

        # Build user preferences text
        preferences_text = request.preferences_prompt or ""
        if request.entertainment_tags:
            tags_text = ", ".join(request.entertainment_tags)
            preferences_text = (
                f"{preferences_text}\n\nUser interests: {tags_text}".strip()
            )

        # Prepare venue data
        venues_data = []
        for v in venues:
            venue_dict = {
                "place_id": v.place_id,
                "title": v.title,
                "rating": v.rating,
                "reviews": v.reviews,
                "price": v.price,
                "type": v.type,
                "types": v.types,
                "address": v.address,
                "description": v.description,
            }
            venues_data.append(venue_dict)

        # System prompt
        system_prompt = f"""You are an expert travel advisor specializing in entertainment and activities.

Your task is to analyze and rank entertainment venues based on user preferences and venue characteristics.

User Preferences:
{preferences_text or 'General traveler preferences'}

For each venue:
1. Assign a score (0.0 to 1.0) based on how well it matches user interests
2. Create a concise title (max 140 chars) explaining why it's recommended
3. Write a short rationale (max 240 chars) with specific reasons
4. Extract 3-8 pros_keywords (positive aspects like "family-friendly", "authentic", "scenic", "interactive")
5. Extract 3-8 cons_keywords (considerations like "crowded", "expensive", "reservation-required", "time-consuming")
6. Add relevant tags (e.g., "culture", "food", "nightlife", "outdoor", "shopping")

Rank venues from best to worst match. Consider:
- User's expressed interests (entertainment_tags)
- Ratings and review counts (higher is better)
- Price level (consider value for money)
- Venue type and description
- Uniqueness and experience quality

Be honest about cons - help users make informed decisions."""

        user_prompt = f"""Rank these {len(venues_data)} entertainment venues:

{json.dumps(venues_data, indent=2)}

Return exactly {len(venues_data)} ranked venues in JSON format following the schema."""

        # Call OpenAI
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "venue_ranking", "schema": response_schema},
            },
            temperature=0.3,
        )

        response_text = completion.choices[0].message.content
        return json.loads(response_text)

    def _parse_openai_response(
        self, response: Dict[str, Any], request: EntertainmentRankRequest
    ) -> EntertainmentRankResponse:
        """Parse and validate OpenAI response."""
        # Create a lookup dictionary for venues by place_id
        venues_by_id = {venue.place_id: venue for venue in request.venues}

        # Parse items and add link from original venue data
        items = []
        for item_data in response["items"]:
            venue = venues_by_id.get(item_data["place_id"])
            item = EntertainmentRankItem(
                **item_data, link=venue.link if venue else None
            )
            items.append(item)

        meta = EntertainmentRankMeta(**response["meta"])

        return EntertainmentRankResponse(
            trip_id=request.trip_id,
            search_id=request.search_id,
            ordered_place_ids=response["ordered_place_ids"],
            items=items,
            meta=meta,
        )

    def _heuristic_ranking(
        self, request: EntertainmentRankRequest, venues: List[GoogleMapsVenue]
    ) -> EntertainmentRankResponse:
        """Fallback heuristic ranking based on ratings and reviews."""
        print("Using heuristic venue ranking (OpenAI unavailable)")

        # Sort by rating * log(reviews + 1)
        scored_venues = []
        for v in venues:
            rating = v.rating or 3.0
            reviews = v.reviews or 0
            score = rating * (1 + (reviews / 1000) ** 0.5) / 6.0  # Normalize to 0-1
            score = min(max(score, 0.0), 1.0)

            # Generate simple pros/cons
            pros = []
            cons = []

            if rating and rating >= 4.5:
                pros.append("highly-rated")
            if reviews and reviews > 500:
                pros.append("popular")
            if v.price in ["$", "$$"]:
                pros.append("affordable")
            if v.description:
                pros.append("detailed-info")

            if rating and rating < 4.0:
                cons.append("lower-rating")
            if reviews and reviews < 50:
                cons.append("limited-reviews")
            if v.price in ["$$$", "$$$$"]:
                cons.append("expensive")

            # Fallback values
            if not pros:
                pros = ["available"]
            if not cons:
                cons = ["none-noted"]

            scored_venues.append(
                {
                    "venue": v,
                    "score": score,
                    "pros": pros,
                    "cons": cons,
                }
            )

        # Sort by score descending
        scored_venues.sort(key=lambda x: x["score"], reverse=True)

        # Build response
        items = []
        ordered_place_ids = []

        for sv in scored_venues:
            v = sv["venue"]
            ordered_place_ids.append(v.place_id)

            item = EntertainmentRankItem(
                place_id=v.place_id,
                score=sv["score"],
                title=f"{v.title} - {v.type or 'Venue'}",
                rationale_short=f"Rating {v.rating or 'N/A'}, {v.reviews or 0} reviews",
                pros_keywords=sv["pros"],
                cons_keywords=sv["cons"],
                tags=v.types[:3] if v.types else [],
                link=v.link,
            )
            items.append(item)

        return EntertainmentRankResponse(
            trip_id=request.trip_id,
            search_id=request.search_id,
            ordered_place_ids=ordered_place_ids,
            items=items,
            meta=EntertainmentRankMeta(
                used_model="heuristic",
                deterministic=True,
                notes=["Fallback heuristic ranking used"],
            ),
        )
