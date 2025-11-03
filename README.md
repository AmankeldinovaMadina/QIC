# Travel Aggregator with Visa Requirements

A FastAPI service that aggregates hidden places from OpenTripMap & OpenStreetMap, plus visa requirement checking via RapidAPI.

## Features

### 🗺️ Travel Discovery
- **Hidden Places**: Finds interesting but lesser-known places near coordinates
- **Multiple Sources**: Combines OpenTripMap + OpenStreetMap data
- **Smart Deduplication**: Merges nearby places to avoid duplicates
- **Distance Sorting**: Results sorted by distance from query point

### 🛂 Visa Requirements
- **Custom Passport Ranking**: Rank passports by visa-free access with custom weights
- **Visa Requirement Check**: Check visa requirements between countries
- **RapidAPI Integration**: Uses professional visa requirement data

### ✈️ Flight AI Ranking & Selection
- **Intelligent Flight Ranking**: AI-powered flight comparison using OpenAI
- **Smart Preferences**: Considers user preferences like price, duration, stops
- **Pros/Cons Analysis**: Automatic generation of flight advantages and disadvantages
- **Flight Selection**: Save your preferred flight to a trip
- **Persistent Storage**: Selected flights are stored with complete details
- **Fallback System**: Uses heuristic ranking when OpenAI is unavailable

## Setup

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn httpx python-dotenv
   ```

2. **Configure API keys in `.env`:**
   ```env
   OPENTRIPMAP_API_KEY=your_opentripmap_key_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```
   Server runs on http://localhost:8001

## API Endpoints

### Health Check
```bash
curl http://localhost:8001/health
```

### Discover Hidden Places
```bash
curl -X POST "http://localhost:8001/discover" \
  -H "Content-Type: application/json" \
  -d '{"lat":43.2566,"lon":76.9286,"radius_m":3000}'
```

### Visa Passport Ranking
```bash
curl -X POST "http://localhost:8001/visa/rank/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "Visa-free": 2,
      "Visa on arrival": 1,
      "Visa required": 0,
      "eVisa": 1,
      "eTA": 1,
      "Tourist card": 0,
      "Freedom of movement": 3,
      "Not admitted": -1
    }
  }'
```

### Check Visa Requirements
```bash
curl "http://localhost:8001/visa/check?passport=KZ&destination=KR"
```

### Authentication Endpoints

**Register a new user:**
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username"}'
```

**Login:**
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username"}'
```

Response includes `access_token` to use in subsequent requests.

### Flight AI Ranking
Rank flight itineraries using AI-powered analysis:

```bash
curl -X POST "http://localhost:8001/api/v1/flights/ai-rank" \
  -H "Content-Type: application/json" \
  -d '{
    "search_id": "demo_jfk_lax",
    "preferences_prompt": "Avoid red-eye flights, prefer non-stop or max one stop, low price is important, but flight duration also matters.",
    "locale": {
      "currency": "USD",
      "hl": "en",
      "tz": "America/New_York"
    },
    "flights": [
      {
        "id": "flight_aa_nonstop",
        "price": { "amount": 250, "currency": "USD" },
        "total_duration_min": 360,
        "stops": 0,
        "emissions_kg": 420,
        "legs": [
          {
            "dep_iata": "JFK",
            "dep_time": "2025-12-15T08:00:00",
            "arr_iata": "LAX",
            "arr_time": "2025-12-15T11:00:00",
            "marketing": "AA",
            "flight_no": "AA100",
            "duration_min": 360
          }
        ]
      },
      {
        "id": "flight_ua_1stop",
        "price": { "amount": 180, "currency": "USD" },
        "total_duration_min": 480,
        "stops": 1,
        "emissions_kg": 510,
        "layovers_min": 95,
        "legs": [
          {
            "dep_iata": "JFK",
            "dep_time": "2025-12-15T20:30:00",
            "arr_iata": "ORD",
            "arr_time": "2025-12-15T22:00:00",
            "marketing": "UA",
            "flight_no": "UA320",
            "duration_min": 150
          },
          {
            "dep_iata": "ORD",
            "dep_time": "2025-12-16T01:00:00",
            "arr_iata": "LAX",
            "arr_time": "2025-12-16T03:30:00",
            "marketing": "UA",
            "flight_no": "UA321",
            "duration_min": 150
          }
        ]
      }
    ]
  }'
