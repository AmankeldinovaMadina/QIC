"""Culture guide endpoint for travel etiquette tips."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
from openai import OpenAI
from app.core.settings import settings

router = APIRouter(prefix="/api/v1", tags=["culture"])

# Initialize OpenAI client with API key from settings
client = OpenAI(api_key=settings.openai_api_key)

# --- Structured Output (Pydantic) ---

TipCategory = Literal[
    "greeting_etiquette", "dress_code", "behavioral_norms", "taboos",
    "dining_etiquette", "tipping", "religion_holidays", "transport_customs",
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

@router.post("/culture-guide", response_model=CultureGuideResponse)
def culture_guide(req: CultureGuideRequest):
    """
    Generate culture-specific travel etiquette tips for a destination.
    
    Uses OpenAI Structured Outputs to guarantee JSON schema compliance.
    Returns 3-4 actionable tips covering greetings, dress code, dining, etc.
    
    Args:
        req: CultureGuideRequest with destination and optional language
        
    Returns:
        CultureGuideResponse with summary and structured tips
        
    Raises:
        HTTPException: 502 if OpenAI API call fails
    """
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
        return CultureGuideResponse(**parsed.model_dump())

    except Exception as e:
        # Bubble up a friendly error for the frontend
        raise HTTPException(status_code=502, detail=f"culture_guide_failed: {str(e)}")
