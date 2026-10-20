import json
import os

import yaml


def load_config():
    config_path = os.path.join("config", "settings.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def ingest_curriculum():
    config = load_config()
    curriculum_dir = config["paths"]["curriculum_dir"]
    
    if not os.path.exists(curriculum_dir):
        os.makedirs(curriculum_dir)
        
    curriculum_files = [
        f for f in os.listdir(curriculum_dir) 
        if f.endswith((".json", ".yaml"))
    ]
    
    parsed_curriculums = []
    
    for file in curriculum_files:
        file_path = os.path.join(curriculum_dir, file)
        try:
            with open(file_path, "r") as f:
                if file.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
                
                # Basic schema validation
                assert "subject_code" in data, f"Missing 'subject_code' in {file}"
                assert "modules" in data, f"Missing 'modules' in {file}"
                
                parsed_curriculums.append(data)
                print(f"[INGESTED] {file} -> {data['subject_name']} ({data['level']})")
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Failed to ingest {file}: {e}")
            
    return parsed_curriculums

if __name__ == "__main__":
    print("=== Phase 4: DHET Curriculum Ingestion ===")
    results = ingest_curriculum()
    print(f"\n[SUCCESS] Successfully ingested {len(results)} curriculum file(s).")