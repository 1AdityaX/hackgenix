import csv
import json
import re
import os
from collections import defaultdict

def parse_subject(cell_content):
    """
    Parses a cell to extract subject, teacher, and section.
    Example: "Writing and Communications (Meenakshi) - Sec1"
    Returns: (subject_with_section, teacher)
    """
    teacher = None
    subject = cell_content.strip()

    # Regex to find a name in parentheses
    match = re.search(r'\((.*?)\)', subject)
    if match:
        # Extract potential teacher name
        potential_name = match.group(1)
        # Simple check to see if it's likely a name (not just numbers or short codes)
        if any(c.isalpha() for c in potential_name) and len(potential_name.split()) < 4:
            teacher = potential_name
            # Remove the teacher part from the subject string
            subject = subject.replace(f'({teacher})', '').strip()

    # Clean up any extra spaces that might result
    subject = re.sub(r'\s{2,}', ' ', subject)
    return subject, teacher

def parse_csv_to_json(file_path):
    """
    Parses a single CSV file and returns a dictionary structure of the timetable.
    """
    timetable = defaultdict(lambda: defaultdict(list))
    
    # Extract batch name from filename, e.g., "Batch A"
    batch_name = "Unknown Batch"
    if "Batch A" in file_path:
        batch_name = "Batch A"
    elif "Batch B" in file_path:
        batch_name = "Batch B"
    elif "Batch C" in file_path:
        batch_name = "Batch C"

    with open(file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
        
        current_day = None
        i = 0
        while i < len(rows):
            row = rows[i]
            # Skip empty rows
            if not any(row):
                i += 1
                continue

            # Check for a new day in the first column
            day_candidate = row[0].replace(" ", "").strip().capitalize()
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day_candidate in days:
                current_day = day_candidate
            
            # Check for a time slot in the second column
            time_slot = row[1].strip()
            # Basic time validation
            if current_day and re.match(r'^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', time_slot) or "LUNCH" in time_slot.upper():
                
                if "LUNCH" in time_slot.upper():
                    timetable[current_day][time_slot].append({
                        "subject": "Lunch Break",
                        "teacher": None,
                        "room": None
                    })
                    i += 1
                    continue

                # The next row should contain room numbers
                room_row = rows[i + 1] if (i + 1) < len(rows) else [''] * len(row)

                # Iterate through the columns for class details
                for col_idx in range(2, len(row)):
                    subject_cell = row[col_idx].strip()
                    if subject_cell:
                        subject, teacher = parse_subject(subject_cell)
                        room = room_row[col_idx].strip() if col_idx < len(room_row) else None
                        
                        period = {
                            "subject": subject,
                            "teacher": teacher,
                            "room": room if room else "N/A"
                        }
                        
                        # Use time_slot as key to group parallel classes
                        # Check if this period (by subject and teacher) is already added for this slot
                        is_duplicate = False
                        for p in timetable[current_day][time_slot]:
                            if p['subject'] == period['subject'] and p['teacher'] == period['teacher']:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                             timetable[current_day][time_slot].append(period)

                i += 2 # Move past the subject row and the room row
            else:
                i += 1
    
    # Convert the defaultdict structure to a regular dict for JSON output
    # And group periods by time slot
    final_timetable = {}
    for day, slots in timetable.items():
        day_schedule = []
        for time, periods in slots.items():
            # For now, just taking the first period found for a time slot.
            # In a more complex scenario, you might want to show all parallel classes.
            # Here we will just list all of them.
            for period in periods:
                 day_schedule.append({
                     "time": time,
                     "subject": period["subject"],
                     "teacher": period["teacher"],
                     "room": period["room"]
                 })
        final_timetable[day] = day_schedule

    return {batch_name: final_timetable}


def merge_timetables(data_list):
    """Merges multiple timetable dictionaries."""
    merged = defaultdict(lambda: defaultdict(list))
    for data in data_list:
        for batch, schedule in data.items():
            for day, periods in schedule.items():
                # Simple merge: append periods. A more robust merge might check for duplicates.
                merged[batch][day].extend(periods)
    
    # Sort periods by time for each day
    for batch in merged:
        for day in merged[batch]:
            # Simple sort on time string, works for HH:MM format
            merged[batch][day] = sorted(merged[batch][day], key=lambda x: x['time'])
            
            # Remove duplicates after merging
            unique_periods = []
            seen = set()
            for period in merged[batch][day]:
                # Create a unique tuple for each period to check for duplicates
                period_tuple = (period['time'], period['subject'], period['teacher'], period['room'])
                if period_tuple not in seen:
                    unique_periods.append(period)
                    seen.add(period_tuple)
            merged[batch][day] = unique_periods


    return json.loads(json.dumps(merged)) # Convert back to regular dict

if __name__ == "__main__":
    # --- Instructions ---
    # 1. Place this script in the same folder as your CSV files.
    # 2. Make sure the CSV files have "Batch A", "Batch B", or "Batch C" in their names.
    # 3. Run the script from your terminal: python csv_to_json_parser.py
    # 4. A file named 'timetable.json' will be created.
    
    all_timetables = []
    # Find all CSV files in the current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} CSV files to process...")

    for filename in csv_files:
        print(f"Parsing {filename}...")
        try:
            parsed_data = parse_csv_to_json(filename)
            all_timetables.append(parsed_data)
        except Exception as e:
            print(f"Could not parse {filename}. Error: {e}")
            
    # Merge all the parsed data
    final_data = merge_timetables(all_timetables)

    # Write the output to a JSON file
    output_filename = 'timetable.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)

    print(f"\nSuccessfully created {output_filename} with all merged timetable data!")