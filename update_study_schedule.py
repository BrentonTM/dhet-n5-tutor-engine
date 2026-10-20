import yaml
import os

config_path = os.path.join("config", "settings.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Update planner settings with target hours and timetable structure
config["planner"]["default_daily_study_hours"] = 4.0
config["planner"]["start_time"] = "16:00"
config["planner"]["session_structure"] = {
    "block_duration_minutes": 50,
    "short_break_minutes": 10,
    "long_break_minutes": 20,
    "total_blocks": 4
}

with open(config_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("[SUCCESS] Planner configuration updated successfully in config/settings.yaml!")