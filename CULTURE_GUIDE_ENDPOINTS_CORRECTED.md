# Culture Guide API - Corrected Endpoints

## ⚠️ IMPORTANT: Endpoint Paths Updated

The culture guide endpoints have been corrected to avoid double prefixes.

## New Endpoints

### 1. Generate/Get Culture Guide (POST)
```
POST /api/v1/culture/guide
```

**Request Body:**
```json
{
  "trip_id": "your-trip-id",
  "destination": "Tokyo, Japan",
  "language": "en"
}
```

**Response: 200 OK**
```json
{
  "destination": "Tokyo, Japan",
  "summary": "Brief cultural summary...",
  "tips": [...]
}
```

### 2. Retrieve Saved Culture Guide (GET)
```
GET /api/v1/culture/guide/{trip_id}
```

**Response: 200 OK**
```json
{
  "destination": "Tokyo, Japan",
  "summary": "Brief cultural summary...",
  "tips": [...]
}
```

## Example Usage

### Using curl:

```bash
# Generate culture guide
curl -X POST http://localhost:8001/api/v1/culture/guide \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "abc123",
    "destination": "Paris, France",
    "language": "en"
  }'

# Retrieve saved guide
curl http://localhost:8001/api/v1/culture/guide/abc123
```

### Using Python:

```python
import requests

BASE_URL = "http://localhost:8001"

# Generate
response = requests.post(
    f"{BASE_URL}/api/v1/culture/guide",
    json={
        "trip_id": "abc123",
        "destination": "Tokyo, Japan",
        "language": "en"
    }
)

# Retrieve
response = requests.get(f"{BASE_URL}/api/v1/culture/guide/abc123")
```

### Using JavaScript:

```javascript
// Generate
const response = await fetch('http://localhost:8001/api/v1/culture/guide', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    trip_id: 'abc123',
    destination: 'Tokyo, Japan',
    language: 'en'
  })
});

// Retrieve
const saved = await fetch('http://localhost:8001/api/v1/culture/guide/abc123');
```

## Testing

Run the test script:
```bash
python test_culture_guide_endpoints.py
```

Or test manually:
```bash
# Make sure server is running
python -m app.main

# In another terminal, run tests
python test_culture_guide_endpoints.py
```

## What Changed

- **OLD**: `POST /api/v1/culture-guide`
- **NEW**: `POST /api/v1/culture/guide`

- **OLD**: `GET /api/v1/culture-guide/{trip_id}`
- **NEW**: `GET /api/v1/culture/guide/{trip_id}`

The change was made because the router was incorrectly configured with a double prefix `/api/v1/api/v1`, which has now been fixed to just `/api/v1/culture`.
