import requests
import json
import math

API_KEY = "AIzaSyAVCS1cG9AccMkG-G7oV3UeBRiB5sEDCC4"
# Load exit data
with open("data/exits.json") as f:
    exits_data = json.load(f)

# Get coordinates
def get_coordinates(place):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={API_KEY}"
    res = requests.get(url).json()

    location = res['results'][0]['geometry']['location']
    return location['lat'], location['lng']

# Calculate distance (km)
def calculate_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat1 - lat2)**2 + (lng1 - lng2)**2) * 111

# Get best exit
def get_best_exit(station, destination):
    dest_lat, dest_lng = get_coordinates(destination)

    exits = exits_data.get(station, {})
    best_exit = None
    min_distance = float('inf')

    for exit_name, coords in exits.items():
        dist = calculate_distance(
            dest_lat, dest_lng,
            coords['lat'], coords['lng']
        )

        if dist < min_distance:
            min_distance = dist
            best_exit = exit_name

    return best_exit if best_exit else "Exit A"

# MAIN LOGIC (REAL)
def get_best_option(station, destination):

    origin = station + " metro station Bangalore"
    destination = destination + " Bangalore"

    walk_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&mode=walking&key={API_KEY}"
    drive_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&mode=driving&key={API_KEY}"

    # ✅ SAFE CALL
    walk_res = safe_request(walk_url)
    drive_res = safe_request(drive_url)

    # ❗ HANDLE FAILURE
    if not walk_res or "rows" not in walk_res:
        return {
            "station": station,
            "destination": destination,
            "error": "Google API failed (check internet/API key)"
        }

    try:
        walk_element = walk_res['rows'][0]['elements'][0]

        if walk_element["status"] != "OK":
            raise Exception("Invalid location")

        distance_text = walk_element['distance']['text']
        walking_time = walk_element['duration']['text']
        distance_km = float(distance_text.split()[0])

    except:
        return {
            "station": station,
            "destination": destination,
            "error": "Invalid location or API issue"
        }

    # ✅ VEHICLE TIME SAFE
    if drive_res and "rows" in drive_res:
        try:
            vehicle_time = drive_res['rows'][0]['elements'][0]['duration']['text']
        except:
            vehicle_time = "N/A"
    else:
        vehicle_time = "N/A"

    # ✅ DECISION LOGIC
    if distance_km <= 1:
        suggestion = "Walk 🚶"
    elif distance_km <= 3:
        suggestion = "Walk or Auto 🚕"
    else:
        suggestion = "Take Auto/Bus 🚕🚌"

    # ✅ EXIT LOGIC SAFE
    try:
        exit_gate = get_best_exit(station, destination)
    except:
        exit_gate = "Exit A"

    return {
        "station": station,
        "destination": destination,
        "distance": distance_text,
        "walking_time": walking_time,
        "vehicle_time": vehicle_time,
        "waiting_time": "3-8 mins",
        "suggestion": suggestion,
        "exit": exit_gate
    }

def safe_request(url):
    try:
        res = requests.get(url, timeout=5)
        return res.json()
    except:
        return None
