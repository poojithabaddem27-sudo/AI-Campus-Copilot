import os
import json
import pydeck as pdk
import pandas as pd
from data.gps_calibration import MAP_REFERENCE_POINTS, CAMPUS_ROUTE_PATHS
from data.official_floor_plans import OFFICIAL_FLOOR_PLANS, search_official_floor_plans
from data.viit_campus_map_data import VIIT_CAMPUS_LOCATIONS

def render_pydeck_gps_map(start_gps, end_gps, start_name, end_name):
    """Renders 2D/3D Pydeck satellite map."""
    center_lat = (start_gps.get("lat", 0.0) + end_gps.get("lat", 0.0)) / 2.0
    center_lng = (start_gps.get("lng", 0.0) + end_gps.get("lng", 0.0)) / 2.0

    pins_df = pd.DataFrame([
        {
            "name": f"📍 Start: {start_name}",
            "lat": start_gps.get("lat", 0.0),
            "lng": start_gps.get("lng", 0.0),
            "color": [34, 197, 94, 230],
            "radius": 15
        },
        {
            "name": f"🏁 End: {end_name}",
            "lat": end_gps.get("lat", 0.0),
            "lng": end_gps.get("lng", 0.0),
            "color": [239, 68, 68, 230],
            "radius": 15
        }
    ])

    path_df = pd.DataFrame([
        {
            "path": [
                [start_gps.get("lng", 0.0), start_gps.get("lat", 0.0)],
                [end_gps.get("lng", 0.0), end_gps.get("lat", 0.0)]
            ],
            "color": [37, 99, 235, 255]
        }
    ])

    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pins_df,
        get_position=["lng", "lat"],
        get_color="color",
        get_radius="radius",
        radius_scale=1,
        radius_min_pixels=10,
        radius_max_pixels=30,
        pickable=True
    )

    path_layer = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        get_color="color",
        width_scale=3,
        width_min_pixels=5,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lng,
        zoom=17.5,
        pitch=45,
        bearing=15
    )

    return pdk.Deck(
        layers=[path_layer, scatterplot_layer],
        initial_view_state=view_state,
        tooltip={"html": "<b>{name}</b>"},
        map_style="mapbox://styles/mapbox/satellite-streets-v11" if os.getenv("MAPBOX_API_KEY") else "light"
    )

def render_google_map_html(start_name, end_name, start_xy, end_xy, path_points, distance_m, walk_mins):
    """Renders custom illustrated campus vector map."""
    return render_custom_illustrated_campus_map(start_name, end_name, start_xy, end_xy, path_points, distance_m, walk_mins)

