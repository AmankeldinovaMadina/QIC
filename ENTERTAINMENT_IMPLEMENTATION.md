# Entertainment Venues API - Implementation Guide

## Overview

The Entertainment Venues API enables users to search, rank, and select entertainment venues for their trips using Google Maps data and OpenAI-powered AI ranking. This is similar to the flights functionality but supports **multiple selections** per trip.

## Features

- 🗺️ **Google Maps Integration**: Fetch real entertainment venues via SerpAPI
- 🤖 **AI-Powered Ranking**: OpenAI ranks venues based on user preferences with pros/cons
- 🎯 **Multiple Selections**: Users can select multiple venues (10-15) per trip
- 📊 **Smart Recommendations**: Considers entertainment_tags, ratings, reviews, price, and descriptions
- 💾 **Persistent Storage**: Venues saved in database and trip JSON for AI planning

## Architecture

### Database Models

#### EntertainmentSelection Table
Stores individual venue selections with full details:

```python
class EntertainmentSelection(Base):
    __tablename__ = "entertainment_selections"
    
    id: UUID
    trip_id: UUID (FK to trips)
    venue_id: str (Google Maps place_id)
    venue_name: str
    venue_type: str (e.g., "Museum", "Restaurant")
    address: str
    rating: Decimal (0-5)
    reviews_count: int
    price_level: str ($, $$, $$$, $$$$)
    latitude/longitude: Decimal
    website: str
    phone: str
    opening_hours: JSON
    types: JSON (array of venue types)
    description: Text
    thumbnail: str (image URL)
    score: Decimal (AI-generated 0-1)
    title: str (AI-generated summary)
    pros_keywords: JSON (array)
    cons_keywords: JSON (array)
    created_at: DateTime
```

#### Trip.selected_entertainments
JSON array storing quick-access venue data for AI planning:

```json
[
  {
    "venue": {
      "place_id": "ChIJ...",
      "title": "Sensoji Temple",
      "type": "Buddhist temple",
      "rating": 4.5,
      "reviews": 50000,
      "address": "2-3-1 Asakusa, Tokyo"
    },
    "ranking": {
      "score": 0.95,
      "title": "Iconic cultural landmark",
      "pros_keywords": ["historic", "cultural", "photo-worthy"],
      "cons_keywords": ["crowded", "no-english-guide"]
    }
  }
]
```

## API Endpoints

### 1. Search Venues
**POST** `/api/v1/entertainment/search`

Fetches entertainment venues from Google Maps based on trip destination and entertainment_tags.

**Request:**
```json
{
  "trip_id": "uuid",
  "destination": "Tokyo",
  "query": "museums and cultural sites", // Optional, otherwise uses entertainment_tags
  "latitude": 35.6762,  // Optional for GPS search
  "longitude": 139.6503,
  "zoom": "14z"  // Map zoom level
}
```

**Response:**
```json
{
  "search_id": "uuid",
  "trip_id": "uuid",
  "query": "museums, art galleries, cultural centers in Tokyo",
  "destination": "Tokyo",
  "total_results": 20,
  "venues": [
    {
      "position": 1,
      "place_id": "ChIJ...",
      "title": "Tokyo National Museum",
      "rating": 4.6,
      "reviews": 12543,
      "price": "$$",
      "type": "Museum",
      "types": ["museum", "tourist_attraction"],
      "address": "13-9 Uenokoen, Taito City, Tokyo 110-8712",
      "gps_coordinates": {
        "latitude": 35.7188,
        "longitude": 139.7764
      },
      "phone": "+81 3-3822-1111",
      "website": "https://www.tnm.jp/",
      "description": "Japan's oldest and largest museum with vast collections",
      "open_state": "Open ⋅ Closes 5 PM",
      "operating_hours": {
        "monday": "9:30 AM–5 PM",
        "tuesday": "9:30 AM–5 PM",
        ...
      },
      "thumbnail": "https://..."
    }
  ]
}
```

### 2. Rank Venues with AI
**POST** `/api/v1/entertainment/rank`

Uses OpenAI to rank venues based on user preferences (entertainment_tags) with pros/cons analysis.

**Request:**
```json
{
  "trip_id": "uuid",
  "search_id": "uuid",
  "venues": [...],  // Array from search response
  "preferences_prompt": "Looking for authentic cultural experiences and great food",  // Optional
  "entertainment_tags": ["culture", "food", "museums"]  // Optional, uses trip's tags if not provided
}
```

