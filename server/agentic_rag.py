from google import genai
from google.genai import types
import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, get_app, firestore, credentials
import json

app = FastAPI()

custom_instruction = """ You are a helpful assistant for a university student. Use the provided tools to assist with tasks related to their courses, schedule, and to-do list. Always respond in a friendly and supportive manner. If you don't know the answer, it's okay to say so. 
Be concise and clear in your responses.
If you are response includes a list of items, format it as a markdown list.
When providing a schedule, format it as follows:
- Class Name: Subject\n
    - Time: Start Time - End Time
    - Teacher: Teacher's Name
    - Room: Room Number
Each in of the above items should be a new line.
When providing an event, format it as follows:
- Event Name: Event Name
    - Time: Start Time - End Time
    - Venue: Venue
    - Details: Event Details
"""

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],  # SvelteKit dev and build ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIREBASE_SERVICE_ACCOUNT = os.environ.get("PRIVATE_FIREBASE_SERVICE_ACCOUNT_JSON")

print("GEMINI_API_KEY present:", bool(GEMINI_API_KEY))
print("FIREBASE_SERVICE_ACCOUNT present:", bool(FIREBASE_SERVICE_ACCOUNT))

if not GEMINI_API_KEY:
    print("Hint: run `echo $GEMINI_API_KEY` in the shell you'll use to run this script,")
    print("or add the variable to VS Code launch configuration / your system environment.")
    raise ValueError("GEMINI_API_KEY environment variable not set.")

if not FIREBASE_SERVICE_ACCOUNT:
    print("Hint: run `echo $PRIVATE_FIREBASE_SERVICE_ACCOUNT_JSON` in the shell you'll use to run this script,")
    print("or add the variable to VS Code launch configuration / your system environment.")
    raise ValueError("PRIVATE_FIREBASE_SERVICE_ACCOUNT_JSON environment variable not set.")

client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Firebase Admin
try:
    get_app()
except ValueError:
    # No app exists, initialize it
    try:
        service_account = json.loads(FIREBASE_SERVICE_ACCOUNT)
        print("Service account loaded successfully")
        print("Project ID:", service_account.get('project_id', 'Not found'))
        
        credential = credentials.Certificate(service_account)
        print("Credential created successfully")
        
        initialize_app(credential)
        print("Firebase app initialized successfully")
    except json.JSONDecodeError as e:
        print(f"Error parsing service account JSON: {e}")
        raise ValueError("Invalid JSON in PRIVATE_FIREBASE_SERVICE_ACCOUNT_JSON")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

db = firestore.client()

# Default user ID for demo purposes
DEFAULT_USER_ID = "demo_user"

# Load JSON data files
def load_json_data():
    """Load data from JSON files"""
    try:
        # Load timetable data
        with open('../src/lib/course/timetable.json', 'r') as f:
            timetable_data = json.load(f)
        
        # Load student course data
        with open('../src/lib/course/studentCourse.json', 'r') as f:
            student_course_data = json.load(f)
        
        # Load events data
        with open('../src/lib/course/events.json', 'r') as f:
            events_data = json.load(f)
        
        return timetable_data, student_course_data, events_data
    except FileNotFoundError as e:
        print(f"Error loading JSON files: {e}")
        return {}, {}, {}

# Load the data
timetable_data, student_course_data, events_data = load_json_data()

def get_student_courses():
    """Returns the student's enrolled courses from studentCourse.json"""
    student = student_course_data.get('student', {})
    courses = student.get('courses', [])
    return {"student": student, "courses": courses}

def get_todos():
    """Returns the student's current list of to-do items."""
    todos_ref = db.collection('users').document(DEFAULT_USER_ID).collection('todos')
    todos = todos_ref.stream()
    todo_list = []
    for todo in todos:
        todo_data = todo.to_dict()
        todo_list.append(todo_data.get('title', ''))
    return {"todos": todo_list}

