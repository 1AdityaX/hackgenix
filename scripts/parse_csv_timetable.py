"""Build src/lib/course/timetable.json from the CSV timetables in scripts/data/.

Usage: python3 scripts/parse_csv_timetable.py

Each CSV names its batch in the filename ("Batch A", "Batch B" or "Batch C").
Inside, a day name in column 0 starts a day; a time slot in column 1 lists the
parallel classes in columns 2+, and the row directly below holds their rooms.
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "scripts" / "data"
OUTPUT = ROOT / "src" / "lib" / "course" / "timetable.json"

DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
BATCHES = ("Batch A", "Batch B", "Batch C")
TIME_SLOT = re.compile(r"^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}")


def parse_subject(cell):
    """'Computer Vision (Ram Prasad K) - Sec1' -> ('Computer Vision - Sec1', 'Ram Prasad K')"""
    subject = cell.strip()
    teacher = None
    match = re.search(r"\((.*?)\)", subject)
    if match:
        name = match.group(1)
        if any(c.isalpha() for c in name) and len(name.split()) < 4:
            teacher = name
            subject = subject.replace(f"({teacher})", "").strip()
    return re.sub(r"\s{2,}", " ", subject), teacher


def parse_csv(path):
    """Return {day: [{time, subject, teacher, room}, ...]} for one CSV."""
    rows = list(csv.reader(path.open(encoding="utf-8")))
    periods = {}
    day = None
    i = 0
    while i < len(rows):
        row = rows[i]
        if not any(row):
            i += 1
            continue

        candidate = row[0].replace(" ", "").strip().capitalize()
        if candidate in DAYS:
            day = candidate

        slot = row[1].strip()
        if "LUNCH" in slot.upper():
            periods.setdefault(day, []).append(
                {"time": slot, "subject": "Lunch Break", "teacher": None, "room": None}
            )
            i += 1
        elif day and TIME_SLOT.match(slot):
            rooms = rows[i + 1] if i + 1 < len(rows) else []
            seen = {(p["subject"], p["teacher"]) for p in periods.get(day, []) if p["time"] == slot}
            for col in range(2, len(row)):
                if not row[col].strip():
                    continue
                subject, teacher = parse_subject(row[col])
                if (subject, teacher) in seen:
                    continue
                seen.add((subject, teacher))
                room = rooms[col].strip() if col < len(rooms) else ""
                periods.setdefault(day, []).append(
                    {"time": slot, "subject": subject, "teacher": teacher, "room": room or "N/A"}
                )
            i += 2
        else:
            i += 1
    return periods


def main():
    timetable = {}
    for path in sorted(DATA_DIR.glob("*.csv")):
        batch = next((b for b in BATCHES if b in path.name), "Unknown Batch")
        for day, periods in parse_csv(path).items():
            timetable.setdefault(batch, {}).setdefault(day, []).extend(periods)

    for days in timetable.values():
        for day, periods in days.items():
            periods.sort(key=lambda p: p["time"])
            unique = {}
            for p in periods:
                unique.setdefault((p["time"], p["subject"], p["teacher"], p["room"]), p)
            days[day] = list(unique.values())

    OUTPUT.write_text(json.dumps(timetable, indent="\t") + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
