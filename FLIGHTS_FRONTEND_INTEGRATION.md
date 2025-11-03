# Flights Frontend Integration Guide

## Overview
This guide provides a complete workflow for integrating flight search, ranking, and selection into your frontend application.

## Architecture Overview

```
Frontend → Backend /flights/search → SerpAPI Google Flights
              ↓
    Backend /flights/rank → OpenAI AI Ranking
              ↓
         Pros/Cons Analysis
              ↓
    Backend /flights/select → Trip Storage
```

## Complete Workflow

### Step 1: User Creates a Trip
**Endpoint:** `POST /api/v1/trips`

```json
{
  "from_city": "New York",
  "to_city": "Tokyo",
  "start_date": "2025-06-01",
  "end_date": "2025-06-10",
  "transport": "flight",
  "adults": 2,
  "children": 0,
  "budget_min": 1000,
  "budget_max": 5000,
  "entertainment_tags": ["culture", "food"],
  "notes": "Prefer direct flights"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "from_city": "New York",
  "to_city": "Tokyo",
  "start_date": "2025-06-01",
  "end_date": "2025-06-10",
  "transport": "flight",
  "adults": 2,
  "children": 0,
  "budget_min": 1000,
  "budget_max": 5000,
  "status": "draft",
  "selected_flight": null,
  "selected_hotel": null,
  "selected_entertainments": []
}
```

---

### Step 2: Search for Flights (Backend API)
**Endpoint:** `GET /api/v1/flights/search`

**Purpose:** Search for flights using the backend (which calls SerpAPI Google Flights)

**Query Parameters:**
- `trip_id` (required): The trip ID to search flights for
- `departure_id` (optional): IATA airport code (e.g., "JFK")
- `arrival_id` (optional): IATA airport code (e.g., "NRT")
- `outbound_date` (optional): Departure date in YYYY-MM-DD format
- `return_date` (optional): Return date in YYYY-MM-DD format
- `adults` (optional): Number of adults (1-20)
- `children` (optional): Number of children (0-20)
- `currency` (optional): Currency code (default: "USD")
- `hl` (optional): Language code (default: "en")

**Note:** All parameters except `trip_id` are optional. If not provided, the backend will:
- Use the trip's `start_date` and `end_date`
- Use the trip's `adults` and `children` count
- Auto-map city names to airport codes (e.g., "New York" → "JFK", "Tokyo" → "NRT")

**Minimal Request (using trip data):**
```
GET /api/v1/flights/search?trip_id=550e8400-e29b-41d4-a716-446655440000
```

**Full Request with custom parameters:**
```
GET /api/v1/flights/search?trip_id=550e8400-e29b-41d4-a716-446655440000&departure_id=JFK&arrival_id=NRT&outbound_date=2025-06-01&return_date=2025-06-10&adults=2&children=0&currency=USD&hl=en
```

