"""AI trip planner using OpenAI Structured Outputs."""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

from app.core.settings import settings
from app.db.models import Trip

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)

# ------------------------- Structured Output Schemas -------------------------

Transport = Literal[
    "walk",
    "bus",
    "metro",
    "tram",
    "train",
    "car",
    "taxi",
    "ferry",
    "bike",
    "rideshare",
    "plane",
    "other",
]
Priority = Literal["essential", "nice_to_have", "optional"]


class TripEvent(BaseModel):
    """Individual event in a trip day."""

    title: str = Field(..., description="Short human title of the event")
    start: str = Field(
        ...,
        description="ISO 8601 datetime with timezone, e.g. 2025-12-14T09:00:00+09:00",
    )
    end: str = Field(
        ...,
        description="ISO 8601 datetime with timezone, e.g. 2025-12-14T10:00:00+09:00",
    )
    location_name: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    transport_reco: Optional[Transport] = None
    transport_notes: Optional[str] = None
    priority: Priority = "essential"

    @field_validator("end")
    @classmethod
    def _end_after_start(cls, v, info):
        """Ensure end time is after start time."""
        try:
            start_val = info.data.get("start")
            if start_val:
                if datetime.fromisoformat(v) <= datetime.fromisoformat(start_val):
                    raise ValueError("end must be after start")
        except Exception:
            # Let overall validator handle - Structured Outputs should prevent this
            pass
        return v


class TripDay(BaseModel):
    """Day in a trip plan."""

    date: str = Field(..., description="Date YYYY-MM-DD in trip timezone")
    summary: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    events: List[TripEvent] = Field(default_factory=list)


class TripPlan(BaseModel):
    """Complete trip plan with daily itinerary."""

    title: str
    timezone: str
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    origin: Optional[str] = None
    destinations: List[str] = Field(default_factory=list)
    adults: int = 1
    children: int = 0
    budget_tier: Literal["budget", "mid", "luxury"] = "mid"
    preferences: List[str] = Field(default_factory=list)
    diet: List[Literal["halal", "vegetarian", "gluten_free", "no_restrictions"]] = (
        Field(default_factory=lambda: ["no_restrictions"])
    )
    avoid_patterns: bool = True
    pacing: Literal["chill", "balanced", "intense"] = "balanced"
    wake_window: List[int] = Field(
        default_factory=lambda: [8, 22]
    )  # [startHour, endHour]
    hard_events: List[TripEvent] = Field(default_factory=list)
    days: List[TripDay] = Field(default_factory=list)


# ------------------------- System Prompt -------------------------

SYSTEM_PROMPT = (
    "You are a meticulous human-quality travel planner.\n"
    "Generate a bespoke daily plan (no rigid templates), respecting user preferences, "
    "wake windows, city logistics, jet lag, check-in windows, mealtimes, and rest. "
    "All days MUST be within [start_date, end_date].\n"
    "Enums:\n"
    "- transport_reco: walk, bus, metro, tram, train, car, taxi, ferry, bike, rideshare, plane, other\n"
    "- priority: essential, nice_to_have, optional\n"
    "- diet: halal, vegetarian, gluten_free, no_restrictions\n"
    "Output MUST conform to the TripPlan schema exactly."
)


# ------------------------- Helper Functions -------------------------