```

### Flight Selection
Save a selected flight to your trip:

```bash
curl -X POST "http://localhost:8001/api/v1/flights/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "trip_id": "856ab99f-ec37-4ea2-be53-de94026fba3a",
    "flight_id": "flight_123_final",
    "airline": "Delta",
    "flight_number": "DL123",
    "departure_airport": "JFK",
    "arrival_airport": "LAX",
    "departure_time": "2025-11-10T08:00:00",
    "arrival_time": "2025-11-10T11:30:00",
    "price": 350.00,
    "currency": "USD",
    "total_duration_min": 330,
    "stops": 0,
    "score": 1.0,
    "title": "Direct morning flight",
    "pros_keywords": ["direct", "convenient time"],
    "cons_keywords": []
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Flight Delta DL123 successfully added to trip",
  "trip_id": "856ab99f-ec37-4ea2-be53-de94026fba3a",
  "flight": {
    "airline": "Delta",
    "flight_number": "DL123",
    "route": "JFK → LAX",
    "price": "$350.0 USD",
    "departure": "2025-11-10T08:00:00"
  }
}
```

**Get trip with selected flight:**
```bash
curl -X GET "http://localhost:8001/api/v1/trips/856ab99f-ec37-4ea2-be53-de94026fba3a" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response includes:**
```json
{
  "id": "856ab99f-ec37-4ea2-be53-de94026fba3a",
  "from_city": "New York",
  "to_city": "Los Angeles",
  "start_date": "2025-12-01T00:00:00",
  "end_date": "2025-12-05T00:00:00",
  "selected_flight": {
    "flight_id": "flight_123_final",
    "airline": "Delta",
    "flight_number": "DL123",
    "departure_airport": "JFK",
    "arrival_airport": "LAX",
    "departure_time": "2025-11-10T08:00:00",
    "arrival_time": "2025-11-10T11:30:00",
    "price": 350.0,
    "currency": "USD",
    "total_duration_min": 330,
    "stops": 0,
    "score": 1.0,
    "title": "Direct morning flight",
    "pros_keywords": ["direct", "convenient time"],
    "cons_keywords": []
  }
}
```

## Complete Flight Selection Workflow

Here's a complete example of using the flight ranking and selection features:

### Step 1: Register/Login
```bash
# Register a new user
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler123"}'

# Save the access_token from the response
```

### Step 2: Create a Trip
```bash
curl -X POST "http://localhost:8001/api/v1/trips" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "from_city": "New York",
    "to_city": "Los Angeles",
    "start_date": "2025-12-01T00:00:00",
    "end_date": "2025-12-05T00:00:00",
    "transport": "flight",
    "adults": 1,
    "budget_max": 1000
  }'

# Save the trip_id from the response
```

### Step 3: Get AI Flight Rankings
```bash
curl -X POST "http://localhost:8001/api/v1/flights/ai-rank" \
  -H "Content-Type: application/json" \
  -d '{
    "search_id": "jfk_lax_search",
    "preferences_prompt": "I prefer direct flights in the morning, price is important but comfort matters too",
    "flights": [
      {
        "id": "delta_dl123",
        "price": {"amount": 350, "currency": "USD"},
        "total_duration_min": 330,
        "stops": 0,
        "legs": [{
          "dep_iata": "JFK",
          "dep_time": "2025-12-01T08:00:00",
          "arr_iata": "LAX",
          "arr_time": "2025-12-01T11:30:00",
          "marketing": "Delta",
          "flight_no": "DL123",
          "duration_min": 330
        }]
      }
    ]
  }'

# Review the AI-ranked results and choose your preferred flight
```

### Step 4: Select and Save Your Flight
```bash
curl -X POST "http://localhost:8001/api/v1/flights/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "trip_id": "YOUR_TRIP_ID",
    "flight_id": "delta_dl123",
    "airline": "Delta",
    "flight_number": "DL123",
    "departure_airport": "JFK",
    "arrival_airport": "LAX",
    "departure_time": "2025-12-01T08:00:00",
    "arrival_time": "2025-12-01T11:30:00",
    "price": 350.00,
    "currency": "USD",
    "total_duration_min": 330,
    "stops": 0,
    "score": 0.95,
    "title": "Direct morning flight",
    "pros_keywords": ["direct", "morning departure", "good price"],
    "cons_keywords": []
  }'
```