**Response:**
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "search_id": "abc-123-def-456",
  "flights": [
    {
      "id": "flight-uuid-123",
      "price": {
        "amount": 1200,
        "currency": "USD"
      },
      "total_duration_min": 780,
      "stops": 0,
      "emissions_kg": 1500,
      "layovers_min": null,
      "legs": [
        {
          "dep_iata": "JFK",
          "dep_time": "2025-06-01T10:00:00",
          "arr_iata": "NRT",
          "arr_time": "2025-06-02T14:00:00",
          "marketing": "American Airlines",
          "flight_no": "AA154",
          "duration_min": 780
        }
      ]
    },
    {
      "id": "flight-uuid-456",
      "price": {
        "amount": 950,
        "currency": "USD"
      },
      "total_duration_min": 900,
      "stops": 1,
      "emissions_kg": 1300,
      "layovers_min": 120,
      "legs": [
        {
          "dep_iata": "JFK",
          "dep_time": "2025-06-01T08:00:00",
          "arr_iata": "LAX",
          "arr_time": "2025-06-01T11:00:00",
          "marketing": "Delta",
          "flight_no": "DL123",
          "duration_min": 360
        },
        {
          "dep_iata": "LAX",
          "dep_time": "2025-06-01T13:00:00",
          "arr_iata": "NRT",
          "arr_time": "2025-06-02T17:00:00",
          "marketing": "Delta",
          "flight_no": "DL456",
          "duration_min": 540
        }
      ]
    }
  ],
  "search_params": {
    "departure_id": "JFK",
    "arrival_id": "NRT",
    "outbound_date": "2025-06-01",
    "return_date": "2025-06-10",
    "adults": 2,
    "children": 0,
    "currency": "USD"
  },
  "total_results": 15
}
```

**Frontend Example:**
```javascript
const searchFlights = async (tripId) => {
  const response = await fetch(
    `http://localhost:8001/api/v1/flights/search?trip_id=${tripId}`, 
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  const data = await response.json();
  return data;
};

// Or with custom parameters
const searchFlightsCustom = async (tripId, customParams) => {
  const params = new URLSearchParams({
    trip_id: tripId,
    ...customParams  // e.g., { departure_id: "LAX", arrival_id: "SFO" }
  });
  
  const response = await fetch(
    `http://localhost:8001/api/v1/flights/search?${params}`, 
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  return await response.json();
};
```

---

### Step 3: Rank Flights with AI
**Endpoint:** `POST /api/v1/flights/rank`

**Purpose:** Send flights to backend for AI-powered ranking based on user preferences

**Request:**
```json
{
  "search_id": "search-uuid-123",
  "flights": [
    {
      "id": "flight-123",
      "price": {
        "amount": 1200,
        "currency": "USD"
      },
      "total_duration_min": 780,
      "stops": 0,
      "emissions_kg": 1500,
      "layovers_min": 0,
      "legs": [
        {
          "dep_iata": "JFK",
          "dep_time": "2025-06-01T10:00:00Z",
          "arr_iata": "NRT",
          "arr_time": "2025-06-02T14:00:00Z",
          "marketing": "American Airlines",
          "flight_no": "AA154",
          "duration_min": 780
        }
      ]
    },
    {
      "id": "flight-456",
      "price": {
        "amount": 950,
        "currency": "USD"
      },
      "total_duration_min": 900,
      "stops": 1,
      "emissions_kg": 1300,
      "layovers_min": 120,
      "legs": [
        {
          "dep_iata": "JFK",
          "dep_time": "2025-06-01T08:00:00Z",
          "arr_iata": "LAX",
          "arr_time": "2025-06-01T11:00:00Z",
          "marketing": "Delta",
          "flight_no": "DL123",
          "duration_min": 360
        },
        {
          "dep_iata": "LAX",
          "dep_time": "2025-06-01T13:00:00Z",
          "arr_iata": "NRT",
          "arr_time": "2025-06-02T17:00:00Z",
          "marketing": "Delta",
          "flight_no": "DL456",
          "duration_min": 540
        }
      ]
    }
  ],
  "preferences_prompt": "I prefer direct flights, comfortable seating, and morning departures. Price is less important than convenience.",
  "locale": {
    "hl": "en",
    "currency": "USD",
    "tz": "America/New_York"
  }
}
```

**Response:**
```json
{
  "search_id": "search-uuid-123",
  "ordered_ids": ["flight-123", "flight-456", "flight-789"],
  "items": [
    {
      "id": "flight-123",
      "score": 0.95,
      "title": "Direct flight, morning departure - Best for convenience",
      "rationale_short": "Perfect match for your preference: direct flight with morning departure, minimal layover time, excellent for business travelers.",
      "pros_keywords": ["direct", "morning", "fast", "convenient"],
      "cons_keywords": ["pricey"],
      "tags": ["recommended", "fastest"]
    },
    {
      "id": "flight-456",
      "score": 0.72,
      "title": "Budget-friendly option with short layover",
      "rationale_short": "Good value with reasonable layover. Departs early morning, arrives evening. Budget-conscious choice.",
      "pros_keywords": ["affordable", "short-layover", "reliable"],
      "cons_keywords": ["one-stop", "longer-duration"],
      "tags": ["budget"]
    }
  ],
  "meta": {
    "used_model": "gpt-4o-mini",
    "deterministic": true,
    "notes": ["Ranked 15 flights", "Considered user preference for direct flights"]
  }
}
```

**Frontend Example:**
```javascript
const rankFlights = async (flights, userPreferences, tripNotes) => {
  const response = await fetch('http://localhost:8001/flights/rank', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      search_id: generateUUID(),
      flights: flights,
      preferences_prompt: `${userPreferences}. ${tripNotes}`,
      locale: {
        hl: navigator.language.split('-')[0],
        currency: 'USD',
        tz: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    })
  });
  
  return await response.json();
};
```

---

### Step 4: Display Ranked Flights to User
**Frontend UI Example:**

```jsx
const FlightList = ({ rankedFlights, originalFlights }) => {
  // Merge ranking data with original flight data
  const enrichedFlights = rankedFlights.ordered_ids.map(id => {
    const flight = originalFlights.find(f => f.id === id);
    const ranking = rankedFlights.items.find(i => i.id === id);
    return { ...flight, ...ranking };
  });

  return (
    <div className="flight-list">
      {enrichedFlights.map((flight) => (
        <FlightCard key={flight.id} flight={flight}>
          <div className="ai-badge">
            <span>AI Score: {(flight.score * 100).toFixed(0)}%</span>
          </div>
          <div className="flight-info">
            <h3>{flight.title}</h3>
            <p className="rationale">{flight.rationale_short}</p>
            <div className="pros-cons">
              <div className="pros">
                {flight.pros_keywords.map(pro => (
                  <span className="badge green">{pro}</span>
                ))}
              </div>
              <div className="cons">
                {flight.cons_keywords.map(con => (
                  <span className="badge red">{con}</span>
                ))}
              </div>
            </div>
            <div className="flight-details">
              <span>{flight.legs[0].marketing} {flight.legs[0].flight_no}</span>
              <span>{flight.legs[0].dep_iata} → {flight.legs[flight.legs.length-1].arr_iata}</span>
              <span>{formatDuration(flight.total_duration_min)}</span>
              <span>${flight.price.amount}</span>
              <span>{flight.stops} stops</span>
            </div>
          </div>
          <button onClick={() => selectFlight(flight)}>
            Select This Flight
          </button>
        </FlightCard>
      ))}
    </div>
  );
};
```

---

### Step 5: User Selects a Flight
**Endpoint:** `POST /flights/select`

**Purpose:** Save the user's selected flight to their trip

**Request:**
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "flight_id": "flight-123",
  "airline": "American Airlines",
  "flight_number": "AA154",
  "departure_airport": "JFK",
  "arrival_airport": "NRT",
  "departure_time": "2025-06-01T10:00:00Z",
  "arrival_time": "2025-06-02T14:00:00Z",
  "price": 1200,
  "currency": "USD",
  "total_duration_min": 780,
  "stops": 0,
  "score": 0.95,
  "title": "Direct flight, morning departure - Best for convenience",
  "pros_keywords": ["direct", "morning", "fast", "convenient"],
  "cons_keywords": ["pricey"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Flight American Airlines AA154 successfully added to trip",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "flight": {
    "airline": "American Airlines",
    "flight_number": "AA154",
    "route": "JFK → NRT",
    "price": "$1200 USD",
    "departure": "2025-06-01T10:00:00Z"
  }
}
```

