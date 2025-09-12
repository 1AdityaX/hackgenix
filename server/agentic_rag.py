from google import genai
from google.genai import types
import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI()

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
print("GEMINI_API_KEY present:", bool(GEMINI_API_KEY))

if not GEMINI_API_KEY:
    print("Hint: run `echo $GEMINI_API_KEY` in the shell you'll use to run this script,")
    print("or add the variable to VS Code launch configuration / your system environment.")
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=GEMINI_API_KEY)

student_data = {
    "todos": ["Finish Math homework", "Prepare for Physics presentation"],
    "schedule": {
        "2025-09-15": [
            {"start_time": "09:00", "end_time": "10:30", "class": "Calculus II"},
            {"start_time": "11:00", "end_time": "12:30", "class": "Data Structures"},
            {"start_time": "14:00", "end_time": "15:00", "class": "Physics Lab"}
        ]
    },
    "events": {
         "2025-09-15": [
            {"start_time": "15:00", "end_time": "17:00", "event": "Dance practice"}
         ]
    },
    "appointments": []
}

def get_todos():
    """Returns the student's current list of to-do items."""
    return {"todos": student_data["todos"]}

def add_todo(task: str):
    """
    Adds a new task to the student's to-do list.
    Args:
        task: The description of the task to be added.
    """
    if not task:
        return {"status": "Error", "message": "Task cannot be empty."}
    student_data["todos"].append(task)
    return {"status": "Success", "message": f"Added '{task}' to your to-do list."}

def get_schedule_for_day(date: str = "today"):
    """
    Retrieves the student's class schedule for a specific day.
    Args:
        date: The date to get the schedule for, in YYYY-MM-DD format. Defaults to 'today'.
    """
    if date == "today":
        target_date = "2025-09-15"
    else:
        target_date = date

    schedule = student_data["schedule"].get(target_date, [])
    if not schedule:
        return {"message": f"You have no classes scheduled for {target_date}."}
    return {"date": target_date, "schedule": schedule}

def get_next_class():
    """
    Finds the next class in the schedule based on the current time.
    """
    now = datetime.datetime.strptime("2025-09-15 10:45", "%Y-%m-%d %H:%M").time()
    target_date = "2025-09-15"
    schedule = student_data["schedule"].get(target_date, [])
    for item in schedule:
        start_time = datetime.datetime.strptime(item["start_time"], "%H:%M").time()
        if start_time > now:
            return {"next_class": item}
    return {"message": "You have no more classes today."}

def check_for_conflicts():
    """Checks if any scheduled classes clash with other events on the same day."""
    target_date = "2025-09-15" 
    schedule = student_data["schedule"].get(target_date, [])
    events = student_data["events"].get(target_date, [])
    conflicts = []
    for class_item in schedule:
        class_start = datetime.datetime.strptime(class_item["start_time"], "%H:%M")
        class_end = datetime.datetime.strptime(class_item["end_time"], "%H:%M")
        for event_item in events:
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
    appointment = {"professor": professor, "time": time, "date": date}
    student_data["appointments"].append(appointment)
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
