import json
import os

import yaml


def load_config():
    config_path = os.path.join("config", "settings.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def ingest_timetables():
    config = load_config()
    timetable_dir = config["paths"]["timetables_dir"]
    
    if not os.path.exists(timetable_dir):
        os.makedirs(timetable_dir)
        
    timetable_files = [
        f for f in os.listdir(timetable_dir) 
        if f.endswith(".json") or f.endswith(".yaml")
    ]
    
    parsed_timetables = []
    
    for file in timetable_files:
        file_path = os.path.join(timetable_dir, file)
        try:
            with open(file_path, "r") as f:
                if file.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
                
                # Schema validation
                assert "examination_body" in data, f"Missing 'examination_body' in {file}"
                assert "exams" in data, f"Missing 'exams' in {file}"
                
                print(f"[INGESTED TIMETABLE] {file} ({data['examination_body']} - {data['trimester']})")
                for exam in data["exams"]:
                    print(f"   -> {exam['subject_name']} ({exam['subject_code']}): {exam['exam_date']} [{exam['session']}]")
                
                parsed_timetables.append(data)
        except Exception as e:
            print(f"[ERROR] Failed to ingest timetable {file}: {e}")
            
    return parsed_timetables

if __name__ == "__main__":
    print("=== Phase 5: Examination Timetable Ingestion ===")
    results = ingest_timetables()
    print(f"\n[SUCCESS] Successfully ingested {len(results)} timetable file(s).")