**Frontend Example:**
```javascript
const selectFlight = async (tripId, flight, ranking) => {
  const response = await fetch('http://localhost:8001/flights/select', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      trip_id: tripId,
      flight_id: flight.id,
      airline: flight.legs[0].marketing,
      flight_number: flight.legs[0].flight_no,
      departure_airport: flight.legs[0].dep_iata,
      arrival_airport: flight.legs[flight.legs.length - 1].arr_iata,
      departure_time: flight.legs[0].dep_time,
      arrival_time: flight.legs[flight.legs.length - 1].arr_time,
      price: flight.price.amount,
      currency: flight.price.currency,
      total_duration_min: flight.total_duration_min,
      stops: flight.stops,
      score: ranking.score,
      title: ranking.title,
      pros_keywords: ranking.pros_keywords,
      cons_keywords: ranking.cons_keywords
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Navigate to next step (hotel selection)
    router.push(`/trips/${tripId}/hotels`);
  }
};
```

---

### Step 6: Retrieve Selected Flight ⭐ NEW ENDPOINT
**Endpoint:** `GET /flights/{trip_id}/selection`

**Purpose:** Get the currently selected flight for a trip

**Response:**
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_flight": {
    "flight_id": "flight-123",
    "airline": "American Airlines",
    "flight_number": "AA154",
    "departure_airport": "JFK",
    "arrival_airport": "NRT",
    "departure_time": "2025-06-01T10:00:00Z",
    "arrival_time": "2025-06-02T14:00:00Z",
    "price": 1200,
    "currency": "USD",
    "total_duration_min": 780,
    "stops": 0,
    "score": 0.95,
    "title": "Direct flight, morning departure - Best for convenience",
    "pros_keywords": ["direct", "morning", "fast", "convenient"],
    "cons_keywords": ["pricey"]
  }
}
```

**Alternative:** Use existing `GET /trips/{trip_id}` which already includes `selected_flight`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "from_city": "New York",
  "to_city": "Tokyo",
  "start_date": "2025-06-01",
  "end_date": "2025-06-10",
  "status": "draft",
  "selected_flight": {
    "flight_id": "flight-123",
    "airline": "American Airlines",
    "flight_number": "AA154",
    // ... full flight details
  },
  "selected_hotel": null,
  "selected_entertainments": []
}
```

