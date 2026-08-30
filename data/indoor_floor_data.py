# ==============================================================================
# ====== ADD YOUR 1st – 5th FLOOR CLASSROOM ARRANGEMENTS HERE ======
# I will provide exact classroom arrangements for floors 1–5 manually later.
# You can add or edit rooms, floors, and coordinates directly in this dictionary!
# ==============================================================================

INDOOR_FLOOR_DATA = {
    "Main Academic Block": {
        "1st Floor": [
            {"room": "IT-101", "type": "Classroom", "x": 140, "y": 150, "desc": "IT Department Lecture Room 101"},
            {"room": "Administration Office", "type": "Office", "x": 340, "y": 150, "desc": "Main Administrative Counter"},
            {"room": "Exam Cell", "type": "Exam Cell", "x": 540, "y": 150, "desc": "Examination Control Office"},
            {"room": "Principal Office", "type": "Office", "x": 740, "y": 150, "desc": "Principal Executive Office"},
            {"room": "Rector Office", "type": "Office", "x": 240, "y": 350, "desc": "Rector Suite"},
            {"room": "Scholarship Section", "type": "Office", "x": 440, "y": 350, "desc": "Student Financial Aid & Scholarship Desk"},
            {"room": "Washroom", "type": "Washroom", "x": 660, "y": 350, "desc": "First Floor Restroom Facilities"}
        ],
        "2nd Floor": [
            {"room": "Vignan Library", "type": "Library", "x": 200, "y": 160, "desc": "Central Academic Vignan Library"},
            {"room": "ECE Classroom 201", "type": "Classroom", "x": 460, "y": 160, "desc": "Electronics & Tech Lecture Hall"},
            {"room": "Laboratories", "type": "Lab", "x": 700, "y": 160, "desc": "Advanced Electronics & Optics Lab"},
            {"room": "Faculty Rooms", "type": "Office", "x": 320, "y": 350, "desc": "Professor Faculty Cubicles"},
            {"room": "Washroom", "type": "Washroom", "x": 620, "y": 350, "desc": "Second Floor Restroom"}
        ],
        "3rd Floor": [
            {"room": "CSE 302", "type": "Classroom", "x": 180, "y": 160, "desc": "Computer Science Smart Classroom 302"},
            {"room": "Computer Labs", "type": "Lab", "x": 480, "y": 160, "desc": "High Performance AI & Cloud Computing Lab"},
            {"room": "IT Classroom 305", "type": "Classroom", "x": 720, "y": 160, "desc": "IT Department Seminar Room 305"}
        ],
        "4th Floor": [
            {"room": "AKCNB", "type": "Auditorium", "x": 220, "y": 160, "desc": "AKCNB Auditorium & Seminar Hall"},
            {"room": "IT Staffroom", "type": "Office", "x": 500, "y": 160, "desc": "IT Department Faculty Desk"},
            {"room": "Classrooms", "type": "Classroom", "x": 740, "y": 160, "desc": "Senior Lecture Hall"},
            {"room": "Washrooms", "type": "Washroom", "x": 460, "y": 350, "desc": "4th Floor Restroom Facilities"}
        ],
        "5th Floor": [
            {"room": "Classrooms", "type": "Classroom", "x": 260, "y": 200, "desc": "Postgraduate Lecture Hall"},
            {"room": "Solar Panels", "type": "Facility", "x": 620, "y": 200, "desc": "Rooftop Green Solar Energy Installation"}
        ]
    }
}

def get_indoor_room_details(room_name):
    """
    Looks up room details across all buildings and floors in INDOOR_FLOOR_DATA.
    """
    if not room_name:
        return None
        
    r_target = room_name.strip().lower()
    
    for building_name, floors in INDOOR_FLOOR_DATA.items():
        for floor_name, rooms in floors.items():
            for r in rooms:
                if r["room"].lower() == r_target or r_target in r["room"].lower() or r["room"].lower() in r_target:
                    return {
                        "building": building_name,
                        "floor": floor_name,
                        "room": r["room"],
                        "type": r["type"],
                        "x": r["x"],
                        "y": r["y"],
                        "desc": r["desc"]
                    }
    return None
