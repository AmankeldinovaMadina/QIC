# Frontend Integration Checklist for Culture Guide

## Overview
The culture guide feature now saves to the database with `trip_id`. Here's what you need to update in the frontend.

## Required Changes

### 1. Update POST Request to Include `trip_id`

**Before:**
```typescript
// Old request body
const requestBody = {
  destination: "Tokyo, Japan",
  language: "en"
};
```

**After:**
```typescript
// New request body (requires trip_id)
const requestBody = {
  trip_id: currentTrip.id,  // ← ADD THIS
  destination: "Tokyo, Japan",
  language: "en"
};
```

### 2. Component Updates Needed

#### Option A: Generate on Trip Page Load
```typescript
// In TripDetails or similar component
useEffect(() => {
  const loadCultureGuide = async () => {
    try {
      // First, try to GET existing guide
      const response = await fetch(`/api/v1/culture-guide/${tripId}`);
      
      if (response.ok) {
        // Guide exists, use it
        const guide = await response.json();
        setCultureGuide(guide);
      } else if (response.status === 404) {
        // Guide doesn't exist, generate it
        await generateCultureGuide();
      }
    } catch (error) {
      console.error('Error loading culture guide:', error);
    }
  };
  
  loadCultureGuide();
}, [tripId]);

const generateCultureGuide = async () => {
  const response = await fetch('/api/v1/culture-guide', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      trip_id: tripId,
      destination: trip.to_city,
      language: 'en'
    })
  });
  
  const guide = await response.json();
  setCultureGuide(guide);
};
```

#### Option B: Generate on Button Click
```typescript
// In CultureGuidePage component
const handleGenerateCultureGuide = async () => {
  setIsLoading(true);
  
  try {
    const response = await fetch('/api/v1/culture-guide', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trip_id: tripId,
        destination: trip.to_city,
        language: 'en'
      })
    });
    
    if (response.ok) {
      const guide = await response.json();
      setCultureGuide(guide);
    } else if (response.status === 404) {
      setError('Trip not found');
    } else {
      setError('Failed to generate culture guide');
    }
  } catch (error) {
    setError('Error generating culture guide');
  } finally {
    setIsLoading(false);
  }
};
```

### 3. Suggested User Flow

```
User opens Trip Details
    ↓
Check if culture guide exists (GET)
    ↓
    ├─── Exists → Display immediately (fast)
    │
    └─── Not exists → Show "Generate" button
              ↓
         User clicks button
              ↓
         POST to generate
              ↓
         Display guide
```

### 4. Example Complete Component

```typescript
import React, { useState, useEffect } from 'react';

interface CultureGuideProps {
  tripId: string;
  destination: string;
}

export const CultureGuideSection: React.FC<CultureGuideProps> = ({ 
  tripId, 
  destination 
}) => {
  const [guide, setGuide] = useState<CultureGuide | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exists, setExists] = useState<boolean | null>(null);

  // Check if guide exists on mount
  useEffect(() => {
    const checkGuide = async () => {
      try {
        const response = await fetch(`/api/v1/culture-guide/${tripId}`);
        
        if (response.ok) {
          const data = await response.json();
          setGuide(data);
          setExists(true);
        } else if (response.status === 404) {
          setExists(false);
        }
      } catch (err) {
        console.error('Error checking culture guide:', err);
      }
    };

    checkGuide();
  }, [tripId]);

  const generateGuide = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/culture-guide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trip_id: tripId,
          destination: destination,
          language: 'en'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGuide(data);
        setExists(true);
      } else {
        setError('Failed to generate culture guide');
      }
    } catch (err) {
      setError('Error generating culture guide');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Generating culture guide...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (exists === false) {
    return (
      <div>
        <p>No culture guide yet for {destination}</p>
        <button onClick={generateGuide}>Generate Culture Guide</button>
      </div>
    );
  }

  if (!guide) {
    return <div>Loading...</div>;
  }

  return (
    <div className="culture-guide">
      <h2>Culture Guide: {guide.destination}</h2>
      <p className="summary">{guide.summary}</p>
      
      <div className="tips">
        {guide.tips.map((tip, index) => (
          <div key={index} className="tip-card">
            <h3>{tip.emoji} {tip.title}</h3>
            <p className="category">{tip.category.replace('_', ' ')}</p>
            <p className="tip-text">{tip.tip}</p>
            
            <div className="do-avoid">
              <div className="do">
                <strong>✅ Do:</strong> {tip.do}
              </div>
              <div className="avoid">
                <strong>❌ Avoid:</strong> {tip.avoid}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Benefits for Frontend

1. **Faster Loading**: Cached guides load instantly (no AI generation wait)
2. **Better UX**: Can show "already generated" vs "generate now" states
3. **Reliability**: Data persists across sessions
4. **Cost Efficient**: No repeated API calls for same guide

## Testing Checklist

- [ ] Generate culture guide for a new trip
- [ ] Reload page - guide should load from database (fast)
- [ ] Navigate away and back - guide should still be there
- [ ] Try to generate again - should return cached version immediately
- [ ] Test with non-existent trip_id - should show error
- [ ] Test GET endpoint directly in browser DevTools

## API Endpoints Summary

```typescript
// Generate or get cached guide
POST /api/v1/culture-guide
Body: { trip_id, destination, language }
Returns: CultureGuide

// Retrieve saved guide
GET /api/v1/culture-guide/{trip_id}
Returns: CultureGuide or 404
```

## TypeScript Types (if needed)

```typescript
interface CultureTip {
  category: string;
  title: string;
  tip: string;
  do: string;
  avoid: string;
  emoji: string;
}

interface CultureGuide {
  destination: string;
  summary: string;
  tips: CultureTip[];
}

interface CultureGuideRequest {
  trip_id: string;
  destination: string;
  language?: 'en';
}
```

## Questions?

If you need help with:
- API integration
- Error handling
- Loading states
- UI/UX patterns

Just ask!
