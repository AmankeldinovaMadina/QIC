# AI Trip Planning Implementation

## Overview

The AI Trip Planning feature automatically generates detailed, day-by-day itineraries when a trip is finalized. It uses OpenAI's Structured Outputs (GPT-4o) to create human-quality travel plans that respect user preferences, selected flights/hotels, and practical travel logistics.

## How It Works

### 1. Trip Finalization Trigger

When a user finalizes their trip via `POST /api/v1/trips/{trip_id}/finalize`, the system:

1. Retrieves all trip information from the database
2. Builds context from:
   - Trip details (dates, origin, destination, travelers)
   - Selected flight information (if any)
   - Selected hotel information (if any)
   - User preferences (entertainment tags, budget, notes)
3. Calls OpenAI with Structured Outputs to generate a complete plan
4. Stores the generated plan in the `trip_plans` table
5. Updates trip status to `planned`

### 2. AI Planning Process

The planner (`app/ai/planner.py`) uses OpenAI's Structured Outputs feature to guarantee type-safe, schema-validated responses.

**System Prompt:**
```
You are a meticulous human-quality travel planner.
Generate a bespoke daily plan (no rigid templates), respecting user preferences,
wake windows, city logistics, jet lag, check-in windows, mealtimes, and rest.
All days MUST be within [start_date, end_date].
```

**Context Provided to AI:**
- Trip title (e.g., "Trip from New York to Tokyo")
- Timezone (e.g., "Asia/Tokyo")
- Date range
- Number of adults and children
- Budget tier (budget/mid/luxury)
- Preferences (e.g., ["culture", "food", "museums"])
- Selected flight details (as a "hard event")
- Selected hotel details (in notes)

### 3. Structured Output Schema

The response follows a strict Pydantic schema ensuring all required fields are present:

```python
class TripPlan:
    title: str
    timezone: str
    start_date: str  # YYYY-MM-DD
    end_date: str
    origin: Optional[str]
    destinations: List[str]
    adults: int
    children: int
    budget_tier: Literal["budget", "mid", "luxury"]
    preferences: List[str]
    diet: List[Literal["halal", "vegetarian", "gluten_free", "no_restrictions"]]
    pacing: Literal["chill", "balanced", "intense"]
    wake_window: List[int]  # [8, 22] = 8 AM to 10 PM
    days: List[TripDay]
```

**Each Day Contains:**
```python
class TripDay:
    date: str  # YYYY-MM-DD
    summary: Optional[str]
    city: Optional[str]
    country: Optional[str]
    events: List[TripEvent]
```

**Each Event Contains:**
```python
class TripEvent:
    title: str
    start: str  # ISO 8601 with timezone
    end: str
    location_name: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    tags: List[str]
    transport_reco: Optional[Transport]  # walk, bus, metro, taxi, etc.
    transport_notes: Optional[str]
    priority: Priority  # essential, nice_to_have, optional
```

## Database Schema

### TripPlan Table

