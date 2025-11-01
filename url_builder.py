from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import math
import urllib.parse
import os, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

# pip install geopy airports-py
from geopy.geocoders import Nominatim
from airports import airport_data  # from airports-py

# ---------- helpers ----------

# Prefer large airports, then medium, then small, then everything else
TYPE_RANK = {
    "large_airport": 0,
    "medium_airport": 1,
    "small_airport": 2,
}
DEFAULT_TYPE_RANK = 3

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def geocode_city(city: str) -> Tuple[float, float]:
    """
    Geocode a city to (lat, lon) using geopy's Nominatim.
    NOTE: Nominatim requires a descriptive user_agent for fair use.
    """
    geocoder = Nominatim(user_agent="qic-trip-url-builder/1.0 (contact: your-email@example.com)")
    loc = geocoder.geocode(city)
    if not loc:
        raise ValueError(f"Could not geocode city: {city!r}")
    return (loc.latitude, loc.longitude)

def best_airports_near(
    lat: float,
    lon: float,
    radius_km: int = 150,
    limit: int = 1,
    require_iata: bool = True,
) -> List[Dict[str, Any]]:
    """
    Use airports-py's proximity search, then sort by (type_rank, distance).
    Return up to `limit` airports.
    """
    nearby: List[Dict[str, Any]] = airport_data.find_nearby_airports(lat, lon, radius_km)  # airports-py
    # Filter to those with IATA if requested
    cleaned = []
    for ap in nearby:
        iata = (ap.get("iata") or "").strip().upper()
        if require_iata and not iata:
            continue
        ap_lat = float(ap.get("latitude"))
        ap_lon = float(ap.get("longitude"))
        d_km = haversine_km(lat, lon, ap_lat, ap_lon)
        ap_type = (ap.get("type") or "").strip().lower()
        rank = TYPE_RANK.get(ap_type, DEFAULT_TYPE_RANK)
        cleaned.append({**ap, "distance_km": d_km, "type_rank": rank, "iata": iata})
    cleaned.sort(key=lambda a: (a["type_rank"], a["distance_km"]))
    return cleaned[:limit]

def to_yymmdd(date_str: str) -> str:
    """
    Accept 'YYYY-MM-DD', 'YYYYMMDD', or 'YYMMDD' and return 'YYMMDD'.
    """
    s = date_str.strip()
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        y, m, d = s.split("-")
        return f"{int(y)%100:02d}{int(m):02d}{int(d):02d}"
    if len(s) == 8 and s.isdigit():  # YYYYMMDD
        return s[2:]
    if len(s) == 6 and s.isdigit():  # YYMMDD
        return s
    raise ValueError(f"Unsupported date format: {date_str!r}")

# ---------- main builder ----------

@dataclass
class TripFilters:
    origin_city: str
    destination_city: str
    outbound_date: str                # 'YYYY-MM-DD' / 'YYYYMMDD' / 'YYMMDD'
    return_date: Optional[str] = None # same formats; if None => one-way
    adults: Optional[int] = 1
    children: Optional[int] = None
    cabinclass: Optional[str] = "economy"  # economy|premiumeconomy|business|first
    outbound_alts: Optional[bool] = None
    inbound_alts: Optional[bool] = None
    fare_attributes: Optional[Iterable[str]] = None  # ['cabin-bag','checked-bag']
    airlines_exclude: Optional[Iterable[str | int]] = None
    prefer_directs: Optional[bool] = None
    market_domain: str = "www.skyscanner.qa"
    # nearby search
    nearby_radius_km: int = 150
    use_mac: bool = False            # if you want to include multiple airports in the city/area

def build_skyscanner_url_with_geocoded_airports(cfg: TripFilters) -> str:
    # 1) geocode cities
    o_lat, o_lon = geocode_city(cfg.origin_city)
    d_lat, d_lon = geocode_city(cfg.destination_city)

    # 2) pick airports (nearest, preferring large/medium/small)
    origin_choices = best_airports_near(o_lat, o_lon, radius_km=cfg.nearby_radius_km,
                                        limit=1 if not cfg.use_mac else 3)
    dest_choices   = best_airports_near(d_lat, d_lon, radius_km=cfg.nearby_radius_km,
                                        limit=1 if not cfg.use_mac else 3)

    if not origin_choices:
        raise RuntimeError(f"No nearby airports found for origin city '{cfg.origin_city}'.")
    if not dest_choices:
        raise RuntimeError(f"No nearby airports found for destination city '{cfg.destination_city}'.")

    # For Skyscanner path we need IATA codes; choose the top-ranked airport (or you could build a MAC)
    origin_iata = origin_choices[0]["iata"].lower()
    dest_iata   = dest_choices[0]["iata"].lower()

    out = to_yymmdd(cfg.outbound_date)
    path = f"/transport/flights/{origin_iata}/{dest_iata}/{out}/"

    query: Dict[str, str] = {}

    if cfg.return_date:
        ret = to_yymmdd(cfg.return_date)
        path += f"{ret}/"
        query["rtn"] = "1"

    if cfg.adults is not None:
        query["adultsv2"] = str(cfg.adults)
    if cfg.children is not None:
        query["childrenv2"] = str(cfg.children)
    if cfg.cabinclass:
        query["cabinclass"] = cfg.cabinclass

    if cfg.outbound_alts is not None:
        query["outboundaltsenabled"] = str(cfg.outbound_alts).lower()
    if cfg.inbound_alts is not None:
        query["inboundaltsenabled"] = str(cfg.inbound_alts).lower()

    if cfg.fare_attributes:
        query["fare-attributes"] = ",".join(cfg.fare_attributes)

    if cfg.airlines_exclude:
        query["airlines"] = ",".join(str(x) for x in cfg.airlines_exclude)

    if cfg.prefer_directs is not None:
        query["preferdirects"] = str(cfg.prefer_directs).lower()

    base = f"https://{cfg.market_domain}"
    return base + path + "?" + urllib.parse.urlencode(query)

# ---------- example ----------

if __name__ == "__main__":
    cfg = TripFilters(
        origin_city="Doha",
        destination_city="Krakow",
        outbound_date="2025-10-30",
        return_date="2025-10-31",
        adults=1,
        cabinclass="economy",
        outbound_alts=False,
        inbound_alts=False,
        fare_attributes=["cabin-bag", "checked-bag"],
        airlines_exclude=[],
        prefer_directs=False,
        nearby_radius_km=150,
    )
    url = build_skyscanner_url_with_geocoded_airports(cfg)
    print(url)