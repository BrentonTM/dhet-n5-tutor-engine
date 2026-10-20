import os
import json

# Ensure target folder exists
timetable_dir = os.path.join("data", "timetables")
os.makedirs(timetable_dir, exist_ok=True)

timetable_payload = {
    "examination_body": "DHET NATED",
    "trimester": "T3-2026",
    "level": "N5",
    "exams": [
        {
            "subject_code": "INST-N5",
            "subject_name": "Instrumentation N5",
            "exam_date": "2026-11-18",
            "session": "Morning (09:00 - 12:00)",
            "paper_code": "8080205"
        },
        {
            "subject_code": "IE-N5",
            "subject_name": "Industrial Electronics N5",
            "exam_date": "2026-11-20",
            "session": "Morning (09:00 - 12:00)",
            "paper_code": "8080235"
        },
        {
            "subject_code": "DE-N5",
            "subject_name": "Digital Electronics N5",
            "exam_date": "2026-11-23",
            "session": "Afternoon (13:00 - 16:00)",
            "paper_code": "8080185"
        },
        {
            "subject_code": "MATH-N5",
            "subject_name": "Mathematics N5",
            "exam_date": "2026-11-25",
            "session": "Morning (09:00 - 12:00)",
            "paper_code": "16030175"
        }
    ]
}

file_path = os.path.join(timetable_dir, "n5_exam_timetable.json")
with open(file_path, "w") as f:
    json.dump(timetable_payload, f, indent=2)

print(f"[SUCCESS] N5 Exam Timetable generated at: {file_path}")
