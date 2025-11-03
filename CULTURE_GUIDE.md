# Culture Guide Endpoint Documentation

## Overview

The `/api/v1/culture-guide` endpoint provides AI-generated, culture-specific travel etiquette tips for any destination using OpenAI's Structured Outputs feature. This ensures type-safe, schema-validated responses every time.

## Features

✅ **Structured Outputs** - Guaranteed JSON schema compliance using OpenAI's response format feature  
✅ **Production-Ready** - Proper error handling, validation, and type safety  
✅ **Actionable Tips** - Each tip includes DO/AVOID guidance  
✅ **Multiple Categories** - Covers greetings, dress code, dining, taboos, and more  
✅ **Emoji Support** - Visual indicators for better UX  

## Endpoint

**POST** `/api/v1/culture-guide`

### Request Schema

```json
{
  "destination": "Tokyo, Japan",
  "language": "en"
}
```

**Fields:**
- `destination` (string, required): City or country name
- `language` (string, optional): Response language, defaults to "en"

### Response Schema

```json
{
  "destination": "Tokyo, Japan",
  "summary": "Brief overview of cultural context (1-2 sentences)",
  "tips": [
    {
      "category": "greeting_etiquette",
      "title": "Bowing is Standard",
      "tip": "Detailed explanation of the cultural practice",
      "do": "Positive actions to take",
      "avoid": "Things to refrain from",
      "emoji": "🙇"
    }
    // 2-3 more tips...
  ]
}
```

**Tip Categories:**
- `greeting_etiquette` - How to greet and meet people
- `dress_code` - Appropriate attire expectations
- `behavioral_norms` - General social conduct
- `taboos` - Things to avoid or respect
- `dining_etiquette` - Restaurant and meal customs
- `tipping` - Tipping practices and expectations
- `religion_holidays` - Religious considerations
- `transport_customs` - Public transport etiquette

### Response Constraints

- Returns exactly **3-4 tips** per destination
- Summary is **1-2 sentences**
- Titles are **3-6 words**
- All fields are required (enforced by Pydantic)

## Usage Examples

### cURL

```bash
# Test with Tokyo
curl -X POST "http://localhost:8001/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "language": "en"
  }'

# Test with Dubai
curl -X POST "http://localhost:8001/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Dubai, UAE"
  }'
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/culture-guide",
    json={
        "destination": "Paris, France",
        "language": "en"
    }
)

data = response.json()
print(f"Destination: {data['destination']}")
print(f"Summary: {data['summary']}")

for tip in data['tips']:
    print(f"\n{tip['emoji']} {tip['title']}")
    print(f"  Category: {tip['category']}")
    print(f"  Do: {tip['do']}")
    print(f"  Avoid: {tip['avoid']}")
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8001/api/v1/culture-guide', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    destination: 'Rome, Italy',
    language: 'en'
  })
});

const data = await response.json();
console.log(data.summary);
data.tips.forEach(tip => {
  console.log(`${tip.emoji} ${tip.title}: ${tip.tip}`);
});
```

## Testing

### Run the Test Suite

```bash
# Make sure the server is running
python -m app.main

# In another terminal, run tests
python test_culture_endpoint.py
```

### Run cURL Tests

```bash
# Make sure the server is running
python -m app.main

# In another terminal
./test_culture_curl.sh
```

## Example Response

