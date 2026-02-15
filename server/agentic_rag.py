import datetime
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pymongo import MongoClient

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "hackgenix")
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"
)
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not set. "
        "Add it to server/.env or your system environment."
    )

# ---------------------------------------------------------------------------
# Data file paths (resolved relative to this script, not cwd)
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent / "src" / "lib" / "course"
TIMETABLE_PATH = _BASE_DIR / "timetable.json"
STUDENT_COURSE_PATH = _BASE_DIR / "studentCourse.json"
EVENTS_PATH = _BASE_DIR / "events.json"
CLASSES_PATH = _BASE_DIR / "classes.json"

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="HackGenix Agentic RAG", version="1.0.0")

origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB_NAME]
todos_collection = db["todos"]

logger.info("Connected to MongoDB: %s / %s", MONGODB_URI, MONGODB_DB_NAME)

CUSTOM_INSTRUCTION = """You are a helpful assistant for a university student. \
Use the provided tools to assist with tasks related to their courses, schedule, \
and to-do list. Always respond in a friendly and supportive manner. If you don't \
know the answer, it's okay to say so.
Be concise and clear in your responses.
If your response includes a list of items, format it as a markdown list.
When providing a schedule, format it as follows:
- Class Name: Subject
    - Time: Start Time - End Time
    - Teacher: Teacher's Name
    - Room: Room Number
Each of the above items should be on a new line.
When providing an event, format it as follows:
- Event Name: Event Name
    - Time: Start Time - End Time
    - Venue: Venue
    - Details: Event Details
"""


# ===================================================================
# Data loading
# ===================================================================
def _load_json(path: Path) -> dict | list:
    """Load and parse a JSON file, returning an empty dict on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Data file not found: %s", path)
        return {}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in: %s", path)
        return {}


timetable_data = _load_json(TIMETABLE_PATH)
student_course_data = _load_json(STUDENT_COURSE_PATH)
events_data = _load_json(EVENTS_PATH)


# ===================================================================
# Tool functions  (used by Gemini function-calling)
# ===================================================================
def get_student_courses() -> dict:
    """Returns the student's enrolled courses from studentCourse.json."""
    student = student_course_data.get("student", {})
    courses = student.get("courses", [])
    return {"student": student, "courses": courses}


def get_todos(user_id: str) -> dict:
    """Returns the student's current list of to-do items.

    Args:
        user_id: The authenticated user's ID.
    """
    docs = todos_collection.find({"userId": user_id}).sort("createdAt", -1)
    todo_list = [doc.get("title", "") for doc in docs]
    return {"todos": todo_list}


