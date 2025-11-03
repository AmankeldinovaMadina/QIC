# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Any, Dict, List, Optional, Tuple
# import math
# import urllib.parse
# import os, certifi
# os.environ["SSL_CERT_FILE"] = certifi.where()

# from geopy.geocoders import Photon
# from airports import airport_data  # airports-py

# # for caching the results from previous calls
# from functools import lru_cache

# TYPE_RANK = {"large_airport": 0, "medium_airport": 1, "small_airport": 2}
# DEFAULT_TYPE_RANK = 3

# def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#     R = 6371.0
#     p1, p2 = math.radians(lat1), math.radians(lat2)
#     dphi = math.radians(lat2 - lat1)
#     dlmb = math.radians(lon2 - lon1)
#     a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
#     return 2 * R * math.asin(math.sqrt(a))

# @lru_cache(maxsize=256)
# def geocode_city(city: str) -> Tuple[float, float]:
#     geocoder = Photon(user_agent="qic-trip-url-builder/1.0")
#     loc = geocoder.geocode(city)
#     if not loc:
#         raise ValueError(f"Could not geocode city: {city!r}")
#     return (loc.latitude, loc.longitude)

# def best_airports_near(
#     lat: float,
#     lon: float,
#     radius_km: int = 150,
#     limit: int = 1,
#     require_iata: bool = True,
# ) -> List[Dict[str, Any]]:
#     nearby: List[Dict[str, Any]] = airport_data.find_nearby_airports(lat, lon, radius_km)
#     cleaned = []
#     for ap in nearby:
#         iata = (ap.get("iata") or "").strip().upper()
#         if require_iata and not iata:
#             continue
#         ap_lat = float(ap.get("latitude"))
#         ap_lon = float(ap.get("longitude"))
#         d_km = haversine_km(lat, lon, ap_lat, ap_lon)
#         ap_type = (ap.get("type") or "").strip().lower()
#         rank = TYPE_RANK.get(ap_type, DEFAULT_TYPE_RANK)
#         cleaned.append({**ap, "distance_km": d_km, "type_rank": rank, "iata": iata})
#     cleaned.sort(key=lambda a: (a["type_rank"], a["distance_km"]))
#     return cleaned[:limit]

# def to_yymmdd(date_str: str) -> str:
#     s = date_str.strip()
#     if len(s) == 10 and s[4] == "-" and s[7] == "-":
#         y, m, d = s.split("-")
#         return f"{int(y)%100:02d}{int(m):02d}{int(d):02d}"
#     if len(s) == 8 and s.isdigit():
#         return s[2:]
#     if len(s) == 6 and s.isdigit():
#         return s
#     raise ValueError(f"Unsupported date format: {date_str!r}")

# @dataclass
# class TripFilters:
#     origin_city: str
#     destination_city: str
#     outbound_date: str
#     return_date: Optional[str] = None          # None => one-way (omit rtn & return date)
#     adults: int = 1                             # explicit
#     children: int = 0                           # explicit 0 is clearer than None
#     cabinclass: str = "economy"                 # economy|premiumeconomy|business|first
#     outbound_alts: Optional[bool] = None        # None => omit param
#     inbound_alts: Optional[bool] = None
#     prefer_directs: Optional[bool] = None
#     # Replaces fare_attributes iterable:
#     cabin_bag: Optional[bool] = None            # True => include; False/None => don’t include
#     checked_bag: Optional[bool] = None
#     market_domain: str = "www.skyscanner.qa"
#     nearby_radius_km: int = 150
#     use_mac: bool = False

# def build_url(cfg: TripFilters) -> str:
#     # 1) geocode
#     o_lat, o_lon = geocode_city(cfg.origin_city)
#     d_lat, d_lon = geocode_city(cfg.destination_city)

#     # 2) airports (top-ranked by type then distance)
#     origin_choices = best_airports_near(o_lat, o_lon, radius_km=cfg.nearby_radius_km,
#                                         limit=1 if not cfg.use_mac else 3)
#     dest_choices   = best_airports_near(d_lat, d_lon, radius_km=cfg.nearby_radius_km,
#                                         limit=1 if not cfg.use_mac else 3)
#     if not origin_choices:
#         raise RuntimeError(f"No nearby airports found for origin city '{cfg.origin_city}'.")
#     if not dest_choices:
#         raise RuntimeError(f"No nearby airports found for destination city '{cfg.destination_city}'.")

#     origin_iata = origin_choices[0]["iata"].lower()
#     dest_iata   = dest_choices[0]["iata"].lower()

#     out = to_yymmdd(cfg.outbound_date)
#     path = f"/transport/flights/{origin_iata}/{dest_iata}/{out}/"

#     query: Dict[str, str] = {}

#     # Two-way only if return_date is provided
#     if cfg.return_date:
#         ret = to_yymmdd(cfg.return_date)
#         path += f"{ret}/"
#         query["rtn"] = "1"  # omit entirely for one-way

#     # Core pax/cabin
#     query["adultsv2"] = str(cfg.adults)
#     query["childrenv2"] = str(cfg.children)
#     if cfg.cabinclass:
#         query["cabinclass"] = cfg.cabinclass

#     # Alt dates & directs — only if explicitly set
#     if cfg.outbound_alts is not None:
#         query["outboundaltsenabled"] = str(cfg.outbound_alts).lower()
#     if cfg.inbound_alts is not None:
#         query["inboundaltsenabled"] = str(cfg.inbound_alts).lower()
#     if cfg.prefer_directs is not None:
#         query["preferdirects"] = str(cfg.prefer_directs).lower()

#     # Fare attributes from booleans
#     fare_attrs: List[str] = []
#     if cfg.cabin_bag:
#         fare_attrs.append("cabin-bag")
#     if cfg.checked_bag:
#         fare_attrs.append("checked-bag")
#     if fare_attrs:
#         query["fare-attributes"] = ",".join(fare_attrs)

#     base = f"https://{cfg.market_domain}"
#     return base + path + "?" + urllib.parse.urlencode(query)

# # ---------- example ----------

# if __name__ == "__main__":
#     cfg1 = TripFilters(
#         origin_city="Doha",
#         destination_city="Krakow",
#         outbound_date="2025-12-15",
#         return_date="2025-12-30",
#         adults=1,
#         cabinclass="economy",
#         outbound_alts=False,
#         inbound_alts=False,
#         cabin_bag=None,
#         checked_bag=True,
#         prefer_directs=False,
#         nearby_radius_km=150,
#     )

#     cfg2 = TripFilters(
#         origin_city="Doha",
#         destination_city="London",
#         outbound_date="2025-12-15",
#         return_date="2025-12-30",
#         adults=1,
#         cabinclass="economy",
#         outbound_alts=False,
#         inbound_alts=False,
#         cabin_bag=None,
#         checked_bag=True,
#         prefer_directs=False,
#         nearby_radius_km=150,
#     )

#     url1 = build_url(cfg1)
#     url2 = build_url(cfg2)

#     print(url1)
#     print(url2)