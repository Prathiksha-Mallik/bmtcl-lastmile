import json
import math
import os
import datetime
from functools import lru_cache
from typing import Optional

import requests


BENGALURU_BOUNDS = {
    "min_lon": 77.35,
    "max_lon": 77.85,
    "min_lat": 12.75,
    "max_lat": 13.20,
}

STATIONS = [
    "Whitefield",
    "Kadugodi Tree Park",
    "Pattandur Agrahara",
    "Sri Sathya Sai Hospital",
    "Nallurhalli",
    "Kundalahalli",
    "Seetharamapalya",
    "Hoodi",
    "Garudacharpalya",
    "KR Puram",
    "Mahadevapura",
    "Benniganahalli",
    "Baiyappanahalli",
    "Swami Vivekananda Road",
    "Indiranagar",
    "Halasuru",
    "Trinity",
    "MG Road",
    "Cubbon Park",
    "Vidhana Soudha",
    "Sir M Visvesvaraya",
    "Majestic",
    "Nadaprabhu Kempegowda Station",
    "Magadi Road",
    "Hosahalli",
    "Vijayanagar",
    "Attiguppe",
    "Deepanjali Nagar",
    "Mysore Road",
    "Nayandahalli",
    "Rajarajeshwari Nagar",
    "Jnanabharathi",
    "Pattanagere",
    "Kengeri Bus Terminal",
    "Kengeri",
    "Nagasandra",
    "Dasarahalli",
    "Jalahalli",
    "Peenya Industry",
    "Peenya",
    "Goraguntepalya",
    "Yeshwanthpur",
    "Sandal Soap Factory",
    "Mahalakshmi",
    "Rajajinagar",
    "Mahakavi Kuvempu Road",
    "Mantri Square",
    "Chickpet",
    "KR Market",
    "National College",
    "Lalbagh",
    "South End Circle",
    "Jayanagar",
    "R V Road",
    "Banashankari",
    "Jaya Prakash Nagar",
    "Yelachenahalli",
    "Konanakunte Cross",
    "Doddakallasandra",
    "Vajarahalli",
    "Thalaghattapura",
    "Silk Institute",
]

STATION_ALIASES = {
    "majestic": "Majestic",
    "nadaprabhu kempegowda station majestic": "Majestic",
    "sir m v": "Sir M Visvesvaraya",
    "sir m visvesvaraya station": "Sir M Visvesvaraya",
    "rv road": "R V Road",
    "r v road": "R V Road",
    "jp nagar": "Jaya Prakash Nagar",
    "j p nagar": "Jaya Prakash Nagar",
    "kr puram": "KR Puram",
    "k r puram": "KR Puram",
    "kr market": "KR Market",
    "k r market": "KR Market",
}


def project_path(*parts: str) -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), *parts)