def add_todo(user_id: str, task: str) -> dict:
    """Adds a new task to the student's to-do list.

    Args:
        user_id: The authenticated user's ID.
        task: The task name to be added.
    """
    if not task:
        return {"status": "Error", "message": "Task cannot be empty."}

    todos_collection.insert_one(
        {
            "userId": user_id,
            "title": task,
            "completed": False,
            "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )
    return {"status": "Success", "message": f"Added '{task}' to your to-do list."}


def get_user_timetable() -> dict:
    """Gets the user's specific timetable based on their enrolled courses.

    Returns a dictionary with days as keys and list of classes as values.
    """
    student = student_course_data.get("student", {})
    courses = student.get("courses", [])

    user_timetable: dict[str, list] = {
        day: []
        for day in (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
    }

    for course in courses:
        subject = course.get("subject", "")
        teacher = course.get("teacher", "")
        for slot in course.get("schedule", []):
            day = slot.get("day", "")
            time_str = slot.get("time", "")
            room = slot.get("room", "")
            if day not in user_timetable:
                continue

            start_time, end_time = "", ""
            if " - " in time_str:
                parts = time_str.split(" - ")
                start_time = parts[0].strip()
                end_time = parts[1].strip()
            else:
                start_time = time_str

            user_timetable[day].append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "class": subject,
                    "teacher": teacher,
                    "room": room,
                }
            )

    for day in user_timetable:
        user_timetable[day].sort(key=lambda x: x["start_time"])

    return user_timetable


def get_schedule_for_day(date: str = "today") -> dict:
    """Retrieves the student's class schedule for a specific day.

    Args:
        date: The date in YYYY-MM-DD format, or 'today'.
    """
    if date == "today":
        day_of_week = datetime.datetime.now().strftime("%A")
    else:
        try:
            parsed = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_of_week = parsed.strftime("%A")
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD."}

    day_schedule = get_user_timetable().get(day_of_week, [])
    if not day_schedule:
        return {"message": f"You have no classes scheduled for {day_of_week}."}
    return {"date": day_of_week, "schedule": day_schedule}


def get_next_class() -> dict:
    """Finds the next upcoming class based on the current time."""
    now = datetime.datetime.now()
    current_time = now.time()
    current_day = now.strftime("%A")

    day_schedule = get_user_timetable().get(current_day, [])
    if not day_schedule:
        return {"message": f"You have no classes scheduled for {current_day}."}

    for item in day_schedule:
        start_str = item.get("start_time", "")
        if not start_str:
            continue
        try:
            start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
            if start_time > current_time:
                return {"next_class": item}
        except ValueError:
            continue

    return {"message": f"You have no more classes today ({current_day})."}


def check_for_conflicts() -> dict:
    """Checks if any classes clash with events today."""
    current_day = datetime.datetime.now().strftime("%A")
    day_schedule = get_user_timetable().get(current_day, [])
    events = events_data.get("events", [])

    conflicts = []
    for class_item in day_schedule:
        cs, ce = class_item.get("start_time", ""), class_item.get("end_time", "")
        if not (cs and ce):
            continue
        try:
            c_start = datetime.datetime.strptime(cs, "%H:%M")
            c_end = datetime.datetime.strptime(ce, "%H:%M")
        except ValueError:
            continue

        for event in events:
            es, ee = event.get("start_time", ""), event.get("end_time", "")
            if not (es and ee):
                continue
            try:
                e_start = datetime.datetime.strptime(es, "%H:%M")
                e_end = datetime.datetime.strptime(ee, "%H:%M")
            except ValueError:
                continue

            if max(c_start, e_start) < min(c_end, e_end):
                conflicts.append(
                    {"conflicting_class": class_item, "conflicting_event": event}
                )

    if not conflicts:
        return {"message": "Great news! You have no scheduling conflicts today."}
    return {"conflicts": conflicts}


def get_current_classes() -> dict:
    """Gets all classes currently in session across all batches."""
    now = datetime.datetime.now()
    current_time = now.time()
    current_day = now.strftime("%A")

    current_classes = []
    for batch_name, batch_schedule in timetable_data.items():
        if not isinstance(batch_schedule, dict):
            continue
        for item in batch_schedule.get(current_day, []):
            time_str = item.get("time", "")
            if " - " not in time_str:
                continue
            try:
                parts = time_str.split(" - ")
                start = datetime.datetime.strptime(parts[0].strip(), "%H:%M").time()
                end = datetime.datetime.strptime(parts[1].strip(), "%H:%M").time()
                if start <= current_time <= end:
                    current_classes.append(
                        {
                            "batch": batch_name,
                            "subject": item.get("subject", ""),
                            "teacher": item.get("teacher", ""),
                            "room": item.get("room", ""),
                            "start_time": parts[0].strip(),
                            "end_time": parts[1].strip(),
                        }
                    )
            except ValueError:
                continue

    return {
        "current_time": current_time.strftime("%H:%M"),
        "current_day": current_day,
        "classes_in_session": current_classes,
        "total_classes": len(current_classes),
    }


def get_free_classrooms() -> dict:
    """Finds classrooms that are currently free (not being used)."""
    classes_data = _load_json(CLASSES_PATH)
    if not classes_data:
        return {"error": "Classroom data not found"}

    all_classrooms: list = classes_data.get("classes", [])
    current = get_current_classes()
    occupied = {
        info.get("room", "").strip()
        for info in current.get("classes_in_session", [])
        if info.get("room", "").strip()
    }

    free = [c for c in all_classrooms if c not in occupied]
    return {
        "current_time": current.get("current_time"),
        "current_day": current.get("current_day"),
        "occupied_classrooms": list(occupied),
        "free_classrooms": free,
        "total_free": len(free),
    }


# ===================================================================
# Tool call execution helper
# ===================================================================
# Map from function name → callable
_TOOL_MAP = {
    "get_student_courses": get_student_courses,
    "get_todos": get_todos,
    "add_todo": add_todo,
    "get_user_timetable": get_user_timetable,
    "get_schedule_for_day": get_schedule_for_day,
    "get_next_class": get_next_class,
    "check_for_conflicts": check_for_conflicts,
    "get_current_classes": get_current_classes,
    "get_free_classrooms": get_free_classrooms,
}


def _execute_tool_call(
    function_call: types.FunctionCall, user_id: str
) -> types.FunctionResponse:
    """Execute a single tool call from Gemini, injecting user_id where needed."""
    fn_name = function_call.name
    fn_args = dict(function_call.args) if function_call.args else {}

    fn = _TOOL_MAP.get(fn_name)
    if fn is None:
        return types.FunctionResponse(
            name=fn_name,
            response={"error": f"Unknown function: {fn_name}"},
        )

    # Inject user_id for functions that require it
    import inspect
    sig = inspect.signature(fn)
    if "user_id" in sig.parameters:
        fn_args["user_id"] = user_id

    try:
        result = fn(**fn_args)
    except Exception as exc:
        logger.exception("Error executing tool %s", fn_name)
        result = {"error": str(exc)}

    return types.FunctionResponse(name=fn_name, response=result)


# ===================================================================
# Routes
# ===================================================================
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/")
def chat(
    query: str = Query(..., min_length=1, max_length=2000, description="User query"),
    user_id: str = Query("anonymous", description="Authenticated user ID"),
):
    """Main chat endpoint that processes queries via Gemini with tool calling."""
    all_tools = [
        get_todos,
        add_todo,
        get_schedule_for_day,
        get_next_class,
        check_for_conflicts,
        get_user_timetable,
        get_current_classes,
        get_free_classrooms,
    ]

    # Build per-request conversation (stateless)
    conversation: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=query)])
    ]

    try:
        # Allow up to 10 rounds of tool calling before giving up
        for _round in range(10):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=conversation,
                config=types.GenerateContentConfig(
                    system_instruction=CUSTOM_INSTRUCTION,
                    tools=all_tools,
                ),
            )

            candidate = response.candidates[0]
            conversation.append(candidate.content)

            # Check if the model wants to call tools
            function_calls = [
                part.function_call
                for part in candidate.content.parts
                if part.function_call is not None
            ]

            if not function_calls:
                # Model returned a text response — we're done
                break

            # Execute all requested tool calls
            tool_responses = [
                _execute_tool_call(fc, user_id) for fc in function_calls
            ]
            conversation.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(r) for r in tool_responses],
                )
            )
        else:
            logger.warning("Tool-call loop exceeded 10 rounds for query: %s", query[:100])

        return {"text": response.text}

    except Exception:
        logger.exception("Error processing chat query")
        raise HTTPException(status_code=500, detail="Failed to process your request.")


# ===================================================================
# Entry point
# ===================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agentic_rag:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
    )
