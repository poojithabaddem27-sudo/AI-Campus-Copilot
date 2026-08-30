import json
import os
import math
from data.floor_locations import FLOOR_LOCATIONS
from data.indoor_floor_data import INDOOR_FLOOR_DATA, get_indoor_room_details
from utils.map_renderer import render_custom_illustrated_campus_map, render_indoor_floor_map

GPS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gps_coordinates.json")

def load_gps_coords():
    """Loads the GPS coordinates mapping dictionary."""
    if not os.path.exists(GPS_PATH):
        return {}
    try:
        with open(GPS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading GPS coordinates: {e}")
        return {}

def save_gps_coords(gps_dict):
    """Saves updated GPS coordinates dictionary to file."""
    try:
        with open(GPS_PATH, "w", encoding="utf-8") as f:
            json.dump(gps_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving GPS coordinates: {e}")
        return False

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates true geodesic distance in meters using Haversine formula."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c)

def get_nearest_building_from_gps(user_lat, user_lng):
    """
    Finds the nearest building based on live user GPS coordinates.
    """
    gps_dict = load_gps_coords()
    if not gps_dict:
        return "Main Entrance", {"lat": 0.0, "lng": 0.0}, 0

    closest_name = "Main Entrance"
    closest_dist = 999999.0
    closest_gps = {"lat": 0.0, "lng": 0.0}

    for bname, coords in gps_dict.items():
        d = haversine_distance(user_lat, user_lng, coords["lat"], coords["lng"])
        if d < closest_dist:
            closest_dist = d
            closest_name = bname
            closest_gps = coords

    return closest_name, closest_gps, closest_dist

def get_location_by_name(name):
    """Search for a location name in FLOOR_LOCATIONS or INDOOR_FLOOR_DATA."""
    if not name or not name.strip():
        return None
        
    target = name.strip().lower()

    # Check indoor rooms first
    indoor_match = get_indoor_room_details(target)
    if indoor_match:
        return {
            "id": f"indoor-{indoor_match['room'].lower().replace(' ', '-')}",
            "name": indoor_match["room"],
            "floor": indoor_match["floor"],
            "block": indoor_match["building"],
            "is_indoor": True,
            "indoor_details": indoor_match
        }

    # Check FLOOR_LOCATIONS
    for floor_name, items in FLOOR_LOCATIONS.items():
        for item in items:
            item_lower = item.lower()
            if target == item_lower or target in item_lower or item_lower in target:
                return {
                    "id": f"{item.lower().replace(' ', '-')}-{floor_name.lower().replace(' ', '-')}",
                    "name": item,
                    "floor": floor_name,
                    "block": "Main Academic Block",
                    "is_indoor": False
                }
    return None

def generate_pathway_waypoints(start_xy, end_xy):
    """Generates realistic campus ring-road & central avenue footpaths."""
    sx, sy = start_xy
    ex, ey = end_xy
    waypoints = [(sx, sy)]

    if abs(sx - ex) > 40 or abs(sy - ey) > 40:
        if sy > 380 and ey < 350:
            waypoints.append((340, 360))
            waypoints.append((340, ey))
        elif sy < 200 and ey > 300:
            waypoints.append((320, 195))
            waypoints.append((340, 360))
        elif sx < 200 and ex > 300:
            waypoints.append((320, sy))
            waypoints.append((320, ey))
        else:
            waypoints.append((sx, ey))

    waypoints.append((ex, ey))
    return waypoints

# Default Map Board Coordinates
MAP_COORDS = {
    "Main Entrance": (380, 445),
    "Main Block": (425, 340),
    "Pharmacy Block": (172, 120),
    "Cricket Ground": (140, 275),
    "Football Ground": (440, 110),
    "Back Gate": (680, 60),
    "CSE Grounds": (410, 235),
    "Dharithri Block": (460, 275),
    "Sagara Block": (445, 235),
    "Girls Hostel & Mess": (160, 55),
    "Canteen": (352, 240),
    "Parking Area": (307, 275),
    "Cricket Nets": (110, 275),
    "Volleyball & Basketball Courts": (442, 405),
    "Facilities Block": (715, 300),
    "ATM Counter": (635, 445)
}

def find_route(start_name, end_name, user_gps=None):
    """
    Generates step-by-step outdoor and indoor floor navigation.
    """
    if not start_name or not end_name:
        return {"success": False, "message": "Please specify both starting point and destination."}

    start_loc = get_location_by_name(start_name)
    end_loc = get_location_by_name(end_name)
    
    if not start_loc:
        start_loc = {
            "id": "custom-start",
            "name": start_name.strip(),
            "floor": "Ground Floor",
            "block": "Main Academic Block",
            "is_indoor": False
        }
    if not end_loc:
        end_loc = {
            "id": "custom-end",
            "name": end_name.strip(),
            "floor": "1st Floor",
            "block": "Main Academic Block",
            "is_indoor": False
        }

    if start_loc["name"].lower() == end_loc["name"].lower():
        return {"success": True, "same_location": True, "message": f"You are already at {start_loc['name']}!"}

    # Load GPS Coordinates
    gps_data = load_gps_coords()
    
    if user_gps and "lat" in user_gps and "lng" in user_gps:
        start_gps = user_gps
    else:
        start_gps = gps_data.get(start_loc["name"], {"lat": 0.0, "lng": 0.0})
        
    end_gps = gps_data.get(end_loc["name"], {"lat": 0.0, "lng": 0.0})

    # Haversine Distance
    gps_dist_m = haversine_distance(start_gps["lat"], start_gps["lng"], end_gps["lat"], end_gps["lng"])
    if gps_dist_m < 15:
        gps_dist_m = 45

    walk_mins = round((gps_dist_m / 68.0), 1)
    if walk_mins < 1.0:
        walk_mins = 1.0

    # Indoor vs Outdoor SVG Map rendering
    indoor_match = get_indoor_room_details(end_loc["name"])
    if indoor_match:
        building = indoor_match["building"]
        floor = indoor_match["floor"]
        all_rooms = INDOOR_FLOOR_DATA.get(building, {}).get(floor, [])
        map_html = render_indoor_floor_map(building, floor, start_loc["name"], indoor_match, all_rooms)
        is_indoor = True
    else:
        building = end_loc.get("block", "Main Academic Block")
        floor = end_loc.get("floor", "Ground Floor")
        start_xy = MAP_COORDS.get(start_loc["name"], (380, 445))
        end_xy = MAP_COORDS.get(end_loc["name"], (425, 340))
        path_points = generate_pathway_waypoints(start_xy, end_xy)
        map_html = render_custom_illustrated_campus_map(start_loc["name"], end_loc["name"], start_xy, end_xy, path_points, gps_dist_m, walk_mins)
        is_indoor = False

    steps = [
        {
            "step_num": 1,
            "icon": "📍",
            "title": f"Start at {start_loc['name']} ({start_loc['floor']})",
            "detail": f"Position: GPS ({start_gps['lat']:.5f}, {start_gps['lng']:.5f})"
        },
        {
            "step_num": 2,
            "icon": "🚶",
            "title": f"Walk towards {end_loc['name']} ({building}, {floor})",
            "detail": f"Follow campus walkway pathway towards destination (~{gps_dist_m} meters)."
        },
        {
            "step_num": 3,
            "icon": "📌",
            "title": f"Arrive at {end_loc['name']} ({building}, {floor})",
            "detail": f"Destination: {end_loc['name']} located on {floor} of {building}."
        }
    ]

    return {
        "success": True,
        "same_location": False,
        "start": start_loc,
        "end": end_loc,
        "building": building,
        "floor": floor,
        "is_indoor": is_indoor,
        "start_gps": start_gps,
        "end_gps": end_gps,
        "distance_meters": gps_dist_m,
        "estimated_minutes": walk_mins,
        "map_html": map_html,
        "steps": steps
    }
