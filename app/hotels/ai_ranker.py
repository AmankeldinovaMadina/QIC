"""AI-powered hotel ranking using OpenAI."""

import json
from typing import Optional

import openai

from app.core.settings import settings
from app.hotels.schemas import (
    HotelRankItem,
    HotelRankMeta,
    HotelRankRequest,
    HotelRankResponse,
)


class OpenAIHotelRanker:
    """Ranks hotels using OpenAI with heuristic fallback."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = None
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def rank_hotels(self, request: HotelRankRequest) -> HotelRankResponse:
        """Rank hotels using AI or fallback to heuristic."""

        if self.client:
            try:
                return await self._rank_with_openai(request)
            except Exception as e:
                print(f"⚠️  OpenAI ranking failed: {e}, falling back to heuristic")
                return self._rank_heuristic(request)
        else:
            print("ℹ️  No OpenAI key, using heuristic ranking")
            return self._rank_heuristic(request)

    async def _rank_with_openai(self, request: HotelRankRequest) -> HotelRankResponse:
        """Rank hotels using OpenAI API."""

        # Build the prompt
        hotels_text = self._build_hotels_summary(request)
        system_prompt = self._build_system_prompt()
        user_prompt = f"""User preferences: {request.preferences_prompt}

Hotels to rank:
{hotels_text}

Return a JSON array of ranked hotels with this exact structure:
[
  {{
    "id": "hotel_id",
    "score": 0.95,
    "title": "Brief descriptive title (max 140 chars)",
    "rationale_short": "Why this hotel ranks here (max 240 chars)",
    "pros_keywords": ["keyword1", "keyword2", ...],
    "cons_keywords": ["keyword1", "keyword2", ...]
  }},
  ...
]

Rules:
- Score from 0.0 to 1.0 (higher is better)
- Order by score descending
- Max 8 keywords per pros/cons
- Consider: location, price, rating, amenities, user preferences
- Be concise and specific
"""

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        # Parse response
        content = response.choices[0].message.content
        parsed = json.loads(content)

        # Handle both array and object with rankings key
        if isinstance(parsed, list):
            rankings = parsed
        elif "rankings" in parsed:
            rankings = parsed["rankings"]
        elif "hotels" in parsed:
            rankings = parsed["hotels"]
        else:
            # Try to find any array in the response
            for value in parsed.values():
                if isinstance(value, list):
                    rankings = value
                    break
            else:
                raise ValueError("Could not find rankings array in OpenAI response")

        # Build response
        items = []
        ordered_ids = []

        for rank in rankings:
            item = HotelRankItem(
                id=rank["id"],
                score=rank["score"],
                title=rank["title"][:140],
                rationale_short=rank["rationale_short"][:240],
                pros_keywords=rank.get("pros_keywords", [])[:8],
                cons_keywords=rank.get("cons_keywords", [])[:8],
                tags=None,
            )
            items.append(item)
            ordered_ids.append(item.id)

        return HotelRankResponse(
            search_id=request.search_id,
            ordered_ids=ordered_ids,
            items=items,
            meta=HotelRankMeta(
                used_model=self.model,
                deterministic=True,
                notes=["Ranked using OpenAI based on user preferences"],
            ),
        )

    def _rank_heuristic(self, request: HotelRankRequest) -> HotelRankResponse:
        """Fallback heuristic ranking based on rating and price."""

        # Calculate scores based on rating and price
        hotels_with_scores = []

        for hotel in request.hotels:
            # Base score from rating (0-5 → 0-0.5)
            rating_score = (hotel.rating or 3.0) / 10.0

            # Price score (lower is better, normalized)
            prices = [h.total_price for h in request.hotels if h.total_price > 0]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                if max_price > min_price:
                    price_score = 0.3 * (
                        1 - (hotel.total_price - min_price) / (max_price - min_price)
                    )
                else:
                    price_score = 0.3
            else:
                price_score = 0.2

            # Review count bonus (up to 0.2)
            review_bonus = min(0.2, (hotel.reviews_count or 0) / 1000 * 0.2)

            total_score = rating_score + price_score + review_bonus
            total_score = min(1.0, max(0.0, total_score))

            # Generate pros/cons
            pros = []
            cons = []

            if hotel.rating and hotel.rating >= 4.5:
                pros.append("highly rated")
            if hotel.free_cancellation:
                pros.append("free cancellation")
            if hotel.amenities and len(hotel.amenities) > 5:
                pros.append("many amenities")
            if hotel.hotel_class and hotel.hotel_class >= 4:
                pros.append(f"{hotel.hotel_class}-star")

            if not hotel.free_cancellation:
                cons.append("no free cancellation")
            if hotel.total_price > (sum(prices) / len(prices) if prices else 0):
                cons.append("higher price")

            hotels_with_scores.append(
                {
                    "hotel": hotel,
                    "score": total_score,
                    "pros": pros or ["good option"],
                    "cons": cons or [],
                }
            )

        # Sort by score descending
        hotels_with_scores.sort(key=lambda x: x["score"], reverse=True)

        # Build response
        items = []
        ordered_ids = []

        for ranked in hotels_with_scores:
            hotel = ranked["hotel"]
            item = HotelRankItem(
                id=hotel.id,
                score=round(ranked["score"], 2),
                title=f"{hotel.name} - {hotel.location}",
                rationale_short=f"Rating {hotel.rating or 'N/A'}/5, ${hotel.total_price:.0f} total, {hotel.reviews_count or 0} reviews",
                pros_keywords=ranked["pros"],
                cons_keywords=ranked["cons"],
                tags=None,
            )
            items.append(item)
            ordered_ids.append(item.id)

        return HotelRankResponse(
            search_id=request.search_id,
            ordered_ids=ordered_ids,
            items=items,
            meta=HotelRankMeta(
                used_model="hotel-ranking-heuristic-v1",
                deterministic=True,
                notes=["Heuristic ranking based on rating, price, and reviews"],
            ),
        )

    def _build_hotels_summary(self, request: HotelRankRequest) -> str:
        """Build a text summary of hotels for the prompt."""

        lines = []
        for i, hotel in enumerate(request.hotels, 1):
            amenities_str = (
                ", ".join(hotel.amenities[:5]) if hotel.amenities else "None listed"
            )

            lines.append(
                f"{i}. {hotel.name} (ID: {hotel.id})\n"
                f"   Location: {hotel.location}\n"
                f"   Price: ${hotel.total_price:.2f} total (${hotel.price_per_night:.2f}/night) {hotel.currency}\n"
                f"   Rating: {hotel.rating or 'N/A'}/5 ({hotel.reviews_count or 0} reviews)\n"
                f"   Class: {hotel.hotel_class or 'N/A'} stars\n"
                f"   Type: {hotel.property_type or 'Hotel'}\n"
                f"   Amenities: {amenities_str}\n"
                f"   Free Cancellation: {'Yes' if hotel.free_cancellation else 'No'}\n"
            )

        return "\n".join(lines)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for OpenAI."""

        return """You are an expert hotel booking advisor. Analyze hotels and rank them based on user preferences.

Consider these factors:
1. **Location**: Proximity to attractions, safety, convenience
2. **Price**: Value for money, within budget
3. **Rating & Reviews**: Guest satisfaction, number of reviews
4. **Amenities**: Pool, gym, WiFi, breakfast, parking, etc.
5. **Property Quality**: Star rating, property type
6. **Policies**: Free cancellation, flexibility
7. **User Preferences**: Specific needs mentioned by the user

Provide honest, balanced assessments. Highlight genuine pros and cons.
Output must be valid JSON matching the specified structure."""
