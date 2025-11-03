# Culture Guide Feature - Testing Guide

## ✅ Implementation Complete!

The culture guide feature has been successfully implemented with database persistence.

## Quick Summary

- **POST** `/api/v1/culture/guide` - Generate or get cached culture guide
- **GET** `/api/v1/culture/guide/{trip_id}` - Retrieve saved culture guide

## Testing Steps

### Step 1: Start the Server

```bash
python -m app.main
```

The server will start on `http://localhost:8001`

### Step 2: Create a Test Trip (if needed)

In a new terminal:

```bash
python create_test_trip.py
```

This will output a trip_id like: `8b79a56b-5e46-4aa7-bfd7-7c8db75103c7`

### Step 3: Test the Endpoints

#### Option A: Use the quick test script

```bash
# Update TRIP_ID in test_culture_quick.py with your trip_id
python test_culture_quick.py
```

#### Option B: Use curl

```bash
# Generate culture guide
curl -X POST http://localhost:8001/api/v1/culture/guide \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "YOUR_TRIP_ID_HERE",
    "destination": "Tokyo, Japan",
    "language": "en"
  }'

# Retrieve saved guide
curl http://localhost:8001/api/v1/culture/guide/YOUR_TRIP_ID_HERE
```

#### Option C: Comprehensive test with trip creation

```bash
python test_culture_guide_with_trip.py
```

## Expected Behavior

### First POST Request
- Validates trip exists
- Generates culture guide via OpenAI
- Saves to database
- Returns guide (takes ~5-10 seconds)

### Second POST Request (same trip_id)
- Returns cached version from database
- Very fast (<1 second)
- No OpenAI API call

### GET Request
- Retrieves saved guide from database
- Returns 404 if guide doesn't exist
- Very fast (<1 second)

## Example Response

```json
{
  "destination": "Tokyo, Japan",
  "summary": "Japan values respect, harmony, and politeness in all interactions...",
  "tips": [
    {
      "category": "greeting_etiquette",
      "title": "Bow When Greeting",
      "tip": "Bowing is the traditional form of greeting in Japan...",
      "do": "Bow slightly when meeting someone new...",
      "avoid": "Avoid overly casual handshakes initially...",
      "emoji": "🙇"
    },
    {
      "category": "dining_etiquette",
      "title": "Chopstick Manners",
      "tip": "Proper use of chopsticks is important...",
      "do": "Rest chopsticks on the holder provided...",
      "avoid": "Never stick chopsticks vertically in rice...",
      "emoji": "🥢"
    }
  ]
}
```

## Files Created

1. **Database Model**: `app/db/models.py` - Added `CultureGuide` model
2. **Router Updates**: `app/culture/router.py` - Updated endpoints
3. **Migration**: `migrate_culture_guide.py` - Creates table (already run ✅)
4. **Test Scripts**:
   - `create_test_trip.py` - Creates test data
   - `test_culture_quick.py` - Quick test with known trip_id
   - `test_culture_guide_with_trip.py` - Comprehensive test
   - `test_culture_guide_endpoints.py` - Original test script

## Troubleshooting

### "Trip not found" Error
- Make sure you created a trip first using `create_test_trip.py`
- Or use a valid trip_id from your database

### Connection Refused
- Make sure the server is running: `python -m app.main`

### Import Errors
- The SQLAlchemy import warnings in the IDE are false positives
- The code runs fine despite these warnings

## Database

The culture guide is stored in the `culture_guides` table:
- `id` - UUID primary key
- `trip_id` - Foreign key to trips table (unique)
- `destination` - Destination name
- `summary` - Brief cultural summary
- `tips_json` - JSON array of tips
- `created_at`, `updated_at` - Timestamps

## Next Steps for Frontend

Update your frontend to:
1. Include `trip_id` in POST requests
2. Use GET endpoint to check for existing guides
3. Display cached guides instantly

See `FRONTEND_CULTURE_GUIDE_INTEGRATION.md` for detailed integration guide.

## Status

✅ Backend implementation complete
✅ Database model created
✅ Endpoints working
✅ Test scripts provided
⏳ Frontend integration needed