```sql
CREATE TABLE trip_plans (
    id VARCHAR(36) PRIMARY KEY,
    trip_id VARCHAR(36) NOT NULL REFERENCES trips(id),
    plan_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The `plan_json` column stores the complete `TripPlan` object as JSON, including all days and events.

## API Endpoints

### 1. Finalize Trip (Generate Plan)

**POST** `/api/v1/trips/{trip_id}/finalize`

Finalizes a trip and generates an AI-powered daily itinerary.

**Authentication:** Required (Bearer token)

**Response:**
```json
{
  "id": "trip-uuid",
  "status": "planned",
  "from_city": "New York",
  "to_city": "Tokyo",
  "start_date": "2025-12-03T00:00:00",
  "end_date": "2025-12-08T00:00:00",
  ...
}
```

### 2. Get Trip Plan

**GET** `/api/v1/trips/{trip_id}/plan`

Retrieves the generated trip plan.

**Authentication:** Required (Bearer token)

**Response:**
```json
{
  "id": "plan-uuid",
  "trip_id": "trip-uuid",
  "plan_json": {
    "title": "Trip from New York to Tokyo",
    "timezone": "Asia/Tokyo",
    "start_date": "2025-12-03",
    "end_date": "2025-12-08",
    "days": [
      {
        "date": "2025-12-03",
        "city": "Tokyo",
        "summary": "Arrival day - settle in and explore nearby neighborhood",
        "events": [
          {
            "title": "Flight to Tokyo",
            "start": "2025-12-03T13:00:00-05:00",
            "end": "2025-12-04T17:00:00+09:00",
            "location_name": "JFK to NRT",
            "transport_reco": "plane",
            "priority": "essential"
          },
          {
            "title": "Hotel Check-in",
            "start": "2025-12-04T19:00:00+09:00",
            "end": "2025-12-04T19:30:00+09:00",
            "location_name": "Tokyo Grand Hotel",
            "priority": "essential"
          },
          {
            "title": "Dinner in Shinjuku",
            "start": "2025-12-04T20:00:00+09:00",
            "end": "2025-12-04T21:30:00+09:00",
            "notes": "Try local ramen or izakaya",
            "tags": ["food", "dinner"],
            "transport_reco": "walk",
            "priority": "essential"
          }
        ]
      },
      {
        "date": "2025-12-04",
        "city": "Tokyo",
        "summary": "Explore traditional Tokyo - temples and gardens",
        "events": [
          {
            "title": "Breakfast at Hotel",
            "start": "2025-12-04T08:00:00+09:00",
            "end": "2025-12-04T09:00:00+09:00",
            "priority": "essential"
          },
          {
            "title": "Senso-ji Temple Visit",
            "start": "2025-12-04T10:00:00+09:00",
            "end": "2025-12-04T12:00:00+09:00",
            "location_name": "Senso-ji Temple, Asakusa",
            "notes": "Tokyo's oldest temple, arrive early to avoid crowds",
            "tags": ["culture", "sightseeing", "temples"],
            "transport_reco": "metro",
            "transport_notes": "Take Ginza Line to Asakusa Station",
            "priority": "essential"
          },
          {
            "title": "Lunch in Asakusa",
            "start": "2025-12-04T12:30:00+09:00",
            "end": "2025-12-04T13:30:00+09:00",
            "notes": "Try tempura or traditional street food",
            "tags": ["food", "lunch"],
            "priority": "essential"
          },
          {
            "title": "Tokyo Skytree",
            "start": "2025-12-04T14:00:00+09:00",
            "end": "2025-12-04T16:00:00+09:00",
            "location_name": "Tokyo Skytree",
            "notes": "Stunning views of the city",
            "tags": ["sightseeing"],
            "transport_reco": "walk",
            "transport_notes": "15 minute walk from Senso-ji",
            "priority": "nice_to_have"
          }
        ]
      }
      // More days...
    ]
  },
  "created_at": "2025-11-03T11:30:00"
}
```

### 3. Get Trip Checklist

**GET** `/api/v1/trips/{trip_id}/checklist`

Retrieves the trip preparation checklist.

**Authentication:** Required (Bearer token)

**Response:**
```json
{
  "id": "checklist-uuid",
  "trip_id": "trip-uuid",
  "checklist_json": {
    "pre_trip": [
      "Check passport validity (6 months minimum)",
      "Apply for visa if required",
      "Book transportation and accommodation"
    ],
    "packing": [
      "Travel documents (passport, visa, tickets)",
      "Clothing appropriate for destination weather"
    ],
    "documents": [
      "Passport",
      "Visa",
      "Flight tickets"
    ],
    "during_trip": [
      "Keep important documents secure",
      "Stay aware of local customs"
    ]
  },
  "created_at": "2025-11-03T11:30:00"
}
```

## Usage Example

### Complete Workflow

```bash
# 1. Register user
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler123"}'

# Save the access_token from response

# 2. Create trip
curl -X POST "http://localhost:8001/api/v1/trips" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "from_city": "New York",
    "to_city": "Tokyo",
    "start_date": "2025-12-03T00:00:00",
    "end_date": "2025-12-08T00:00:00",
    "transport": "flight",
    "adults": 2,
    "budget_max": 3000,
    "entertainment_tags": ["culture", "food", "sightseeing"],
    "notes": "First time in Japan, interested in traditional culture and amazing food",
    "timezone": "Asia/Tokyo"
  }'

# Save the trip_id from response

# 3. Select flight (optional but improves plan quality)
curl -X POST "http://localhost:8001/api/v1/flights/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "trip_id": "TRIP_ID",
    "flight_id": "flight_001",
    "airline": "JAL",
    "flight_number": "JL006",
    "departure_airport": "JFK",
    "arrival_airport": "NRT",
    "departure_time": "2025-12-03T13:00:00",
    "arrival_time": "2025-12-04T17:00:00",
    "price": 1200,
    "currency": "USD",
    "total_duration_min": 840,
    "stops": 0
  }'

# 4. Select hotel (optional but improves plan quality)
curl -X POST "http://localhost:8001/api/v1/hotels/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "trip_id": "TRIP_ID",
    "hotel_id": "hotel_001",
    "hotel_name": "Tokyo Grand Hotel",
    "location": "Shinjuku, Tokyo",
    "check_in_date": "2025-12-04",
    "check_out_date": "2025-12-08",
    "price_per_night": 180,
    "total_price": 720,
    "currency": "USD",
    "rating": 4.5
  }'

