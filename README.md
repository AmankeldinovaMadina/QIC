# QICO - AI-Powered Trip Planner

An intelligent travel planning platform powered by OpenAI and FastAPI. QICO helps users plan trips faster, discover destinations, rank hotels and entertainment venues, and get AI-generated personalized itineraries—all enhanced with a conversational AI companion and shareable trip summaries.

## Features

### 🤖 AI Companion (Chat + Voice)
- **Conversational Interface**: Chat or voice commands to plan trips, modify itineraries, and get recommendations
- **Natural Language**: Ask "Find me halal-friendly restaurants" or "Add 2 nights at a luxury hotel"
- **Context-Aware Assistance**: AI remembers your trip context and preferences
- **Smart CTAs**: Intelligent suggestions for insurance, bookings, and add-ons

### 🛂 Visa & Passport Services
- **Custom Passport Ranking**: Rank passports by visa-free access with weighted scoring
- **Visa Requirement Check**: Check visa requirements between countries instantly
- **RapidAPI Integration**: Professional, up-to-date visa requirement data

### ✈️ Flight Search, Ranking & Selection
- **Google Flights Integration**: Search real flights via SerpAPI Google Flights API
- **Smart Airport Mapping**: Automatically maps city names to IATA airport codes (300+ cities)
- **AI-Powered Flight Ranking**: OpenAI intelligent comparison of flight options
- **Pros/Cons Analysis**: Automatic generation of flight advantages and disadvantages
- **Flight Selection**: Save preferred flight to trip with complete details and scoring
- **Flexible Queries**: Support cabin classes, round trips, adult/children counts, currency
- **Fallback System**: Heuristic ranking when OpenAI is unavailable
- **Skyscanner Redirect**: Generate direct Skyscanner links for one-click booking

### 🏨 Hotel Search, Ranking & Selection
- **Google Hotels Integration**: Search hotels via SerpAPI Google Hotels API
- **Property Details**: Get detailed information for specific hotel properties
- **AI-Powered Hotel Ranking**: OpenAI intelligent hotel comparison by user preferences
- **Smart Filtering**: Location, price, rating, amenities, cancellation policy, reviews
- **Link Preservation**: Every ranked hotel includes direct booking URL
- **Hotel Selection**: Save preferred hotel to trip with complete details and scoring
- **Amenities Tracking**: Store and display amenities (WiFi, breakfast, gym, pool, etc.)
- **Fallback System**: Heuristic ranking when OpenAI is unavailable

### 🎭 Entertainment Ranking
- **Google Maps Integration**: Discover restaurants, museums, attractions
- **AI-Powered Venue Ranking**: Intelligent entertainment recommendations
- **Link-Enabled Results**: Every venue includes Google Maps link
- **Preference Matching**: Filter by cuisine, type, rating, reviews
- **Fallback System**: Heuristic ranking for robust recommendations

### 🌍 Culture Guide (Persistent)
- **AI-Generated Guides**: Culture-specific etiquette and local tips per destination
- **Persisted by Trip**: Guides stored and reusable by `trip_id`
- **Structured Outputs**: Type-safe, schema-validated responses
- **Actionable Advice**: DO/AVOID guidance for dining, greetings, dress, taboos
- **Shareable**: Include in trip summary for group planning

### 🎯 AI Trip Planning
- **Automated Itinerary**: OpenAI generates detailed day-by-day plans
- **Structured Outputs**: Type-safe TripPlan with guaranteed schema compliance
- **Context-Aware**: Considers flights, hotels, preferences, and destination
- **Smart Scheduling**: Respects wake windows, mealtimes, jet lag, travel times
- **Flexible Pacing**: Choose chill, balanced, or intense itineraries
- **Transport Recommendations**: Suggests walk, metro, taxi, car, etc. for each event
- **Priority System**: Events marked essential, nice-to-have, or optional
- **Database Storage**: Generated plans stored and retrievable by trip_id

### 📋 Trip Summary & Sharing
- **Auto-Generated Summaries**: AI creates shareable trip snapshots
- **ICS Export**: Download trips as .ics files for calendar import
- **Social Copy**: Suggested hashtags and social media snippets
- **Viral Growth**: Share on social platforms to bring new users