**Response:**
```json
{
  "trip_id": "uuid",
  "search_id": "uuid",
  "ordered_place_ids": ["ChIJ...", "ChIJ..."],
  "items": [
    {
      "place_id": "ChIJ...",
      "score": 0.95,
      "title": "Must-visit cultural landmark with world-class exhibits",
      "rationale_short": "Highly rated museum with authentic Japanese art, perfect for culture enthusiasts. Excellent value with 12,500+ positive reviews.",
      "pros_keywords": ["authentic", "world-class", "cultural", "educational", "popular", "well-reviewed"],
      "cons_keywords": ["crowded", "reservation-required"],
      "tags": ["culture", "museum", "art"]
    }
  ],
  "meta": {
    "used_model": "gpt-4o-mini",
    "deterministic": false,
    "notes": []
  }
}
```

### 3. Select Multiple Venues
**POST** `/api/v1/entertainment/select`

Saves multiple selected venues to the trip (typically 5-10 venues).

**Request:**
```json
{
  "trip_id": "uuid",
  "selections": [
    {
      "venue": { /* full venue object from search */ },
      "ranking": { /* ranking data from AI */ }
    },
    {
      "venue": { /* another venue */ },
      "ranking": { /* another ranking */ }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully added 5 entertainment venues to trip",
  "trip_id": "uuid",
  "selected_count": 5,
  "selections": [
    {
      "id": "selection-uuid",
      "venue_name": "Tokyo National Museum",
      "venue_type": "Museum",
      "address": "13-9 Uenokoen, Taito City",
      "rating": 4.6,
      "price": "$$",
      "score": 0.95,
      "title": "Must-visit cultural landmark"
    }
  ]
}
```

### 4. Get Selections
**GET** `/api/v1/entertainment/{trip_id}/selections`

Retrieves all entertainment selections for a trip.

**Response:**
```json
{
  "trip_id": "uuid",
  "total_selections": 5,
  "selections": [
    {
      "id": "selection-uuid",
      "venue_id": "ChIJ...",
      "venue_name": "Tokyo National Museum",
      "venue_type": "Museum",
      "address": "13-9 Uenokoen, Taito City",
      "rating": 4.6,
      "reviews_count": 12543,
      "price_level": "$$",
      "latitude": 35.7188,
      "longitude": 139.7764,
      "website": "https://www.tnm.jp/",
      "phone": "+81 3-3822-1111",
      "types": ["museum", "tourist_attraction"],
      "description": "Japan's oldest and largest museum",
      "thumbnail": "https://...",
      "score": 0.95,
      "title": "Must-visit cultural landmark",
      "pros_keywords": ["authentic", "world-class", "cultural"],
      "cons_keywords": ["crowded", "reservation-required"],
      "created_at": "2024-11-03T12:00:00Z"
    }
  ]
}
```

## Google Maps Integration

### SerpAPI Configuration

The system uses SerpAPI to fetch Google Maps data. Add to `.env`:

```bash
SERPAPI_KEY=your_serpapi_key_here
```

### Query Building

The service automatically builds search queries from `entertainment_tags`:

| Tag | Google Maps Query |
|-----|-------------------|
| culture | museums, art galleries, cultural centers |
| food | restaurants, food markets, culinary experiences |
| nightlife | bars, clubs, night entertainment |
| sightseeing | landmarks, attractions, viewpoints |
| museums | museums, exhibitions, galleries |
| shopping | shopping centers, markets, boutiques |
| outdoor | parks, outdoor activities, nature |

### Search Parameters

- `engine`: google_maps
- `type`: search
- `q`: Generated query from tags
- `ll`: @latitude,longitude,zoom (optional)
- Location is geocoded automatically from destination name

## AI Ranking System

### OpenAI Model
Uses `gpt-4o-mini` with JSON schema structured outputs for guaranteed format.

### Ranking Criteria

1. **User Preferences**: Matches entertainment_tags (culture, food, etc.)
2. **Rating & Reviews**: Higher ratings (4.5+) and more reviews (500+) score better
3. **Price Level**: Considers budget_tier from trip (budget/mid/luxury)
4. **Venue Type**: Matches user interests
5. **Description Quality**: Unique experiences score higher

### Pros/Cons Keywords

**Common Pros:**
- authentic, cultural, popular, family-friendly
- scenic, interactive, educational, unique
- well-reviewed, affordable, accessible
- photo-worthy, historic, modern

**Common Cons:**
- crowded, expensive, reservation-required
- time-consuming, limited-english, tourist-trap
- seasonal, weather-dependent, remote

### Fallback Heuristic

If OpenAI fails, uses rating × √(reviews/1000) scoring:
- Prioritizes highly-rated venues (4.5+)
- Considers review volume (500+)
- Factors in price level
- Still generates basic pros/cons

## Integration with AI Trip Planner

### Context Building

Selected entertainment venues are passed to the AI planner in `_build_planning_context()`:

```python
# Added to planning context notes:
"""
Selected Entertainment Venues (user wants to visit these):
1. Tokyo National Museum (Museum) - 4.6★
   Address: 13-9 Uenokoen, Taito City
   Highlights: authentic, world-class, cultural, educational

2. Sensoji Temple (Buddhist temple) - 4.5★
   Address: 2-3-1 Asakusa, Taito City
   Highlights: historic, cultural, photo-worthy, spiritual
"""
```

