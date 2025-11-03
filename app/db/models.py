"""Database models for the travel planning application."""

# Enums
import enum
import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import VARCHAR, TypeDecorator

from app.db.database import Base


class TransportType(str, enum.Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    CAR = "car"
    BOAT = "boat"


class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ItineraryItemType(str, enum.Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    ACTIVITY = "activity"
    NOTE = "note"


# Custom type for SQLite compatibility with arrays
class JSONArray(TypeDecorator):
    """SQLite-compatible array type that stores arrays as JSON strings."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


# UUID type for SQLite
try:
    from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

    UUID = PostgresUUID
except ImportError:
    UUID = String(36)  # Use String for SQLite


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    trips = relationship("Trip", back_populates="user")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    from_city = Column(String(100), nullable=False)
    to_city = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    transport = Column(Enum(TransportType), nullable=False)
    adults = Column(Integer, nullable=False, default=1)
    children = Column(Integer, nullable=False, default=0)
    budget_min = Column(Numeric(10, 2), nullable=True)
    budget_max = Column(Numeric(10, 2), nullable=True)
    entertainment_tags = Column(JSONArray, nullable=True)  # SQLite-compatible array
    notes = Column(Text, nullable=True)
    status = Column(Enum(TripStatus), nullable=False, default=TripStatus.DRAFT)
    timezone = Column(String(50), nullable=True)
    ics_token = Column(String(36), default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Selected flight information
    selected_flight_id = Column(String(255), nullable=True)
    selected_flight_airline = Column(String(100), nullable=True)
    selected_flight_number = Column(String(50), nullable=True)
    selected_flight_departure_airport = Column(String(10), nullable=True)
    selected_flight_arrival_airport = Column(String(10), nullable=True)
    selected_flight_departure_time = Column(DateTime(timezone=True), nullable=True)
    selected_flight_arrival_time = Column(DateTime(timezone=True), nullable=True)
    selected_flight_price = Column(Numeric(10, 2), nullable=True)
    selected_flight_currency = Column(String(10), nullable=True)
    selected_flight_duration_min = Column(Integer, nullable=True)
    selected_flight_stops = Column(Integer, nullable=True)
    selected_flight_score = Column(Numeric(3, 2), nullable=True)
    selected_flight_title = Column(String(255), nullable=True)
    selected_flight_pros = Column(JSON, nullable=True)  # Array of pros keywords
    selected_flight_cons = Column(JSON, nullable=True)  # Array of cons keywords

    # Selected hotel information
    selected_hotel_id = Column(String(255), nullable=True)
    selected_hotel_name = Column(String(255), nullable=True)
    selected_hotel_location = Column(String(500), nullable=True)
    selected_hotel_price_per_night = Column(Numeric(10, 2), nullable=True)
    selected_hotel_total_price = Column(Numeric(10, 2), nullable=True)
    selected_hotel_currency = Column(String(10), nullable=True)
    selected_hotel_check_in = Column(String(50), nullable=True)
    selected_hotel_check_out = Column(String(50), nullable=True)
    selected_hotel_rating = Column(Numeric(3, 2), nullable=True)
    selected_hotel_reviews_count = Column(Integer, nullable=True)
    selected_hotel_class = Column(Integer, nullable=True)
    selected_hotel_amenities = Column(JSON, nullable=True)  # Array of amenities
    selected_hotel_free_cancellation = Column(Boolean, nullable=True)
    selected_hotel_score = Column(Numeric(3, 2), nullable=True)
    selected_hotel_title = Column(String(255), nullable=True)
    selected_hotel_pros = Column(JSON, nullable=True)  # Array of pros keywords
    selected_hotel_cons = Column(JSON, nullable=True)  # Array of cons keywords
    selected_hotel_thumbnail = Column(String(1000), nullable=True)

    # Relationships
    user = relationship("User", back_populates="trips")
    flight_searches = relationship("FlightSearch", back_populates="trip")
    hotel_searches = relationship("HotelSearch", back_populates="trip")
    activity_searches = relationship("ActivitySearch", back_populates="trip")
    itinerary_items = relationship("ItineraryItem", back_populates="trip")


class FlightSearch(Base):
    __tablename__ = "flight_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    query = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="flight_searches")
    options = relationship("FlightOption", back_populates="search")


class FlightOption(Base):
    __tablename__ = "flight_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id = Column(String(36), ForeignKey("flight_searches.id"), nullable=False)
    provider = Column(String(100), nullable=False)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)
    payload = Column(JSON, nullable=False)
    pros = Column(JSONArray, nullable=True)  # SQLite-compatible array
    cons = Column(JSONArray, nullable=True)  # SQLite-compatible array
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    search = relationship("FlightSearch", back_populates="options")
    selections = relationship("FlightSelection", back_populates="option")


class FlightSelection(Base):
    __tablename__ = "flight_selections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    option_id = Column(String(36), ForeignKey("flight_options.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    option = relationship("FlightOption", back_populates="selections")


class HotelSearch(Base):
    __tablename__ = "hotel_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    query = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="hotel_searches")
    options = relationship("HotelOption", back_populates="search")


class HotelOption(Base):
    __tablename__ = "hotel_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id = Column(String(36), ForeignKey("hotel_searches.id"), nullable=False)
    provider = Column(String(100), nullable=False)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)
    payload = Column(JSON, nullable=False)
    pros = Column(JSONArray, nullable=True)  # SQLite-compatible array
    cons = Column(JSONArray, nullable=True)  # SQLite-compatible array
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    search = relationship("HotelSearch", back_populates="options")
    selections = relationship("HotelSelection", back_populates="option")


class HotelSelection(Base):
    __tablename__ = "hotel_selections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    option_id = Column(String(36), ForeignKey("hotel_options.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    option = relationship("HotelOption", back_populates="selections")


class ActivitySearch(Base):
    __tablename__ = "activity_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    query = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="activity_searches")
    activities = relationship("Activity", back_populates="search")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id = Column(String(36), ForeignKey("activity_searches.id"), nullable=False)
    provider = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    pros = Column(JSONArray, nullable=True)  # SQLite-compatible array
    cons = Column(JSONArray, nullable=True)  # SQLite-compatible array
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    search = relationship("ActivitySearch", back_populates="activities")


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    day_date = Column(DateTime(timezone=True), nullable=False)
    type = Column(Enum(ItineraryItemType), nullable=False)
    ref_table = Column(String(50), nullable=True)
    ref_id = Column(String(36), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="itinerary_items")


class TripPlan(Base):
    __tablename__ = "trip_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    plan_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TripChecklist(Base):
    __tablename__ = "trip_checklists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    checklist_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CultureTip(Base):
    __tablename__ = "culture_tips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_code = Column(String(3), nullable=False, index=True)
    content_md = Column(Text, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Calendar integration models
class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    google_user_id = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tokens = relationship("GoogleToken", back_populates="account")


class GoogleToken(Base):
    __tablename__ = "google_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_account_id = Column(
        String(36), ForeignKey("google_accounts.id"), nullable=False
    )
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), nullable=False, default="Bearer")
    scope = Column(String(500), nullable=True)
    expiry = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    account = relationship("GoogleAccount", back_populates="tokens")


class CalendarBinding(Base):
    __tablename__ = "calendar_bindings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    google_account_id = Column(
        String(36), ForeignKey("google_accounts.id"), nullable=False
    )
    calendar_id = Column(String(255), nullable=False)
    sync_mode = Column(String(20), nullable=False)  # "push" or "ics"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    itinerary_item_id = Column(
        String(36), ForeignKey("itinerary_items.id"), nullable=False
    )
    google_event_id = Column(String(255), nullable=False)
    etag = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