## Quick Start

### Prerequisites
- **Python**: 3.9 or higher (tested on 3.9, 3.10, 3.11, 3.12)
- **pip**: Package installer for Python

### Installation

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or: .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
   
   **Note**: The `requirements.txt` uses flexible version constraints (`>=min,<max`) to ensure compatibility across different Python versions and operating systems. If you encounter any compatibility issues, please run:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

2. **Set up environment variables in `.env`:**
   ```env
   OPENAI_API_KEY=sk-...
   RAPIDAPI_KEY=your_rapidapi_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   SERPAPI_KEY=your_serpapi_key
   DATABASE_URL=sqlite+aiosqlite:///./qico.db
   ```

3. **Run database migrations:**
   ```bash
   python migrate_hotel_link.py
   python migrate_culture_guide.py
   ```

4. **Start the server:**
   ```bash
   python app.py
   # or
   uvicorn app.main:app --reload --port 8001
   ```

   Server runs on `http://localhost:8001`

5. **Access the frontend:**
   ```bash
   cd frontendQIC
   npm install
   npm run dev
   ```

## Core API Endpoints

### Health Check
```bash
curl http://localhost:8001/health
```

### AI Trip Planning
```bash
curl -X POST "http://localhost:8001/ai/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tokyo Holiday",
    "timezone": "Asia/Tokyo",
    "start_date": "2025-12-01",
    "end_date": "2025-12-05",
    "destinations": ["Tokyo"],
    "adults": 2,
    "preferences": ["museums", "food", "nature"],
    "budget_tier": "mid",
    "pacing": "balanced"
  }'
```

### Generate Culture Guide
```bash
curl -X POST "http://localhost:8001/api/v1/culture/guide" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "your-trip-id",
    "destination": "Tokyo"
  }'
```

### Retrieve Culture Guide
```bash
curl -X GET "http://localhost:8001/api/v1/culture/guide/your-trip-id"
```

### Rank Hotels
```bash
curl -X POST "http://localhost:8001/api/v1/hotels/rank" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "your-trip-id",
    "search_id": "tokyo_hotel_search",
    "preferences_prompt": "Near tourist attractions, good breakfast, modern amenities, good value",
    "hotels": [
      {
        "serp_id": "hotel_1",
        "title": "Tokyo Grand Hotel",
        "location": "Shinjuku, Tokyo",
        "price": 180.0,
        "rating": 4.5,
        "reviews": 1250,
        "amenities": ["WiFi", "Breakfast", "Gym", "Pool"],
        "free_cancellation": true,
        "link": "https://www.booking.com/..."
      },
      {
        "serp_id": "hotel_2",
        "title": "Budget Inn Tokyo",
        "location": "Asakusa, Tokyo",
        "price": 80.0,
        "rating": 4.0,
        "reviews": 456,
        "amenities": ["WiFi", "Breakfast"],
        "free_cancellation": false,
        "link": "https://www.booking.com/..."
      }
    ]
  }'
```
Returns: Ranked hotels with scores, pros/cons analysis, and booking links

### Search Hotels (Google Hotels API)
```bash
curl -X GET "http://localhost:8001/api/v1/hotels/search?q=Tokyo&check_in_date=2025-12-01&check_out_date=2025-12-05&adults=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
Returns: Hotel listings from Google Hotels with prices, ratings, and property tokens

### Get Hotel Property Details
```bash
curl -X GET "http://localhost:8001/api/v1/hotels/property?property_token=abc123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
Returns: Detailed information for specific hotel including amenities, reviews, and policies

### Select Hotel for Trip
```bash
curl -X POST "http://localhost:8001/api/v1/hotels/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "trip_id": "your-trip-id",
    "hotel_id": "hotel_1",
    "hotel_name": "Tokyo Grand Hotel",
    "location": "Shinjuku, Tokyo",
    "price_per_night": 180.0,
    "total_price": 900.0,
    "currency": "USD",
    "check_in_date": "2025-12-01",
    "check_out_date": "2025-12-06",
    "rating": 4.5,
    "reviews_count": 1250,
    "hotel_class": 4,
    "amenities": ["WiFi", "Breakfast", "Gym", "Pool", "Restaurant"],
    "free_cancellation": true,
    "score": 0.92,
    "title": "Tokyo Grand Hotel - Comfortable Stay in Shinjuku",
    "pros_keywords": ["great location", "high rating", "free WiFi", "good breakfast"],
    "cons_keywords": ["higher price"],
    "thumbnail": "https://...",
    "link": "https://www.booking.com/..."
  }'
```
Returns: Success confirmation with hotel saved to trip