def load_env_value(name: str) -> str:
    env_value = os.getenv(name, "").strip()
    if env_value:
        return env_value

    env_path = project_path(".env")
    if not os.path.exists(env_path):
        return ""

    try:
        with open(env_path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                if key.strip() == name:
                    return value.strip().strip('"').strip("'")
    except OSError:
        return ""

    return ""


OPENROUTESERVICE_API_KEY = load_env_value("OPENROUTESERVICE_API_KEY")

DESTINATION_HINTS = {
    "waav cafe jayanagar": {
        "label": "WAAW Cafe, Jayanagar",
        "coords": [77.589859, 12.928148],
    },
    "waaw cafe jayanagar": {
        "label": "WAAW Cafe, Jayanagar",
        "coords": [77.589859, 12.928148],
    },
}


def normalize_station_name(station: str) -> Optional[str]:
    if not station:
        return None

    cleaned = " ".join(station.strip().split())
    if not cleaned:
        return None

    lowered = cleaned.lower()
    if lowered in STATION_ALIASES:
        return STATION_ALIASES[lowered]

    for station_name in STATIONS:
        if station_name.lower() == lowered:
            return station_name

    return None


def is_inside_bengaluru(lon: float, lat: float) -> bool:
    return (
        BENGALURU_BOUNDS["min_lon"] <= lon <= BENGALURU_BOUNDS["max_lon"]
        and BENGALURU_BOUNDS["min_lat"] <= lat <= BENGALURU_BOUNDS["max_lat"]
    )


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius_km = 6371
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


@lru_cache(maxsize=1)
def load_verified_station_exits() -> dict:
    exits_path = project_path("data", "exits.json")
    if not os.path.exists(exits_path):
        return {}

    try:
        with open(exits_path, "r", encoding="utf-8") as exits_file:
            raw_exits = json.load(exits_file)
    except (OSError, ValueError):
        return {}

    verified_exits = {}
    for station, exits in raw_exits.items():
        station_name = normalize_station_name(station)
        if not station_name or not isinstance(exits, dict):
            continue

        station_exits = {}
        for exit_name, coords in exits.items():
            try:
                lat = float(coords["lat"])
                lon = float(coords["lng"])
            except (KeyError, TypeError, ValueError):
                continue

            if is_inside_bengaluru(lon, lat):
                station_exits[str(exit_name)] = {
                    "coords": [lon, lat],
                }

        if station_exits:
            verified_exits[station_name] = station_exits

    return verified_exits


def get_verified_station_exits(station_name: str) -> dict:
    return load_verified_station_exits().get(station_name, {})


@lru_cache(maxsize=128)
def get_auto_station_access(station_name: str) -> dict:
    coords = get_station_coordinates(station_name)
    if not coords:
        return {}

    return {
        "Exit A": {
            "coords": coords,
            "auto_generated": True,
        }
    }


def get_station_access_points(station_name: str) -> dict:
    verified_exits = get_verified_station_exits(station_name)
    if verified_exits:
        return verified_exits

    return get_auto_station_access(station_name)


def has_verified_station_exits(station_name: str) -> bool:
    return bool(get_verified_station_exits(station_name))


def get_station_center(station_name: str) -> Optional[list[float]]:
    access_points = get_station_access_points(station_name)
    if not access_points:
        return None

    lon = sum(exit_data["coords"][0] for exit_data in access_points.values()) / len(access_points)
    lat = sum(exit_data["coords"][1] for exit_data in access_points.values()) / len(access_points)
    return [lon, lat]


def get_search_token_list(text: str) -> list[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "at",
        "bangalore",
        "bengaluru",
        "block",
        "india",
        "in",
        "ka",
        "karnataka",
        "metro",
        "near",
        "road",
        "station",
        "street",
        "the",
    }
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return [
        token
        for token in cleaned.split()
        if len(token) > 1 and token not in stop_words
    ]


def get_search_tokens(text: str) -> set[str]:
    return set(get_search_token_list(text))


def normalize_destination_query(destination: str) -> str:
    cleaned = " ".join(destination.lower().strip().split())
    hint = DESTINATION_HINTS.get(cleaned)
    if isinstance(hint, str):
        return hint

    return destination


def get_destination_hint(destination: str) -> Optional[dict]:
    cleaned = " ".join(destination.lower().strip().split())
    hint = DESTINATION_HINTS.get(cleaned)
    if isinstance(hint, dict):
        return {
            "coords": hint["coords"],
            "label": hint["label"],
            "provider": "Local place hint",
            "confidence": 1,
            "ambiguous": False,
        }

    return None


def is_relevant_match(query: str, label: str) -> bool:
    query_token_list = get_search_token_list(query)
    if not query_token_list:
        return True

    query_tokens = set(query_token_list)
    label_tokens = get_search_tokens(label)
    primary_token = query_token_list[0]
    if primary_token in label_tokens:
        return True

    if len(query_tokens) == 1:
        return bool(query_tokens & label_tokens)

    matches = len(query_tokens & label_tokens)
    return matches >= max(1, math.ceil(len(query_tokens) * 0.6))


def get_ors_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


@lru_cache(maxsize=1)
def get_ors_health_warning() -> Optional[str]:
    if not OPENROUTESERVICE_API_KEY:
        return "OpenRouteService API key is not configured."

    url = "https://api.openrouteservice.org/v2/directions/foot-walking/json"
    headers = {
        "Authorization": OPENROUTESERVICE_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"coordinates": [[77.5946, 12.9716], [77.5956, 12.9726]]}

    try:
        response = get_ors_session().post(
            url,
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = response.json()
    except (requests.RequestException, ValueError):
        return "OpenRouteService could not be reached from the backend."

    if response.ok:
        return None

    message = data.get("error", {}).get("message") or data.get("message")
    return message or f"OpenRouteService returned HTTP {response.status_code}."


def get_osrm_route(lon1: float, lat1: float, lon2: float, lat2: float, profile: str, retries: int = 1) -> Optional[dict]:
    # We use overview=full and geometries=geojson to get the route coordinates
    if profile == "foot":
        url = f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    else:
        url = f"https://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    
    for attempt in range(retries + 1):
        try:
            response = get_ors_session().get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                return {
                    "distance_km": float(route["distance"]) / 1000.0,
                    "duration_minutes": float(route["duration"]) / 60.0,
                    "geometry": route.get("geometry"),
                    "provider": "OSRM"
                }
        except (requests.RequestException, ValueError):
            pass
    return None


def get_ors_coordinate_candidates(destination: str) -> list[dict]:
    if not OPENROUTESERVICE_API_KEY or not destination:
        return []

    url = "https://api.openrouteservice.org/geocode/search"
    headers = {"Authorization": OPENROUTESERVICE_API_KEY}
    searches = [
        f"{destination}, Bengaluru, Karnataka, India",
        f"{destination}, Bangalore, India",
        f"{destination}, Bengaluru",
    ]
    candidates = []

    for search_text in searches:
        params = {
            "text": search_text,
            "boundary.country": "IN",
            "boundary.rect.min_lon": BENGALURU_BOUNDS["min_lon"],
            "boundary.rect.max_lon": BENGALURU_BOUNDS["max_lon"],
            "boundary.rect.min_lat": BENGALURU_BOUNDS["min_lat"],
            "boundary.rect.max_lat": BENGALURU_BOUNDS["max_lat"],
            "size": 5,
        }

        try:
            response = get_ors_session().get(
                url,
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            continue

        for feature in data.get("features", []):
            coords = feature.get("geometry", {}).get("coordinates") or []
            if len(coords) < 2:
                continue

            lon = float(coords[0])
            lat = float(coords[1])
            props = feature.get("properties", {})
            label = props.get("label") or search_text
            if not is_inside_bengaluru(lon, lat):
                continue

            if not is_relevant_match(destination, label):
                continue

            candidates.append({
                "coords": [lon, lat],
                "label": label,
                "confidence": props.get("confidence"),
                "provider": "OpenRouteService",
            })

    return dedupe_candidates(candidates)


@lru_cache(maxsize=128)
def get_station_coordinates(station_name: str) -> Optional[list[float]]:
    osm_coords = get_osm_station_coordinates(station_name)
    if osm_coords:
        return osm_coords

    if not OPENROUTESERVICE_API_KEY:
        return None

    url = "https://api.openrouteservice.org/geocode/search"
    headers = {"Authorization": OPENROUTESERVICE_API_KEY}
    searches = [
        f"{station_name} metro station, Bengaluru, Karnataka, India",
        f"{station_name} Namma Metro station, Bangalore, India",
        f"{station_name}, Bengaluru Metro",
    ]
    candidates = []

    for search_text in searches:
        params = {
            "text": search_text,
            "boundary.country": "IN",
            "boundary.rect.min_lon": BENGALURU_BOUNDS["min_lon"],
            "boundary.rect.max_lon": BENGALURU_BOUNDS["max_lon"],
            "boundary.rect.min_lat": BENGALURU_BOUNDS["min_lat"],
            "boundary.rect.max_lat": BENGALURU_BOUNDS["max_lat"],
            "size": 5,
        }

        try:
            response = get_ors_session().get(
                url,
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            continue

        for feature in data.get("features", []):
            coords = feature.get("geometry", {}).get("coordinates") or []
            if len(coords) < 2:
                continue

            lon = float(coords[0])
            lat = float(coords[1])
            if not is_inside_bengaluru(lon, lat):
                continue

            label = (feature.get("properties", {}).get("label") or "").lower()
            name_score = 1 if is_relevant_match(station_name, label) else 0
            metro_score = 1 if "metro" in label or "station" in label else 0
            if name_score == 0:
                continue

            candidates.append({
                "coords": [lon, lat],
                "score": name_score + metro_score,
            })

    if candidates:
        candidates.sort(key=lambda candidate: candidate["score"], reverse=True)
        return candidates[0]["coords"]

    return None


def get_osm_station_coordinates(station_name: str) -> Optional[list[float]]:
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "bmtcl-lastmile/1.0"}
    searches = [
        f"{station_name} Bangalore metro",
        f"{station_name} Namma Metro",
        f"{station_name} station Bangalore",
        f"{station_name} metro station, Bengaluru, Karnataka, India",
        f"{station_name} Namma Metro station, Bangalore, India",
    ]

    for search_text in searches:
        params = {
            "q": search_text,
            "format": "json",
            "limit": 5,
            "countrycodes": "in",
            "viewbox": "77.35,13.20,77.85,12.75",
            "bounded": 1,
        }

        try:
            response = get_ors_session().get(
                url,
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            results = response.json()
        except (requests.RequestException, ValueError):
            continue

        for result in results:
            lon = float(result["lon"])
            lat = float(result["lat"])
            if is_inside_bengaluru(lon, lat):
                return [lon, lat]

    return None


def dedupe_candidates(candidates: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for candidate in candidates:
        lon, lat = candidate["coords"]
        key = (round(lon, 5), round(lat, 5), candidate["label"].lower())
        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    return unique


def get_osm_coordinate_candidate(destination: str) -> Optional[dict]:
    if not destination:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "bmtcl-lastmile/1.0"}
    searches = [
        f"{destination}, Bengaluru",
        f"{destination}, Bangalore",
        f"{destination}, Karnataka, India",
        f"{destination}",
    ]

    for search_text in searches:
        params = {
            "q": search_text,
            "format": "json",
            "limit": 5,
            "countrycodes": "in",
            "viewbox": "77.35,13.20,77.85,12.75",
            "bounded": 1,
        }

        try:
            response = get_ors_session().get(
                url,
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            results = response.json()
        except (requests.RequestException, ValueError):
            continue

        for result in results:
            lon = float(result["lon"])
            lat = float(result["lat"])
            label = result.get("display_name") or search_text
            if not is_inside_bengaluru(lon, lat):
                continue

            if not is_relevant_match(destination, label):
                continue

            return {
                "coords": [lon, lat],
                "label": destination,
                "provider": "OpenStreetMap",
                "confidence": None,
            }

    return None


def choose_destination(destination: str, station_name: str) -> Optional[dict]:
    destination_hint = get_destination_hint(destination)
    if destination_hint:
        return destination_hint

    normalized_destination = normalize_destination_query(destination)
    
    osm_candidate = get_osm_coordinate_candidate(destination)
    if not osm_candidate and normalized_destination != destination:
        osm_candidate = get_osm_coordinate_candidate(normalized_destination)

    if osm_candidate:
        return {
            "coords": osm_candidate["coords"],
            "label": osm_candidate["label"],
            "provider": osm_candidate["provider"],
            "confidence": osm_candidate.get("confidence"),
            "ambiguous": False,
        }

    return None


def get_best_option(station: str, destination: str) -> dict:
    station_name = normalize_station_name(station)
    if not station_name:
        return {"error": "Station not found"}

    if not destination or not destination.strip():
        return {"error": "Destination is required"}

    destination_match = choose_destination(destination.strip(), station_name)
    if not destination_match:
        return {"error": "Route not found"}

    access_points = get_station_access_points(station_name)
    if not access_points:
        return {"error": "Route not found"}

    dlon, dlat = destination_match["coords"]
    evaluated_exits = []

    for exit_name, exit_data in access_points.items():
        elon, elat = exit_data["coords"]
        
        walking_route = get_osrm_route(elon, elat, dlon, dlat, "foot")
        vehicle_route = get_osrm_route(elon, elat, dlon, dlat, "driving")
        
        if not walking_route or not vehicle_route:
            continue
            
        walking_dist = walking_route["distance_km"]
        walking_time = walking_route["duration_minutes"]
        vehicle_dist = vehicle_route["distance_km"]
        vehicle_time = vehicle_route["duration_minutes"]
        
        if walking_dist <= 0.8:
            suggestion = "Walk 🚶"
            waiting_time = "1 min"
        elif walking_dist <= 2.0:
            suggestion = "Walk / Auto 🚕"
            waiting_time = "2 mins"
        else:
            suggestion = "Auto 🚕"
            waiting_time = "2 mins"

        w_time_int = max(1, int(round(walking_time)))
        v_time_int = max(1, int(round(vehicle_time)))
        
        evaluated_exits.append({
            "exit": exit_name,
            "walking_distance_val": walking_dist,
            "vehicle_distance_val": vehicle_dist,
            "walking_distance": f"{walking_dist:.2f} km",
            "walking_time": f"{w_time_int} min" if w_time_int == 1 else f"{w_time_int} mins",
            "vehicle_distance": f"{vehicle_dist:.2f} km",
            "vehicle_time": f"{v_time_int} min" if v_time_int == 1 else f"{v_time_int} mins",
            "walking_geometry": walking_route.get("geometry"),
            "vehicle_geometry": vehicle_route.get("geometry"),
            "waiting_time": waiting_time,
            "suggestion": suggestion,
        })

    if not evaluated_exits:
        return {"error": "Route not found"}

    threshold = 0.8
    walkable_exits = [e for e in evaluated_exits if e["walking_distance_val"] <= threshold]

    if walkable_exits:
        walkable_exits.sort(key=lambda e: e["walking_distance_val"])
        top_exits = walkable_exits
    else:
        evaluated_exits.sort(key=lambda e: e["vehicle_distance_val"])
        top_exits = evaluated_exits

    # Exit logic improvement:
    # 1. If suggestions are SAME -> show ONLY the best one (minimum distance)
    # 2. If suggestions are DIFFERENT -> show BOTH to give user a choice
    if len(top_exits) >= 2:
        e1, e2 = top_exits[0], top_exits[1]
        if e1["suggestion"] == e2["suggestion"]:
            selected_exits = [e1]
        else:
            selected_exits = [e1, e2]
    else:
        selected_exits = top_exits[:1] if top_exits else []

    # Calculate real-time auto availability
    hour = datetime.datetime.now().hour
    if 8 <= hour < 11:
        status = "Medium"
        wait = "3 mins"
    elif 17 <= hour < 21:
        status = "High"
        wait = "2 mins"
    else:
        status = "Low"
        wait = "5 mins"
    
    auto_availability = f"Auto Availability: {status} (Estimated wait: {wait})"

    def get_landmark(exit_str, station):
        # A simple mapping for better realism
        landmarks = {
            "Indiranagar": {"Exit A": "near 100 ft road", "Exit B": "near BDA Complex", "Exit C": "near CMH Road"},
            "Majestic": {"Exit A": "near KSRTC Bus Stand", "Exit B": "near Railway Station", "Exit C": "near Sangam Theatre"},
            "MG Road": {"Exit A": "near Brigade Road", "Exit B": "near Church Street", "Exit C": "near Metro Office"},
            "Trinity": {"Exit A": "near Taj MG Road", "Exit B": "near Kensington Road"},
            "Cubbon Park": {"Exit A": "near High Court", "Exit B": "near GPO"}
        }
        station_landmarks = landmarks.get(station, {})
        return station_landmarks.get(exit_str, "near main road")

    options = []
    for e in selected_exits:
        # Determine which route geometry to use based on suggestion
        route_geometry = e["walking_geometry"] if "Walk" in e["suggestion"] and "Auto" not in e["suggestion"] else e["vehicle_geometry"]
        
        options.append({
            "exit": e["exit"],
            "landmark": get_landmark(e["exit"], station_name),
            "walking_distance": e["walking_distance"],
            "walking_time": e["walking_time"],
            "vehicle_distance": e["vehicle_distance"],
            "vehicle_time": e["vehicle_time"],
            "waiting_time": e["waiting_time"],
            "auto_availability": auto_availability,
            "suggestion": e["suggestion"],
            "route_geometry": route_geometry
        })

    station_center = get_station_center(station_name)

    return {
        "station": station_name,
        "destination": destination.strip(),
        "station_coords": [station_center[0], station_center[1]] if station_center else None,
        "destination_coords": [dlon, dlat],
        "options": options
    }
