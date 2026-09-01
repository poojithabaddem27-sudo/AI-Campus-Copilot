import streamlit as st
import streamlit.components.v1 as components
import os
import pypdf
import json
from data.floor_locations import FLOOR_LOCATIONS, get_location_icon
from data.indoor_floor_data import INDOOR_FLOOR_DATA, get_indoor_room_details
from data.gps_calibration import MAP_REFERENCE_POINTS
from data.official_floor_plans import OFFICIAL_FLOOR_PLANS, search_official_floor_plans
from data.viit_campus_map_data import VIIT_CAMPUS_LOCATIONS
from utils.campus_db_helper import (
    load_campus_data,
    get_all_locations,
    get_categories,
    search_locations,
    parse_room_code
)
from utils.navigation_helper import (
    find_route,
    load_gps_coords,
    save_gps_coords,
    haversine_distance,
    get_nearest_building_from_gps
)
from utils.map_renderer import (
    render_pydeck_gps_map,
    render_custom_illustrated_campus_map,
    render_indoor_floor_map,
    render_realtime_gps_navigation_app,
    render_google_maps_outdoor_app,
    render_official_viit_interactive_map
)
from utils.ai_helper import generate_campus_response, summarize_study_material, get_gemini_api_key, get_google_maps_api_key
from utils.voice_helper import render_inside_input_mic_button, render_speech_synthesis_player

# 1. Page Configuration
st.set_page_config(
    page_title="AI Campus Copilot | Navigation & Floor Map",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Advanced Custom CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #0D9488 100%);
        border-radius: 16px;
        padding: 1.8rem 2rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.3);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #E0F2FE;
        margin-bottom: 0.8rem;
        font-weight: 400;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        color: white;
        text-align: center;
    }
    .stat-num {
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #BAE6FD;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    .directory-result-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .floor-item-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0284C7;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .route-step-card {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
    }

    .badge-cat {
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Session States
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Welcome to **AI Campus Copilot**! Explore the official VIIT digital campus map and real-time GPS navigation!"}
    ]

# 3. Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/100/graduation-cap.png", width=75)
    st.title("🎓 Campus Copilot")
    st.caption("Official VIIT Floor Plan Portal")
    
    st.divider()
    
    st.subheader("⚙️ System Status")
    gemini_key = get_gemini_api_key()
    gmaps_key = get_google_maps_api_key()

    if gemini_key:
        st.success("✅ AI Assistant Connected (Gemini Flash)", icon="⚡")
    else:
        st.info("ℹ️ AI Running in Grounded Campus Database Mode (Add GEMINI_API_KEY to secrets.toml for live GenAI).")

    st.success("✅ Campus Database Available (VIIT Dataset)", icon="📚")
    st.success("✅ GPS Real-Time Device Location Ready", icon="📍")

    if gmaps_key:
        st.success("🗺️ Google Maps Satellite Navigation Connected", icon="🛰️")
    else:
        st.info("ℹ️ Running in Vector Campus Map Mode (Add GOOGLE_MAPS_API_KEY to secrets.toml for live Google Maps satellite).")

    st.divider()


    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Chat reset! How can I help you today?"}
        ]
        st.rerun()

# 4. Hero Header Banner
locations_all = get_all_locations()

st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">🏫 AI Campus Copilot</div>
        <div class="hero-subtitle">Official VIIT Digital Interactive Campus Map & Navigation Portal</div>
        <div style="display: flex; gap: 1rem; margin-top: 0.8rem;">
            <div class="stat-card" style="flex: 1;">
                <div class="stat-num">VIIT Map</div>
                <div class="stat-label">Official Campus Layout</div>
            </div>
            <div class="stat-card" style="flex: 1;">
                <div class="stat-num">4 Floors</div>
                <div class="stat-label">Detailed Indoor Plans</div>
            </div>
            <div class="stat-card" style="flex: 1;">
                <div class="stat-num">Navigation</div>
                <div class="stat-label">Campus Route Finder</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 5. Multi-Tab Navigation
tab_route, tab_chat, tab_dir, tab_floors, tab_study = st.tabs([
    "🧭 Campus Route Finder",
    "💬 AI Assistant",
    "📍 Campus Directory",
    "🗺️ Interactive Floor Map",
    "📚 Study Helper"
])