### Rank Entertainment Venues
```bash
curl -X POST "http://localhost:8001/api/v1/entertainment/rank" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "trip_id": "your-trip-id",
    "search_id": "tokyo_venue_search",
    "preferences_prompt": "Sushi restaurants with traditional atmosphere",
    "entertainment_tags": ["food", "traditional"],
    "venues": [
      {
        "place_id": "venue_1",
        "title": "Tsukiji Sushi",
        "rating": 4.7,
        "reviews": 500,
        "link": "https://maps.google.com/..."
      }
    ]
  }'
```

### Visa Check
```bash
curl "http://localhost:8001/visa/check?passport=KZ&destination=JP"
```

### Flight Link (Skyscanner Redirect)
```bash
curl -X POST "http://localhost:8001/flight/link" \
  -H "Content-Type: application/json" \
  -d '{
    "origin_city": "New York",
    "destination_city": "Tokyo",
    "outbound_date": "2025-12-01",
    "return_date": "2025-12-05",
    "adults": 2,
    "cabinclass": "economy"
  }'
```

### Search Flights (Google Flights API)
```bash
curl -X GET "http://localhost:8001/api/v1/flights/search?trip_id=your-trip-id&departure_id=JFK&arrival_id=NRT&outbound_date=2025-12-01&return_date=2025-12-05&adults=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
Returns: Flight options with prices, duration, stops, and Google Flights URL

### Rank Flights (AI-powered)
```bash
curl -X POST "http://localhost:8001/api/v1/flights/rank" \
  -H "Content-Type: application/json" \
  -d '{
    "search_id": "jfk_nrt_search",
    "preferences_prompt": "I prefer non-stop or max 1 stop, morning departure, good price-to-comfort ratio",
    "flights": [
      {
        "id": "flight_1",
        "price": {"amount": 850, "currency": "USD"},
        "total_duration_min": 660,
        "stops": 0,
        "legs": [{
          "dep_iata": "JFK",
          "dep_time": "2025-12-01T09:00:00",
          "arr_iata": "NRT",
          "arr_time": "2025-12-02T14:00:00",
          "marketing": "ANA",
          "flight_no": "NH111",
          "duration_min": 660
        }]
      }
    ]
  }'
```
Returns: Ranked flights with scores, pros/cons analysis, and AI rationale

### Select Flight for Trip
```bash
curl -X POST "http://localhost:8001/api/v1/flights/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "trip_id": "your-trip-id",
    "flight_id": "flight_1",
    "airline": "ANA",
    "flight_number": "NH111",
    "departure_airport": "JFK",
    "arrival_airport": "NRT",
    "departure_time": "2025-12-01T09:00:00",
    "arrival_time": "2025-12-02T14:00:00",
    "price": 850.00,
    "currency": "USD",
    "total_duration_min": 660,
    "stops": 0,
    "score": 0.95,
    "title": "Non-stop morning flight ANA NH111",
    "pros_keywords": ["non-stop", "morning", "direct"],
    "cons_keywords": []
  }'
```
Returns: Success confirmation with flight saved to trip

### Get Selected Flight for Trip
```bash
curl -X GET "http://localhost:8001/api/v1/flights/your-trip-id/selection" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
Returns: Previously selected flight for the trip

### Trip Summary & ICS Export
```bash
curl -X POST "http://localhost:8001/ai/plan/ics-file" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tokyo Trip",
    "timezone": "Asia/Tokyo",
    "start_date": "2025-12-01",
    "end_date": "2025-12-05",
    "destinations": ["Tokyo"]
  }'
```

## Authentication

**Register a user:**
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler123"}'
```

**Login:**
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler123"}'
```

