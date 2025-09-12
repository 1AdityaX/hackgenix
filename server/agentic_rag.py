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
        task: The description of the task to be added.
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

def get_schedule_for_day(date: str = "today"):
    """
    Retrieves the student's class schedule for a specific day.
    Args:
        date: The date to get the schedule for, in YYYY-MM-DD format. Defaults to 'today'.
    """
    # Get the student's batch from studentCourse.json
    student_batch = student_course_data.get('student', {}).get('batch', 'Batch C')
    
    # Get day of week from date (simplified - using Monday as default for demo)
    if date == "today":
        day_of_week = "Monday"  # Default to Monday for demo
    else:
        # In a real implementation, you'd parse the date to get the day of week
        day_of_week = "Monday"  # Simplified for demo
    
    # Get schedule from timetable.json
    batch_schedule = timetable_data.get(student_batch, {})
    day_schedule = batch_schedule.get(day_of_week, [])
    
    if not day_schedule:
        return {"message": f"You have no classes scheduled for {day_of_week}."}
    
    # Convert to the expected format
    schedule = []
    for class_item in day_schedule:
        schedule.append({
            "start_time": class_item.get("time", "").split(" - ")[0],
            "end_time": class_item.get("time", "").split(" - ")[1] if " - " in class_item.get("time", "") else "",
            "class": class_item.get("subject", ""),
            "teacher": class_item.get("teacher", ""),
            "room": class_item.get("room", "")
        })
    
    return {"date": day_of_week, "schedule": schedule}

def get_next_class():
    """
    Finds the next class in the schedule based on the current time.
    """
    now = datetime.datetime.strptime("2025-09-15 10:45", "%Y-%m-%d %H:%M").time()
    
    # Get the student's batch from studentCourse.json
    student_batch = student_course_data.get('student', {}).get('batch', 'Batch C')
    
    # Get today's schedule (using Monday as default for demo)
    day_of_week = "Monday"
    batch_schedule = timetable_data.get(student_batch, {})
    day_schedule = batch_schedule.get(day_of_week, [])
    
    if not day_schedule:
        return {"message": "You have no more classes today."}
    
    # Convert to the expected format and find next class
    for class_item in day_schedule:
        time_str = class_item.get("time", "")
        if " - " in time_str:
            start_time_str = time_str.split(" - ")[0]
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            if start_time > now:
                return {"next_class": {
                    "start_time": start_time_str,
                    "end_time": time_str.split(" - ")[1],
                    "class": class_item.get("subject", ""),
                    "teacher": class_item.get("teacher", ""),
                    "room": class_item.get("room", "")
                }}
    
    return {"message": "You have no more classes today."}

def check_for_conflicts():
    """Checks if any scheduled classes clash with other events on the same day."""
    # Get the student's batch from studentCourse.json
    student_batch = student_course_data.get('student', {}).get('batch', 'Batch C')
    
    # Get today's schedule (using Monday as default for demo)
    day_of_week = "Monday"
    batch_schedule = timetable_data.get(student_batch, {})
    day_schedule = batch_schedule.get(day_of_week, [])
    
    # Convert schedule to expected format
    schedule = []
    for class_item in day_schedule:
        time_str = class_item.get("time", "")
        if " - " in time_str:
            schedule.append({
                "start_time": time_str.split(" - ")[0],
                "end_time": time_str.split(" - ")[1],
                "class": class_item.get("subject", ""),
                "teacher": class_item.get("teacher", ""),
                "room": class_item.get("room", "")
            })
    
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
    for class_item in schedule:
        class_start = datetime.datetime.strptime(class_item["start_time"], "%H:%M")
        class_end = datetime.datetime.strptime(class_item["end_time"], "%H:%M")
        for event_item in today_events:
            event_start = datetime.datetime.strptime(event_item["start_time"], "%H:%M")
            event_end = datetime.datetime.strptime(event_item["end_time"], "%H:%M")
            if max(class_start, event_start) < min(class_end, event_end):
                conflicts.append({"conflicting_class": class_item, "conflicting_event": event_item})
    
    if not conflicts:
        return {"message": "Great news! You have no scheduling conflicts today."}
    return {"conflicts": conflicts}

def book_appointment(professor: str, time: str, date: str):
    """
    Books an appointment with a professor on a specific date and time.
    Args:
        professor: The name of the professor.
        time: The time of the appointment (e.g., '16:00').
        date: The date of the appointment in YYYY-MM-DD format.
    """
    appointments_ref = db.collection('users').document(DEFAULT_USER_ID).collection('appointments')
    appointments_ref.add({
        'professor': professor,
        'time': time,
        'date': date,
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    return {"status": "Success", "message": f"Appointment with {professor} on {date} at {time} has been booked."}

@app.get("/")
def chat_command(query: str):
    all_tools = [get_todos, add_todo, get_schedule_for_day, get_next_class, check_for_conflicts, book_appointment]

    conversation_history = []
    conversation_history.append(types.Content(role='user', parts=[types.Part.from_text(text=query)]))

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=conversation_history,
        config=types.GenerateContentConfig(
            tools=all_tools,
        )
    )

    conversation_history.append(response.candidates[0].content)

    return {"text": response.text}
