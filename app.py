# app.py
# FastAPI travel planner with OpenAI Structured Outputs + Visa API + ICS export
import os
import uuid
import json
import math
from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional
from fastapi.responses import Response, PlainTextResponse


import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator
from openai import OpenAI

# Module for flight search redirection
import url_builder 

load_dotenv()

# ------------------------- FastAPI setup -------------------------
app = FastAPI(title="Travel Planner (Structured Outputs)", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# ------------------------- OpenAI client -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- Visa API config -----------------------
RAPID_KEY = os.getenv("RAPIDAPI_KEY", "")
VISA_BASE = "https://visa-requirement.p.rapidapi.com"
VISA_HEADERS = {
    "x-rapidapi-key": RAPID_KEY,
    "x-rapidapi-host": "visa-requirement.p.rapidapi.com",
    "Content-Type": "application/json",
}
class VisaApiError(Exception): pass

# ---------------------- Flight Redirect schema -------------------
class FlightTicketsModel(BaseModel):
    origin_city: str
    destination_city: str
    outbound_date: str
    return_date: Optional[str] = None

    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)

    cabinclass: Literal["economy","premiumeconomy","business","first"] = "economy"
    outbound_alts: Optional[bool] = None
    inbound_alts: Optional[bool] = None
    prefer_directs: Optional[bool] = None

    # booleans exactly matching your TripFilters
    cabin_bag: Optional[bool] = None
    checked_bag: Optional[bool] = None

    market_domain: str = "www.skyscanner.qa"
    nearby_radius_km: int = Field(default=150, ge=10, le=500)
    use_mac: bool = False

class FlightLinkResponse(BaseModel):
    url: str

# ------------------------- Trip plan schema ----------------------
Transport = Literal["walk","bus","metro","tram","train","car","taxi","ferry","bike","rideshare","plane","other"]
Priority  = Literal["essential","nice_to_have","optional"]

class TripEvent(BaseModel):
    title: str = Field(..., description="Short human title of the event")
    start: str = Field(..., description="ISO 8601 datetime with timezone, e.g. 2025-12-14T09:00:00+09:00")
    end:   str = Field(..., description="ISO 8601 datetime with timezone, e.g. 2025-12-14T10:00:00+09:00")
    location_name: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    transport_reco: Optional[Transport] = None
    transport_notes: Optional[str] = None
    priority: Priority = "essential"

    @field_validator("end")
    @classmethod
    def _end_after_start(cls, v, values):
        try:
            s = values.get("start")
            if s:
                if datetime.fromisoformat(v) <= datetime.fromisoformat(s):
                    raise ValueError("end must be after start")
        except Exception:
            # If model fails timezone etc., let overall validator handle – Structured Outputs should prevent this.
            pass
        return v

class TripDay(BaseModel):
    date: str = Field(..., description="Date YYYY-MM-DD in trip timezone")
    summary: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    events: List[TripEvent] = Field(default_factory=list)

class TripPlan(BaseModel):
    title: str
    timezone: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    origin: Optional[str] = None
    destinations: List[str] = Field(default_factory=list)
    adults: int = 1
    children: int = 0
    budget_tier: Literal["budget","mid","luxury"] = "mid"
    preferences: List[str] = Field(default_factory=list)
    diet: List[Literal["halal","vegetarian","gluten_free","no_restrictions"]] = Field(default_factory=lambda: ["no_restrictions"])
    avoid_patterns: bool = True
    pacing: Literal["chill","balanced","intense"] = "balanced"
    wake_window: List[int] = Field(default_factory=lambda: [8, 22])  # [startHour, endHour]
    hard_events: List[TripEvent] = Field(default_factory=list)
    days: List[TripDay] = Field(default_factory=list)

# request/response for planning endpoint
class PlanRequest(BaseModel):
    session_id: Optional[str] = None
    title: str
    timezone: str
    start_date: str
    end_date: str
    origin: Optional[str] = None
    destinations: List[str]
    adults: int = 1
    children: int = 0
    budget_tier: Literal["budget","mid","luxury"] = "mid"
    preferences: List[str] = Field(default_factory=list)
    diet: List[Literal["halal","vegetarian","gluten_free","no_restrictions"]] = Field(default_factory=list)
    avoid_patterns: bool = True
    pacing: Literal["chill","balanced","intense"] = "balanced"
    wake_window: List[int] = Field(default_factory=lambda: [8, 22])
    hard_events: List[TripEvent] = Field(default_factory=list)