# 5. Finalize trip and generate AI plan
curl -X POST "http://localhost:8001/api/v1/trips/TRIP_ID/finalize" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Retrieve the generated plan
curl -X GET "http://localhost:8001/api/v1/trips/TRIP_ID/plan" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 7. Get the checklist
curl -X GET "http://localhost:8001/api/v1/trips/TRIP_ID/checklist" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# Create session
response = requests.post(f"{BASE_URL}/auth/register", json={"username": "traveler"})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create trip
trip_response = requests.post(
    f"{BASE_URL}/trips",
    json={
        "from_city": "New York",
        "to_city": "Tokyo",
        "start_date": "2025-12-03T00:00:00",
        "end_date": "2025-12-08T00:00:00",
        "transport": "flight",
        "adults": 2,
        "budget_max": 3000,
        "entertainment_tags": ["culture", "food"],
        "timezone": "Asia/Tokyo"
    },
    headers=headers
)
trip_id = trip_response.json()["id"]

# Finalize and generate plan
finalize_response = requests.post(
    f"{BASE_URL}/trips/{trip_id}/finalize",
    headers=headers
)

# Retrieve plan
plan_response = requests.get(
    f"{BASE_URL}/trips/{trip_id}/plan",
    headers=headers
)
plan = plan_response.json()["plan_json"]

# Print daily itinerary
for day in plan["days"]:
    print(f"\n{day['date']} - {day['city']}")
    print(f"Summary: {day['summary']}")
    for event in day["events"]:
        print(f"  {event['start']} - {event['title']}")
```

## Testing

Run the comprehensive test suite:

```bash
# Ensure server is running
python -m app.main

# In another terminal
python test_ai_planner.py
```

The test suite validates:
1. ✅ User registration and trip creation
2. ✅ Flight and hotel selection
3. ✅ AI plan generation on finalization
4. ✅ Plan retrieval and structure validation
5. ✅ Checklist generation

## Implementation Files

```
app/
├── ai/
│   ├── __init__.py          # Module exports
│   └── planner.py           # AI planning logic with Structured Outputs
├── trips/
│   ├── router.py            # Updated finalize endpoint
│   ├── service.py           # Trip business logic
│   └── schemas.py           # Trip DTOs
└── db/
    └── models.py            # Database models (TripPlan table)

test_ai_planner.py           # Test suite
AI_PLANNING.md               # This documentation
```

## Key Features

### Context-Aware Planning

The AI considers:
- **Flight schedules**: Arrival/departure times affect first/last day plans
- **Hotel location**: Activities planned near accommodation
- **Budget tier**: Luxury travelers get fine dining, budget travelers get street food
- **Preferences**: Entertainment tags influence activity selection
- **Timezone**: All times properly localized
- **Travel logistics**: Realistic travel times between locations

### Smart Scheduling

- **Wake windows**: Respects user's preferred activity hours (default 8 AM - 10 PM)
- **Meal planning**: Breakfast, lunch, dinner appropriately scheduled
- **Rest periods**: Includes downtime after long flights or intense activities
- **Transport suggestions**: Recommends walk/metro/taxi based on distance and convenience

### Priority System

Events are marked with priority levels:
- **essential**: Must-do activities (meals, check-ins, key attractions)
- **nice_to_have**: Recommended but flexible
- **optional**: If time permits

### Pacing Options

- **chill**: Relaxed schedule with plenty of free time
- **balanced**: Mix of planned activities and flexibility (default)
- **intense**: Packed itinerary maximizing attractions

## Future Enhancements

Potential improvements:
1. **Real-time Activity Data**: Integrate with Google Places, TripAdvisor
2. **Weather Integration**: Adjust plans based on forecasts
3. **Collaborative Planning**: Allow multiple users to edit plans
4. **Alternative Suggestions**: Generate backup activities
5. **Budget Tracking**: Calculate estimated costs per day
6. **Map Integration**: Visual itinerary on interactive maps
7. **Reservation Links**: Direct booking links for restaurants/attractions
8. **ICS Export**: Export to calendar apps

## Error Handling

The system gracefully handles failures:
- **OpenAI API errors**: Returns 502 with detailed error message
- **Invalid trip state**: Returns 400 if trip already finalized
- **Missing trip**: Returns 404 if trip not found
- **Schema validation**: Pydantic ensures data integrity

## Performance

- **Average generation time**: 10-30 seconds (depends on trip length)
- **Token usage**: ~3000-6000 tokens per plan
- **Caching**: Plans stored in database, no regeneration needed
- **Concurrent requests**: Supported via async architecture

---

**Last Updated**: November 3, 2025  
**Model**: GPT-4o-2024-08-06  
**Feature Status**: ✅ Production Ready