---

## Complete Frontend Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CREATE TRIP                                              │
│    POST /api/v1/trips                                       │
│    → Returns trip_id                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SEARCH FLIGHTS (Backend API → SerpAPI)                  │
│    POST /api/v1/flights/search                             │
│    → Send trip_id (backend auto-fills from trip)           │
│    → Backend calls SerpAPI Google Flights                  │
│    → Returns 15-20 flight options                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. RANK FLIGHTS                                             │
│    POST /api/v1/flights/rank                               │
│    → Send flights + user preferences                        │
│    → Backend uses OpenAI to rank and analyze               │
│    → Returns ordered list with pros/cons                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DISPLAY RESULTS                                          │
│    → Show flights ordered by AI score                       │
│    → Display pros/cons badges                               │
│    → Show AI reasoning (title, rationale_short)            │
│    → User clicks "Select Flight"                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. SELECT FLIGHT                                            │
│    POST /api/v1/flights/select                             │
│    → Saves flight details to trip                          │
│    → Returns success message                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. VIEW/EDIT SELECTION                                      │
│    GET /api/v1/trips/{trip_id}                             │
│    → Returns trip with selected_flight                      │
│    → User can change selection (repeat from step 2)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend State Management Example

```javascript
// Redux/Zustand store example
const tripStore = {
  currentTrip: null,
  flightSearch: {
    loading: false,
    results: [],
    ranked: null,
    selected: null
  },
  
  actions: {
    // Step 1: Create trip
    async createTrip(tripData) {
      const response = await api.post('/api/v1/trips', tripData);
      this.currentTrip = response.data;
      return response.data.id;
    },
    
    // Step 2: Search flights (backend API)
    async searchFlights() {
      this.flightSearch.loading = true;
      const params = new URLSearchParams({ trip_id: this.currentTrip.id });
      const response = await api.get(`/api/v1/flights/search?${params}`);
      this.flightSearch.results = response.data.flights;
      this.flightSearch.loading = false;
      return response.data;
    },
    
    // Step 3: Rank flights with AI
    async rankFlights(preferences) {
      const ranked = await api.post('/api/v1/flights/rank', {
        search_id: generateUUID(),
        flights: this.flightSearch.results,
        preferences_prompt: preferences,
        locale: { hl: 'en', currency: 'USD' }
      });
      this.flightSearch.ranked = ranked.data;
    },
    
    // Step 4: Select flight
    async selectFlight(flight, ranking) {
      const response = await api.post('/api/v1/flights/select', {
        trip_id: this.currentTrip.id,
        flight_id: flight.id,
        airline: flight.legs[0].marketing,
        flight_number: flight.legs[0].flight_no,
        // ... other fields
        score: ranking.score,
        title: ranking.title,
        pros_keywords: ranking.pros_keywords,
        cons_keywords: ranking.cons_keywords
      });
      
      if (response.data.success) {
        this.flightSearch.selected = flight;
        // Refresh trip data
        await this.loadTrip(this.currentTrip.id);
      }
    },
    
    // Step 5: Load trip with selections
    async loadTrip(tripId) {
      const response = await api.get(`/api/v1/trips/${tripId}`);
      this.currentTrip = response.data;
      this.flightSearch.selected = response.data.selected_flight;
    }
  }
};
```

---

## Error Handling

```javascript
const handleFlightSelection = async (tripId, flight, ranking) => {
  try {
    const response = await fetch('http://localhost:8001/api/v1/flights/select', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ /* ... */ })
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      switch (response.status) {
        case 404:
          showError('Trip not found. Please refresh and try again.');
          break;
        case 401:
          showError('Please log in to continue.');
          router.push('/login');
          break;
        case 500:
          showError('Server error. Please try again later.');
          break;
        default:
          showError(error.detail || 'Failed to select flight');
      }
      return;
    }
    
    const result = await response.json();
    showSuccess(result.message);
    router.push(`/trips/${tripId}/hotels`);
    
  } catch (error) {
    console.error('Flight selection error:', error);
    showError('Network error. Please check your connection.');
  }
};
```

