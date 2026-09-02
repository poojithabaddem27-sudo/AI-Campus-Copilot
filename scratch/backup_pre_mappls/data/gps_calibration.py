# ==========================================
# CAMPUS GPS MAP CALIBRATION
# EDIT ONLY WITH REAL CAMPUS COORDINATES
# ==========================================
# Use known reference points on the real campus map.
# I will manually enter the REAL GPS coordinates for these points.
# ==========================================

MAP_REFERENCE_POINTS = [
    {
        "name": "Main Entrance",
        "latitude": 0.0,
        "longitude": 0.0,
        "x": 380,
        "y": 445
    },
    {
        "name": "Main Block",
        "latitude": 0.0,
        "longitude": 0.0,
        "x": 425,
        "y": 340
    },
    {
        "name": "AKCNB",
        "latitude": 0.0,
        "longitude": 0.0,
        "x": 220,
        "y": 160
    },
    {
        "name": "Cricket Ground",
        "latitude": 0.0,
        "longitude": 0.0,
        "x": 140,
        "y": 275
    },
    {
        "name": "Pharmacy Block",
        "latitude": 0.0,
        "longitude": 0.0,
        "x": 172,
        "y": 120
    }
]

# ==========================================
# EDITABLE CAMPUS PATHWAYS NETWORK
# I will manually define the real campus pathways/waypoints based on the college map.
# ==========================================

CAMPUS_ROUTE_PATHS = {
    "main_entrance": {"x": 380, "y": 445, "name": "Main Entrance Gate"},
    "south_junction": {"x": 380, "y": 430, "name": "South Entrance Junction"},
    "central_avenue_south": {"x": 340, "y": 360, "name": "Central Avenue South"},
    "main_block_plaza": {"x": 425, "y": 340, "name": "Main Block Plaza"},
    "central_avenue_mid": {"x": 320, "y": 270, "name": "Central Plaza Junction"},
    "canteen_square": {"x": 307, "y": 240, "name": "Canteen Square"},
    "quad_north": {"x": 340, "y": 195, "name": "North Quad Junction"},
    "akcnb_entrance": {"x": 220, "y": 160, "name": "AKCNB Main Entrance"},
    "pharmacy_wing": {"x": 172, "y": 120, "name": "Pharmacy Wing Pathway"},
    "cricket_oval": {"x": 140, "y": 275, "name": "Cricket Oval Walkway"}
}