def _build_planning_context(trip: Trip) -> Dict[str, Any]:
    """Build context dictionary from trip data for OpenAI."""
    context = {
        "title": f"Trip from {trip.from_city} to {trip.to_city}",
        "timezone": trip.timezone or "UTC",
        "start_date": trip.start_date.strftime("%Y-%m-%d"),
        "end_date": trip.end_date.strftime("%Y-%m-%d"),
        "origin": trip.from_city,
        "destinations": [trip.to_city],
        "adults": trip.adults,
        "children": trip.children,
        "preferences": trip.entertainment_tags or [],
        "notes": trip.notes or "",
    }

    # Infer budget tier from budget_max
    if trip.budget_max:
        budget_max = float(trip.budget_max)
        if budget_max < 1000:
            context["budget_tier"] = "budget"
        elif budget_max < 5000:
            context["budget_tier"] = "mid"
        else:
            context["budget_tier"] = "luxury"
    else:
        context["budget_tier"] = "mid"

    # Add flight information if available
    if trip.selected_flight_airline:
        flight_event = {
            "title": f"Flight {trip.selected_flight_airline} {trip.selected_flight_number}",
            "start": (
                trip.selected_flight_departure_time.isoformat()
                if trip.selected_flight_departure_time
                else ""
            ),
            "end": (
                trip.selected_flight_arrival_time.isoformat()
                if trip.selected_flight_arrival_time
                else ""
            ),
            "location_name": f"{trip.selected_flight_departure_airport} to {trip.selected_flight_arrival_airport}",
            "notes": f"Flight from {trip.selected_flight_departure_airport} to {trip.selected_flight_arrival_airport}",
            "transport_reco": "plane",
            "priority": "essential",
        }
        context["hard_events"] = [flight_event]
    else:
        context["hard_events"] = []

    # Add hotel information if available
    if trip.selected_hotel_name:
        hotel_note = (
            f"Hotel: {trip.selected_hotel_name} in {trip.selected_hotel_location}. "
            f"Check-in: {trip.selected_hotel_check_in}, Check-out: {trip.selected_hotel_check_out}. "
            f"Plan activities around this accommodation."
        )
        if context.get("notes"):
            context["notes"] += f"\n\n{hotel_note}"
        else:
            context["notes"] = hotel_note

    # Add selected entertainment venues if available
    if trip.selected_entertainments and len(trip.selected_entertainments) > 0:
        entertainment_notes = (
            "\n\nSelected Entertainment Venues (user wants to visit these):\n"
        )
        for i, ent_data in enumerate(trip.selected_entertainments, 1):
            if isinstance(ent_data, dict):
                venue = ent_data.get("venue", {})
                ranking = ent_data.get("ranking", {})

                venue_name = venue.get("title", "Unknown")
                venue_type = venue.get("type", "")
                address = venue.get("address", "")
                rating = venue.get("rating", "")
                pros = ranking.get("pros_keywords", [])

                entertainment_notes += f"{i}. {venue_name}"
                if venue_type:
                    entertainment_notes += f" ({venue_type})"
                if rating:
                    entertainment_notes += f" - {rating}★"
                entertainment_notes += f"\n   Address: {address}\n"
                if pros:
                    entertainment_notes += f"   Highlights: {', '.join(pros[:4])}\n"

        if context.get("notes"):
            context["notes"] += entertainment_notes
        else:
            context["notes"] = entertainment_notes

    return context


def _normalize_trip_plan(plan: TripPlan) -> TripPlan:
    """Normalize transport and priority values in the plan."""
    ALLOWED_TRANSPORT = {
        "walk",
        "bus",
        "metro",
        "tram",
        "train",
        "car",
        "taxi",
        "ferry",
        "bike",
        "rideshare",
        "plane",
        "other",
    }
    TRANSPORT_SYNONYMS = {
        "boat": "ferry",
        "ship": "ferry",
        "speedboat": "ferry",
        "water_taxi": "ferry",
        "uber": "rideshare",
        "lyft": "rideshare",
        "grab": "rideshare",
        "scooter": "bike",
    }
    PRIORITY_CANON = {"essential", "nice_to_have", "optional"}
    PRIORITY_SYNONYMS = {
        "must": "essential",
        "high": "essential",
        "nice": "nice_to_have",
        "medium": "nice_to_have",
        "low": "optional",
    }

    for day in plan.days:
        for ev in day.events:
            # Normalize transport
            if ev.transport_reco:
                vv = ev.transport_reco.strip().lower()
                if vv not in ALLOWED_TRANSPORT:
                    ev.transport_reco = TRANSPORT_SYNONYMS.get(vv, "other")  # type: ignore

            # Normalize priority
            if ev.priority:
                vv = PRIORITY_SYNONYMS.get(
                    ev.priority.strip().lower(), ev.priority.strip().lower()
                )
                if vv not in PRIORITY_CANON:
                    ev.priority = "essential"  # type: ignore
                else:
                    ev.priority = vv  # type: ignore

            # Clean tags
            if ev.tags:
                ev.tags = [str(t).strip().lower() for t in ev.tags if str(t).strip()]

    return plan


# ------------------------- Main Planning Function -------------------------


def generate_trip_plan(trip: Trip) -> Dict[str, Any]:
    """
    Generate a structured trip plan using OpenAI Structured Outputs.

    Args:
        trip: Trip model instance with all trip details

    Returns:
        Dictionary containing the generated trip plan

    Raises:
        Exception: If OpenAI API call fails or returns invalid data
    """
    # Build planning context from trip
    context = _build_planning_context(trip)

    # Call OpenAI with Structured Outputs
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",  # Structured outputs snapshot
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Produce TripPlan JSON for this request.\n{json.dumps(context, ensure_ascii=False, default=str)}",
            },
        ],
        response_format=TripPlan,
        max_tokens=6000,
    )

    # Check completion status
    if not completion.choices:
        raise Exception("OpenAI returned no choices")

    # Extract parsed plan
    parsed_message = completion.choices[0].message
    if not hasattr(parsed_message, "parsed") or not parsed_message.parsed:
        raise Exception("OpenAI did not return a parsed TripPlan")

    plan: TripPlan = parsed_message.parsed

    # Normalize and validate
    plan = _normalize_trip_plan(plan)

    # Convert to dict for storage
    return plan.model_dump()
