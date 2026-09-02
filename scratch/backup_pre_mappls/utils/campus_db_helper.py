import json
import os
import re
from data.floor_locations import FLOOR_LOCATIONS, get_location_icon

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "campus_db.json")

def load_campus_data():
    """Load campus info and events."""
    if not os.path.exists(DB_PATH):
        return {"campus_info": {}, "locations": [], "events": []}
    
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading campus data: {e}")
        return {"campus_info": {}, "locations": [], "events": []}

def get_all_locations():
    """
    Returns a unified list of all campus locations generated ONLY from FLOOR_LOCATIONS.
    Each item is a dictionary with 'name', 'floor', 'block', 'description', 'icon'.
    """
    all_items = []
    for floor_name, items in FLOOR_LOCATIONS.items():
        for item in items:
            all_items.append({
                "id": f"{item.lower().replace(' ', '-')}-{floor_name.lower().replace(' ', '-')}",
                "name": item,
                "floor": floor_name,
                "block": "Campus Building",
                "status": "Open",
                "timing": "8:00 AM - 6:00 PM",
                "description": f"{item} is located on the {floor_name}.",
                "icon": get_location_icon(item)
            })
    return all_items

def get_all_events():
    """Return all campus events."""
    data = load_campus_data()
    return data.get("events", [])

def get_categories():
    """Return list of available floors as categories."""
    return ["All"] + list(FLOOR_LOCATIONS.keys())

def search_locations(query):
    """
    Performs case-insensitive, space-trimmed partial substring search across ALL floors in FLOOR_LOCATIONS.
    Supports multiple location entries across different floors.
    """
    if not query or not query.strip():
        return get_all_locations()
    
    q_clean = query.strip().lower()
    results = []

    for floor_name, items in FLOOR_LOCATIONS.items():
        for item in items:
            item_lower = item.lower()
            # Check if query string is a substring of item_lower
            if q_clean in item_lower:
                results.append({
                    "id": f"{item.lower().replace(' ', '-')}-{floor_name.lower().replace(' ', '-')}",
                    "name": item,
                    "floor": floor_name,
                    "block": "Campus Building",
                    "status": "Open",
                    "timing": "8:00 AM - 6:00 PM",
                    "description": f"{item} is located on the {floor_name}.",
                    "icon": get_location_icon(item)
                })

    return results

def get_floor_content(floor_query):
    """
    Returns all locations listed under a specific floor query (e.g. '4th Floor', '4th', '1st').
    """
    if not floor_query or not floor_query.strip():
        return None, []
    
    fq_clean = floor_query.strip().lower()
    
    for floor_name, items in FLOOR_LOCATIONS.items():
        f_lower = floor_name.lower()
        if fq_clean in f_lower or f_lower in fq_clean or fq_clean.replace("floor", "").strip() in f_lower:
            return floor_name, items
            
    return None, []

def parse_room_code(query):
    """
    Room code parser for room codes like 'A-123', 'B-204', 'C-312', 'M-201'.
    """
    q = query.strip()
    pattern = r"(?:room\s*)?([A-Za-z])[- ]?([0-5])([0-9]{2}|[0-9]{1})"
    match = re.search(pattern, q, re.IGNORECASE)

    if match:
        block = match.group(1).upper()
        floor_num = int(match.group(2))
        room_num = match.group(3)

        floor_names = {
            0: "Ground Floor",
            1: "1st Floor",
            2: "2nd Floor",
            3: "3rd Floor",
            4: "4th Floor",
            5: "5th Floor"
        }
        floor_text = floor_names.get(floor_num, f"{floor_num}th Floor")

        return {
            "is_valid": True,
            "block": f"Block {block}",
            "side": f"Wing {block}",
            "floor": floor_text,
            "room_code": f"{block}-{floor_num}{room_num}",
            "description": f"Room {block}-{floor_num}{room_num} is located on the {floor_text} in Block {block}."
        }
    
    return None

def get_campus_context_for_prompt():
    """Generates a text summary of FLOOR_LOCATIONS for AI RAG context."""
    lines = ["--- CAMPUS FLOOR LOCATIONS DIRECTORY (SINGLE SOURCE OF TRUTH) ---"]
    for floor_name, items in FLOOR_LOCATIONS.items():
        lines.append(f"• {floor_name}: {', '.join(items)}")
    return "\n".join(lines)