### Step 5: Retrieve Your Trip with Flight Details
```bash
curl -X GET "http://localhost:8001/api/v1/trips/YOUR_TRIP_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response will include all trip details plus the selected_flight object
```

## Configuration Notes

### RapidAPI Setup
1. Get your API key from [RapidAPI visa-requirement service](https://rapidapi.com/hub)
2. Add it to `.env` as `RAPIDAPI_KEY=your_key_here`
3. **Important**: Keep API keys server-side only, never expose in frontend code

### Endpoint Customization
The visa check endpoint path might need adjustment based on your specific RapidAPI plan. Common variations:
- `/v2/visa/requirements` (current)
- `/v2/passport/requirements/{from}/{to}`
- `/v2/visa/check`

Check your RapidAPI dashboard's "Endpoints" tab for the exact path and update the `get_visa_requirement` function accordingly.

## Example Responses

### Hidden Places
```json
{
  "places": [
    {
      "id": "osm:641793048",
      "name": "Казкоммерцбанк",
      "lat": 43.2543989,
      "lon": 76.9317289,
      "categories": ["bank"],
      "rating": null,
      "distance": 352.29,
      "source": "OpenStreetMap"
    }
  ]
}
```

### Visa Check
```json
{
  "passport": "KZ",
  "destination": "KR", 
  "result": {
    "requirement": "Visa required",
    "days": 0,
    "notes": "Tourist visa required"
  }
}
```

### Flight AI Ranking
```json
{
  "search_id": "demo_jfk_lax",
  "ordered_ids": [
    "flight_aa_nonstop",
    "flight_ua_1stop"
  ],
  "items": [
    {
      "id": "flight_aa_nonstop",
      "score": 0.9,
      "title": "Non-stop Flight AA100: JFK to LAX",
      "rationale_short": "Best option with no stops and reasonable duration, but slightly higher price.",
      "pros_keywords": [
        "non-stop",
        "short duration",
        "direct flight"
      ],
      "cons_keywords": [
        "higher price than 1-stop"
      ],
      "tags": null
    },
    {
      "id": "flight_ua_1stop",
      "score": 0.7,
      "title": "1-stop Flight UA320/UA321: JFK to LAX via ORD",
      "rationale_short": "Lower price but longer duration and one stop, which may be less convenient.",
      "pros_keywords": [
        "lower price",
        "1 stop",
        "acceptable layover"
      ],
      "cons_keywords": [
        "longer total duration",
        "1 stop",
        "late departure"
      ],
      "tags": null
    }
  ],
  "meta": {
    "used_model": "gpt-4o-mini",
    "deterministic": true,
    "notes": [
      "Ranked based on user preferences for non-stop or minimal stops, price, and duration."
    ]
  }
}
```

## Production Notes

- **Security**: Keep `RAPIDAPI_KEY`, `OPENTRIPMAP_API_KEY`, and `OPENAI_API_KEY` in environment variables only
- **Caching**: Consider caching visa results (rules don't change frequently)
- **Rate Limits**: All APIs have rate limits; implement retry logic for production use
- **Error Handling**: 502 errors indicate upstream API issues; 500 errors are internal
- **OpenAI Fallback**: Flight ranking automatically falls back to heuristic ranking when OpenAI is unavailable

## File Structure

```
QIC/
├── app.py              # Main FastAPI application
├── app/                # Modular application structure
│   ├── main.py         # FastAPI app initialization
│   ├── flights/        # Flight ranking module
│   │   ├── ai_ranker.py # OpenAI flight ranking logic
│   │   ├── router.py   # Flight endpoints
│   │   └── schemas.py  # Flight data models
│   ├── api/            # API routing
│   ├── auth/           # Authentication module
│   ├── trips/          # Trip management
│   ├── core/           # Core settings and logging
│   └── db/             # Database models
├── requirements.txt    # Python dependencies  
├── .env               # API keys (keep private!)
└── README.md          # This file
```