### AI Planner Usage

The trip planner:
1. Receives list of user-selected venues
2. Integrates them into daily itinerary
3. Schedules around opening hours (if provided)
4. Considers location proximity (GPS coordinates)
5. Accounts for time requirements
6. Suggests optimal visit times
7. Recommends transport between venues

## Usage Example

### Complete Workflow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 1. Create trip with entertainment tags
trip = requests.post(f"{BASE_URL}/trips", json={
    "from_city": "San Francisco",
    "to_city": "Tokyo",
    "start_date": "2024-12-15T09:00:00Z",
    "end_date": "2024-12-21T18:00:00Z",
    "transport": "flight",
    "adults": 2,
    "entertainment_tags": ["culture", "food", "museums", "sightseeing"],
    "budget_max": 5000
}, headers=headers).json()

trip_id = trip["id"]

# 2. Search entertainment venues
search = requests.post(f"{BASE_URL}/entertainment/search", json={
    "trip_id": trip_id,
    "destination": "Tokyo"
}, headers=headers).json()

# 3. Rank venues with AI
ranking = requests.post(f"{BASE_URL}/entertainment/rank", json={
    "trip_id": trip_id,
    "search_id": search["search_id"],
    "venues": search["venues"],
    "preferences_prompt": "Looking for authentic experiences"
}, headers=headers).json()

# 4. Select top 5 venues
selections = []
for i in range(5):
    venue = next(v for v in search["venues"] if v["place_id"] == ranking["items"][i]["place_id"])
    selections.append({
        "venue": venue,
        "ranking": ranking["items"][i]
    })

result = requests.post(f"{BASE_URL}/entertainment/select", json={
    "trip_id": trip_id,
    "selections": selections
}, headers=headers).json()

print(f"Selected {result['selected_count']} venues")

# 5. Finalize trip (generates AI plan with entertainment venues)
finalize = requests.post(f"{BASE_URL}/trips/{trip_id}/finalize", 
    headers=headers).json()
```

### curl Examples

```bash
# Search venues
curl -X POST http://localhost:8000/api/v1/entertainment/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "uuid",
    "destination": "Tokyo"
  }'

# Rank venues
curl -X POST http://localhost:8000/api/v1/entertainment/rank \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "uuid",
    "search_id": "uuid",
    "venues": [...],
    "preferences_prompt": "Authentic cultural experiences"
  }'

# Select venues
curl -X POST http://localhost:8000/api/v1/entertainment/select \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "uuid",
    "selections": [...]
  }'

# Get selections
curl -X GET http://localhost:8000/api/v1/entertainment/{trip_id}/selections \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

Run the comprehensive test suite:

```bash
python test_entertainment_endpoints.py
```

Test coverage:
- ✓ User registration and trip creation
- ✓ Google Maps venue search
- ✓ AI venue ranking with pros/cons
- ✓ Multiple venue selection
- ✓ Retrieve selections
- ✓ Verify trip data contains selections

## Differences from Flights

| Feature | Flights | Entertainment |
|---------|---------|--------------|
| **Data Source** | Google Flights API | Google Maps API (SerpAPI) |
| **Selection Model** | Single selection | Multiple selections (5-15) |
| **Storage** | 15 columns in Trip table | EntertainmentSelection table + JSON |
| **AI Context** | Hard event (fixed time) | Flexible scheduling |
| **User Flow** | Search → Rank → Select ONE | Search → Rank → Select MANY |
| **Database** | Denormalized in Trip | Normalized + JSON cache |

## Benefits

1. **Flexibility**: Users can select 5-15 venues per trip
2. **Rich Data**: Full venue details (hours, location, photos, website)
3. **AI Integration**: Seamlessly integrated into trip planning
4. **Smart Ranking**: Personalized recommendations based on preferences
5. **Scalability**: Database normalized for efficiency
6. **User Experience**: Multiple selections in one request

## Future Enhancements

- [ ] Filter by opening hours (only show venues open during trip)
- [ ] Distance-based filtering (within X km of hotel)
- [ ] Category-based search (only museums, only restaurants)
- [ ] Booking integration (reserve tickets through API)
- [ ] Real-time availability checking
- [ ] User reviews and ratings integration
- [ ] Photo gallery for each venue
- [ ] Estimated visit duration
- [ ] Crowd level predictions
- [ ] Alternative suggestions if venue is closed

## Summary

The Entertainment Venues API provides a complete solution for discovering, ranking, and selecting multiple entertainment venues for trips. It combines Google Maps data with OpenAI intelligence to deliver personalized recommendations with detailed pros/cons analysis, seamlessly integrating with the AI trip planner for optimal itinerary generation.
