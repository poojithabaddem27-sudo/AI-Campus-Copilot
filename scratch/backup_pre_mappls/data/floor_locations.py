from data.official_floor_plans import OFFICIAL_FLOOR_PLANS

# Build FLOOR_LOCATIONS dynamically from OFFICIAL_FLOOR_PLANS to maintain 100% single source of truth
FLOOR_LOCATIONS = {}

for floor_name, blocks in OFFICIAL_FLOOR_PLANS.items():
    room_list = []
    for block_name, rooms in blocks.items():
        for r in rooms:
            if r["roomName"] != "Open to Sky":
                room_list.append(f"{r['roomNumber']} - {r['roomName']} ({block_name})")
    FLOOR_LOCATIONS[floor_name] = room_list

# Backwards compatibility for 5th floor if needed
if "Fifth Floor" not in FLOOR_LOCATIONS:
    FLOOR_LOCATIONS["Fifth Floor"] = ["Classrooms", "Solar Panels"]

def get_location_icon(location_name):
    name_lower = location_name.lower().strip()
    
    if "office" in name_lower or "administration" in name_lower or "rector" in name_lower or "principal" in name_lower or "staff" in name_lower or "scholarship" in name_lower or "board" in name_lower:
        return "🏢"
    elif "exam" in name_lower:
        return "📝"
    elif "library" in name_lower or "vignan" in name_lower:
        return "📚"
    elif "computing" in name_lower or "computer" in name_lower or "aryabhatta" in name_lower:
        return "💻"
    elif "lab" in name_lower:
        return "🧪"
    elif "lecture" in name_lower or "hall" in name_lower or "classroom" in name_lower:
        return "🏫"
    elif "toilet" in name_lower or "restroom" in name_lower or "washroom" in name_lower:
        return "🚻"
    elif "lift" in name_lower:
        return "🛗"
    elif "open" in name_lower or "sky" in name_lower or "yard" in name_lower:
        return "🌿"
    elif "akcnb" in name_lower or "auditorium" in name_lower or "kalam" in name_lower:
        return "🎭"
    else:
        return "📍"
