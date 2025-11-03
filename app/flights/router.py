from fastapi import APIRouter, HTTPException

from app.flights.ai_ranker import OpenAIFlightRanker
from app.flights.schemas import RankRequest, RankResponse

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/rank", response_model=RankResponse)
async def rank_flights(req: RankRequest):
	"""Rank flight itineraries using AI (or heuristic fallback)."""
	try:
		ranker = OpenAIFlightRanker()
		result = await ranker.rank_flights(req)
		return result
	except Exception as e:
		print(f"ERROR in rank_flights: {e}")
		# If OpenAI unavailable, use heuristic fallback directly
		# This should not happen since OpenAIFlightRanker has internal fallback
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-rank", response_model=RankResponse)
async def rank_flights_alias(req: RankRequest):
    """Legacy alias: /ai-rank -> /rank"""
    return await rank_flights(req)
