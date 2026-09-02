# ==============================================================================
# OFFICIAL VIIT CAMPUS CONTACT & NAVIGATION HELP HELPER
# Provides directory of official campus help desks, emergency contacts,
# and integrated step-by-step navigation guidance.
# ==============================================================================

from data.viit_campus_map_data import VIIT_CAMPUS_LOCATIONS
from data.official_floor_plans import OFFICIAL_FLOOR_PLANS, search_official_floor_plans

# Official Campus Contact Information (Exact College Phone Numbers)
CAMPUS_CONTACTS = [
    {
        "id": "nav_help",
        "name": "Navigation Help / Help Desk",
        "icon": "📍",
        "purpose": "Campus directions, visitor assistance, building guidance, and lost & found support.",
        "phone": "+91 8639923152",
        "phone_raw": "+918639923152",
        "category": "Navigation",
        "hours": "8:30 AM – 5:30 PM (Mon–Sat)"
    },
    {
        "id": "security",
        "name": "Campus Security",
        "icon": "🛡️",
        "purpose": "24/7 security checkpoint, campus surveillance, visitor vehicle entry, and safety escort.",
        "phone": "+91 9866399930",
        "phone_raw": "+919866399930",
        "category": "Security",
        "hours": "24/7 Round the Clock"
    },
    {
        "id": "reception",
        "name": "Reception / Information Desk",
        "icon": "🏢",
        "purpose": "Main Block reception, visitor entry passes, admissions inquiry, and administrative guidance.",
        "phone": "+91 9133300359",
        "phone_raw": "+919133300359",
        "category": "Administrative",
        "hours": "9:00 AM – 5:00 PM (Mon–Sat)"
    },
    {
        "id": "transport",
        "name": "Transport Help",
        "icon": "🚌",
        "purpose": "College bus routes, transport schedules, driver contacts, and campus parking assistance.",
        "phone": "+91 89781 43769",
        "phone_raw": "+918978143769",
        "category": "Transport",
        "hours": "7:00 AM – 7:00 PM (College Days)"
    },
    {
        "id": "emergency",
        "name": "Emergency Contact",
        "icon": "🚨",
        "purpose": "Campus health center, on-duty doctor, immediate first aid, and 24/7 ambulance emergency.",
        "phone": "+91 9166399921",
        "phone_raw": "+919166399921",
        "category": "Emergency",
        "hours": "24/7 Emergency Service"
    },
    {
        "id": "toll_free",
        "name": "Toll-Free Number",
        "icon": "☎️",
        "purpose": "Official college toll-free help line for student support, admissions, and campus inquiries.",
        "phone": "0891-2755333",
        "phone_raw": "08912755333",
        "category": "Toll-Free",
        "hours": "9:00 AM – 6:00 PM (Toll Free)"
    }
]

def get_all_searchable_destinations():
    """
    Returns a unified sorted list of major campus buildings, facilities, and indoor rooms/labs/offices.
    """
    destinations = []
    
    # 1. Outdoor Campus Buildings & Facilities
    for name, info in VIIT_CAMPUS_LOCATIONS.items():
        destinations.append({
            "label": f"🏢 {name} ({info.get('type', 'Building')})",
            "name": name,
            "is_indoor": False,
            "building": name,
            "floor": "Ground Level",
            "block": "Main Campus",
            "roomNumber": "",
            "roomName": name
        })
        
    # 2. Indoor Rooms, Labs, and Offices across all floors
    for floor_name, blocks in OFFICIAL_FLOOR_PLANS.items():
        for block_name, rooms in blocks.items():
            for r in rooms:
                if r["roomName"] != "Open to Sky":
                    destinations.append({
                        "label": f"📍 {r['roomName']} [{r['roomNumber']}] — {floor_name}, {block_name}",
                        "name": r["roomName"],
                        "is_indoor": True,
                        "building": "Main Block",
                        "floor": floor_name,
                        "block": block_name,
                        "roomNumber": r["roomNumber"],
                        "roomName": r["roomName"]
                    })
                    
    return destinations

