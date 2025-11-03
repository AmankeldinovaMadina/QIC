"""Router for entertainment venues search, ranking, and selection."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import User, get_async_session, EntertainmentSelection
from app.entertainment.ai_ranker import OpenAIEntertainmentRanker
from app.entertainment.schemas import (
    EntertainmentRankRequest,
    EntertainmentRankResponse,
    EntertainmentSearchRequest,
    EntertainmentSearchResponse,
    EntertainmentSelectionRequest,
    EntertainmentSelectionResponse,
)
from app.entertainment.service import google_maps_service
from app.trips.service import trips_service

router = APIRouter(prefix="/entertainment", tags=["entertainment"])


@router.post("/search", response_model=EntertainmentSearchResponse)
async def search_entertainment_venues(
    req: EntertainmentSearchRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Search for entertainment venues using Google Maps API."""
    try:
        # Verify trip exists and user owns it
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        print(f"🎭 Searching entertainment for trip {req.trip_id} in {req.destination}")

        # Fetch venues from Google Maps
        result = await google_maps_service.search_venues(
            request=req,
            entertainment_tags=trip.entertainment_tags
        )

        print(f"✅ Found {result.total_results} venues")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR in search_entertainment_venues: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rank", response_model=EntertainmentRankResponse)
async def rank_entertainment_venues(
    req: EntertainmentRankRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Rank entertainment venues using AI."""
    try:
        # Verify trip exists and user owns it
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        print(f"🤖 Ranking {len(req.venues)} venues for trip {req.trip_id}")

        # Use trip's entertainment_tags if not provided in request
        if not req.entertainment_tags and trip.entertainment_tags:
            req.entertainment_tags = trip.entertainment_tags

        # Rank venues using AI
        ranker = OpenAIEntertainmentRanker()
        result = await ranker.rank_venues(req)

        print(f"✅ Ranked venues with model: {result.meta.used_model}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR in rank_entertainment_venues: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select", response_model=EntertainmentSelectionResponse)
async def select_entertainment_venues(
    req: EntertainmentSelectionRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Select multiple entertainment venues and save to trip."""
    try:
        print(f"🎭 Selecting {len(req.selections)} venues for trip {req.trip_id}")

        # Get the trip and verify ownership
        trip = await trips_service.get_trip_by_id(session, req.trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        print(f"✅ Trip found: {trip.from_city} → {trip.to_city}")

        # Create EntertainmentSelection records
        created_selections = []

        for selection_data in req.selections:
            # Extract venue data
            venue = selection_data.get("venue", {})
            ranking = selection_data.get("ranking", {})

            # Create selection record
            selection = EntertainmentSelection(
                trip_id=req.trip_id,
                venue_id=venue.get("place_id", ""),
                venue_name=venue.get("title", "Unknown Venue"),
                venue_type=venue.get("type"),
                address=venue.get("address"),
                rating=venue.get("rating"),
                reviews_count=venue.get("reviews"),
                price_level=venue.get("price"),
                latitude=venue.get("gps_coordinates", {}).get("latitude") if venue.get("gps_coordinates") else None,
                longitude=venue.get("gps_coordinates", {}).get("longitude") if venue.get("gps_coordinates") else None,
                website=venue.get("website"),
                phone=venue.get("phone"),
                opening_hours=venue.get("operating_hours"),
                types=venue.get("types"),
                description=venue.get("description"),
                thumbnail=venue.get("thumbnail"),
                score=ranking.get("score"),
                title=ranking.get("title"),
                pros_keywords=ranking.get("pros_keywords"),
                cons_keywords=ranking.get("cons_keywords"),
            )

            session.add(selection)
            created_selections.append(selection)

        # Also update trip's selected_entertainments JSON for quick access
        if trip.selected_entertainments is None:
            trip.selected_entertainments = []

        # Append new selections (avoid duplicates by place_id)
        existing_ids = {e.get("place_id") for e in trip.selected_entertainments if isinstance(e, dict)}
        
        for selection_data in req.selections:
            venue = selection_data.get("venue", {})
            place_id = venue.get("place_id")
            if place_id and place_id not in existing_ids:
                trip.selected_entertainments.append(selection_data)

        # Mark as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(trip, "selected_entertainments")

        # Save to database
        await session.commit()

        # Refresh to get IDs
        for sel in created_selections:
            await session.refresh(sel)

        print(f"✅ Saved {len(created_selections)} entertainment selections!")

        # Build response
        response_selections = []
        for sel in created_selections:
            response_selections.append({
                "id": sel.id,
                "venue_name": sel.venue_name,
                "venue_type": sel.venue_type,
                "address": sel.address,
                "rating": float(sel.rating) if sel.rating else None,
                "price": sel.price_level,
                "score": float(sel.score) if sel.score else None,
                "title": sel.title,
            })

        return EntertainmentSelectionResponse(
            success=True,
            message=f"Successfully added {len(created_selections)} entertainment venues to trip",
            trip_id=trip.id,
            selected_count=len(created_selections),
            selections=response_selections,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR in select_entertainment_venues: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trip_id}/selections")
async def get_entertainment_selections(
    trip_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get all entertainment selections for a trip."""
    try:
        # Verify trip exists and user owns it
        trip = await trips_service.get_trip_by_id(session, trip_id, current_user.id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        # Query selections
        from sqlalchemy import select
        stmt = select(EntertainmentSelection).where(EntertainmentSelection.trip_id == trip_id)
        result = await session.execute(stmt)
        selections = result.scalars().all()

        # Build response
        selections_data = []
        for sel in selections:
            selections_data.append({
                "id": sel.id,
                "venue_id": sel.venue_id,
                "venue_name": sel.venue_name,
                "venue_type": sel.venue_type,
                "address": sel.address,
                "rating": float(sel.rating) if sel.rating else None,
                "reviews_count": sel.reviews_count,
                "price_level": sel.price_level,
                "latitude": float(sel.latitude) if sel.latitude else None,
                "longitude": float(sel.longitude) if sel.longitude else None,
                "website": sel.website,
                "phone": sel.phone,
                "types": sel.types,
                "description": sel.description,
                "thumbnail": sel.thumbnail,
                "score": float(sel.score) if sel.score else None,
                "title": sel.title,
                "pros_keywords": sel.pros_keywords,
                "cons_keywords": sel.cons_keywords,
                "created_at": sel.created_at.isoformat() if sel.created_at else None,
            })

        return {
            "trip_id": trip_id,
            "total_selections": len(selections_data),
            "selections": selections_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 ERROR in get_entertainment_selections: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
