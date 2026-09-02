# ==============================================================================
# VIIT DIGITAL CAMPUS ROAD & PATHWAY NETWORK GRAPH
# Graph representation of campus roads, junctions, and walkways
# ==============================================================================

# Campus Road Waypoint Nodes (x, y coordinates on the digital map grid)
CAMPUS_GRAPH_NODES = {
    "main_entrance": {"x": 380, "y": 450, "name": "Main Entrance"},
    "main_road_narva": {"x": 200, "y": 480, "name": "Main Road to Narva"},
    "south_junction": {"x": 380, "y": 420, "name": "South Entrance Junction"},
    "sports_junction": {"x": 460, "y": 420, "name": "Sports Courts Plaza"},
    "east_gate_path": {"x": 635, "y": 445, "name": "ATM & East Approach"},
    "central_avenue_south": {"x": 340, "y": 360, "name": "Central Avenue South"},
    "main_block_plaza": {"x": 425, "y": 320, "name": "Main Block Plaza"},
    "parking_junction": {"x": 310, "y": 275, "name": "Parking Area Junction"},
    "canteen_square": {"x": 350, "y": 240, "name": "Canteen Square"},
    "central_courtyard": {"x": 440, "y": 230, "name": "Central Plaza & Courtyard"},
    "north_quad_junction": {"x": 340, "y": 160, "name": "North Quad Junction"},
    "pharmacy_wing": {"x": 170, "y": 120, "name": "Pharmacy College"},
    "cricket_oval": {"x": 140, "y": 275, "name": "Cricket Ground"},
    "football_pitch": {"x": 440, "y": 110, "name": "Football Ground"},
    "girls_hostel_path": {"x": 680, "y": 160, "name": "Girls Hostel & Mess"},
    "facilities_path": {"x": 715, "y": 300, "name": "Facilities Block"}
}

# Campus Road Network Edges (Connected Waypoint Paths)
CAMPUS_GRAPH_EDGES = [
    ("main_road_narva", "main_entrance"),
    ("main_entrance", "south_junction"),
    ("south_junction", "sports_junction"),
    ("south_junction", "central_avenue_south"),
    ("sports_junction", "east_gate_path"),
    ("central_avenue_south", "main_block_plaza"),
    ("central_avenue_south", "parking_junction"),
    ("parking_junction", "cricket_oval"),
    ("parking_junction", "canteen_square"),
    ("canteen_square", "main_block_plaza"),
    ("canteen_square", "central_courtyard"),
    ("canteen_square", "north_quad_junction"),
    ("north_quad_junction", "pharmacy_wing"),
    ("north_quad_junction", "football_pitch"),
    ("football_pitch", "girls_hostel_path"),
    ("main_block_plaza", "facilities_path"),
    ("girls_hostel_path", "facilities_path")
]