def format_quick_route_breadcrumb(start_location_name, target_dest_info):
    """
    Returns a clean breadcrumb trail like:
    Library ➔ Central Corridor ➔ Stairs / Lift ➔ 1st Floor (Prudhvi Block) ➔ Exam Cell
    """
    dest_name = target_dest_info.get("name", "Destination")
    is_indoor = target_dest_info.get("is_indoor", False)
    target_building = target_dest_info.get("building", "Main Block")
    target_floor = target_dest_info.get("floor", "1st Floor")
    target_block = target_dest_info.get("block", "Central")
    
    if not is_indoor:
        if start_location_name == target_building:
            return f"**{start_location_name}** ➔ **{dest_name}**"
        return f"**{start_location_name}** ➔ Central Walkway ➔ **{dest_name}**"
        
    if "First" in target_floor or "1st" in target_floor:
        return f"**{start_location_name}** ➔ Main Block Entrance ➔ Ground Corridor ➔ **{target_block}** ➔ **{dest_name}**"
    elif "Second" in target_floor or "2nd" in target_floor:
        return f"**{start_location_name}** ➔ Main Block Lobby ➔ Stairs / Lift ➔ **2nd Floor ({target_block})** ➔ **{dest_name}**"
    elif "Third" in target_floor or "3rd" in target_floor:
        return f"**{start_location_name}** ➔ Main Block Lobby ➔ Stairs / Lift ➔ **3rd Floor ({target_block})** ➔ **{dest_name}**"
    elif "Fourth" in target_floor or "4th" in target_floor:
        return f"**{start_location_name}** ➔ Main Block Lobby ➔ Stairs / Lift ➔ **4th Floor ({target_block})** ➔ **{dest_name}**"
    else:
        return f"**{start_location_name}** ➔ Main Block Lobby ➔ Stairs / Lift ➔ **{target_floor} ({target_block})** ➔ **{dest_name}**"

def generate_step_by_step_navigation_help(start_location_name, target_dest_info):
    """
    Generates step-by-step navigation instructions connecting outdoor and indoor routes.
    """
    dest_name = target_dest_info.get("name", "Destination")
    is_indoor = target_dest_info.get("is_indoor", False)
    target_building = target_dest_info.get("building", "Main Block")
    target_floor = target_dest_info.get("floor", "1st Floor")
    target_block = target_dest_info.get("block", "Central")
    room_code = target_dest_info.get("roomNumber", "")
    
    steps = []
    
    # Step 1: Outdoor Departure
    if start_location_name == target_building and not is_indoor:
        steps.append(f"📍 You are currently at **{target_building}**.")
    else:
        steps.append(f"🚶 **Step 1: Start at {start_location_name}** — Proceed along the central campus walkway towards **{target_building}**.")
    
    # Step 2: Reaching Building Entrance
    if target_building == "Main Block":
        steps.append("🏛️ **Step 2: Enter Main Academic Block** — Walk through the main entrance lobby facing the Central Courtyard.")
    elif target_building == "AKCNB Hall":
        steps.append("🎭 **Step 2: Enter AKCNB Auditorium** — Access the auditorium lobby from the north-west corridor walkway.")
    elif target_building == "Pharmacy College":
        steps.append("💊 **Step 2: Enter Pharmacy College** — Follow the north-west avenue past the cricket ground.")
    else:
        steps.append(f"🏢 **Step 2: Reach {target_building}** — Look for the official entrance signage.")
        
    # Step 3: Indoor Floor & Block Guidance (if destination is an indoor facility)
    if is_indoor:
        if "First" in target_floor or "1st" in target_floor:
            steps.append(f"🏬 **Step 3: Ground / 1st Floor Navigation** — Stay on the entrance level and follow corridor signs to **{target_block}**.")
        elif "Second" in target_floor or "2nd" in target_floor:
            steps.append(f"🏬 **Step 3: Take Stairs / Elevator to 2nd Floor** — Use the central staircase or elevator in Main Block to reach the **2nd Floor**, then proceed to **{target_block}**.")
        elif "Third" in target_floor or "3rd" in target_floor:
            steps.append(f"🏬 **Step 3: Take Stairs / Elevator to 3rd Floor** — Head up to the **3rd Floor** via the central stairs or elevator, then turn towards **{target_block}**.")
        elif "Fourth" in target_floor or "4th" in target_floor:
            steps.append(f"🏬 **Step 3: Take Stairs / Elevator to 4th Floor** — Head up to the **4th Floor** and follow the walkway to **{target_block}**.")
        else:
            steps.append(f"🏬 **Step 3: Proceed to {target_floor}** — Follow the building directory signage to **{target_block}**.")
            
        # Step 4: Room Location
        room_label = f"Room {room_code}" if room_code else "Facility"
        steps.append(f"📌 **Step 4: Arrive at {dest_name} ({room_label})** — Located within **{target_block}** corridor. Look for room door plate **{room_code}**.")
    else:
        steps.append(f"🎯 **Step 3: Destination Reached** — **{dest_name}** is situated right in front of you.")
        
    return steps