def add_todo(task: str):
    """
    Adds a new task to the student's to-do list.
    Args:
        task: The task name to be added.
    """
    if not task:
        return {"status": "Error", "message": "Task cannot be empty."}
    
    todos_ref = db.collection('users').document(DEFAULT_USER_ID).collection('todos')
    todos_ref.add({
        'title': task,
        'completed': False,
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    return {"status": "Success", "message": f"Added '{task}' to your to-do list."}

def get_user_timetable():
    """
    Gets the user's specific timetable based on their enrolled courses from studentCourse.json.
    Returns a dictionary with days as keys and list of classes as values.
    """
    student = student_course_data.get('student', {})
    courses = student.get('courses', [])
    
    # Initialize timetable structure
    user_timetable = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": []
    }
    
    # Process each enrolled course
    for course in courses:
        subject = course.get('subject', '')
        teacher = course.get('teacher', '')
        schedule = course.get('schedule', [])
        
        # Add each scheduled class to the appropriate day
        for class_schedule in schedule:
            day = class_schedule.get('day', '')
            time = class_schedule.get('time', '')
            room = class_schedule.get('room', '')
            
            if day in user_timetable:
                # Parse time to get start and end times
                if " - " in time:
                    start_time = time.split(" - ")[0].strip()
                    end_time = time.split(" - ")[1].strip()
                else:
                    start_time = time
                    end_time = ""
                
                user_timetable[day].append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "class": subject,
                    "teacher": teacher,
                    "room": room
                })
    
    # Sort classes by start time for each day
    for day in user_timetable:
        user_timetable[day].sort(key=lambda x: x["start_time"])
    
    return user_timetable

def get_schedule_for_day(date: str = "today"):
    """
    Retrieves the student's class schedule for a specific day based on their enrolled courses.
    Args:
        date: The date to get the schedule for, in YYYY-MM-DD format. Defaults to 'today'.
    """
    # Get day of week from date
    if date == "today":
        # Use current date to get actual day of week
        today = datetime.datetime.now()
        day_of_week = today.strftime("%A")
    else:
        try:
            # Parse the provided date to get day of week
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_of_week = parsed_date.strftime("%A")
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD format."}
    
    # Get user's specific timetable
    user_timetable = get_user_timetable()
    day_schedule = user_timetable.get(day_of_week, [])
    
    if not day_schedule:
        return {"message": f"You have no classes scheduled for {day_of_week}."}
    
    return {"date": day_of_week, "schedule": day_schedule}

def get_next_class():
    """
    Finds the next class in the schedule based on the current time.
    """
    # Use current real time
    now = datetime.datetime.now()
    current_time = now.time()
    current_day = now.strftime("%A")
    
    # Get today's schedule
    user_timetable = get_user_timetable()
    day_schedule = user_timetable.get(current_day, [])
    
    if not day_schedule:
        return {"message": f"You have no classes scheduled for {current_day}."}
    
    # Find next class
    for class_item in day_schedule:
        start_time_str = class_item.get("start_time", "")
        if start_time_str:
            try:
                start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                if start_time > current_time:
                    return {"next_class": {
                        "start_time": start_time_str,
                        "end_time": class_item.get("end_time", ""),
                        "class": class_item.get("class", ""),
                        "teacher": class_item.get("teacher", ""),
                        "room": class_item.get("room", "")
                    }}
            except ValueError:
                # Skip invalid time formats
                continue
    
    return {"message": f"You have no more classes today ({current_day})."}

def check_for_conflicts():
    """Checks if any scheduled classes clash with other events on the same day."""
    # Get today's schedule using current day
    current_day = datetime.datetime.now().strftime("%A")
    user_timetable = get_user_timetable()
    day_schedule = user_timetable.get(current_day, [])
    
    # Get events for today (simplified - using first event as demo)
    events = events_data.get('events', [])
    today_events = []
    for event in events:
        # For demo, check if event is on Monday (simplified)
        today_events.append({
            "start_time": event.get("start_time", ""),
            "end_time": event.get("end_time", ""),
            "event": event.get("event_name", ""),
            "venue": event.get("venue", ""),
            "details": event.get("details", "")
        })
    
    conflicts = []
    for class_item in day_schedule:
        class_start_str = class_item.get("start_time", "")
        class_end_str = class_item.get("end_time", "")
        
        if class_start_str and class_end_str:
            try:
                class_start = datetime.datetime.strptime(class_start_str, "%H:%M")
                class_end = datetime.datetime.strptime(class_end_str, "%H:%M")
                
                for event_item in today_events:
                    event_start_str = event_item.get("start_time", "")
                    event_end_str = event_item.get("end_time", "")
                    
                    if event_start_str and event_end_str:
                        try:
                            event_start = datetime.datetime.strptime(event_start_str, "%H:%M")
                            event_end = datetime.datetime.strptime(event_end_str, "%H:%M")
                            
                            if max(class_start, event_start) < min(class_end, event_end):
                                conflicts.append({"conflicting_class": class_item, "conflicting_event": event_item})
                        except ValueError:
                            # Skip invalid time formats
                            continue
            except ValueError:
                # Skip invalid time formats
                continue
    
    if not conflicts:
        return {"message": "Great news! You have no scheduling conflicts today."}
    return {"conflicts": conflicts}