def render_custom_illustrated_campus_map(start_name, end_name, start_xy, end_xy, path_points, distance_m, walk_mins):
    """Renders custom illustrated outdoor campus SVG map."""
    sx, sy = start_xy
    ex, ey = end_xy
    polyline_points = " ".join([f"{pt[0]},{pt[1]}" for pt in path_points])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background: #0F172A; font-family: sans-serif; overflow: hidden; }}
            .map-container {{ position: relative; width: 100%; height: 500px; background: #1E293B; border-radius: 14px; overflow: hidden; }}
            @keyframes dash {{ to {{ stroke-dashoffset: -40; }} }}
            .path-glow {{ stroke: #38BDF8; stroke-width: 10; fill: none; opacity: 0.4; filter: blur(4px); }}
            .path-line {{ stroke: #0284C7; stroke-width: 6; fill: none; stroke-dasharray: 12, 8; animation: dash 1.5s linear infinite; }}
            .building {{ fill: #334155; stroke: #475569; stroke-width: 2; rx: 8; }}
            .road {{ stroke: #475569; stroke-width: 22; fill: none; }}
            .road-inner {{ stroke: #64748B; stroke-width: 18; fill: none; }}
            .text-label {{ fill: #F8FAFC; font-size: 13px; font-weight: 700; text-anchor: middle; }}
        </style>
    </head>
    <body>
        <div class="map-container">
            <svg width="100%" height="100%" viewBox="0 0 900 520">
                <rect width="900" height="520" fill="#0F172A"/>
                <path class="road" d="M 380 500 L 380 430 Q 380 360 340 360 L 150 360 Q 60 360 60 270 Q 60 180 150 180 L 750 180 Q 840 180 840 270 L 840 430"/>
                <path class="road-inner" d="M 380 500 L 380 430 Q 380 360 340 360 L 150 360 Q 60 360 60 270 Q 60 180 150 180 L 750 180 Q 840 180 840 270 L 840 430"/>
                
                <rect class="building" x="320" y="440" width="120" height="50" fill="#1E3A8A"/>
                <text class="text-label" x="380" y="470">Main Entrance</text>

                <rect class="building" x="360" y="290" width="160" height="60"/>
                <text class="text-label" x="440" y="325">Main Block</text>

                <rect class="building" x="180" y="130" width="120" height="50"/>
                <text class="text-label" x="240" y="160">AKCNB</text>

                <polyline class="path-glow" points="{polyline_points}"/>
                <polyline class="path-line" points="{polyline_points}"/>

                <circle cx="{sx}" cy="{sy}" r="12" fill="#10B981" stroke="#FFFFFF" stroke-width="3"/>
                <text class="text-label" x="{sx}" y="{sy - 16}" fill="#10B981">📍 Start: {start_name}</text>

                <circle cx="{ex}" cy="{ey}" r="10" fill="#EF4444" stroke="#FFFFFF" stroke-width="2"/>
                <text class="text-label" x="{ex}" y="{ey - 14}" fill="#EF4444">📌 {end_name}</text>
            </svg>
        </div>
    </body>
    </html>
    """

def render_indoor_floor_map(building_name, floor_name, start_room, target_room_info, all_floor_rooms):
    """Renders architectural indoor floor map."""
    tx = target_room_info.get("x", 450) if target_room_info else 450
    ty = target_room_info.get("y", 160) if target_room_info else 160
    t_name = target_room_info.get("room", "Target") if target_room_info else "Target"

    room_boxes = ""
    for r in all_floor_rooms:
        rx = r.get("x", 200)
        ry = r.get("y", 150)
        rname = r.get("room", "")
        is_target = target_room_info and (rname.lower() == target_room_info.get("room", "").lower())
        fill_color = "#1D4ED8" if is_target else "#334155"
        
        room_boxes += f"""
        <g>
            <rect x="{rx - 70}" y="{ry - 40}" width="140" height="80" rx="8" fill="{fill_color}" stroke="#60A5FA" stroke-width="2"/>
            <text x="{rx}" y="{ry}" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle">{rname}</text>
        </g>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background: #0F172A; font-family: sans-serif; overflow: hidden; }}
            .indoor-container {{ position: relative; width: 100%; height: 500px; background: #1E293B; border-radius: 14px; overflow: hidden; }}
        </style>
    </head>
    <body>
        <div class="indoor-container">
            <svg width="100%" height="100%" viewBox="0 0 900 520">
                <rect x="40" y="60" width="820" height="400" rx="16" fill="#0F172A" stroke="#334155" stroke-width="3"/>
                <rect x="60" y="230" width="780" height="50" fill="#1E293B" stroke="#475569" stroke-width="1.5"/>
                {room_boxes}
                <circle cx="{tx}" cy="{ty + 40}" r="10" fill="#EF4444" stroke="#FFFFFF" stroke-width="2"/>
                <text x="{tx}" y="{ty - 45}" font-size="14" font-weight="800" fill="#38BDF8" text-anchor="middle">📌 {t_name}</text>
            </svg>
        </div>
    </body>
    </html>
    """

def render_realtime_gps_navigation_app(destination_name, dest_xy, dest_gps=None, start_name="Main Entrance", start_xy=(380, 450), start_gps=None):
    """
    Renders an Official VIIT Digital Campus Vector Map inside Campus Route Finder,
    featuring interactive building markers, location cards, destination search,
    floor-map cross-links, manual starting location selection, zoom/pan controls,
    and direction arrowheads along the route path.
    """
    locations_json = json.dumps(VIIT_CAMPUS_LOCATIONS)
    dest_x, dest_y = dest_xy
    init_start_x, init_start_y = start_xy

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background: #0F172A; font-family: 'Segoe UI', system-ui, sans-serif; color: white; overflow: hidden; }}
            .nav-box {{ position: relative; width: 100%; height: 600px; background: #1E293B; border-radius: 16px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 12px 30px rgba(0,0,0,0.4); user-select: none; }}
            
            .controls-bar {{ position: absolute; top: 12px; left: 12px; right: 12px; z-index: 100; display: flex; gap: 10px; flex-wrap: wrap; background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(12px); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); align-items: center; }}
            .btn {{ padding: 8px 14px; border-radius: 8px; border: none; font-weight: 700; font-size: 13px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }}
            .btn-zoom {{ background: #334155; color: white; border: 1px solid #475569; }}
            .btn-zoom:hover {{ background: #475569; }}
            .btn-start {{ background: #2563EB; color: white; }}
            .btn-start:hover {{ background: #1D4ED8; }}
            .btn-dest {{ background: #EF4444; color: white; }}
            .btn-dest:hover {{ background: #DC2626; }}
            .status-banner {{ font-size: 12px; font-weight: 600; color: #38BDF8; display: flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 6px; background: rgba(56, 189, 248, 0.1); }}
            
            .search-box-input {{ background: #0F172A; border: 1px solid #3B82F6; color: white; padding: 7px 12px; border-radius: 8px; font-size: 13px; outline: none; width: 210px; }}
            .search-box-input:focus {{ border-color: #60A5FA; box-shadow: 0 0 8px rgba(96, 165, 250, 0.4); }}

            .location-card {{ position: absolute; bottom: 70px; right: 16px; width: 310px; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(14px); padding: 14px 16px; border-radius: 14px; border: 1px solid #38BDF8; z-index: 110; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: none; animation: slideUp 0.3s ease-out; }}
            @keyframes slideUp {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
            .card-title {{ font-size: 15px; font-weight: 800; color: #38BDF8; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
            .card-type {{ font-size: 12px; font-weight: 700; color: #F59E0B; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }}
            .card-desc {{ font-size: 12px; color: #94A3B8; margin-bottom: 12px; line-height: 1.4; }}
            .card-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
            .btn-floor {{ background: #8B5CF6; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: 700; font-size: 12px; cursor: pointer; }}
            .btn-floor:hover {{ background: #7C3AED; }}

            .arrival-popup {{ position: absolute; top: 80px; left: 50%; transform: translateX(-50%); background: #10B981; color: white; padding: 14px 24px; border-radius: 12px; font-weight: 800; font-size: 16px; z-index: 200; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4); display: none; text-align: center; }}
            
            @keyframes route-flow {{ to {{ stroke-dashoffset: -32; }} }}
            .route-glow {{ stroke: #0284C7; stroke-width: 10; fill: none; opacity: 0.35; stroke-linecap: round; }}
            .route-flowing {{ stroke: #38BDF8; stroke-width: 5; fill: none; stroke-linecap: round; stroke-dasharray: 12, 8; animation: route-flow 1.2s linear infinite; marker-mid: url(#arrow-mid); marker-end: url(#arrow-head); }}
            .user-pulse {{ animation: pulse-ring 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite; }}
            @keyframes pulse-ring {{ 0% {{ r: 10px; opacity: 0.9; }} 50% {{ r: 24px; opacity: 0.2; }} 100% {{ r: 10px; opacity: 0.9; }} }}
            
            .marker-g {{ cursor: pointer; transition: transform 0.2s; }}
            .marker-g:hover {{ transform: scale(1.15); }}
            
            .compass-box {{ position: absolute; top: 75px; right: 16px; z-index: 90; background: rgba(15,23,42,0.85); backdrop-filter: blur(8px); padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.15); font-weight: 800; font-size: 12px; color: #38BDF8; display: flex; align-items: center; gap: 6px; }}
        </style>
    </head>
    <body>
        <div class="nav-box">
            <!-- Controls Bar -->
            <div class="controls-bar">
                <button class="btn btn-zoom" onclick="zoomIn()">➕ Zoom In</button>
                <button class="btn btn-zoom" onclick="zoomOut()">➖ Zoom Out</button>
                <button class="btn btn-zoom" onclick="resetMap()">🔄 Reset View</button>
                <input class="search-box-input" type="text" id="map-search" placeholder="🔍 Search campus location..." oninput="onSearchLocation(this.value)"/>
                <div class="status-banner" id="nav-status"><span>🚩 Route: {start_name} ➔ {destination_name}</span></div>
            </div>

            <!-- Compass / North Indicator -->
            <div class="compass-box">
                <span>🧭</span> <span>NORTH ▲</span>
            </div>

            <!-- Arrival Banner -->
            <div class="arrival-popup" id="arrival-banner">
                🎉 You have arrived!<br>
                <span style="font-size: 13px; font-weight: 600;" id="arrival-dest-name">📍 Destination: {destination_name}</span>
            </div>

            <!-- Information Card Popup -->
            <div class="location-card" id="info-card">
                <div class="card-title" id="card-name">🏢 Main Block</div>
                <div class="card-type" id="card-type">Academic & Administrative</div>
                <div class="card-desc" id="card-desc">Contains 1st–4th Floors...</div>
                <div class="card-actions">
                    <button class="btn btn-start" style="padding: 6px 12px; font-size: 11px;" onclick="setCardAsStart()">🚩 Set as Start</button>
                    <button class="btn btn-dest" style="padding: 6px 12px; font-size: 11px;" onclick="selectCardDestination()">🎯 Set Destination</button>
                    <button class="btn-floor" id="btn-view-floor" style="display: none;" onclick="openFloorMapTab()">🏢 Floor Map</button>
                </div>
            </div>

            <!-- Distance & Walking Time Metrics Bar -->
            <div style="position: absolute; bottom: 16px; left: 16px; z-index: 100; background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(10px); padding: 8px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); display: flex; gap: 16px;">
                <div><span style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Walking Distance</span><br><b id="dist-val" style="color: #38BDF8; font-size: 13px;">-- m</b></div>
                <div><span style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Est. Walking Time</span><br><b id="time-val" style="color: #38BDF8; font-size: 13px;">-- min</b></div>
            </div>

            <!-- OFFICIAL VIIT VECTOR DIGITAL MAP CANVAS -->
            <svg id="campus-svg" width="100%" height="100%" viewBox="0 0 950 540" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <marker id="arrow-head" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#38BDF8"/>
                    </marker>
                    <marker id="arrow-mid" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#60A5FA"/>
                    </marker>
                </defs>

                <rect width="950" height="540" fill="#0F172A"/>

                <!-- TRANSFORMABLE MAP WORLD GROUP (ZOOM / PAN) -->
                <g id="map-world" transform="scale(1) translate(0, 0)">
                    <!-- Outdoor Campus Road Pathways -->
                    <!-- Main Approach Road to Narva -->
                    <path d="M 120 500 L 380 500 L 380 430 Q 380 360 340 360 L 150 360 Q 60 360 60 270 Q 60 180 150 180 L 750 180 Q 840 180 840 270 L 840 430" stroke="#334155" stroke-width="24" fill="none"/>
                    <path d="M 120 500 L 380 500 L 380 430 Q 380 360 340 360 L 150 360 Q 60 360 60 270 Q 60 180 150 180 L 750 180 Q 840 180 840 270 L 840 430" stroke="#475569" stroke-width="18" fill="none"/>

                    <!-- DIGITAL CAMPUS BUILDINGS & FACILITIES (TRACED FROM OFFICIAL VIIT MAP) -->
                    <g id="campus-buildings">
                        <!-- Main Entrance & Security -->
                        <rect x="320" y="430" width="120" height="40" rx="8" fill="#1E3A8A" stroke="#3B82F6" stroke-width="2"/>
                        <text x="380" y="455" fill="#FFFFFF" font-size="11" font-weight="700" text-anchor="middle">🚪 Main Entrance</text>

                        <!-- Main Road to Narva Label -->
                        <rect x="140" y="465" width="120" height="30" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1.5"/>
                        <text x="200" y="484" fill="#94A3B8" font-size="10" font-weight="700" text-anchor="middle">🛣️ Main Road to Narva</text>

                        <!-- Main Academic Block -->
                        <rect x="360" y="290" width="160" height="60" rx="8" fill="#1E293B" stroke="#38BDF8" stroke-width="2.5"/>
                        <text x="440" y="325" fill="#38BDF8" font-size="12" font-weight="800" text-anchor="middle">🏢 Main Block (1st-4th Floors)</text>

                        <!-- Pharmacy College -->
                        <rect x="100" y="90" width="140" height="50" rx="8" fill="#1E293B" stroke="#10B981" stroke-width="2"/>
                        <text x="170" y="120" fill="#10B981" font-size="11" font-weight="700" text-anchor="middle">💊 Pharmacy College</text>

                        <!-- Sports Grounds & Courts -->
                        <!-- Cricket Ground -->
                        <circle cx="140" cy="275" r="55" fill="#064E3B" stroke="#10B981" stroke-width="2" stroke-dasharray="4,3"/>
                        <text x="140" y="278" fill="#A7F3D0" font-size="11" font-weight="800" text-anchor="middle">🏏 Cricket Ground</text>

                        <!-- Football Ground -->
                        <rect x="360" y="80" width="160" height="65" rx="10" fill="#064E3B" stroke="#10B981" stroke-width="2"/>
                        <text x="440" y="118" fill="#A7F3D0" font-size="11" font-weight="800" text-anchor="middle">⚽ Football Ground</text>

                        <!-- Volleyball Court -->
                        <rect x="395" y="390" width="38" height="30" rx="4" fill="#7C2D12" stroke="#F97316" stroke-width="1.5"/>
                        <text x="414" y="410" fill="#FFEDD5" font-size="9" font-weight="700" text-anchor="middle">🏐 VB</text>

                        <!-- Basketball Court -->
                        <rect x="440" y="390" width="40" height="30" rx="4" fill="#7C2D12" stroke="#F97316" stroke-width="1.5"/>
                        <text x="460" y="410" fill="#FFEDD5" font-size="9" font-weight="700" text-anchor="middle">🏀 BB</text>

                        <!-- Tennis Court -->
                        <rect x="520" y="390" width="38" height="30" rx="4" fill="#065F46" stroke="#34D399" stroke-width="1.5"/>
                        <text x="539" y="410" fill="#D1FAE5" font-size="9" font-weight="700" text-anchor="middle">🎾 Tennis</text>

                        <!-- Indoor Sports Hall -->
                        <rect x="485" y="390" width="32" height="30" rx="4" fill="#581C87" stroke="#A855F7" stroke-width="1.5"/>
                        <text x="501" y="410" fill="#F3E8FF" font-size="9" font-weight="700" text-anchor="middle">🏸 Ind</text>

                        <!-- Outdoor Badminton Court -->
                        <rect x="562" y="390" width="38" height="30" rx="4" fill="#581C87" stroke="#C084FC" stroke-width="1.5"/>
                        <text x="581" y="410" fill="#F3E8FF" font-size="9" font-weight="700" text-anchor="middle">🏸 Badm</text>

                        <!-- Girls Hostel & Mess -->
                        <rect x="620" y="130" width="130" height="55" rx="8" fill="#1E293B" stroke="#F43F5E" stroke-width="2"/>
                        <text x="685" y="162" fill="#FDA4AF" font-size="11" font-weight="700" text-anchor="middle">🏠 Girls Hostel & Mess</text>

                        <!-- Facilities Block -->
                        <rect x="660" y="275" width="110" height="50" rx="8" fill="#1E293B" stroke="#64748B" stroke-width="2"/>
                        <text x="715" y="305" fill="#CBD5E1" font-size="11" font-weight="700" text-anchor="middle">🛠️ Facilities Block</text>

                        <!-- Campus Canteen -->
                        <rect x="310" y="220" width="85" height="40" rx="6" fill="#78350F" stroke="#F59E0B" stroke-width="1.5"/>
                        <text x="352" y="245" fill="#FEF08A" font-size="11" font-weight="700" text-anchor="middle">☕ Canteen</text>

                        <!-- Student Parking -->
                        <rect x="270" y="260" width="75" height="35" rx="6" fill="#334155" stroke="#94A3B8" stroke-width="1.5"/>
                        <text x="307" y="282" fill="#E2E8F0" font-size="10" font-weight="700" text-anchor="middle">🅿️ Parking</text>

                        <!-- Faculty Parking -->
                        <rect x="350" y="260" width="75" height="35" rx="6" fill="#334155" stroke="#60A5FA" stroke-width="1.5"/>
                        <text x="387" y="282" fill="#93C5FD" font-size="10" font-weight="700" text-anchor="middle">🚗 Faculty Park</text>

                        <!-- ATM Counter -->
                        <rect x="600" y="430" width="70" height="35" rx="6" fill="#14532D" stroke="#22C55E" stroke-width="1.5"/>
                        <text x="635" y="452" fill="#86EFAC" font-size="10" font-weight="700" text-anchor="middle">🏧 ATM</text>

                        <!-- Central Courtyard -->
                        <rect x="400" y="210" width="90" height="40" rx="8" fill="#064E3B" stroke="#34D399" stroke-width="1.5" stroke-dasharray="4,2"/>
                        <text x="445" y="234" fill="#A7F3D0" font-size="10" font-weight="700" text-anchor="middle">🌳 Courtyard</text>
                    </g>

                    <!-- Dynamic Flowing Blue Route Layer -->
                    <polyline id="route-glow-line" class="route-glow" points=""/>
                    <polyline id="route-flow-line" class="route-flowing" points=""/>

                    <!-- INTERACTIVE TAPPABLE LOCATION MARKERS -->
                    <g id="interactive-markers"></g>

                    <!-- STARTING CAMPUS POSITION MARKER (🚩 START) -->
                    <g id="user-marker" transform="translate({init_start_x}, {init_start_y})">
                        <circle class="user-pulse" cx="0" cy="0" r="16" fill="#3B82F6"/>
                        <circle cx="0" cy="0" r="9" fill="#2563EB" stroke="#FFFFFF" stroke-width="2.5"/>
                        <circle cx="0" cy="0" r="3" fill="#FFFFFF"/>
                        <text id="start-label-text" x="0" y="-18" fill="#60A5FA" font-size="11" font-weight="800" text-anchor="middle">🚩 START ({start_name})</text>
                    </g>

                    <!-- TARGET DESTINATION MARKER -->
                    <g id="target-dest-marker" transform="translate({dest_x}, {dest_y})">
                        <circle cx="0" cy="0" r="14" fill="#EF4444" opacity="0.3"/>
                        <circle cx="0" cy="0" r="8" fill="#EF4444" stroke="#FFFFFF" stroke-width="2"/>
                        <text id="dest-label-text" x="0" y="-16" fill="#F87171" font-size="12" font-weight="800" text-anchor="middle">🔴 {destination_name}</text>
                    </g>
                </g>
            </svg>
        </div>

        <script>
            const campusLocations = {locations_json};

            let startName = "{start_name}";
            let currentX = {init_start_x};
            let currentY = {init_start_y};

            let currentDestName = "{destination_name}";
            let currentDestX = {dest_x};
            let currentDestY = {dest_y};
            let selectedLocationObj = null;

            let currentScale = 1.0;

            function zoomIn() {{
                if (currentScale < 2.2) {{
                    currentScale += 0.2;
                    applyTransform();
                }}
            }}

            function zoomOut() {{
                if (currentScale > 0.7) {{
                    currentScale -= 0.2;
                    applyTransform();
                }}
            }}

            function resetMap() {{
                currentScale = 1.0;
                applyTransform();
            }}

            function applyTransform() {{
                document.getElementById("map-world").setAttribute("transform", "scale(" + currentScale + ")");
            }}

            function updateStatus(msg, isError = false) {{
                const el = document.getElementById("nav-status");
                el.innerHTML = (isError ? "⚠️ " : "🚩 ") + msg;
                el.style.color = isError ? "#F87171" : "#38BDF8";
            }}

            function renderInteractiveMarkers() {{
                const layer = document.getElementById("interactive-markers");
                layer.innerHTML = "";

                for (let key in campusLocations) {{
                    let loc = campusLocations[key];
                    let g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                    g.setAttribute("class", "marker-g");
                    g.setAttribute("transform", "translate(" + loc.x + ", " + loc.y + ")");
                    g.onclick = function() {{
                        selectLocation(key);
                    }};

                    let circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                    circle.setAttribute("cx", "0");
                    circle.setAttribute("cy", "0");
                    circle.setAttribute("r", "7");
                    circle.setAttribute("fill", "#F59E0B");
                    circle.setAttribute("stroke", "#FFFFFF");
                    circle.setAttribute("stroke-width", "1.5");

                    g.appendChild(circle);
                    layer.appendChild(g);
                }}
            }}

            function selectLocation(key) {{
                let loc = campusLocations[key];
                if (!loc) return;

                selectedLocationObj = loc;
                document.getElementById("card-name").innerText = loc.icon + " " + loc.name;
                document.getElementById("card-type").innerText = loc.type;
                document.getElementById("card-desc").innerText = loc.description;
                
                const btnFloor = document.getElementById("btn-view-floor");
                btnFloor.style.display = loc.has_floor_map ? "inline-block" : "none";

                document.getElementById("info-card").style.display = "block";
            }}

            function setCardAsStart() {{
                if (!selectedLocationObj) return;
                startName = selectedLocationObj.name;
                currentX = selectedLocationObj.x;
                currentY = selectedLocationObj.y;

                document.getElementById("user-marker").setAttribute("transform", "translate(" + currentX + ", " + currentY + ")");
                document.getElementById("start-label-text").textContent = "🚩 START (" + startName + ")";

                updateLiveRoute(currentX, currentY);
                updateStatus("Route: " + startName + " ➔ " + currentDestName);
            }}

            function selectCardDestination() {{
                if (!selectedLocationObj) return;
                currentDestName = selectedLocationObj.name;
                currentDestX = selectedLocationObj.x;
                currentDestY = selectedLocationObj.y;

                document.getElementById("target-dest-marker").setAttribute("transform", "translate(" + currentDestX + ", " + currentDestY + ")");
                document.getElementById("dest-label-text").textContent = "🔴 " + currentDestName;
                document.getElementById("arrival-dest-name").innerText = "📍 Destination: " + currentDestName;

                updateLiveRoute(currentX, currentY);
                updateStatus("Route: " + startName + " ➔ " + currentDestName);
            }}

            function onSearchLocation(query) {{
                if (!query || !query.trim()) return;
                let q = query.trim().toLowerCase();
                for (let key in campusLocations) {{
                    let loc = campusLocations[key];
                    if (key.toLowerCase().includes(q) || loc.name.toLowerCase().includes(q) || loc.type.toLowerCase().includes(q)) {{
                        selectLocation(key);
                        break;
                    }}
                }}
            }}

            function openFloorMapTab() {{
                alert("Click on the '🗺️ Interactive Floor Map' tab above to view the detailed 1st-4th floor plans of Main Block!");
            }}

            function updateLiveRoute(x, y) {{
                let ptsStr = x + "," + y + " 340,360 " + currentDestX + "," + currentDestY;
                document.getElementById("route-glow-line").setAttribute("points", ptsStr);
                document.getElementById("route-flow-line").setAttribute("points", ptsStr);

                let distM = Math.round(Math.hypot(currentDestX - x, currentDestY - y) * 0.8);
                document.getElementById("dist-val").innerText = distM + " m";
                document.getElementById("time-val").innerText = Math.max(1, Math.round(distM / 68)) + " min";
            }}

            renderInteractiveMarkers();
            updateLiveRoute(currentX, currentY);
        </script>
    </body>
    </html>
    """

def render_official_viit_interactive_map(selected_floor, selected_block, search_query=""):
    """
    Renders the official 4-floor, 7-block VIIT interactive vector digital map.
    Blocks: Vayu, Aakash, Prudhvi, Teja, Varun, Agni, G Block.
    Highlights searched rooms, displays room info cards, and supports floor & block filters.
    """
    floor_data = OFFICIAL_FLOOR_PLANS.get(selected_floor, OFFICIAL_FLOOR_PLANS.get("First Floor", {}))
    floor_json = json.dumps(floor_data)
    all_floors_json = json.dumps(OFFICIAL_FLOOR_PLANS)
    search_q = (search_query or "").strip().lower()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background: #0F172A; font-family: 'Segoe UI', system-ui, sans-serif; color: white; }}
            .map-card {{ position: relative; width: 100%; height: 600px; background: #1E293B; border-radius: 16px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 12px 30px rgba(0,0,0,0.4); }}
            
            .info-panel {{ position: absolute; bottom: 16px; right: 16px; width: 320px; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(14px); padding: 14px 18px; border-radius: 14px; border: 1px solid #38BDF8; z-index: 100; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: none; animation: slideIn 0.3s ease-out; }}
            @keyframes slideIn {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
            .info-title {{ font-size: 16px; font-weight: 800; color: #38BDF8; margin-bottom: 4px; }}
            .info-sub {{ font-size: 13px; color: #E2E8F0; font-weight: 600; margin-bottom: 2px; }}
            .info-meta {{ font-size: 12px; color: #94A3B8; margin-top: 6px; line-height: 1.4; }}
            
            .legend-bar {{ position: absolute; top: 14px; left: 14px; z-index: 90; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); padding: 8px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.15); display: flex; gap: 12px; flex-wrap: wrap; font-size: 11px; font-weight: 600; }}
            .lg-item {{ display: flex; align-items: center; gap: 5px; }}
            .lg-dot {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; }}
            
            .room-rect {{ cursor: pointer; transition: all 0.2s ease-in-out; }}
            .room-rect:hover {{ stroke: #38BDF8 !important; stroke-width: 3px !important; filter: drop-shadow(0 0 8px #38BDF8); }}
            
            @keyframes gold-pulse {{
                0% {{ stroke: #F59E0B; stroke-width: 3px; }}
                50% {{ stroke: #FBBF24; stroke-width: 6px; }}
                100% {{ stroke: #F59E0B; stroke-width: 3px; }}
            }}
            .highlight-target {{ animation: gold-pulse 1.2s infinite; fill: #78350F !important; }}
        </style>
    </head>
    <body>
        <div class="map-card">
            <!-- Legend Bar -->
            <div class="legend-bar">
                <div class="lg-item"><span class="lg-dot" style="background:#1E3A8A"></span> Office</div>
                <div class="lg-item"><span class="lg-dot" style="background:#065F46"></span> Lecture Hall</div>
                <div class="lg-item"><span class="lg-dot" style="background:#831843"></span> Lab / Research</div>
                <div class="lg-item"><span class="lg-dot" style="background:#581C87"></span> Library / Computing</div>
                <div class="lg-item"><span class="lg-dot" style="background:#701A75"></span> Staff Room</div>
                <div class="lg-item"><span class="lg-dot" style="background:#475569"></span> Restroom / Lift</div>
                <div class="lg-item"><span class="lg-dot" style="background:#14532D"></span> Open to Sky</div>
            </div>

            <!-- Click Info Panel -->
            <div class="info-panel" id="room-card">
                <div class="info-title" id="card-room">📌 Room: --</div>
                <div class="info-sub" id="card-name">🏷️ Name: --</div>
                <div class="info-meta" id="card-block">🏢 Block: --</div>
                <div class="info-meta" id="card-floor">📶 Floor: {selected_floor}</div>
                <div class="info-meta" id="card-wings" style="color: #38BDF8; font-weight: 600; margin-top: 6px;"></div>
            </div>

            <!-- SVG Digital Campus Canvas -->
            <svg id="viit-svg" width="100%" height="100%" viewBox="0 0 950 560" preserveAspectRatio="xMidYMid meet">
                <rect width="950" height="560" fill="#0F172A"/>

                <!-- Main Outer Courtyard Corridor Framework -->
                <rect x="80" y="50" width="790" height="450" rx="18" fill="none" stroke="#334155" stroke-width="4"/>
                <rect x="180" y="140" width="590" height="270" rx="14" fill="#1E293B" stroke="#475569" stroke-width="2"/>

                <!-- BLOCK CONTAINERS & LABELS -->
                <!-- 1. VAYU BLOCK (Top Left) -->
                <g id="vayu-group">
                    <rect x="90" y="60" width="370" height="70" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="100" y="78" fill="#38BDF8" font-size="11" font-weight="800">VAYU BLOCK (North-West)</text>
                </g>

                <!-- 2. AAKASH BLOCK (Top Right) -->
                <g id="aakash-group">
                    <rect x="490" y="60" width="370" height="70" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="500" y="78" fill="#38BDF8" font-size="11" font-weight="800">AAKASH BLOCK (North-East)</text>
                </g>

                <!-- 3. PRUDHVI BLOCK (West Wing) -->
                <g id="prudhvi-group">
                    <rect x="90" y="140" width="80" height="270" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="130" y="160" fill="#38BDF8" font-size="11" font-weight="800" text-anchor="middle" transform="rotate(-90 130 160)">PRUDHVI BLOCK</text>
                </g>

                <!-- 4. TEJA BLOCK (East Wing) -->
                <g id="teja-group">
                    <rect x="780" y="140" width="80" height="270" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="820" y="160" fill="#38BDF8" font-size="11" font-weight="800" text-anchor="middle" transform="rotate(90 820 160)">TEJA BLOCK</text>
                </g>

                <!-- 5. AGNI BLOCK (Bottom Left) -->
                <g id="agni-group">
                    <rect x="90" y="420" width="370" height="70" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="100" y="480" fill="#38BDF8" font-size="11" font-weight="800">AGNI BLOCK (South-West)</text>
                </g>

                <!-- 6. VARUN BLOCK (Bottom Right) -->
                <g id="varun-group">
                    <rect x="490" y="420" width="370" height="70" rx="10" fill="rgba(30, 41, 59, 0.8)" stroke="#38BDF8" stroke-width="1.5"/>
                    <text x="500" y="480" fill="#38BDF8" font-size="11" font-weight="800">VARUN BLOCK (South-East)</text>
                </g>

                <!-- 7. G BLOCK (Central Courtyard & Core Hub) -->
                <g id="gblock-group">
                    <rect x="250" y="180" width="450" height="190" rx="14" fill="#0F172A" stroke="#F59E0B" stroke-width="2" stroke-dasharray="6,4"/>
                    <text x="475" y="200" fill="#F59E0B" font-size="13" font-weight="800" text-anchor="middle">G BLOCK - CENTRAL COURTYARD & HUB</text>
                </g>

                <!-- DYNAMICALLY RENDERED ROOM BLOCKS LAYER -->
                <g id="rooms-layer"></g>
            </svg>
        </div>

        <script>
            const floorData = {floor_json};
            const selectedFloorName = "{selected_floor}";
            const selectedBlockName = "{selected_block}";
            const searchQuery = "{search_q}";

            function getRoomColor(type) {{
                switch(type) {{
                    case "Office": return "#1E3A8A";
                    case "LectureHall": return "#065F46";
                    case "Lab": return "#831843";
                    case "Library":
                    case "ComputingCenter":
                    case "Auditorium": return "#581C87";
                    case "StaffRoom": return "#701A75";
                    case "Toilet":
                    case "Lift": return "#475569";
                    case "OpenArea": return "#14532D";
                    default: return "#334155";
                }}
            }}

            function renderRooms() {{
                const layer = document.getElementById("rooms-layer");
                layer.innerHTML = "";

                let targetMatched = false;

                for (let blockName in floorData) {{
                    if (selectedBlockName !== "All Blocks" && selectedBlockName !== blockName) {{
                        continue;
                    }}

                    let rooms = floorData[blockName];
                    for (let r of rooms) {{
                        let rnum = r.roomNumber;
                        let rname = r.roomName;
                        let rtype = r.type || "General";
                        let x = r.x;
                        let y = r.y;
                        let isGBlock = (blockName === "G Block");
                        
                        let width = isGBlock ? 380 : 54;
                        let height = isGBlock ? 110 : 44;

                        let isMatch = searchQuery && (
                            rnum.toLowerCase().includes(searchQuery) ||
                            rname.toLowerCase().includes(searchQuery) ||
                            blockName.toLowerCase().includes(searchQuery)
                        );

                        let fill = getRoomColor(rtype);
                        let stroke = isMatch ? "#F59E0B" : "#475569";
                        let className = "room-rect" + (isMatch ? " highlight-target" : "");

                        let g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                        g.onclick = function() {{
                            showCard(rnum, rname, blockName, selectedFloorName, r.wings || []);
                        }};

                        let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                        rect.setAttribute("class", className);
                        rect.setAttribute("x", x - (width/2));
                        rect.setAttribute("y", y - (height/2));
                        rect.setAttribute("width", width);
                        rect.setAttribute("height", height);
                        rect.setAttribute("rx", "6");
                        rect.setAttribute("fill", fill);
                        rect.setAttribute("stroke", stroke);
                        rect.setAttribute("stroke-width", isMatch ? "3" : "1.5");

                        let textNum = document.createElementNS("http://www.w3.org/2000/svg", "text");
                        textNum.setAttribute("x", x);
                        textNum.setAttribute("y", isGBlock ? y - 10 : y - 4);
                        textNum.setAttribute("fill", "#FFFFFF");
                        textNum.setAttribute("font-size", isGBlock ? "14" : "10");
                        textNum.setAttribute("font-weight", "800");
                        textNum.setAttribute("text-anchor", "middle");
                        textNum.setAttribute("pointer-events", "none");
                        textNum.textContent = rnum;

                        let textName = document.createElementNS("http://www.w3.org/2000/svg", "text");
                        textName.setAttribute("x", x);
                        textName.setAttribute("y", isGBlock ? y + 12 : y + 10);
                        textName.setAttribute("fill", isMatch ? "#FDE047" : "#CBD5E1");
                        textName.setAttribute("font-size", isGBlock ? "12" : "8");
                        textName.setAttribute("font-weight", "600");
                        textName.setAttribute("text-anchor", "middle");
                        textName.setAttribute("pointer-events", "none");
                        textName.textContent = rname.length > 18 ? rname.substring(0, 16) + "..." : rname;

                        g.appendChild(rect);
                        g.appendChild(textNum);
                        g.appendChild(textName);
                        layer.appendChild(g);

                        if (isMatch && !targetMatched) {{
                            targetMatched = true;
                            showCard(rnum, rname, blockName, selectedFloorName, r.wings || []);
                        }}
                    }}
                }}
            }}

            function showCard(rnum, rname, bname, fname, wings) {{
                const card = document.getElementById("room-card");
                document.getElementById("card-room").innerText = "📌 Room: " + rnum;
                document.getElementById("card-name").innerText = "🏷️ Name: " + rname;
                document.getElementById("card-block").innerText = "🏢 Block: " + bname;
                document.getElementById("card-floor").innerText = "📶 Floor: " + fname;
                
                let wingsEl = document.getElementById("card-wings");
                if (wings && wings.length > 0) {{
                    wingsEl.innerText = "💻 Wings: " + wings.join(", ");
                }} else {{
                    wingsEl.innerText = "";
                }}

                card.style.display = "block";
            }}

            renderRooms();
        </script>
    </body>
    </html>
    """