Response includes `access_token` for authenticated endpoints.

## Flight Feature Workflow

### Complete Flight Journey: Search → Rank → Select → Book

**Step 1: Search Flights via Google Flights API**
```bash
curl -X GET "http://localhost:8001/api/v1/flights/search?trip_id=abc123&adults=2&outbound_date=2025-12-01" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Automatically maps city names to airport codes (e.g., "Tokyo" → "NRT")
- Returns available flights with prices, duration, stops, and Google Flights URL

**Step 2: Get AI-Ranked Flight Recommendations**
- Take the flight list from Step 1
- Call `/api/v1/flights/rank` with user preferences
- Receives ranked flights with scores and rationale
- If OpenAI unavailable, falls back to heuristic ranking

**Step 3: Select and Save Preferred Flight**
- User picks their favorite ranked flight
- POST to `/api/v1/flights/select` with flight details
- Flight is persisted to trip with full details (price, times, scoring)

**Step 4: Retrieve Anytime**
- GET `/api/v1/flights/{trip_id}/selection` to fetch saved flight
- Use Google Flights URL for direct booking link

### Airport Code Mapping
The system automatically maps 300+ cities to IATA codes including:
- USA: JFK, LAX, ORD, SFO, MIA, BOS, SEA, etc.
- Europe: LHR, CDG, FRA, AMS, ZRH, VIE, etc.
- Asia: NRT, KIX, PVG, HKG, BKK, SIN, DXB, etc.
- And many more worldwide destinations

---

## Hotel Feature Workflow

### Complete Hotel Journey: Search → Details → Rank → Select → Book

**Step 1: Search Hotels via Google Hotels API**
```bash
curl -X GET "http://localhost:8001/api/v1/hotels/search?q=Tokyo&check_in_date=2025-12-01&check_out_date=2025-12-05&adults=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Search by location, dates, and guest count
- Returns hotel listings with prices, ratings, amenities, and property tokens
- Includes cancellation policy and review information

**Step 2: Get Detailed Property Information (Optional)**
- Use property_token from search results
- Call `/api/v1/hotels/property` for complete hotel details
- Includes high-resolution images, full amenities list, guest reviews

**Step 3: Get AI-Ranked Hotel Recommendations**
- Take the hotel list from Step 1
- Call `/api/v1/hotels/rank` with user preferences (location preference, budget, amenities wanted)
- Receives ranked hotels with scores, pros/cons, and rationale
- If OpenAI unavailable, falls back to heuristic ranking

**Step 4: Select and Save Preferred Hotel**
- User picks their favorite ranked hotel
- POST to `/api/v1/hotels/select` with hotel details
- Hotel is persisted to trip with full information (price, amenities, dates, booking link)

**Step 5: Retrieve Anytime**
- Hotel information is stored with trip
- Available for trip summary and itinerary planning
- Booking link included for direct reservation

---