class PlanResponse(BaseModel):
    session_id: str
    plan: TripPlan

# --------------------- Structured Outputs prompt -----------------
SYSTEM_SO = (
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

def _build_payload(req: PlanRequest) -> Dict[str, Any]:
    return req.model_dump()

# Optional normalizers (rare with Structured Outputs, but safe to keep)
ALLOWED_TRANSPORT = {"walk","bus","metro","tram","train","car","taxi","ferry","bike","rideshare","plane","other"}
TRANSPORT_SYNONYMS = {
    "boat":"ferry","ship":"ferry","speedboat":"ferry","water_taxi":"ferry",
    "uber":"rideshare","lyft":"rideshare","grab":"rideshare","scooter":"bike",
}
PRIORITY_CANON = {"essential","nice_to_have","optional"}
PRIORITY_SYNONYMS = {"must":"essential","high":"essential","nice":"nice_to_have","medium":"nice_to_have","low":"optional"}

def _norm_transport(v: Optional[str]) -> Optional[str]:
    if not v: return v
    vv = v.strip().lower()
    if vv in ALLOWED_TRANSPORT: return vv
    if vv in TRANSPORT_SYNONYMS: return TRANSPORT_SYNONYMS[vv]
    return "other"

def _norm_priority(v: Optional[str]) -> Optional[str]:
    if not v: return v
    vv = PRIORITY_SYNONYMS.get(v.strip().lower(), v.strip().lower())
    return vv if vv in PRIORITY_CANON else "essential"

def _normalize_trip_plan(plan: TripPlan) -> TripPlan:
    for day in plan.days:
        for ev in day.events:
            if ev.transport_reco:
                ev.transport_reco = _norm_transport(ev.transport_reco)  # type: ignore
            if ev.priority:
                ev.priority = _norm_priority(ev.priority)  # type: ignore
            if ev.tags:
                ev.tags = [str(t).strip().lower() for t in ev.tags if str(t).strip()]
    return plan

def generate_trip_plan_structured(req: PlanRequest) -> TripPlan:
    payload = _build_payload(req)
    completion = client.responses.parse(
        model="gpt-4o-2024-08-06",  # structured outputs snapshot
        input=[
            {"role":"system","content":SYSTEM_SO},
            {"role":"user","content":f"Produce TripPlan JSON for this request.\n{json.dumps(payload, ensure_ascii=False)}"},
        ],
        text_format=TripPlan,  # ← parses & validates directly into TripPlan
        max_output_tokens=6000,
    )

    if getattr(completion, "status", "completed") != "completed":
        raise HTTPException(status_code=502, detail=f"Model status: {completion.status}; details: {getattr(completion,'incomplete_details',None)}")

    plan: Optional[TripPlan] = getattr(completion, "output_parsed", None)
    if not plan:
        raise HTTPException(status_code=502, detail="Model did not return a parsed TripPlan")

    return _normalize_trip_plan(plan)

# ------------------------- Helpers -------------------------------
def _to_tripfilters(cfg: FlightTicketsModel) -> url_builder.TripFilters:
    """
    Construct url_builder.TripFilters via keyword args (matches your __init__).
    """
    return url_builder.TripFilters(**cfg.model_dump())

def _date(s: str) -> datetime:
    return datetime.fromisoformat(s if "T" in s else f"{s}T00:00:00")

def _check_range(plan: TripPlan):
    s0 = _date(plan.start_date).date()
    e0 = _date(plan.end_date).date()
    day_dates = [datetime.fromisoformat(d.date).date() for d in plan.days]
    if not day_dates:
        raise HTTPException(status_code=400, detail="Plan has no days")
    if min(day_dates) < s0 or max(day_dates) > e0:
        raise HTTPException(status_code=400, detail="Days fall outside requested range")

# ------------------------- ICS export ----------------------------
def plan_to_ics(plan: TripPlan) -> str:
    # Minimal, RFC5545-ish ICS
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TripPlanner//StructuredOutputs//EN",
    ]
    for day in plan.days:
        for ev in day.events:
            try:
                dtstart = datetime.fromisoformat(ev.start)
                dtend = datetime.fromisoformat(ev.end)
            except Exception:
                continue
            uid = str(uuid.uuid4())
            def _ical_dt(dt: datetime) -> str:
                # Keep timezone by serializing as UTC (Z) to be safe across calendars
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            lines += [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"SUMMARY:{ev.title}".replace("\n", " "),
                f"DTSTART:{_ical_dt(dtstart)}",
                f"DTEND:{_ical_dt(dtend)}",
                f"LOCATION:{(ev.location_name or ev.address or '').replace('\n',' ')}",
                f"DESCRIPTION:{(ev.notes or '').replace('\n',' ')}",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

# ------------------------- Visa services -------------------------
async def get_custom_passport_rank(weights: Dict[str, int]) -> Any:
    async with httpx.AsyncClient(timeout=15.0, headers=VISA_HEADERS) as client_http:
        r = await client_http.post(f"{VISA_BASE}/v2/passport/rank/custom", json={"weights": weights})
        if r.is_error:
            raise VisaApiError(f"{r.status_code}: {r.text}")
        return r.json()

async def get_visa_requirement(passport_iso2: str, destination_iso2: str) -> Any:
    params = {"from": passport_iso2.upper(), "to": destination_iso2.upper()}
    async with httpx.AsyncClient(timeout=15.0, headers=VISA_HEADERS) as client_http:
        r = await client_http.get(f"{VISA_BASE}/v2/visa/requirements", params=params)
        if r.is_error:
            raise VisaApiError(f"{r.status_code}: {r.text}")
        return r.json()

# ------------------------- Endpoints -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/flight/link", response_model=FlightLinkResponse)
async def flight_link(filters: FlightTicketsModel):
    """
    Build and return a Skyscanner URL for client-side navigation.
    Your frontend can handle the redirect, e.g. window.location = url.
    """
    try:
        tf = _to_tripfilters(filters)
        url = url_builder.build_url(tf)
        return FlightLinkResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not build flight link: {str(e)}")

@app.post("/ai/plan", response_model=PlanResponse)
def ai_plan(req: PlanRequest):
    sid = req.session_id or str(uuid.uuid4())
    try:
        plan = generate_trip_plan_structured(req)
        _check_range(plan)
        return PlanResponse(session_id=sid, plan=plan)
    except ValidationError as e:
        # Very rare with Structured Outputs, but keep a guard
        raise HTTPException(status_code=502, detail=f"Validation failed: {e}")

@app.post("/ai/plan/ics")
def ai_plan_ics(req: PlanRequest):
    # Convenience: generate plan and return ICS text
    plan = generate_trip_plan_structured(req)
    _check_range(plan)
    ics = plan_to_ics(plan)
    return {"filename": "trip.ics", "ics": ics}

class RankWeights(BaseModel):
    weights: Dict[str, int] = Field(
        default={
            "Visa-free": 2,
            "Visa on arrival": 1,
            "Visa required": 0,
            "eVisa": 1,
            "eTA": 1,
            "Tourist card": 0,
            "Freedom of movement": 3,
            "Not admitted": -1,
        }
    )

@app.post("/ai/plan/ics-file")
def ai_plan_ics_file(req: PlanRequest):
    """Return a real .ics file (not JSON) so browsers download/import directly."""
    plan = generate_trip_plan_structured(req)
    _check_range(plan)
    ics_text = plan_to_ics(plan)

    # If you prefer inline preview in some browsers, change 'attachment' to 'inline'
    headers = {
        "Content-Disposition": 'attachment; filename="trip.ics"',
        "Cache-Control": "no-store",
    }
    return Response(content=ics_text, media_type="text/calendar", headers=headers)


@app.post("/visa/rank/custom")
async def visa_rank_custom(body: RankWeights):
    try:
        data = await get_custom_passport_rank(body.weights)
        return data
    except VisaApiError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/visa/check")
async def visa_check(
    passport: str = Query(..., min_length=2, max_length=2, description="ISO2 passport, e.g., KZ"),
    destination: str = Query(..., min_length=2, max_length=2, description="ISO2 destination, e.g., KR"),
):
    try:
        data = await get_visa_requirement(passport, destination)
        return {"passport": passport.upper(), "destination": destination.upper(), "result": data}
    except VisaApiError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ------------------------- Uvicorn -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