---

## UI/UX Best Practices

### 1. **Loading States**
```jsx
{isSearching && <Spinner message="Finding flights..." />}
{isRanking && <Spinner message="AI is analyzing flights..." />}
{isSelecting && <Spinner message="Saving your selection..." />}
```

### 2. **AI Transparency**
Show users why the AI ranked flights in a certain order:
```jsx
<div className="ai-explanation">
  <InfoIcon />
  <p>Our AI analyzed {totalFlights} flights based on your preferences:
     "{userPreferences}". Flights are ranked by convenience, price, 
     and alignment with your needs.</p>
</div>
```

### 3. **Comparison View**
Allow users to compare top 3 flights side-by-side:
```jsx
<ComparisonTable>
  <Column flight={rankedFlights[0]} badge="Best Match" />
  <Column flight={rankedFlights[1]} badge="Budget" />
  <Column flight={rankedFlights[2]} badge="Fastest" />
</ComparisonTable>
```

### 4. **Editing Selections**
```jsx
{selectedFlight && (
  <SelectedFlightCard flight={selectedFlight}>
    <button onClick={changeSelection}>
      Change Flight Selection
    </button>
  </SelectedFlightCard>
)}
```

---

## API Authentication

All endpoints (except `/rank` in current implementation) require authentication:

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${accessToken}`
};
```

Get access token from login:
```javascript
const login = async (username) => {
  const response = await fetch('http://localhost:8001/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  });
  
  const data = await response.json();
  localStorage.setItem('accessToken', data.access_token);
  return data.access_token;
};
```

---

## Complete React Component Example

```jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const FlightSelection = () => {
  const { tripId } = useParams();
  const navigate = useNavigate();
  
  const [trip, setTrip] = useState(null);
  const [flights, setFlights] = useState([]);
  const [rankedFlights, setRankedFlights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFlight, setSelectedFlight] = useState(null);

  // Load trip details
  useEffect(() => {
    fetchTrip();
  }, [tripId]);

  const fetchTrip = async () => {
    const response = await fetch(`http://localhost:8001/trips/${tripId}`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    const data = await response.json();
    setTrip(data);
    setSelectedFlight(data.selected_flight);
  };

  // Step 1: Search flights via backend API
  const searchFlights = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ trip_id: tripId });
      const response = await fetch(
        `http://localhost:8001/api/v1/flights/search?${params}`, 
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${getToken()}`
          }
        }
      );
      
      const data = await response.json();
      setFlights(data.flights);
      
      // Automatically rank after search
      await rankFlights(data.flights, data.search_id);
    } catch (error) {
      console.error('Flight search error:', error);
      alert('Failed to search flights');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Rank flights with AI
  const rankFlights = async (flightList, searchId) {  // Step 2: Rank flights with AI
  const rankFlights = async (flightList) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/flights/rank', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_id: `search-${Date.now()}`,
          flights: flightList.map(f => ({
            id: f.id || `flight-${f.flights[0]?.flight_number}`,
            price: { amount: f.price, currency: 'USD' },
            total_duration_min: f.total_duration,
            stops: f.flights.length - 1,
            legs: f.flights.map(leg => ({
              dep_iata: leg.departure_airport.id,
              dep_time: leg.departure_airport.time,
              arr_iata: leg.arrival_airport.id,
              arr_time: leg.arrival_airport.time,
              marketing: leg.airline,
              flight_no: leg.flight_number,
              duration_min: leg.duration
            }))
          })),
          preferences_prompt: trip.notes || 'Find the best flight option',
          locale: { hl: 'en', currency: 'USD' }
        })
      });
      
      const ranked = await response.json();
      setRankedFlights(ranked);
    } catch (error) {
      console.error('Flight ranking error:', error);
      alert('Failed to rank flights');
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Select a flight
  const selectFlight = async (flight, ranking) => {
    setLoading(true);
    try {
      const firstLeg = flight.legs[0];
      const lastLeg = flight.legs[flight.legs.length - 1];
      
      const response = await fetch('http://localhost:8001/flights/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
          trip_id: tripId,
          flight_id: flight.id,
          airline: firstLeg.marketing,
          flight_number: firstLeg.flight_no,
          departure_airport: firstLeg.dep_iata,
          arrival_airport: lastLeg.arr_iata,
          departure_time: firstLeg.dep_time,
          arrival_time: lastLeg.arr_time,
          price: flight.price.amount,
          currency: flight.price.currency,
          total_duration_min: flight.total_duration_min,
          stops: flight.stops,
          score: ranking.score,
          title: ranking.title,
          pros_keywords: ranking.pros_keywords,
          cons_keywords: ranking.cons_keywords
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(result.message);
        navigate(`/trips/${tripId}/hotels`); // Next step: hotel selection
      }
    } catch (error) {
      console.error('Flight selection error:', error);
      alert('Failed to select flight');
    } finally {
      setLoading(false);
    }
  };

  // Render
  return (
    <div className="flight-selection">
      <h1>Select Flight for {trip?.from_city} → {trip?.to_city}</h1>
      
      {selectedFlight && (
        <div className="selected-flight-banner">
          <h3>✓ Flight Selected</h3>
          <p>{selectedFlight.airline} {selectedFlight.flight_number}</p>
          <button onClick={() => setSelectedFlight(null)}>Change Selection</button>
        </div>
      )}
      
      <button onClick={searchFlights} disabled={loading}>
        {loading ? 'Searching...' : 'Search Flights'}
      </button>
      
      {rankedFlights && (
        <div className="flights-list">
          <p className="ai-note">
            🤖 AI analyzed {flights.length} flights based on your preferences
          </p>
          
          {rankedFlights.ordered_ids.map((id, index) => {
            const flight = flights.find(f => f.id === id);
            const ranking = rankedFlights.items.find(i => i.id === id);
            
            return (
              <div key={id} className="flight-card">
                <div className="rank-badge">#{index + 1}</div>
                <div className="ai-score">
                  AI Score: {(ranking.score * 100).toFixed(0)}%
                </div>
                
                <h3>{ranking.title}</h3>
                <p className="rationale">{ranking.rationale_short}</p>
                
                <div className="badges">
                  <div className="pros">
                    {ranking.pros_keywords.map(pro => (
                      <span key={pro} className="badge green">✓ {pro}</span>
                    ))}
                  </div>
                  <div className="cons">
                    {ranking.cons_keywords.map(con => (
                      <span key={con} className="badge red">✗ {con}</span>
                    ))}
                  </div>
                </div>
                
                <div className="flight-details">
                  <span>{flight.legs[0].marketing} {flight.legs[0].flight_no}</span>
                  <span>{flight.legs[0].dep_iata} → {flight.legs[flight.legs.length-1].arr_iata}</span>
                  <span>{formatDuration(flight.total_duration_min)}</span>
                  <span>${flight.price.amount}</span>
                  <span>{flight.stops === 0 ? 'Direct' : `${flight.stops} stop(s)`}</span>
                </div>
                
                <button 
                  onClick={() => selectFlight(flight, ranking)}
                  disabled={loading}
                  className="select-button"
                >
                  Select This Flight
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Helper functions
const getToken = () => localStorage.getItem('accessToken');

const getCityCode = (city) => {
  const codes = {
    'New York': 'JFK',
    'Tokyo': 'NRT',
    'London': 'LHR',
    // ... add more mappings
  };
  return codes[city] || city;
};

const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

export default FlightSelection;
```

---

## Summary

### Key Points:
1. **Flight Search**: Backend GET endpoint `/api/v1/flights/search` calls SerpAPI
2. **AI Ranking**: Backend endpoint `/flights/rank` analyzes flights
3. **Selection**: Backend endpoint `/flights/select` saves to trip
4. **Retrieval**: Use `/trips/{trip_id}` to get trip with selected flight
5. **Single Selection**: User can only select ONE flight per trip (unlike entertainments)

### Endpoint Summary:
- ✅ `POST /api/v1/trips` - Create trip
- ✅ `GET /api/v1/flights/search` - Search flights (⭐ GET request - RESTful!)
- ✅ `POST /api/v1/flights/rank` - AI rank flights (no auth required)
- ✅ `POST /api/v1/flights/select` - Save selected flight (auth required)
- ✅ `GET /api/v1/trips/{trip_id}` - Get trip with selected flight (auth required)
- ⭐ **NEW:** `GET /api/v1/flights/{trip_id}/selection` - Get only flight selection

### Next Steps:
Would you like me to:
1. Add the GET endpoint for retrieving just the flight selection?
2. Create a similar integration guide for hotels?
3. Add frontend validation examples?
4. Create TypeScript types for all these interfaces?
