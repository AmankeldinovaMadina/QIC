# Culture Guide API - Quick Reference

## Endpoints

### 1. Generate/Get Culture Guide (POST)
**Generates a new culture guide or returns cached version if exists**

```bash
POST /api/v1/culture-guide
Content-Type: application/json

{
  "trip_id": "string",
  "destination": "string",
  "language": "en"
}
```

**Response: 200 OK**
```json
{
  "destination": "Tokyo, Japan",
  "summary": "Japan values respect, harmony, and politeness...",
  "tips": [
    {
      "category": "greeting_etiquette",
      "title": "Bow When Greeting",
      "tip": "Bowing is the traditional form of greeting...",
      "do": "Bow slightly when meeting someone...",
      "avoid": "Avoid overly casual handshakes...",
      "emoji": "🙇"
    }
  ]
}
```

**Errors:**
- `404`: Trip not found
- `502`: OpenAI API error

---

### 2. Retrieve Saved Culture Guide (GET)
**Fetches a previously generated culture guide**

```bash
GET /api/v1/culture-guide/{trip_id}
```

**Response: 200 OK**
```json
{
  "destination": "Tokyo, Japan",
  "summary": "Japan values respect, harmony, and politeness...",
  "tips": [...]
}
```

**Errors:**
- `404`: Culture guide not found for this trip

---

## Example Usage

### Using curl:

```bash
# 1. Generate culture guide for a trip
curl -X POST http://localhost:8000/api/v1/culture-guide \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "abc123",
    "destination": "Tokyo, Japan",
    "language": "en"
  }'

# 2. Retrieve saved culture guide
curl http://localhost:8000/api/v1/culture-guide/abc123
```

### Using Python requests:

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate culture guide
response = requests.post(
    f"{BASE_URL}/api/v1/culture-guide",
    json={
        "trip_id": "abc123",
        "destination": "Tokyo, Japan",
        "language": "en"
    }
)
guide = response.json()

# Retrieve saved guide
response = requests.get(f"{BASE_URL}/api/v1/culture-guide/abc123")
saved_guide = response.json()
```

### Using JavaScript fetch:

```javascript
// Generate culture guide
const response = await fetch('http://localhost:8000/api/v1/culture-guide', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    trip_id: 'abc123',
    destination: 'Tokyo, Japan',
    language: 'en'
  })
});
const guide = await response.json();

// Retrieve saved guide
const savedResponse = await fetch('http://localhost:8000/api/v1/culture-guide/abc123');
const savedGuide = await savedResponse.json();
```

---

## Tip Categories

The `category` field in tips can be one of:

- `greeting_etiquette` - How to greet people
- `dress_code` - Appropriate clothing
- `behavioral_norms` - Expected behaviors
- `taboos` - Things to avoid
- `dining_etiquette` - Table manners and food customs
- `tipping` - Tipping practices
- `religion_holidays` - Religious customs and holidays
- `transport_customs` - Transportation etiquette

---

## Workflow

```
┌─────────────────┐
│  Create Trip    │
└────────┬────────┘
         │ trip_id
         ▼
┌─────────────────────────┐
│ POST /culture-guide     │
│ (with trip_id)          │
└────────┬────────────────┘
         │
         ├─── First time → Generate & Save
         │                  (OpenAI API call)
         │
         └─── Already exists → Return cached
                               (No API call)
         │
         ▼
┌─────────────────────────┐
│  Culture Guide Response │
└─────────────────────────┘

Later...

┌─────────────────────────┐
│ GET /culture-guide/id   │
│ (retrieve saved)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Culture Guide Response │
└─────────────────────────┘
```

---

## Notes

1. **Caching**: Once generated, the guide is cached. Calling POST again with the same `trip_id` returns the cached version.

2. **Performance**: GET endpoint is much faster than POST (no AI generation).

3. **Trip Validation**: POST endpoint validates that the trip exists before generating.

4. **One Guide Per Trip**: Each trip can have only one culture guide (enforced by unique constraint on `trip_id`).
