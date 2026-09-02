import os
import re
import streamlit as st
from data.floor_locations import FLOOR_LOCATIONS, get_location_icon
from utils.campus_db_helper import (
    get_campus_context_for_prompt,
    search_locations,
    get_floor_content,
    parse_room_code
)
from utils.navigation_helper import find_route

# Try importing Google GenAI SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def get_gemini_api_key():
    """Retrieves GEMINI_API_KEY safely from Streamlit Secrets or environment variables."""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
            if key:
                return key
    except Exception as e:
        print(f"Streamlit secrets lookup note: {e}")

    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key and str(env_key).strip():
        return str(env_key).strip()

    return None


def get_genai_client(api_key=None):
    """Initializes and returns a Google GenAI Client if API key is present in Streamlit Secrets."""
    if not GENAI_AVAILABLE:
        return None

    key = api_key or get_gemini_api_key()
    if not key:
        return None

    try:
        client = genai.Client(api_key=key)
        return client
    except Exception as e:
        print(f"Error initializing GenAI Client: {e}")
        return None

def generate_campus_response(user_query, api_key=None, history=None):
    """
    Main AI response generator.
    Enforces FLOOR_LOCATIONS as the SINGLE SOURCE OF TRUTH.
    """
    client = get_genai_client(api_key)
    campus_context = get_campus_context_for_prompt()
    q_trim = user_query.strip()
    q_lower = q_trim.lower()

    # Check navigation query patterns ("from X to Y")
    if "from " in q_lower and (" to " in q_lower or " reach " in q_lower):
        try:
            parts = q_lower.split("from ")
            after_from = parts[1]
            if " to " in after_from:
                start_str, end_str = after_from.split(" to ")
                route_res = find_route(start_str, end_str)
                if route_res.get("success") and not route_res.get("same_location"):
                    s = route_res["start"]["name"]
                    e = route_res["end"]["name"]
                    res = f"🧭 **Route Directions: {s} ➔ {e}**\n\n"
                    res += f"📏 **Distance:** ~{route_res['distance_meters']}m | ⏱️ **Walk Time:** ~{route_res['estimated_minutes']} mins\n\n"
                    for step in route_res["steps"]:
                        res += f"{step['icon']} **Step {step['step_num']}: {step['title']}**\n{step['detail']}\n\n"
                    return res
        except Exception as err:
            print(f"Error parsing navigation query: {err}")

    # Dynamic System Instruction using ONLY FLOOR_LOCATIONS
    system_instruction = (
        "You are the AI Campus Copilot assistant.\n"
        "STRICT GROUNDING RULES YOU MUST FOLLOW WITHOUT EXCEPTION:\n"
        "1. You MUST read location information ONLY from the provided FLOOR_LOCATIONS directory.\n"
        "2. Do NOT invent, assume, or reference any external or old campus locations.\n"
        "3. When a user asks 'Where is [Location]?' (e.g., AKCNB, Exam Cell, Vignan Library), reply strictly with:\n"
        "   '📍 [Location Name] is located on the [Floor Name].'\n"
        "4. When a user asks 'What is on [Floor]?' (e.g., 4th Floor, 1st Floor), list ALL locations under that floor.\n"
        "5. If a requested location does not exist in FLOOR_LOCATIONS, respond strictly with:\n"
        "   'Location not found on the campus map.'\n\n"
        f"{campus_context}"
    )

    if client:
        try:
            prompt = f"User Query: {user_query}"
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error (falling back to local engine): {e}")

    # --- LOCAL ENGINE (Guaranteed 100% Deterministic Fallback) ---
    
    # 1. Check if user is asking "What is on [Floor]?" or query mentions a floor
    if "what is on" in q_lower or "what's on" in q_lower or "floor" in q_lower or "which floor" in q_lower:
        floor_name, floor_items = get_floor_content(q_lower)
        if floor_name and floor_items:
            res = f"📍 **{floor_name}**\n\n"
            for item in floor_items:
                icon = get_location_icon(item)
                res += f"• {icon} **{item}**\n"
            return res

    # 2. Check regex room code (e.g. M-201, A-123)
    parsed_room = parse_room_code(q_trim)
    if parsed_room:
        return (
            f"📍 **{parsed_room['room_code']} Location Details**\n\n"
            f"• **Floor:** {parsed_room['floor']}\n"
            f"• **Wing/Side:** {parsed_room['side']}\n"
            f"• **Details:** {parsed_room['description']}"
        )

    # 3. Clean search term for location query (e.g., "Where is AKCNB?", "AKCNB", "akcnb", "AKC", "exam")
    clean_term = q_lower
    prefixes = ["where is the ", "where is ", "location of ", "find ", "search ", "where ", "the "]
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if clean_term.startswith(prefix):
                clean_term = clean_term[len(prefix):].strip()
                changed = True
                break
    clean_term = clean_term.strip(" ?!.")

    # Handle "show me the route" or "yes, show route" voice queries
    if ("route" in q_lower or "way" in q_lower or "navigate" in q_lower) and ("show" in q_lower or "yes" in q_lower or "how" in q_lower):
        return (
            "🗺️ **Opening Campus Map & Navigation Route!**\n\n"
            "I have updated the target destination in the **Campus Route Finder**. "
            "Switch to the **🧭 Campus Route Finder** tab above to view the interactive animated route and walking directions!"
        )

    matches = search_locations(clean_term)
    if matches:
        if len(matches) == 1:
            m = matches[0]
            return f"📍 **{m['name']}** is located on the **{m['floor']}**.\n\n🗺️ *Would you like me to show you the route on the campus map? Click the **🧭 Campus Route Finder** tab above or say 'Yes, show me the route'!*"
        else:
            res = "📍 **Matching Campus Locations:**\n\n"
            for m in matches:
                res += f"• {m['icon']} **{m['name']}** — {m['floor']}\n"
            res += "\n🗺️ *Say 'Where is [Location]' or 'Show me the route' for directions!*"
            return res

    # 4. Check floor content fallback if clean_term was a floor string
    floor_name, floor_items = get_floor_content(clean_term)
    if floor_name and floor_items:
        res = f"📍 **{floor_name}**\n\n"
        for item in floor_items:
            icon = get_location_icon(item)
            res += f"• {icon} **{item}**\n"
        return res

    return "Location not found on the campus map."

def summarize_study_material(text_content, api_key=None):
    """Summarizes uploaded study notes or syllabus text."""
    client = get_genai_client(api_key)

    if not client:
        lines = [line.strip() for line in text_content.split("\n") if line.strip()]
        preview = " ".join(lines[:5])
        return (
            "📝 **Study Material Summary (Local Offline Preview)**\n\n"
            f"• **Word Count:** {len(text_content.split())} words\n"
            f"• **Lines:** {len(lines)} lines\n\n"
            f"**Preview:** {preview}...\n\n"
            "💡 *Configure `GEMINI_API_KEY` in Streamlit Secrets (`.streamlit/secrets.toml`) for automated key takeaway extraction & quiz generation!*"
        )

    prompt = (
        "Analyze the following study material and provide:\n"
        "1. A concise executive summary (3-4 bullet points).\n"
        "2. Top 5 Key Concepts to Remember.\n"
        "3. 3 Practice Quiz Questions with answers.\n\n"
        f"Study Content:\n{text_content[:8000]}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error generating summary: {e}"
