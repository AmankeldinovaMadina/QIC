# Quick Start Guide - Frontend & Backend Integration

## ✅ Configuration Status

### Backend Configuration
- **CORS**: ✅ Configured with `allow_origins=["*"]`
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8001`
- **Health Check**: ✅ Working at `http://localhost:8001/api/v1/health`

### Frontend Configuration
- **API Base URL**: `http://localhost:8001/api/v1`
- **Development Port**: `3000`
- **Token Storage**: localStorage

## 🚀 Starting the Application

### 1. Start Backend Server

```bash
cd /Users/danazhaksylyk/QIC
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Or in background:
```bash
cd /Users/danazhaksylyk/QIC
source venv/bin/activate
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 > server_output.log 2>&1 &
```

### 2. Start Frontend Server

In a new terminal:
```bash
cd /Users/danazhaksylyk/QIC/frontendQIC
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 3. Verify Connection

Open browser and navigate to: `http://localhost:3000`

Expected behavior:
- ✅ Login page appears
- ✅ Enter username (min 3 characters)
- ✅ Click "Continue"
- ✅ Should automatically register/login
- ✅ Token stored in browser localStorage
- ✅ Navigate to main page

## 🧪 Testing Endpoints

### Test Backend Health
```bash
curl http://localhost:8001/api/v1/health
```
Expected: `{"status":"ok","version":"1.0.0"}`

### Test CORS
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"username":"testuser"}'
```

Check response headers include:
- `access-control-allow-origin: *`
- `access-control-allow-credentials: true`

### Test Authentication
```bash
# Register
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"myuser123"}'

# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"myuser123"}'
```

## 🔍 Troubleshooting

### Backend Won't Start

**Error: Port 8001 already in use**
```bash
# Find and kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Or check what's using the port
lsof -i :8001
```

**Error: Module not found**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Can't Connect to Backend

**Check backend is running:**
```bash
curl http://localhost:8001/api/v1/health
```

**Check CORS:**
Look for CORS headers in response:
```
access-control-allow-origin: *
access-control-allow-credentials: true
```

**Check browser console:**
- Open DevTools (F12)
- Check Console for errors
- Check Network tab for failed requests

**Common errors:**
- `Connection refused`: Backend not running
- `CORS error`: Backend CORS not configured (already fixed)
- `401 Unauthorized`: Token missing or expired
- `404 Not Found`: Wrong API endpoint

### Frontend Won't Start

**Error: Port 3000 already in use**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Error: Module not found**
```bash
# Reinstall dependencies
npm install
```

**Port conflict:**
Edit `frontendQIC/vite.config.ts`:
```typescript
server: {
  port: 3001,  // Change from 3000 to 3001
  open: true,
}
```

## 📊 API Endpoints Reference

### Authentication
```
POST   /api/v1/auth/register    # Register new user
POST   /api/v1/auth/login       # Login user
POST   /api/v1/auth/logout      # Logout user
GET    /api/v1/auth/me          # Get current user
```

### Trips
```
POST   /api/v1/trips                      # Create trip
GET    /api/v1/trips                      # List trips
GET    /api/v1/trips/{trip_id}            # Get trip
PATCH  /api/v1/trips/{trip_id}            # Update trip
DELETE /api/v1/trips/{trip_id}            # Delete trip
POST   /api/v1/trips/{trip_id}/finalize   # Finalize trip
GET    /api/v1/trips/{trip_id}/plan       # Get trip plan
GET    /api/v1/trips/{trip_id}/checklist  # Get checklist
```

### Flights
```
POST   /api/v1/flights/rank    # Rank flights
POST   /api/v1/flights/select  # Select flight
```

### Hotels
```
GET    /api/v1/hotels/search   # Search hotels
POST   /api/v1/hotels/rank     # Rank hotels
POST   /api/v1/hotels/select   # Select hotel
```

### Entertainment
```
POST   /api/v1/entertainment/search        # Search venues
POST   /api/v1/entertainment/rank          # Rank venues
POST   /api/v1/entertainment/select        # Select venues
GET    /api/v1/entertainment/{trip_id}/selections  # Get selections
```

### Culture
```
POST   /api/v1/culture-guide   # Get culture guide
```

## 🔐 Authentication Flow

1. User enters username in LoginPage
2. Frontend calls `POST /api/v1/auth/login`
3. If user doesn't exist (401), auto-register via `POST /api/v1/auth/register`
4. Backend returns `access_token`
5. Frontend stores token in `localStorage`
6. Token included in all subsequent requests as `Authorization: Bearer {token}`

## 🗄️ Database

**Location**: `travel_db.sqlite`

**Reset database** (if needed):
```bash
rm travel_db.sqlite
python -m uvicorn app.main:app --reload
```

Database will be automatically recreated on first startup.

## 📝 Environment Variables

Create `.env` file in project root (optional):
```env
# Debug mode
DEBUG=true

# Database
DATABASE_URL=sqlite+aiosqlite:///./travel_db.sqlite

# API Keys (optional for MVP)
OPENAI_API_KEY=your_key_here
SERPAPI_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

## 🐛 Debugging

### Backend Logs
```bash
# View logs
tail -f server_output.log

# Or run in foreground to see logs
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Debug Mode
Open browser DevTools and check:
1. **Console**: JavaScript errors
2. **Network**: API requests/responses
3. **Application**: localStorage tokens
4. **Elements**: DOM issues

### Check Token in Browser
```javascript
// In browser console
localStorage.getItem('access_token')
```

## ✅ Integration Checklist

- [x] Backend CORS configured
- [x] Frontend API utilities created
- [x] Authentication integrated
- [x] Trip creation connected
- [x] Trip listing connected
- [x] Token management working
- [x] Error handling implemented
- [x] Loading states added
- [ ] TripDetailPage connected (optional)
- [ ] TripPlannerStepByStepPage connected (optional)

## 🎯 Current Working Features

1. **User Registration & Login**
   - Automatic registration if user doesn't exist
   - Token-based authentication
   - Session persistence

2. **Trip Creation**
   - Multi-step chat form
   - Data validation
   - Backend storage

3. **Trip Listing**
   - Fetch all user trips
   - Display with progress bars
   - Navigation to trip details

## 🚧 Not Yet Implemented

- Trip detail view (mock data)
- Flight/Hotel/Entertainment selection
- AI trip planning
- Profile management
- Trip sharing
- Real-time updates

## 📞 Need Help?

1. Check backend logs: `tail -f server_output.log`
2. Check browser console for errors
3. Verify ports are not in use
4. Ensure dependencies installed
5. Try restarting both servers