# def get_weekly_timetable():
#     """
#     Gets the user's complete weekly timetable based on their enrolled courses.
#     Returns a dictionary with all days of the week and their scheduled classes.
#     """
#     user_timetable = get_user_timetable()
    
#     # Filter out empty days for cleaner output
#     weekly_schedule = {}
#     for day, classes in user_timetable.items():
#         if classes:  # Only include days with classes
#             weekly_schedule[day] = classes
    
#     if not weekly_schedule:
#         return {"message": "You have no classes scheduled for this week."}
    
#     return {"weekly_timetable": weekly_schedule}

def get_current_classes():
    """
    Gets all classes currently happening right now across all batches.
    Returns a list of classes that are currently in session.
    """
    now = datetime.datetime.now()
    current_time = now.time()
    current_day = now.strftime("%A")
    
    current_classes = []
    
    # Check all batches in timetable.json
    for batch_name, batch_schedule in timetable_data.items():
        day_schedule = batch_schedule.get(current_day, [])
        
        for class_item in day_schedule:
            time_str = class_item.get("time", "")
            if " - " in time_str:
                try:
                    start_time_str = time_str.split(" - ")[0].strip()
                    end_time_str = time_str.split(" - ")[1].strip()
                    
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
                    
                    # Check if current time is between start and end time
                    if start_time <= current_time <= end_time:
                        current_classes.append({
                            "batch": batch_name,
                            "subject": class_item.get("subject", ""),
                            "teacher": class_item.get("teacher", ""),
                            "room": class_item.get("room", ""),
                            "start_time": start_time_str,
                            "end_time": end_time_str
                        })
                except ValueError:
                    # Skip invalid time formats
                    continue
    
    return {
        "current_time": current_time.strftime("%H:%M"),
        "current_day": current_day,
        "classes_in_session": current_classes,
        "total_classes": len(current_classes)
    }

def get_free_classrooms():
    """
    Finds classrooms that are currently free (not being used).
    Returns a list of available classrooms.
    """
    # Load classroom data
    try:
        with open('../src/lib/course/classes.json', 'r') as f:
            classes_data = json.load(f)
        all_classrooms = classes_data.get('classes', [])
    except FileNotFoundError:
        return {"error": "Classroom data not found"}
    
    # Get current classes to find occupied rooms
    current_classes_result = get_current_classes()
    occupied_rooms = set()
    
    for class_info in current_classes_result.get("classes_in_session", []):
        room = class_info.get("room", "").strip()
        if room:
            occupied_rooms.add(room)
    
    # Find free classrooms
    free_classrooms = []
    for classroom in all_classrooms:
        if classroom not in occupied_rooms:
            free_classrooms.append(classroom)
    
    return {
        "current_time": current_classes_result.get("current_time"),
        "current_day": current_classes_result.get("current_day"),
        "occupied_classrooms": list(occupied_rooms),
        "free_classrooms": free_classrooms,
        "total_free": len(free_classrooms)
    }

# def book_appointment(professor: str, time: str, date: str):
#     """
#     Books an appointment with a professor on a specific date and time.
#     Args:
#         professor: The name of the professor.
#         time: The time of the appointment (e.g., '16:00').
#         date: The date of the appointment in YYYY-MM-DD format.
#     """
#     appointments_ref = db.collection('users').document(DEFAULT_USER_ID).collection('appointments')
#     appointments_ref.add({
#         'professor': professor,
#         'time': time,
#         'date': date,
#         'createdAt': firestore.SERVER_TIMESTAMP
#     })
#     return {"status": "Success", "message": f"Appointment with {professor} on {date} at {time} has been booked."}

conversation_history = []

@app.get("/")
def chat_command(query: str):
    all_tools = [get_todos, add_todo, get_schedule_for_day, get_next_class, check_for_conflicts, get_user_timetable, get_current_classes, get_free_classrooms]

    conversation_history.append(types.Content(role='user', parts=[types.Part.from_text(text=query)]))

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=conversation_history,
        config=types.GenerateContentConfig(
            system_instruction=custom_instruction,
            tools=all_tools,
        )
    )

    conversation_history.append(response.candidates[0].content)

    return {"text": response.text}