# ==============================================================================
# TAB 1: CAMPUS ROUTE FINDER (OFFICIAL VIIT DIGITAL VECTOR CAMPUS MAP)
# ==============================================================================
with tab_route:
    st.subheader("🧭 Campus Route Finder & Digital Interactive Map")
    st.write("Source of truth digital interactive map of **Vignan's Institute of Information Technology**. Select your starting campus location and target destination to view the route, walking distance, and floor plans.")

    # Starting Location & Target Destination Selection
    col_nav1, col_nav2 = st.columns([1, 1])

    viit_location_names = sorted(list(VIIT_CAMPUS_LOCATIONS.keys()))

    with col_nav1:
        start_choice = st.selectbox(
            "🚩 Select Starting Campus Location:",
            ["Main Entrance"] + [n for n in viit_location_names if n != "Main Entrance"] + ["Other / Enter location manually"]
        )
        if start_choice == "Other / Enter location manually":
            manual_start_name = st.text_input("Type starting location name:", value="Back Gate")
            start_name = manual_start_name if manual_start_name else "Manual Start"
            start_xy = (680, 60)
        else:
            start_name = start_choice
            s_info = VIIT_CAMPUS_LOCATIONS.get(start_name, VIIT_CAMPUS_LOCATIONS["Main Entrance"])
            start_xy = (s_info["x"], s_info["y"])

    with col_nav2:
        dest_select = st.selectbox(
            "🎯 Select Target Destination:",
            viit_location_names,
            index=viit_location_names.index("Main Block") if "Main Block" in viit_location_names else 0
        )
        dest_info = VIIT_CAMPUS_LOCATIONS.get(dest_select, VIIT_CAMPUS_LOCATIONS["Main Block"])
        dest_xy = (dest_info["x"], dest_info["y"])

    if st.button("🚀 Find Route & Show Digital Campus Map", type="primary", use_container_width=True):
        st.success(f"Showing Campus Route: **{start_name}** ➔ **{dest_select}**")

    st.markdown("---")

    gmaps_key = get_google_maps_api_key()
    if gmaps_key:
        st.info("🗺️ **Google Maps Outdoor Navigation Active**: Satellite view enabled with real-time GPS tracking & walking ETA.")
        realtime_nav_html = render_google_maps_outdoor_app(
            dest_select, dest_xy, {},
            start_name=start_name, start_xy=start_xy, start_gps={},
            api_key=gmaps_key
        )
    else:
        st.info("ℹ️ **Vector Campus Map Mode**: Add `GOOGLE_MAPS_API_KEY` to Streamlit Secrets (`.streamlit/secrets.toml`) to activate live Google Maps satellite rendering.")
        realtime_nav_html = render_realtime_gps_navigation_app(
            dest_select, dest_xy, {},
            start_name=start_name, start_xy=start_xy, start_gps={}
        )
    components.html(realtime_nav_html, height=635, scrolling=False)

    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.9); border: 1.5px solid #38BDF8; padding: 14px 18px; border-radius: 12px; margin-top: 14px;">
        <h4 style="color: #38BDF8; margin: 0 0 8px 0;">🏢 Outdoor-to-Indoor Navigation Flow</h4>
        <p style="color: #CBD5E1; font-size: 13px; margin: 0 0 10px 0;">
            GPS Geolocation provides outdoor route navigation across VIIT campus buildings. When you arrive at your target building, switch to the <b>🗺️ Interactive Floor Map</b> tab to view exact room-level architectural floor plans (1st–4th Floors).
        </p>
        <div style="font-size: 13px; font-weight: 700; color: #34D399;">
            📍 GPS Outdoor Location ➔ 🏢 Campus Building ➔ 🏬 Floor Selection ➔ 🗺️ Official Floor Plan Map ➔ 📌 Target Room
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# TAB 2: AI ASSISTANT (Chatbot)
# ==============================================================================
# TAB 2: AI ASSISTANT (Voice & Text Chatbot)
# ==============================================================================
with tab_chat:
    st.subheader("💬 AI Campus Assistant & Voice Input")
    st.write("Ask questions about official VIIT floor plans, rooms, labs, library, or campus routes.")

    # Check for automatic Speech-to-Text query URL parameter
    auto_voice_param = st.query_params.get("vq", None)
    voice_query_text = None
    if auto_voice_param and auto_voice_param.strip():
        voice_query_text = auto_voice_param.strip()
        st.query_params.clear()

    st.write("**🎤 Sample Questions:**")
    v_cols = st.columns(5)
    voice_shortcut = None
    if v_cols[0].button("📚 Where is library?"):
        voice_shortcut = "Where is the library?"
    if v_cols[1].button("🔬 Where is CSE Lab?"):
        voice_shortcut = "Where is the CSE laboratory?"
    if v_cols[2].button("🎭 Seminar Hall floor?"):
        voice_shortcut = "Which floor is the seminar hall on?"
    if v_cols[3].button("🏛️ Admin Office?"):
        voice_shortcut = "Where is the administration office?"
    if v_cols[4].button("🗺️ Show me the route"):
        voice_shortcut = "Yes, show me the route."

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and len(msg["content"]) > 10:
                components.html(render_speech_synthesis_player(msg["content"], element_id=f"tts-{idx}"), height=42, scrolling=False)

    # Render microphone button directly INSIDE st.chat_input container [ Ask about floor plans... 🎤 ➤ ]
    components.html(render_inside_input_mic_button(), height=0, scrolling=False)
    user_input = st.chat_input("Ask about floor plans, rooms, routes...")
    target_query = voice_query_text or voice_shortcut or user_input

    if target_query:
        st.session_state.messages.append({"role": "user", "content": target_query})
        with st.chat_message("user"):
            st.markdown(target_query)

        api_key = get_gemini_api_key()
        with st.chat_message("assistant"):
            with st.spinner("Searching official VIIT floor database..."):
                ai_response = generate_campus_response(target_query, api_key=api_key)
                st.markdown(ai_response)
                components.html(render_speech_synthesis_player(ai_response, element_id=f"tts-live-{len(st.session_state.messages)}"), height=42, scrolling=False)

        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==============================================================================