```json
{
  "destination": "Tokyo, Japan",
  "summary": "Tokyo blends traditional respect with modern efficiency. Politeness and quiet consideration for others are paramount in public spaces.",
  "tips": [
    {
      "category": "greeting_etiquette",
      "title": "Bowing Over Handshakes",
      "tip": "Bowing is the traditional greeting in Japan. A slight bow (15-30 degrees) is appropriate for casual encounters; deeper bows show more respect.",
      "do": "Return bows with a similar depth; keep hands at sides; maintain eye contact briefly before bowing.",
      "avoid": "Don't bow and shake hands simultaneously; avoid prolonged staring; don't touch while bowing.",
      "emoji": "🙇"
    },
    {
      "category": "behavioral_norms",
      "title": "Quiet in Public Transit",
      "tip": "Tokyo's trains and subways are remarkably silent. Speaking loudly or taking phone calls is considered rude.",
      "do": "Set phone to silent/vibrate; speak in whispers if necessary; offer seats to elderly.",
      "avoid": "Don't talk on the phone; avoid eating or drinking; don't play music without headphones.",
      "emoji": "🤫"
    },
    {
      "category": "dining_etiquette",
      "title": "Slurping Noodles is Polite",
      "tip": "Slurping ramen or soba noodles is not only acceptable but encouraged—it shows appreciation for the meal.",
      "do": "Slurp audibly when eating noodles; finish your meal; say 'itadakimasu' before eating.",
      "avoid": "Don't stick chopsticks upright in rice; avoid blowing your nose at the table; don't tip.",
      "emoji": "🍜"
    },
    {
      "category": "taboos",
      "title": "Remove Shoes Indoors",
      "tip": "Many Japanese homes, temples, and some restaurants require removing shoes. Look for shoe racks or slippers at entrances.",
      "do": "Remove shoes when you see others doing so; wear clean socks; place shoes neatly pointing outward.",
      "avoid": "Don't wear outdoor shoes on tatami mats; avoid stepping on door thresholds; don't wear slippers in tatami rooms.",
      "emoji": "👞"
    }
  ]
}
```

## Implementation Details

### Technology Stack

- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4o** - With Structured Outputs (schema enforcement)
- **Pydantic** - Data validation and schema definition
- **Python 3.10+** - Type hints and modern syntax

### System Prompt

The endpoint uses a carefully crafted system prompt:

```
You are a concise travel etiquette expert.
Return STRICT JSON that matches the provided schema.
Focus on culture-specific, practical advice for short-term visitors.
Use neutral tone; avoid stereotyping; be respectful and factual.
If the destination is a city, bias to local norms; otherwise use country-level norms.
Keep each tip clear and actionable. Avoid repeating the same idea across tips.
```

### Error Handling

The endpoint returns a `502 Bad Gateway` status with details if the OpenAI API call fails:

```json
{
  "detail": "culture_guide_failed: [error message]"
}
```

### Schema Validation

Using OpenAI's Structured Outputs feature ensures:
- ✅ Response always matches the Pydantic schema
- ✅ No manual JSON parsing errors
- ✅ Type safety throughout the application
- ✅ Automatic field validation

## Integration with Trip Planning

This endpoint can be integrated into the trip workflow:

1. User creates a trip to a destination
2. System automatically fetches culture guide
3. Tips are displayed during trip planning
4. Tips can be saved to trip notes or checklist

### Example Integration

```python
# In trip creation endpoint
@router.post("/trips")
async def create_trip(trip: TripCreate, current_user: User):
    # Create trip
    new_trip = await trips_service.create(trip, current_user.id)
    
    # Fetch culture guide
    try:
        culture_response = requests.post(
            "http://localhost:8001/api/v1/culture-guide",
            json={"destination": trip.to_city}
        )
        culture_data = culture_response.json()
        
        # Add to trip notes or metadata
        new_trip.culture_tips = culture_data
    except:
        pass  # Optional, don't fail trip creation
    
    return new_trip
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Files Created

```
app/culture/
├── __init__.py          # Module exports
└── router.py            # Culture guide endpoint

test_culture_endpoint.py # Python test suite
test_culture_curl.sh     # cURL test script
CULTURE_GUIDE.md         # This documentation
```

## Next Steps

Potential enhancements:

1. **Caching** - Cache responses by destination to reduce API calls
2. **Language Support** - Expand beyond English
3. **Custom Preferences** - Allow users to specify interests (business, leisure, family)
4. **Trip Integration** - Automatically fetch culture tips when creating trips
5. **User Feedback** - Allow users to rate tip helpfulness
6. **Offline Mode** - Pre-generate guides for popular destinations

## Support

For issues or questions:
- Check the FastAPI logs for error details
- Verify OpenAI API key is set in environment
- Review the Pydantic validation errors for schema issues
- Test with the provided test scripts

---

**Last Updated**: November 3, 2025  
**API Version**: 1.0.0  
**OpenAI Model**: gpt-4o-2024-08-06
