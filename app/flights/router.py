from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import User, get_async_session
from app.flights.ai_ranker import OpenAIFlightRanker
from app.flights.schemas import FlightSearchResponse, RankRequest, RankResponse
from app.flights.service import flight_search_service
from app.trips.schemas import FlightSelectionRequest, FlightSelectionResponse
from app.trips.service import trips_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search", response_model=FlightSearchResponse)
async def search_flights(
    trip_id: str = Query(..., description="Trip ID to search flights for"),
    departure_id: Optional[str] = Query(
        None, description="IATA departure airport code (e.g., 'JFK')"
    ),
    arrival_id: Optional[str] = Query(
        None, description="IATA arrival airport code (e.g., 'NRT')"
    ),
    outbound_date: Optional[str] = Query(
        None, description="Departure date (YYYY-MM-DD)"
    ),
    return_date: Optional[str] = Query(None, description="Return date (YYYY-MM-DD)"),
    adults: Optional[int] = Query(None, ge=1, le=20, description="Number of adults"),
    children: Optional[int] = Query(
        None, ge=0, le=20, description="Number of children"
    ),
    currency: Optional[str] = Query("USD", description="Currency code (e.g., 'USD')"),
    hl: Optional[str] = Query("en", description="Language code (e.g., 'en')"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Search for flights using SerpAPI Google Flights.

    If departure_id, arrival_id, or dates are not provided,
    they will be automatically pulled from the trip.
    """
    try:
        # Get trip details
        trip = await trips_service.get_trip_by_id(session, trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        # Use trip data as defaults
        dep_id = departure_id
        arr_id = arrival_id
        out_date = outbound_date or trip.start_date.strftime("%Y-%m-%d")
        ret_date = return_date or trip.end_date.strftime("%Y-%m-%d")
        num_adults = adults if adults is not None else trip.adults
        num_children = children if children is not None else trip.children

        # Debug: Print what we got from trip
        print(f"🏙️  Trip cities: from_city='{trip.from_city}', to_city='{trip.to_city}'")
        print(f"🎫 Provided codes: dep='{dep_id}', arr='{arr_id}'")

        # If no IATA codes provided, try to map from city names
        if not dep_id:
            dep_id = _get_airport_code(trip.from_city)
            print(f"   Mapped '{trip.from_city}' → '{dep_id}'")
        if not arr_id:
            arr_id = _get_airport_code(trip.to_city)
            print(f"   Mapped '{trip.to_city}' → '{arr_id}'")

        print(
            f"🔍 Searching flights: {dep_id} → {arr_id}, "
            f"{out_date} to {ret_date}, {num_adults} adults, {num_children} children"
        )

        # Search flights via SerpAPI
        try:
            flights, google_flights_url = await flight_search_service.search_flights(
                departure_id=dep_id,
                arrival_id=arr_id,
                outbound_date=out_date,
                return_date=ret_date,
                adults=num_adults,
                children=num_children,
                currency=currency,
                hl=hl,
            )
            
            # Add the Google Flights URL to all flights
            for flight in flights:
                flight.google_flights_url = google_flights_url
                
            print(f"✅ Found {len(flights)} flights")
        except Exception as e:
            print(f"⚠️  Flight search returned an error: {e}")
            flights = []

        # Generate search ID
        import uuid

        search_id = str(uuid.uuid4())

        return FlightSearchResponse(
            trip_id=trip_id,
            search_id=search_id,
            flights=flights,
            search_params={
                "departure_id": dep_id,
                "arrival_id": arr_id,
                "outbound_date": out_date,
                "return_date": ret_date,
                "adults": num_adults,
                "children": num_children,
                "currency": currency,
            },
            total_results=len(flights),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR in search_flights: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _get_airport_code(city_name: str) -> str:
    """Map city name to primary airport IATA code."""
    # Simple mapping - in production, use a proper airport lookup service
    city_to_airport = {
        # USA
        "new york": "JFK",
        "los angeles": "LAX",
        "chicago": "ORD",
        "san francisco": "SFO",
        "miami": "MIA",
        "boston": "BOS",
        "seattle": "SEA",
        "las vegas": "LAS",
        "orlando": "MCO",
        "atlanta": "ATL",
        "washington": "IAD",
        "denver": "DEN",
        "phoenix": "PHX",
        "dallas": "DFW",
        "houston": "IAH",
        "philadelphia": "PHL",
        "detroit": "DTW",
        "minneapolis": "MSP",
        "tampa": "TPA",
        "charlotte": "CLT",
        "portland": "PDX",
        "austin": "AUS",
        "nashville": "BNA",
        "salt lake city": "SLC",
        "baltimore": "BWI",
        "san diego": "SAN",
        
        # UK
        "london": "LHR",
        "manchester": "MAN",
        "edinburgh": "EDI",
        "birmingham": "BHX",
        "glasgow": "GLA",
        
        # France
        "paris": "CDG",
        "nice": "NCE",
        "lyon": "LYS",
        "marseille": "MRS",
        "bordeaux": "BOD",
        
        # Germany
        "munich": "MUC",
        "frankfurt": "FRA",
        "berlin": "BER",
        "hamburg": "HAM",
        "cologne": "CGN",
        
        # Italy
        "rome": "FCO",
        "milan": "MXP",
        "venice": "VCE",
        "florence": "FLR",
        "naples": "NAP",
        
        # Spain
        "barcelona": "BCN",
        "madrid": "MAD",
        "valencia": "VLC",
        "seville": "SVQ",
        "malaga": "AGP",
        
        # Netherlands
        "amsterdam": "AMS",
        "rotterdam": "RTM",
        
        # Switzerland
        "zurich": "ZRH",
        "geneva": "GVA",
        
        # Austria
        "vienna": "VIE",
        "salzburg": "SZG",
        
        # Portugal
        "lisbon": "LIS",
        "porto": "OPO",
        
        # Greece
        "athens": "ATH",
        "thessaloniki": "SKG",
        "rhodes": "RHO",
        
        # Turkey
        "istanbul": "IST",
        "ankara": "ESB",
        "antalya": "AYT",
        "izmir": "ADB",
        
        # Russia
        "moscow": "SVO",
        "saint petersburg": "LED",
        
        # China
        "beijing": "PEK",
        "shanghai": "PVG",
        "guangzhou": "CAN",
        "shenzhen": "SZX",
        "chengdu": "CTU",
        "xian": "XIY",
        "hangzhou": "HGH",
        
        # Japan
        "tokyo": "NRT",
        "osaka": "KIX",
        "kyoto": "KIX",
        "fukuoka": "FUK",
        "sapporo": "CTS",
        
        # South Korea
        "seoul": "ICN",
        "busan": "PUS",
        
        # Thailand
        "bangkok": "BKK",
        "phuket": "HKT",
        "chiang mai": "CNX",
        
        # Malaysia
        "kuala lumpur": "KUL",
        "penang": "PEN",
        
        # Singapore
        "singapore": "SIN",
        
        # Indonesia
        "bali": "DPS",
        "jakarta": "CGK",
        "yogyakarta": "JOG",
        
        # Philippines
        "manila": "MNL",
        "cebu": "CEB",
        
        # Vietnam
        "ho chi minh city": "SGN",
        "hanoi": "HAN",
        "da nang": "DAD",
        
        # India
        "delhi": "DEL",
        "mumbai": "BOM",
        "bangalore": "BLR",
        "chennai": "MAA",
        "kolkata": "CCU",
        "hyderabad": "HYD",
        "pune": "PNQ",
        "goa": "GOI",
        
        # UAE
        "dubai": "DXB",
        "abu dhabi": "AUH",
        
        # Saudi Arabia
        "riyadh": "RUH",
        "jeddah": "JED",
        "makkah": "JED",
        "medina": "MED",
        
        # Qatar
        "doha": "DOH",
        
        # Kuwait
        "kuwait city": "KWI",
        
        # Bahrain
        "manama": "BAH",
        
        # Oman
        "muscat": "MCT",
        
        # Egypt
        "cairo": "CAI",
        "alexandria": "ALY",
        "luxor": "LXR",
        "sharm el sheikh": "SSH",
        
        # Morocco
        "casablanca": "CMN",
        "marrakech": "RAK",
        "rabat": "RBA",
        "fes": "FEZ",
        
        # South Africa
        "johannesburg": "JNB",
        "cape town": "CPT",
        "durban": "DUR",
        
        # Australia
        "sydney": "SYD",
        "melbourne": "MEL",
        "brisbane": "BNE",
        "perth": "PER",
        "adelaide": "ADL",
        "gold coast": "OOL",
        
        # New Zealand
        "auckland": "AKL",
        "wellington": "WLG",
        "christchurch": "CHC",
        
        # Canada
        "toronto": "YYZ",
        "vancouver": "YVR",
        "montreal": "YUL",
        "calgary": "YYC",
        "ottawa": "YOW",
        "edmonton": "YEG",
        
        # Mexico
        "mexico city": "MEX",
        "cancun": "CUN",
        "guadalajara": "GDL",
        "monterrey": "MTY",
        "tijuana": "TIJ",
        
        # Brazil
        "sao paulo": "GRU",
        "rio de janeiro": "GIG",
        "brasilia": "BSB",
        "salvador": "SSA",
        
        # Argentina
        "buenos aires": "EZE",
        "cordoba": "COR",
        
        # Chile
        "santiago": "SCL",
        "valparaiso": "SCL",
        
        # Peru
        "lima": "LIM",
        "cuzco": "CUZ",
        
        # Colombia
        "bogota": "BOG",
        "medellin": "MDE",
        "cartagena": "CTG",
        
        # Panama
        "panama city": "PTY",
        
        # Costa Rica
        "san jose": "SJO",
        
        # Cuba
        "havana": "HAV",
        
        # Dominican Republic
        "punta cana": "PUJ",
        
        # Jamaica
        "kingston": "KIN",
        
        # Israel
        "tel aviv": "TLV",
        "jerusalem": "TLV",
        
        # Jordan
        "amman": "AMM",
        
        # Lebanon
        "beirut": "BEY",
        
        # Hong Kong
        "hong kong": "HKG",
        
        # Taiwan
        "taipei": "TPE",
        
        # Iceland
        "reykjavik": "KEF",
        
        # Denmark
        "copenhagen": "CPH",
        "aarhus": "AAR",
        
        # Sweden
        "stockholm": "ARN",
        "gothenburg": "GOT",
        
        # Norway
        "oslo": "OSL",
        "bergen": "BGO",
        
        # Finland
        "helsinki": "HEL",
        
        # Belgium
        "brussels": "BRU",
        "antwerp": "ANR",
        
        # Ireland
        "dublin": "DUB",
        "cork": "ORK",
        
        # Poland
        "warsaw": "WAW",
        "krakow": "KRK",
        
        # Czech Republic
        "prague": "PRG",
        
        # Hungary
        "budapest": "BUD",
        
        # Croatia
        "zagreb": "ZAG",
        "dubrovnik": "DBV",
        
        # Serbia
        "belgrade": "BEG",
        
        # Romania
        "bucharest": "OTP",
        
        # Bulgaria
        "sofia": "SOF",
        
        # Ukraine
        "kyiv": "KBP",
        "kiev": "KBP",
    }

    # Handle city names with countries like "Paris, France" or "Dubai, UAE"
    # Split by comma and take the first part
    city_only = city_name.split(',')[0].lower().strip()
    return city_to_airport.get(city_only, city_name.upper()[:3])


@router.post("/rank", response_model=RankResponse)
async def rank_flights(req: RankRequest):
    """Rank flight itineraries using AI (or heuristic fallback)."""
    try:
        ranker = OpenAIFlightRanker()
        result = await ranker.rank_flights(req)
        return result
    except Exception as e:
        print(f"ERROR in rank_flights: {e}")
        # If OpenAI unavailable, use heuristic fallback directly
        # This should not happen since OpenAIFlightRanker has internal fallback
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-rank", response_model=RankResponse)
async def rank_flights_alias(req: RankRequest):
    """Legacy alias: /ai-rank -> /rank"""
    return await rank_flights(req)


@router.post("/select")
async def select_flight_for_trip(
    req: FlightSelectionRequest,
    session=Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Select a flight and save it to a trip - simplified working version."""
    try:
        print(f"🛫 Flight selection for trip {req.trip_id}")

        # Get the trip and verify ownership
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        print(f"✅ Trip found: {trip.from_city} → {trip.to_city}")

        # Update trip with flight information directly
        trip.selected_flight_id = req.flight_id
        trip.selected_flight_airline = req.airline
        trip.selected_flight_number = req.flight_number
        trip.selected_flight_departure_airport = req.departure_airport
        trip.selected_flight_arrival_airport = req.arrival_airport
        trip.selected_flight_departure_time = req.departure_time
        trip.selected_flight_arrival_time = req.arrival_time
        trip.selected_flight_price = req.price
        trip.selected_flight_currency = req.currency
        trip.selected_flight_duration_min = req.total_duration_min
        trip.selected_flight_stops = req.stops
        trip.selected_flight_score = req.score
        trip.selected_flight_title = req.title
        trip.selected_flight_pros = req.pros_keywords
        trip.selected_flight_cons = req.cons_keywords

        # Save to database
        await session.commit()
        await session.refresh(trip)

        print(f"✅ Flight {req.airline} {req.flight_number} saved successfully!")

        # Return simple success response
        return {
            "success": True,
            "message": f"Flight {req.airline} {req.flight_number} successfully added to trip",
            "trip_id": trip.id,
            "flight": {
                "airline": req.airline,
                "flight_number": req.flight_number,
                "route": f"{req.departure_airport} → {req.arrival_airport}",
                "price": f"${req.price} {req.currency}",
                "departure": (
                    req.departure_time.isoformat() if req.departure_time else None
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trip_id}/selection")
async def get_flight_selection(
    trip_id: str,
    session=Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get the selected flight for a trip."""
    try:
        # Get the trip and verify ownership
        trip = await trips_service.get_trip_by_id(session, trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        # Build flight info
        selected_flight = trips_service._build_selected_flight_info(trip)

        if not selected_flight:
            return {
                "trip_id": trip_id,
                "selected_flight": None,
                "message": "No flight selected for this trip yet",
            }

        return {
            "trip_id": trip_id,
            "selected_flight": selected_flight,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