# TAB 3: CAMPUS DIRECTORY
# ==============================================================================
with tab_dir:
    st.subheader("📍 VIIT Campus Directory Search")
    st.write("Search through official rooms, labs, offices, and facilities across all 4 floors and 7 blocks.")

    col_f1, col_f2 = st.columns([3, 1])
    search_term = col_f1.text_input("🔍 Search Room, Lab, or Facility (e.g. D-32, A-22, Library, G-03, AKCNB):", value="D-32", placeholder="Type D-32, Library, G-03, etc...")
    category_filter = col_f2.selectbox("Filter Floor:", ["All"] + list(OFFICIAL_FLOOR_PLANS.keys()))

    matching_results = search_locations(search_term) if search_term else locations_all

    if category_filter != "All":
        matching_results = [m for m in matching_results if m.get("floor") == category_filter]

    st.caption(f"Showing **{len(matching_results)}** matching location(s)")

    if not matching_results:
        st.warning("⚠️ No matching location found.")
    else:
        grid_cols = st.columns(2)
        for idx, item in enumerate(matching_results):
            with grid_cols[idx % 2]:
                st.markdown(f"""
                    <div class="directory-result-card">
                        <div style="font-size: 1.2rem; font-weight: 800; color: #0F172A; margin-bottom: 0.4rem;">
                            {item['icon']} {item['name']}
                        </div>
                        <div style="font-size: 0.95rem; color: #2563EB; font-weight: 700; margin-bottom: 0.3rem;">
                            🏢 Located on: <b>{item['floor']}</b> ({item['block']})
                        </div>
                        <div style="font-size: 0.85rem; color: #64748B;">
                            Official VIIT floor plan entry
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# TAB 4: INTERACTIVE FLOOR MAP (OFFICIAL VIIT 4-FLOOR 7-BLOCK DIGITAL MAP)
# ==============================================================================
with tab_floors:
    st.subheader("🗺️ Official VIIT Interactive Digital Campus Floor Map")
    st.write("Source of truth schematic floor plans for **Vignan's Institute of Information Technology** (First, Second, Third, Fourth Floor).")

    # 1. FLOOR SWITCHER BUTTONS
    st.markdown("#### 1. Select Floor Level:")
    floor_list = list(OFFICIAL_FLOOR_PLANS.keys())
    f_cols = st.columns(len(floor_list))
    
    if "current_floor_select" not in st.session_state:
        st.session_state.current_floor_select = "Third Floor"
        
    for idx, fname in enumerate(floor_list):
        if f_cols[idx].button(f"📶 {fname}", type="primary" if st.session_state.current_floor_select == fname else "secondary", use_container_width=True):
            st.session_state.current_floor_select = fname
            st.rerun()

    current_selected_floor = st.session_state.current_floor_select

    # 2. BLOCK FILTER BUTTONS
    st.markdown("#### 2. Filter by Block:")
    block_list = ["All Blocks", "Vayu Block", "Aakash Block", "Prudhvi Block", "Teja Block", "Varun Block", "Agni Block", "G Block"]
    b_cols = st.columns(len(block_list))
    
    if "current_block_select" not in st.session_state:
        st.session_state.current_block_select = "All Blocks"
        
    for idx, bname in enumerate(block_list):
        if b_cols[idx].button(bname, type="primary" if st.session_state.current_block_select == bname else "secondary", use_container_width=True):
            st.session_state.current_block_select = bname
            st.rerun()

    current_selected_block = st.session_state.current_block_select

    # 3. SEARCH & AUTOMATIC HIGHLIGHTING
    st.markdown("#### 3. Search & Focus Location:")
    col_s1, col_s2 = st.columns([3, 1])
    search_map_input = col_s1.text_input(
        "Search room number, room name, block or facility (e.g. D-32, A-22, Library, G-03, AKCNB, Varun Block)...",
        placeholder="e.g. D-32, Library, G-03, AKCNB..."
    )

    # Auto-switch floor if search term matches room on another floor
    if search_map_input:
        search_matches = search_official_floor_plans(search_map_input)
        if search_matches:
            top_match = search_matches[0]
            if top_match["floor"] != current_selected_floor:
                st.session_state.current_floor_select = top_match["floor"]
                col_s2.success(f"Auto-switched to **{top_match['floor']}** for match `{top_match['roomNumber']}`!")
                current_selected_floor = top_match["floor"]

    st.markdown("---")

    # Render Official VIIT Interactive Map
    viit_map_html = render_official_viit_interactive_map(
        current_selected_floor,
        current_selected_block,
        search_map_input
    )
    components.html(viit_map_html, height=625, scrolling=False)

    # Room List Grid for current floor
    st.markdown(f"#### 📋 Rooms & Facilities on **{current_selected_floor}** ({current_selected_block}):")
    floor_rooms_data = OFFICIAL_FLOOR_PLANS.get(current_selected_floor, {})
    
    room_grid_cols = st.columns(3)
    col_idx = 0
    for bname, rlist in floor_rooms_data.items():
        if current_selected_block != "All Blocks" and current_selected_block != bname:
            continue
        for r in rlist:
            icon = get_location_icon(r["roomName"])
            with room_grid_cols[col_idx % 3]:
                st.markdown(f"""
                    <div class="floor-item-card">
                        <span style="font-size: 1.4rem;">{icon}</span>
                        <div>
                            <div style="font-weight: 800; color: #0F172A;">{r['roomNumber']} — {r['roomName']}</div>
                            <div style="font-size: 0.8rem; color: #64748B;">🏢 {bname}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            col_idx += 1

# ==============================================================================
# TAB 5: STUDY HELPER
# ==============================================================================
with tab_study:
    st.subheader("📚 Study Material Summarizer & Quiz Generator")
    st.write("Upload course slides, syllabus PDFs, or paste lecture notes to extract summaries and revision quizzes.")

    uploaded_file = st.file_uploader("Upload Notes or Syllabus (.pdf or .txt)", type=["txt", "pdf"])
    pasted_text = st.text_area("Or paste lecture notes directly:", height=150, placeholder="Paste course material or exam topics here...")

    content_to_analyze = ""

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            content_to_analyze = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            try:
                pdf_reader = pypdf.PdfReader(uploaded_file)
                extracted_pages = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
                content_to_analyze = "\n".join(extracted_pages)
                st.success(f"Extracted content from {len(pdf_reader.pages)} PDF pages!")
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
    elif pasted_text.strip():
        content_to_analyze = pasted_text.strip()

    if st.button("✨ Generate Key Summary & Practice Quiz", type="primary", use_container_width=True):
        if not content_to_analyze:
            st.warning("Please upload a file or paste text first.")
        else:
            api_key = get_gemini_api_key()
            with st.spinner("Generating study guide & quiz..."):
                summary_output = summarize_study_material(content_to_analyze, api_key=api_key)
                st.markdown("---")
                st.markdown(summary_output)