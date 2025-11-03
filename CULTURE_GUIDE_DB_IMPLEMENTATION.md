# Culture Guide Implementation

## Overview
The culture guide feature has been enhanced to save generated guides to the database with `trip_id` for future retrieval.

## Changes Made

### 1. Database Model (`app/db/models.py`)
Added a new `CultureGuide` model to store culture guides:

```python
class CultureGuide(Base):
    __tablename__ = "culture_guides"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False, unique=True, index=True)
    destination = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    tips_json = Column(JSON, nullable=False)  # Store the array of tips as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Key Features:**
- `trip_id` is a foreign key to the `trips` table
- `trip_id` has a unique constraint - one culture guide per trip
- `tips_json` stores the array of tips as JSON
- Timestamps for tracking creation and updates

### 2. Updated Culture Router (`app/culture/router.py`)

#### POST `/api/v1/culture-guide`
**Changes:**
- Now requires `trip_id` in the request body
- Validates that the trip exists before generating
- Checks if a culture guide already exists for the trip
  - If exists: returns the cached version (no OpenAI call)
  - If not: generates new guide and saves to database
- Returns the same response format as before

**Request Body:**
```json
{
  "trip_id": "string",
  "destination": "string",
  "language": "en"
}
```

**Response:**
```json
{
  "destination": "string",
  "summary": "string",
  "tips": [
    {
      "category": "greeting_etiquette",
      "title": "string",
      "tip": "string",
      "do": "string",
      "avoid": "string",
      "emoji": "string"
    }
  ]
}
```

#### GET `/api/v1/culture-guide/{trip_id}`
**New Endpoint** for retrieving saved culture guides:

**Parameters:**
- `trip_id` (path parameter): The ID of the trip

**Response:**
- `200`: Returns the culture guide (same format as POST)
- `404`: Culture guide not found for this trip

**Example:**
```bash
curl http://localhost:8000/api/v1/culture-guide/your-trip-id-here
```

### 3. Migration Script (`migrate_culture_guide.py`)
Created a migration script to add the `culture_guides` table to existing databases.

**Usage:**
```bash
python migrate_culture_guide.py
```

### 4. Test Script (`test_culture_guide_endpoints.py`)
Created a comprehensive test script to verify both endpoints.

**Usage:**
```bash
# Make sure the server is running first
python -m app.main

# In another terminal
python test_culture_guide_endpoints.py
```

## Benefits

1. **Performance**: Cached culture guides avoid repeated OpenAI API calls
2. **Cost Savings**: Only generate once per trip destination
3. **Consistency**: Same guide returned for a trip across multiple requests
4. **Data Persistence**: Culture guides are preserved with trip data
5. **Easy Retrieval**: Simple GET endpoint to fetch saved guides

## API Usage Examples

### Generate Culture Guide (First Time)
```bash
curl -X POST http://localhost:8000/api/v1/culture-guide \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "abc123",
    "destination": "Tokyo, Japan",
    "language": "en"
  }'
```

### Retrieve Saved Culture Guide
```bash
curl http://localhost:8000/api/v1/culture-guide/abc123
```

### Generate for Same Trip Again (Returns Cached)
```bash
curl -X POST http://localhost:8000/api/v1/culture-guide \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "abc123",
    "destination": "Tokyo, Japan",
    "language": "en"
  }'
```

## Error Handling

- **404**: Trip not found (POST endpoint)
- **404**: Culture guide not found (GET endpoint)
- **502**: OpenAI API failure (POST endpoint)

## Frontend Integration

The frontend can now:
1. Generate a culture guide when creating/viewing a trip
2. Check if a guide exists using GET before generating
3. Display cached guides instantly without waiting for AI generation
4. Update the guide by calling POST again (current behavior returns cached version)

## Future Enhancements

Potential improvements:
- Add a `regenerate` parameter to force new guide generation
- Support multiple languages per trip
- Add versioning for culture guide updates
- Include guide generation timestamp in response
- Add endpoint to delete culture guides
