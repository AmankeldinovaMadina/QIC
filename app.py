import asyncio
import math
import os
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

# LangGraph imports
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

app = FastAPI(title="Travel Aggregator", version="1.0.0")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=OPENAI_API_KEY)

# Visa API Configuration
RAPID_KEY = os.getenv("RAPIDAPI_KEY")
VISA_BASE = "https://visa-requirement.p.rapidapi.com"
VISA_HEADERS = {
    "x-rapidapi-key": RAPID_KEY or "",
    "x-rapidapi-host": "visa-requirement.p.rapidapi.com",
    "Content-Type": "application/json",
}


class VisaApiError(Exception):
    pass


# Models
class Place(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    categories: List[str] = []
    rating: float = None
    distance: Optional[float] = None
    source: str


class DiscoverRequest(BaseModel):
    lat: float
    lon: float
    radius_m: int = 2000


class DiscoverResponse(BaseModel):
    places: List[Place]


# Visa Models
class RankWeights(BaseModel):
    weights: Dict[str, int] = {
        "Visa-free": 2,
        "Visa on arrival": 1,
        "Visa required": 0,
        "eVisa": 1,
        "eTA": 1,
        "Tourist card": 0,
        "Freedom of movement": 3,
        "Not admitted": -1,
    }


# Trip Planning Models
class TransportType(str, Enum):
    PLANE = "plane"
    CAR = "car"
    TRAIN = "train"
    BUS = "bus"


class FlightClass(str, Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


class TripType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"


class ActivityType(str, Enum):
    BEACHES = "beaches"
    CITY_SIGHTSEEING = "city"
    OUTDOOR_ADVENTURES = "hiking"
    FESTIVALS = "festival"
    FOOD_EXPLORATION = "restaurant2"
    NIGHTLIFE = "nightlife"
    SHOPPING = "online-shopping"
    SPA_WELLNESS = "massage"


class DietType(str, Enum):
    HALAL = "halal"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    NO_RESTRICTIONS = "no_restrictions"


class TripPlanningState(TypedDict):
    messages: List[BaseMessage]
    current_step: str
    transport_type: Optional[TransportType]
    traveler_count: Optional[int]
    adults: Optional[int]
    children: Optional[int]
    flight_class: Optional[FlightClass]
    flight_type: Optional[str]  # "direct" or "transit"
    destination: Optional[str]
    departure_location: Optional[str]
    trip_type: Optional[TripType]
    departure_date: Optional[str]
    return_date: Optional[str]
    activities: List[ActivityType]
    budget: Optional[str]
    diet_preferences: List[DietType]
    completed_steps: List[str]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggestions: Optional[List[str]] = None
    is_complete: bool = False


# Trip Planning State Storage (in production, use Redis or database)
trip_sessions: Dict[str, TripPlanningState] = {}


# Simplified Trip Planner
def simple_trip_planner(
    state: TripPlanningState, user_message: str
) -> TripPlanningState:
    """Process a user message and update state"""
    current_step = state.get("current_step", "transport")
    user_msg = user_message.lower()

    if current_step == "transport":
        if any(word in user_msg for word in ["plane", "fly", "flight", "airplane"]):
            state["transport_type"] = TransportType.PLANE
            state["current_step"] = "flight_details"
            response = """✈️ Great choice! Flying it is.

✨ **Flight Class**: What class would you prefer?
- 💺 Economy
- 💼 Business  
- 👑 First Class"""
        elif any(word in user_msg for word in ["car", "drive", "driving"]):
            state["transport_type"] = TransportType.CAR
            state["current_step"] = "travelers"
            response = """🚗 Perfect! Road trip adventure!

👥 **Travelers**: How many people will be traveling?
Please tell me the number of adults and children (if any)."""
        else:
            response = """I didn't catch that. Could you please choose your transportation:
- ✈️ Plane
- 🚗 Car
- 🚆 Train  
- 🚌 Bus"""

    elif current_step == "flight_details":
        if "economy" in user_msg:
            state["flight_class"] = FlightClass.ECONOMY
        elif "business" in user_msg:
            state["flight_class"] = FlightClass.BUSINESS
        elif "first" in user_msg:
            state["flight_class"] = FlightClass.FIRST

        state["current_step"] = "travelers"
        response = """👥 **Travelers**: How many people will be traveling?

Please tell me:
- Number of adults
- Number of children (if any)
- Or just say "solo" if you're traveling alone"""

    elif current_step == "travelers":
        if "solo" in user_msg or "alone" in user_msg:
            state["adults"] = 1
            state["children"] = 0
        else:
            import re

            numbers = re.findall(r"\d+", user_msg)
            if numbers:
                state["adults"] = int(numbers[0])
                state["children"] = int(numbers[1]) if len(numbers) > 1 else 0
            else:
                state["adults"] = 1
                state["children"] = 0

        state["current_step"] = "destination"
        traveler_summary = f"{state.get('adults', 0)} adult(s)"
        if state.get("children", 0) > 0:
            traveler_summary += f" and {state['children']} child(ren)"

        response = f"""Perfect! So {traveler_summary} will be traveling.

🌍 **Destination**: Where would you like to go?
Just tell me your dream destination!"""

    elif current_step == "destination":
        state["destination"] = user_message.strip()
        state["current_step"] = "departure"
        response = f"""🏠 **Departure**: Where will you be departing from?
Please tell me your departure city."""

    elif current_step == "departure":
        state["departure_location"] = user_message.strip()
        state["current_step"] = "trip_type"
        response = """🎫 **Trip Type**: 
- 🔄 Round trip (going and coming back)
- ➡️ One way (not returning)

What type of trip is this?"""

    elif current_step == "trip_type":
        if "round" in user_msg:
            state["trip_type"] = TripType.ROUND_TRIP
            response = """📅 **Travel Dates**: When do you want to travel?
Example: "Leave December 15, return January 5" """
        else:
            state["trip_type"] = TripType.ONE_WAY
            response = """📅 **Departure Date**: When would you like to leave?
Example: "December 15, 2024" """

        state["current_step"] = "dates"

    elif current_step == "dates":
        state["departure_date"] = user_message
        state["current_step"] = "activities"
        response = """🎯 **Activities**: What interests you? (Select multiple)

🏖️ Beaches | 🏛️ City sightseeing | 🥾 Outdoor adventures
🎉 Festivals | 🍽️ Food exploration | 🌙 Nightlife
🛍️ Shopping | 💆 Spa wellness

Just list what interests you!"""

    elif current_step == "activities":
        activities = []
        activity_map = {
            "beach": ActivityType.BEACHES,
            "city": ActivityType.CITY_SIGHTSEEING,
            "hiking": ActivityType.OUTDOOR_ADVENTURES,
            "festival": ActivityType.FESTIVALS,
            "food": ActivityType.FOOD_EXPLORATION,
            "nightlife": ActivityType.NIGHTLIFE,
            "shopping": ActivityType.SHOPPING,
            "spa": ActivityType.SPA_WELLNESS,
        }

        for keyword, activity in activity_map.items():
            if keyword in user_msg:
                activities.append(activity)

        state["activities"] = activities
        state["current_step"] = "budget"
        response = """💰 **Budget**: What's your budget range per person?
- 💵 Budget-friendly ($50-100/day)
- 💳 Mid-range ($100-300/day)  
- 💎 Luxury ($300+/day)

What works for you?"""

    elif current_step == "budget":
        state["budget"] = user_message
        state["current_step"] = "diet"
        response = """🥗 **Dietary Preferences**: Any dietary restrictions?
- 🕌 Halal | 🌱 Vegetarian | 🌾 Gluten-free | ❌ None"""

    elif current_step == "diet":
        diet_prefs = []
        if "halal" in user_msg:
            diet_prefs.append(DietType.HALAL)
        if "vegetarian" in user_msg:
            diet_prefs.append(DietType.VEGETARIAN)
        if "gluten" in user_msg:
            diet_prefs.append(DietType.GLUTEN_FREE)
        if not diet_prefs:
            diet_prefs.append(DietType.NO_RESTRICTIONS)

        state["diet_preferences"] = diet_prefs
        state["current_step"] = "complete"

        # Generate summary
        response = f"""🎉 **Trip Planning Complete!**

🚗 **Transport**: {state.get('transport_type', 'N/A').value if state.get('transport_type') else 'N/A'}
👥 **Travelers**: {state.get('adults', 0)} adult(s){f", {state.get('children', 0)} child(ren)" if state.get('children', 0) > 0 else ""}
🌍 **Destination**: {state.get('destination', 'N/A')}
🏠 **From**: {state.get('departure_location', 'N/A')}
🎫 **Trip Type**: {state.get('trip_type', 'N/A').value if state.get('trip_type') else 'N/A'}
📅 **Dates**: {state.get('departure_date', 'N/A')}
🎯 **Activities**: {', '.join([a.value for a in state.get('activities', [])]) if state.get('activities') else 'General'}
💰 **Budget**: {state.get('budget', 'N/A')}
🥗 **Diet**: {', '.join([d.value for d in state.get('diet_preferences', [])]) if state.get('diet_preferences') else 'None'}

Ready to find amazing places for your trip! 🌟"""

    else:
        response = "Your trip planning is complete! Ask me to find places or check visa requirements."

    # Add the response message
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(AIMessage(content=response))

    return state


# Visa Services
async def get_custom_passport_rank(weights: Dict[str, int]):
    """Get custom passport ranking based on weights"""
    async with httpx.AsyncClient(timeout=15.0, headers=VISA_HEADERS) as client:
        response = await client.post(
            f"{VISA_BASE}/v2/passport/rank/custom", json={"weights": weights}
        )
        if response.is_error:
            raise VisaApiError(f"{response.status_code}: {response.text}")
        return response.json()


async def get_visa_requirement(passport_iso2: str, destination_iso2: str):
    """Return visa requirement for a passport holder traveling to destination"""
    params = {"from": passport_iso2.upper(), "to": destination_iso2.upper()}
    async with httpx.AsyncClient(timeout=15.0, headers=VISA_HEADERS) as client:
        response = await client.get(f"{VISA_BASE}/v2/visa/requirements", params=params)
        if response.is_error:
            raise VisaApiError(f"{response.status_code}: {response.text}")
        return response.json()


# Trip Planning Workflow
def create_trip_planning_workflow():
    """Create the LangGraph workflow for trip planning"""

    def start_planning(state: TripPlanningState) -> TripPlanningState:
        """Initialize trip planning conversation"""
        if not state.get("current_step"):
            state["current_step"] = "transport"
            state["completed_steps"] = []
            state["activities"] = []
            state["diet_preferences"] = []

            welcome_msg = AIMessage(
                content="""🌟 Welcome to your AI Trip Planner! 
            
I'll help you plan the perfect trip by asking you a few questions. Let's start!

🚗 **Transportation**: How would you like to travel?
- ✈️ Plane
- 🚗 Car  
- 🚆 Train
- 🚌 Bus

Just type your preference (e.g., "plane" or "I want to fly")"""
            )

            if "messages" not in state:
                state["messages"] = []
            state["messages"].append(welcome_msg)

        return state

    def ask_transport(state: TripPlanningState) -> TripPlanningState:
        """Ask about transportation preferences"""
        user_msg = state["messages"][-1].content.lower() if state["messages"] else ""

        if any(word in user_msg for word in ["plane", "fly", "flight", "airplane"]):
            state["transport_type"] = TransportType.PLANE
            state["current_step"] = "flight_class"
            state["completed_steps"].append("transport")

            msg = AIMessage(
                content="""✈️ Great choice! Flying it is.

✨ **Flight Class**: What class would you prefer?
- 💺 Economy
- 💼 Business  
- 👑 First Class

Type your preference!"""
            )
        elif any(word in user_msg for word in ["car", "drive", "driving"]):
            state["transport_type"] = TransportType.CAR
            state["current_step"] = "travelers"
            state["completed_steps"].append("transport")

            msg = AIMessage(
                content="""🚗 Perfect! Road trip adventure!

👥 **Travelers**: How many people will be traveling?
- Are you traveling solo?
- With family? 
- With friends?

Please tell me the number of adults and children (if any)."""
            )
        else:
            msg = AIMessage(
                content="""I didn't catch that. Could you please choose your transportation:
- ✈️ Plane
- 🚗 Car
- 🚆 Train  
- 🚌 Bus"""
            )

        state["messages"].append(msg)
        return state

    def ask_flight_details(state: TripPlanningState) -> TripPlanningState:
        """Ask about flight class and type"""
        user_msg = state["messages"][-1].content.lower()

        if state["current_step"] == "flight_class":
            if "economy" in user_msg:
                state["flight_class"] = FlightClass.ECONOMY
            elif "business" in user_msg:
                state["flight_class"] = FlightClass.BUSINESS
            elif "first" in user_msg:
                state["flight_class"] = FlightClass.FIRST
            else:
                msg = AIMessage(
                    content="Please choose: Economy, Business, or First Class"
                )
                state["messages"].append(msg)
                return state

            state["current_step"] = "flight_type"
            msg = AIMessage(
                content="""🎯 **Flight Type**: Do you prefer:
- 🎯 Direct flights (faster, more convenient)
- 🔄 Flights with transit (often cheaper, more options)

What's your preference?"""
            )

        elif state["current_step"] == "flight_type":
            if any(word in user_msg for word in ["direct", "nonstop"]):
                state["flight_type"] = "direct"
            elif any(
                word in user_msg
                for word in ["transit", "connection", "layover", "stop"]
            ):
                state["flight_type"] = "transit"
            else:
                msg = AIMessage(content="Please choose: Direct or Transit flights")
                state["messages"].append(msg)
                return state

            state["current_step"] = "travelers"
            state["completed_steps"].append("flight_details")
            msg = AIMessage(
                content="""👥 **Travelers**: How many people will be traveling?

Please tell me:
- Number of adults
- Number of children (if any)
- Or just say "solo" if you're traveling alone"""
            )

        state["messages"].append(msg)
        return state

    def ask_travelers(state: TripPlanningState) -> TripPlanningState:
        """Ask about number of travelers"""
        user_msg = state["messages"][-1].content.lower()

        if "solo" in user_msg or "alone" in user_msg or "just me" in user_msg:
            state["adults"] = 1
            state["children"] = 0
            state["traveler_count"] = 1
        else:
            # Try to extract numbers
            import re

            numbers = re.findall(r"\d+", user_msg)
            if numbers:
                if "adult" in user_msg and "child" in user_msg:
                    # Handle "2 adults 1 child" format
                    if len(numbers) >= 2:
                        state["adults"] = int(numbers[0])
                        state["children"] = int(numbers[1])
                elif "adult" in user_msg:
                    state["adults"] = int(numbers[0])
                    state["children"] = 0
                else:
                    # Assume total count
                    total = int(numbers[0])
                    state["traveler_count"] = total
                    state["adults"] = total  # Default assumption
                    state["children"] = 0
            else:
                msg = AIMessage(
                    content="""I need more specific information. Please tell me:
- Number of adults
- Number of children (if any)
- Or just say "solo" if traveling alone

Example: "2 adults and 1 child" or "solo" """
                )
                state["messages"].append(msg)
                return state

        state["current_step"] = "destination"
        state["completed_steps"].append("travelers")

        traveler_summary = f"{state.get('adults', 0)} adult(s)"
        if state.get("children", 0) > 0:
            traveler_summary += f" and {state['children']} child(ren)"

        msg = AIMessage(
            content=f"""Perfect! So {traveler_summary} will be traveling.

🌍 **Destination**: Where would you like to go?
- A specific city (e.g., "Paris", "Tokyo")
- A country (e.g., "Japan", "France")  
- A region (e.g., "Southeast Asia", "Europe")

What's your dream destination?"""
        )

        state["messages"].append(msg)
        return state

    def ask_destination(state: TripPlanningState) -> TripPlanningState:
        """Ask about destination and departure details"""
        user_msg = state["messages"][-1].content

        if state["current_step"] == "destination":
            state["destination"] = user_msg.strip()
            state["current_step"] = "departure"
            state["completed_steps"].append("destination")

            msg = AIMessage(
                content=f"""🏠 **Departure**: Where will you be departing from?
            
Please tell me your departure city or airport."""
            )

        elif state["current_step"] == "departure":
            state["departure_location"] = user_msg.strip()
            state["current_step"] = "trip_type"
            state["completed_steps"].append("departure")

            msg = AIMessage(
                content="""🎫 **Trip Type**: 
- 🔄 Round trip (going and coming back)
- ➡️ One way (not returning)

What type of trip is this?"""
            )

        state["messages"].append(msg)
        return state

    def ask_dates(state: TripPlanningState) -> TripPlanningState:
        """Ask about trip dates"""
        user_msg = state["messages"][-1].content.lower()

        if "round" in user_msg or "return" in user_msg:
            state["trip_type"] = TripType.ROUND_TRIP
            state["current_step"] = "dates_round"
            msg = AIMessage(
                content="""📅 **Travel Dates**: 
            
Please provide:
- Departure date
- Return date

Example: "Leave on December 15, return January 5" or "Dec 15 - Jan 5" """
            )
        elif "one way" in user_msg or "oneway" in user_msg:
            state["trip_type"] = TripType.ONE_WAY
            state["current_step"] = "dates_oneway"
            msg = AIMessage(
                content="""📅 **Departure Date**: When would you like to leave?

Example: "December 15" or "Dec 15, 2024" """
            )
        else:
            msg = AIMessage(content="Please choose: Round trip or One way")
            state["messages"].append(msg)
            return state

        state["completed_steps"].append("trip_type")
        state["messages"].append(msg)
        return state

    def ask_activities(state: TripPlanningState) -> TripPlanningState:
        """Ask about activity preferences"""
        user_msg = state["messages"][-1].content

        # Handle date parsing (simplified)
        if state["current_step"] in ["dates_round", "dates_oneway"]:
            if state["trip_type"] == TripType.ROUND_TRIP:
                state["departure_date"] = user_msg  # In production, parse properly
                state["return_date"] = user_msg  # In production, parse properly
            else:
                state["departure_date"] = user_msg

            state["current_step"] = "activities"
            state["completed_steps"].append("dates")

            msg = AIMessage(
                content="""🎯 **Activities**: What activities interest you? (Select multiple)

🏖️ **Beaches** - Sun, sand, and relaxation
🏛️ **City sightseeing** - Museums, landmarks, culture  
🥾 **Outdoor adventures** - Hiking, nature, sports
🎉 **Festivals/events** - Local celebrations, concerts
🍽️ **Food exploration** - Local cuisine, food tours
🌙 **Nightlife** - Bars, clubs, entertainment
🛍️ **Shopping** - Markets, malls, souvenirs
💆 **Spa wellness** - Relaxation, massage, wellness

Just list what interests you! (e.g., "beaches, food, nightlife")"""
            )
        else:
            # Parse activities
            activities = []
            activity_map = {
                "beach": ActivityType.BEACHES,
                "city": ActivityType.CITY_SIGHTSEEING,
                "sight": ActivityType.CITY_SIGHTSEEING,
                "hiking": ActivityType.OUTDOOR_ADVENTURES,
                "outdoor": ActivityType.OUTDOOR_ADVENTURES,
                "festival": ActivityType.FESTIVALS,
                "food": ActivityType.FOOD_EXPLORATION,
                "restaurant": ActivityType.FOOD_EXPLORATION,
                "nightlife": ActivityType.NIGHTLIFE,
                "shopping": ActivityType.SHOPPING,
                "spa": ActivityType.SPA_WELLNESS,
                "massage": ActivityType.SPA_WELLNESS,
                "wellness": ActivityType.SPA_WELLNESS,
            }

            for keyword, activity in activity_map.items():
                if keyword in user_msg.lower():
                    activities.append(activity)

            state["activities"] = activities
            state["current_step"] = "budget"
            state["completed_steps"].append("activities")

            activity_list = (
                ", ".join([a.value for a in activities])
                if activities
                else "general activities"
            )
            msg = AIMessage(
                content=f"""Great! You're interested in: {activity_list}

💰 **Budget**: What's your budget range per person?
- 💵 Budget-friendly ($50-100/day)
- 💳 Mid-range ($100-300/day)  
- 💎 Luxury ($300+/day)
- Or tell me a specific amount

What works for you?"""
            )

        state["messages"].append(msg)
        return state

    def ask_dietary(state: TripPlanningState) -> TripPlanningState:
        """Ask about dietary preferences"""
        user_msg = state["messages"][-1].content.lower()

        state["budget"] = user_msg  # Store budget info
        state["current_step"] = "diet"
        state["completed_steps"].append("budget")

        msg = AIMessage(
            content="""🥗 **Dietary Preferences**: Do you have any dietary restrictions?

- 🕌 Halal
- 🌱 Vegetarian
- 🌾 Gluten-free  
- ❌ No restrictions

You can select multiple or say "none"."""
        )

        state["messages"].append(msg)
        return state

    def complete_planning(state: TripPlanningState) -> TripPlanningState:
        """Complete the trip planning process"""
        user_msg = state["messages"][-1].content.lower()

        # Parse dietary preferences
        diet_prefs = []
        if "halal" in user_msg:
            diet_prefs.append(DietType.HALAL)
        if "vegetarian" in user_msg:
            diet_prefs.append(DietType.VEGETARIAN)
        if "gluten" in user_msg:
            diet_prefs.append(DietType.GLUTEN_FREE)
        if not diet_prefs or "none" in user_msg or "no restriction" in user_msg:
            diet_prefs.append(DietType.NO_RESTRICTIONS)

        state["diet_preferences"] = diet_prefs
        state["current_step"] = "complete"
        state["completed_steps"].append("diet")

        # Generate summary
        summary = f"""🎉 **Trip Planning Complete!** Here's your itinerary summary:

🚗 **Transport**: {state.get('transport_type', 'N/A').value if state.get('transport_type') else 'N/A'}
{f"✈️ **Flight**: {state.get('flight_class', 'N/A').value if state.get('flight_class') else 'N/A'} class, {state.get('flight_type', 'N/A')}" if state.get('transport_type') == TransportType.PLANE else ""}
👥 **Travelers**: {state.get('adults', 0)} adult(s){f", {state.get('children', 0)} child(ren)" if state.get('children', 0) > 0 else ""}
🌍 **Destination**: {state.get('destination', 'N/A')}
🏠 **From**: {state.get('departure_location', 'N/A')}
🎫 **Trip Type**: {state.get('trip_type', 'N/A').value if state.get('trip_type') else 'N/A'}
📅 **Dates**: {state.get('departure_date', 'N/A')}{f" - {state.get('return_date')}" if state.get('return_date') else ""}
🎯 **Activities**: {', '.join([a.value for a in state.get('activities', [])]) if state.get('activities') else 'General sightseeing'}
💰 **Budget**: {state.get('budget', 'N/A')}
🥗 **Diet**: {', '.join([d.value for d in state.get('diet_preferences', [])]) if state.get('diet_preferences') else 'No restrictions'}

🌟 **Next Steps**: 
- I can now search for hidden gems and local experiences in {state.get('destination', 'your destination')}
- Check visa requirements if traveling internationally
- Find local transportation and accommodation options

Would you like me to start finding places and experiences for your trip?"""

        msg = AIMessage(content=summary)
        state["messages"].append(msg)
        return state

    def route_conversation(state: TripPlanningState) -> str:
        """Route the conversation based on current step"""
        current_step = state.get("current_step", "start")

        if current_step == "start" or not current_step:
            return "start_planning"
        elif current_step == "transport":
            return "ask_transport"
        elif current_step in ["flight_class", "flight_type"]:
            return "ask_flight_details"
        elif current_step == "travelers":
            return "ask_travelers"
        elif current_step in ["destination", "departure"]:
            return "ask_destination"
        elif current_step == "trip_type":
            return "ask_dates"
        elif current_step in ["dates_round", "dates_oneway", "activities"]:
            return "ask_activities"
        elif current_step == "budget":
            return "ask_dietary"
        elif current_step == "diet":
            return "complete_planning"
        else:
            return END

    # Build the workflow
    workflow = StateGraph(TripPlanningState)

    # Add nodes
    workflow.add_node("start_planning", start_planning)
    workflow.add_node("ask_transport", ask_transport)
    workflow.add_node("ask_flight_details", ask_flight_details)
    workflow.add_node("ask_travelers", ask_travelers)
    workflow.add_node("ask_destination", ask_destination)
    workflow.add_node("ask_dates", ask_dates)
    workflow.add_node("ask_activities", ask_activities)
    workflow.add_node("ask_dietary", ask_dietary)
    workflow.add_node("complete_planning", complete_planning)

    # Set entry point
    workflow.set_entry_point("start_planning")

    # Add conditional routing
    workflow.add_conditional_edges(
        "start_planning",
        route_conversation,
        {
            "start_planning": "start_planning",
            "ask_transport": "ask_transport",
            "ask_flight_details": "ask_flight_details",
            "ask_travelers": "ask_travelers",
            "ask_destination": "ask_destination",
            "ask_dates": "ask_dates",
            "ask_activities": "ask_activities",
            "ask_dietary": "ask_dietary",
            "complete_planning": "complete_planning",
            END: END,
        },
    )

    # Add edges from each node back to routing
    for node in [
        "ask_transport",
        "ask_flight_details",
        "ask_travelers",
        "ask_destination",
        "ask_dates",
        "ask_activities",
        "ask_dietary",
    ]:
        workflow.add_conditional_edges(
            node,
            route_conversation,
            {
                "start_planning": "start_planning",
                "ask_transport": "ask_transport",
                "ask_flight_details": "ask_flight_details",
                "ask_travelers": "ask_travelers",
                "ask_destination": "ask_destination",
                "ask_dates": "ask_dates",
                "ask_activities": "ask_activities",
                "ask_dietary": "ask_dietary",
                "complete_planning": "complete_planning",
                END: END,
            },
        )

    workflow.add_edge("complete_planning", END)

    return workflow.compile()


# Initialize the workflow
trip_planner = create_trip_planning_workflow()


# Utils
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


# Services
async def fetch_opentripmap(lat: float, lon: float, radius: int) -> List[Place]:
    api_key = os.getenv("OPENTRIPMAP_API_KEY", "")
    if not api_key:
        return []

    url = f"https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "apikey": api_key,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": 50,
        "rate": 2,
        "kinds": "interesting_places,museums,monuments,architecture",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            places = []
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                geom = feature.get("geometry", {})
                coords = geom.get("coordinates", [None, None])

                if coords[0] and coords[1] and props.get("name"):
                    places.append(
                        Place(
                            id=f"otm:{props.get('xid', 'unknown')}",
                            name=props.get("name"),
                            lat=coords[1],
                            lon=coords[0],
                            categories=props.get("kinds", "").split(","),
                            rating=props.get("rate"),
                            source="OpenTripMap",
                        )
                    )
            return places
        except Exception as e:
            print(f"OpenTripMap error: {e}")
            return []


async def fetch_overpass(lat: float, lon: float, radius: int) -> List[Place]:
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"](around:{radius},{lat},{lon});
      way["tourism"](around:{radius},{lat},{lon});
      relation["tourism"](around:{radius},{lat},{lon});
      node["amenity"](around:{radius},{lat},{lon});
      way["amenity"](around:{radius},{lat},{lon});
      relation["amenity"](around:{radius},{lat},{lon});
    );
    out center 50;
    """

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                data=query,
                headers={"Content-Type": "text/plain"},
            )
            response.raise_for_status()
            data = response.json()

            places = []
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                name = tags.get("name")

                # extract coords: node has lat/lon, ways/relations have 'center'
                lat_e = element.get("lat") or (element.get("center") or {}).get("lat")
                lon_e = element.get("lon") or (element.get("center") or {}).get("lon")

                if name and lat_e is not None and lon_e is not None:
                    categories = []
                    if tags.get("tourism"):
                        categories.append(tags["tourism"])
                    if tags.get("amenity"):
                        categories.append(tags["amenity"])
                    if tags.get("cuisine"):
                        categories.append(tags["cuisine"])

                    places.append(
                        Place(
                            id=f"osm:{element.get('id')}",
                            name=name,
                            lat=lat_e,
                            lon=lon_e,
                            categories=categories,
                            source="OpenStreetMap",
                        )
                    )
            return places
        except Exception as e:
            print(f"Overpass error: {e}")
            return []


def merge_places(places_list: List[List[Place]]) -> List[Place]:
    """Simple deduplication by distance"""
    all_places = []
    for places in places_list:
        all_places.extend(places)

    unique_places = []
    for place in all_places:
        is_duplicate = False
        for existing in unique_places:
            distance = haversine(place.lat, place.lon, existing.lat, existing.lon)
            if distance < 50:  # 50m threshold
                is_duplicate = True
                break

        if not is_duplicate:
            unique_places.append(place)

    return unique_places


# Endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat/trip-planning", response_model=ChatResponse)
async def chat_trip_planning(request: ChatRequest):
    """Interactive trip planning chat"""
    import uuid

    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())

    # Get or create session state
    if session_id not in trip_sessions:
        trip_sessions[session_id] = TripPlanningState(
            messages=[],
            current_step="transport",
            activities=[],
            diet_preferences=[],
            completed_steps=[],
        )

    state = trip_sessions[session_id]

    # Add user message to state
    user_msg = HumanMessage(content=request.message)
    state["messages"].append(user_msg)

    try:
        # Initialize state if it's the first message
        if not state.get("current_step"):
            state["current_step"] = "transport"
            state["activities"] = []
            state["diet_preferences"] = []

            # Welcome message
            welcome_response = """🌟 Welcome to your AI Trip Planner! 

I'll help you plan the perfect trip by asking you a few questions. Let's start!

🚗 **Transportation**: How would you like to travel?
- ✈️ Plane
- 🚗 Car  
- 🚆 Train
- 🚌 Bus

Just type your preference (e.g., "plane" or "car")"""

            state["messages"] = [AIMessage(content=welcome_response)]

            return ChatResponse(
                response=welcome_response,
                session_id=session_id,
                suggestions=["Plane", "Car", "Train", "Bus"],
                is_complete=False,
            )

        # Process the message using simplified planner
        updated_state = simple_trip_planner(state, request.message)

        # Update session state
        trip_sessions[session_id] = updated_state

        # Get the latest AI response
        response_content = (
            updated_state["messages"][-1].content
            if updated_state["messages"]
            else "Let's continue planning!"
        )

        # Check if planning is complete
        is_complete = updated_state.get("current_step") == "complete"

        # Generate suggestions based on current step
        suggestions = []
        current_step = updated_state.get("current_step", "")

        if current_step == "transport":
            suggestions = ["Plane", "Car", "Train", "Bus"]
        elif current_step == "flight_class":
            suggestions = ["Economy", "Business", "First Class"]
        elif current_step == "flight_type":
            suggestions = ["Direct flights", "Flights with transit"]
        elif current_step == "travelers":
            suggestions = ["Solo", "2 adults", "Family with kids"]
        elif current_step == "trip_type":
            suggestions = ["Round trip", "One way"]
        elif current_step == "activities":
            suggestions = [
                "Beaches",
                "City sightseeing",
                "Food exploration",
                "Nightlife",
                "Shopping",
            ]
        elif current_step == "budget":
            suggestions = ["Budget-friendly", "Mid-range", "Luxury"]
        elif current_step == "diet":
            suggestions = ["Halal", "Vegetarian", "Gluten-free", "No restrictions"]
        elif is_complete:
            suggestions = [
                "Find hidden places",
                "Check visa requirements",
                "Plan itinerary",
            ]

        return ChatResponse(
            response=response_content,
            session_id=session_id,
            suggestions=suggestions,
            is_complete=is_complete,
        )

    except Exception as e:
        # Handle errors gracefully
        error_response = f"I encountered an issue: {str(e)}. Let's try again!"
        return ChatResponse(
            response=error_response,
            session_id=session_id,
            suggestions=["Start over"],
            is_complete=False,
        )


@app.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session state"""
    if session_id not in trip_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = trip_sessions[session_id]
    return {
        "session_id": session_id,
        "current_step": state.get("current_step"),
        "completed_steps": state.get("completed_steps", []),
        "trip_summary": {
            "transport": state.get("transport_type"),
            "destination": state.get("destination"),
            "travelers": f"{state.get('adults', 0)} adults, {state.get('children', 0)} children",
            "budget": state.get("budget"),
            "activities": [a.value for a in state.get("activities", [])],
            "diet_preferences": [d.value for d in state.get("diet_preferences", [])],
        },
    }


@app.post("/visa/rank/custom")
async def visa_rank_custom(body: RankWeights):
    """Get custom passport ranking based on visa-free access weights"""
    try:
        data = await get_custom_passport_rank(body.weights)
        return data
    except VisaApiError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/visa/check")
async def visa_check(
    passport: str = Query(
        ..., min_length=2, max_length=2, description="ISO2 of passport, e.g., KZ"
    ),
    destination: str = Query(
        ..., min_length=2, max_length=2, description="ISO2 of destination, e.g., KR"
    ),
):
    """Check visa requirement for passport holder traveling to destination"""
    try:
        data = await get_visa_requirement(passport, destination)
        return {
            "passport": passport.upper(),
            "destination": destination.upper(),
            "result": data,
        }
    except VisaApiError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# AI-Powered Travel Recommendations
class TripRecommendationRequest(BaseModel):
    session_id: str
    include_places: bool = True
    include_itinerary: bool = True
    include_tips: bool = True


class TripRecommendationResponse(BaseModel):
    session_id: str
    destination: str
    recommendations: str
    suggested_places: List[str] = []
    daily_itinerary: List[str] = []
    travel_tips: List[str] = []


class SmartQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class SmartQueryResponse(BaseModel):
    answer: str
    suggestions: List[str] = []
    related_actions: List[str] = []


@app.post("/ai/smart-query", response_model=SmartQueryResponse)
async def smart_travel_query(request: SmartQueryRequest):
    """Answer travel questions using AI with context awareness"""

    context_info = ""
    if request.context:
        context_info = f"Additional context: {request.context}"

    prompt = f"""You are an expert travel advisor AI. Answer the following travel question concisely and helpfully:

Question: {request.query}
{context_info}

Provide a clear, practical answer. If the question is about specific destinations, include relevant tips.
If the question is vague, ask clarifying questions. Keep responses under 200 words but informative.
"""

    try:
        response = await openai_llm.ainvoke([HumanMessage(content=prompt)])

        # Generate suggestions based on the query
        suggestions = []
        if any(
            word in request.query.lower()
            for word in ["where", "destination", "travel", "visit"]
        ):
            suggestions = [
                "Get trip recommendations",
                "Plan full itinerary",
                "Check visa requirements",
            ]
        elif any(
            word in request.query.lower()
            for word in ["budget", "cost", "price", "money"]
        ):
            suggestions = [
                "Budget planning tips",
                "Find budget destinations",
                "Cost breakdown",
            ]
        elif any(
            word in request.query.lower() for word in ["food", "restaurant", "cuisine"]
        ):
            suggestions = [
                "Local food recommendations",
                "Dietary restrictions help",
                "Restaurant finder",
            ]
        else:
            suggestions = [
                "Start trip planning",
                "Discover places",
                "Get recommendations",
            ]

        related_actions = [
            "Start new trip planning",
            "Discover places nearby",
            "Get AI recommendations",
        ]

        return SmartQueryResponse(
            answer=response.content,
            suggestions=suggestions,
            related_actions=related_actions,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query error: {str(e)}")


@app.post("/ai/trip-recommendations", response_model=TripRecommendationResponse)
async def get_ai_trip_recommendations(request: TripRecommendationRequest):
    """Get AI-powered personalized trip recommendations"""

    # Get session data
    if request.session_id not in trip_sessions:
        raise HTTPException(status_code=404, detail="Trip session not found")

    session = trip_sessions[request.session_id]

    if not session.get("current_step") == "complete":
        raise HTTPException(status_code=400, detail="Trip planning not completed yet")

    # Build context from session data
    trip_context = f"""
    Destination: {session.get('destination', 'Unknown')}
    Travelers: {session.get('adults', 0)} adults, {session.get('children', 0)} children
    Transport: {session.get('transport_type', 'Unknown')}
    Budget: {session.get('budget', 'Unknown')}
    Activities: {', '.join([a.value for a in session.get('activities', [])]) if session.get('activities') else 'General sightseeing'}
    Dietary preferences: {', '.join([d.value for d in session.get('diet_preferences', [])]) if session.get('diet_preferences') else 'None'}
    Trip dates: {session.get('departure_date', 'Not specified')}
    Trip type: {session.get('trip_type', 'Unknown')}
    Departure location: {session.get('departure_location', 'Unknown')}
    """

    try:
        # Create AI recommendations
        if request.include_places:
            places_prompt = f"""Based on this trip information:
{trip_context}

Suggest 5-7 specific must-visit places in {session.get('destination', 'the destination')} that match their interests. 
Be specific with place names and briefly explain why each place fits their preferences.
Format as a simple list with place names."""

            places_response = await openai_llm.ainvoke(
                [HumanMessage(content=places_prompt)]
            )
            suggested_places = [
                place.strip()
                for place in places_response.content.split("\n")
                if place.strip() and not place.strip().startswith("Based on")
            ]
        else:
            suggested_places = []

        if request.include_itinerary:
            itinerary_prompt = f"""Based on this trip information:
{trip_context}

Create a day-by-day itinerary suggestion for their trip to {session.get('destination', 'the destination')}. 
Consider their budget, interests, and travel style. Provide 3-5 days of recommendations.
Format as: "Day 1: Morning - ..., Afternoon - ..., Evening - ..." """

            itinerary_response = await openai_llm.ainvoke(
                [HumanMessage(content=itinerary_prompt)]
            )
            daily_itinerary = [
                day.strip()
                for day in itinerary_response.content.split("\n")
                if day.strip() and "Day" in day
            ]
        else:
            daily_itinerary = []

        if request.include_tips:
            tips_prompt = f"""Based on this trip information:
{trip_context}

Provide 5-7 practical travel tips specific to {session.get('destination', 'the destination')} considering their budget, 
dietary preferences, and travel style. Include tips about local customs, transportation, food, and money-saving advice.
Format as bullet points."""

            tips_response = await openai_llm.ainvoke(
                [HumanMessage(content=tips_prompt)]
            )
            travel_tips = [
                tip.strip().lstrip("•-*")
                for tip in tips_response.content.split("\n")
                if tip.strip() and not tip.strip().startswith("Based on")
            ]
        else:
            travel_tips = []

        # Generate overall recommendations
        main_prompt = f"""As an expert travel advisor, create personalized recommendations for this trip:
{trip_context}

Provide a comprehensive but concise travel recommendation that includes:
1. Why this destination is perfect for them
2. Best travel approach considering their transport and budget
3. Highlights they shouldn't miss based on their interests
4. Any special considerations for their group

Keep it engaging and practical, around 200-300 words."""

        main_response = await openai_llm.ainvoke([HumanMessage(content=main_prompt)])

        return TripRecommendationResponse(
            session_id=request.session_id,
            destination=session.get("destination", "Unknown"),
            recommendations=main_response.content,
            suggested_places=suggested_places[:7],
            daily_itinerary=daily_itinerary[:5],
            travel_tips=travel_tips[:7],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI recommendation error: {str(e)}"
        )


@app.post("/discover", response_model=DiscoverResponse)
async def discover_places(request: DiscoverRequest):
    """Discover hidden places near coordinates"""

    # Fetch from multiple sources
    otm_task = fetch_opentripmap(request.lat, request.lon, request.radius_m)
    osm_task = fetch_overpass(request.lat, request.lon, request.radius_m)

    otm_places, osm_places = await asyncio.gather(otm_task, osm_task)

    # Merge and deduplicate
    merged_places = merge_places([otm_places, osm_places])

    # Sort by distance
    for place in merged_places:
        place.distance = haversine(request.lat, request.lon, place.lat, place.lon)

    merged_places.sort(key=lambda p: getattr(p, "distance", 0))

    return DiscoverResponse(places=merged_places[:30])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