For comprehensive documentation, see:
- **[Project Documentation](DOCS/PROJECT_DOCUMENTATION.md)** — Full feature reference, technical implementation, monetization strategy, and developer guide
- **[Feature Reference](DOCS/PROJECT_DOCUMENTATION.md#feature-reference--how-each-feature-works-and-technical-implementation)** — Detailed breakdown of each feature with code references
- **[AI Companion Guide](DOCS/PROJECT_DOCUMENTATION.md#2-ai-companion--chat-and-voice-assistant)** — Chat and voice interaction patterns
- **[Monetization Strategy](DOCS/PROJECT_DOCUMENTATION.md#5-monetization--business-benefits-for-qic)** — How CTAs, insurance offers, and conversions work

## Configuration Notes

### API Keys & Services
1. **OpenAI**: Get key from [OpenAI Dashboard](https://platform.openai.com/api-keys)
2. **Google Maps**: Get key from [Google Cloud Console](https://console.cloud.google.com/)
3. **SerpApi**: Get key from [SerpApi Dashboard](https://serpapi.com/)
4. **RapidAPI**: Get visa API key from [RapidAPI Visa Service](https://rapidapi.com/)

### Environment Setup
- Keep all API keys in `.env` file
- Never commit `.env` to version control
- For production, use secure environment variable management (e.g., AWS Secrets Manager)

## Production Notes

- **Security**: All API keys must be kept server-side only
- **Rate Limits**: Implement retry logic for external API calls
- **Caching**: Cache visa results and culture guides to reduce model calls
- **Monitoring**: Track OpenAI usage, fallback rates, and error patterns
- **Error Handling**: 502 indicates upstream API issues; 500 indicates internal errors
- **Fallback System**: Hotel and entertainment ranking automatically falls back to heuristic when OpenAI is unavailable

## File Structure

```
QIC/
├── app.py                      # Main FastAPI app (legacy entry point)
├── requirements.txt            # Python dependencies
├── .env                        # API keys (keep private!)
├── DOCS/
│   └── PROJECT_DOCUMENTATION.md # Comprehensive project guide
├── app/                        # Main application package
│   ├── main.py                # FastAPI app initialization
│   ├── ai/                    # AI services (planning, ranking)
│   │   ├── planner.py        # Trip planning logic
│   │   └── ranker.py         # Ranking base logic
│   ├── api/                   # API routing
│   ├── auth/                  # Authentication & authorization
│   ├── trips/                 # Trip management
│   ├── flights/               # Flight ranking & selection
│   │   ├── ai_ranker.py      # OpenAI flight ranking with heuristic fallback
│   │   ├── router.py         # Flight endpoints (search, rank, select)
│   │   ├── schemas.py        # Flight data models
│   │   └── service.py        # Google Flights API integration via SerpApi
│   ├── hotels/                # Hotel search, ranking & selection
│   │   ├── ai_ranker.py      # OpenAI hotel ranking with heuristic fallback
│   │   ├── router.py         # Hotel endpoints (search, property details, rank, select)
│   │   ├── schemas.py        # Hotel data models (with link field)
│   │   └── service.py        # Google Hotels API integration via SerpApi
│   ├── entertainment/         # Entertainment/venue ranking
│   │   ├── ai_ranker.py      # OpenAI entertainment ranking (with link)
│   │   ├── router.py         # Entertainment endpoints
│   │   └── schemas.py        # Venue schemas (with link field)
│   ├── culture/               # Culture guide generation & retrieval
│   │   ├── router.py         # Culture guide endpoints
│   │   └── schemas.py        # Culture guide schemas
│   ├── core/                  # Core settings & utilities
│   ├── db/                    # Database models & migrations
│   │   └── models.py         # SQLAlchemy ORM models (CultureGuide, selected links)
│   └── __init__.py
├── frontendQIC/               # React/Vite frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # Context providers
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main app component
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   └── vite.config.ts
├── migrations/                # Database migration scripts
│   ├── migrate_hotel_link.py
│   └── migrate_culture_guide.py
└── tests/                     # Test files
    ├── test_entertainment_ranker_direct.py
    ├── test_hotel_ranking_link.py
    ├── test_entertainment_ranking_link.py
    └── ...
```

## Testing

Run all tests:
```bash
pytest -q
```

Run specific test file:
```bash
python test_entertainment_ranker_direct.py
```

Key test files:
- `test_entertainment_ranker_direct.py` — Tests entertainment ranking with link preservation (no auth required)
- `test_hotel_ranking_link.py` — Tests hotel ranking with link preservation
- Integration tests — Test full flows with authentication

## Contributing

1. Create a feature branch
2. Make changes (update tests if needed)
3. Run tests to ensure nothing breaks
4. Commit and push to GitHub
5. Create a pull request

## Roadmap

**Near-term (1-2 months):**
- Robust voice assistant (bi-directional voice, seamless STT/TTS)
- Personalization engine for better ranking
- Partner integrations for in-app booking and insurance

**Medium-term (3-6 months):**
- Mobile SDKs for QIC ecosystem integration
- AB testing framework for CTA placement
- Real-time collaborative trip planning

**Long-term (6+ months):**
- ML model for predicting user preferences
- Advanced social features (share plans, group voting)
- Live concierge service integration

## Support

For issues, questions, or feature requests, open an issue on GitHub or contact the team.

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Status**: Alpha (Active Development)