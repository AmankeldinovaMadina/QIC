"""Culture guide endpoint for travel etiquette tips."""

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.database import get_async_session
from app.db.models import CultureGuide as CultureGuideModel
from app.db.models import Trip

router = APIRouter(prefix="/culture", tags=["culture"])

# Initialize OpenAI client with API key from settings
client = OpenAI(api_key=settings.openai_api_key)

# --- Structured Output (Pydantic) ---

TipCategory = Literal[
    "greeting_etiquette",
    "dress_code",
    "behavioral_norms",
    "taboos",
    "dining_etiquette",
    "tipping",
    "religion_holidays",
    "transport_customs",
]


class CultureTip(BaseModel):
    """Individual culture tip with actionable advice."""

    category: TipCategory
    title: str
    tip: str
    do: str
    avoid: str
    emoji: str  # small UX flourish for frontend


class CultureGuide(BaseModel):
    """Complete culture guide for a destination."""

    destination: str
    summary: str
    tips: List[CultureTip] = Field(..., min_items=3, max_items=4)

    @field_validator("destination")
    @classmethod
    def normalize_dest(cls, v: str) -> str:
        """Normalize destination by stripping whitespace."""
        return v.strip()


# --- Request/Response Models ---


class CultureGuideRequest(BaseModel):
    """Request model for culture guide endpoint."""

    trip_id: str
    destination: str
    language: Optional[Literal["en"]] = "en"  # keep it simple as requested


class CultureGuideResponse(CultureGuide):
    """Response model for culture guide endpoint."""

    pass


# --- System Prompt ---

SYSTEM_PROMPT = (
    "You are a concise travel etiquette expert. "
    "Return STRICT JSON that matches the provided schema. "
    "Focus on culture-specific, practical advice for short-term visitors. "
    "Use neutral tone; avoid stereotyping; be respectful and factual. "
    "If the destination is a city, bias to local norms; otherwise use country-level norms. "
    "Keep each tip clear and actionable. Avoid repeating the same idea across tips."
)

# --- Endpoint ---


@router.post("/guide", response_model=CultureGuideResponse)
async def culture_guide(
    req: CultureGuideRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Generate culture-specific travel etiquette tips for a destination.

    Uses OpenAI Structured Outputs to guarantee JSON schema compliance.
    Returns 3-4 actionable tips covering greetings, dress code, dining, etc.

    Args:
        req: CultureGuideRequest with trip_id, destination and optional language
        session: Database session

    Returns:
        CultureGuideResponse with summary and structured tips

    Raises:
        HTTPException: 404 if trip not found, 502 if OpenAI API call fails
    """
    # Verify trip exists
    result = await session.execute(select(Trip).where(Trip.id == req.trip_id))
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Check if culture guide already exists for this trip
    result = await session.execute(
        select(CultureGuideModel).where(CultureGuideModel.trip_id == req.trip_id)
    )
    existing_guide = result.scalar_one_or_none()

    if existing_guide:
        # Return existing guide
        return CultureGuideResponse(
            destination=existing_guide.destination,
            summary=existing_guide.summary,
            tips=[CultureTip(**tip) for tip in existing_guide.tips_json],
        )

    try:
        # Use Structured Outputs (schema-enforced)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Destination: {req.destination}\n"
                        f"Language: {req.language}\n"
                        "Generate 3–4 tips only. "
                        "Make 'summary' 1–2 sentences. "
                        "Keep 'title' short (3–6 words)."
                    ),
                },
            ],
            response_format=CultureGuide,
        )

        parsed: CultureGuide = completion.choices[0].message.parsed  # schema-validated

        # Save to database
        culture_guide_db = CultureGuideModel(
            trip_id=req.trip_id,
            destination=parsed.destination,
            summary=parsed.summary,
            tips_json=[tip.model_dump() for tip in parsed.tips],
        )
        session.add(culture_guide_db)
        await session.commit()
        await session.refresh(culture_guide_db)

        return CultureGuideResponse(**parsed.model_dump())

    except Exception as e:
        # Bubble up a friendly error for the frontend
        raise HTTPException(status_code=502, detail=f"culture_guide_failed: {str(e)}")


@router.get("/guide/{trip_id}", response_model=CultureGuideResponse)
async def get_culture_guide(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieve a saved culture guide for a specific trip.

    Args:
        trip_id: The ID of the trip
        session: Database session

    Returns:
        CultureGuideResponse with summary and structured tips

    Raises:
        HTTPException: 404 if culture guide not found for this trip
    """
    # Check if culture guide exists for this trip
    result = await session.execute(
        select(CultureGuideModel).where(CultureGuideModel.trip_id == trip_id)
    )
    culture_guide = result.scalar_one_or_none()

    if not culture_guide:
        raise HTTPException(
            status_code=404,
            detail="Culture guide not found for this trip. Please generate one first.",
        )

    # Return the saved guide
    return CultureGuideResponse(
        destination=culture_guide.destination,
        summary=culture_guide.summary,
        tips=[CultureTip(**tip) for tip in culture_guide.tips_json],
    )
