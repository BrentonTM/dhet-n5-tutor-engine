import os
import json
import sqlite3
import yaml
from datetime import datetime

# 1. Update instrumentation_n5.json payload directly
n5_payload = {
	"subject_code": "INST-N5",
	"subject_name": "Instrumentation N5",
	"level": "N5",
	"modules": [
		{
			"module_id": 1,
			"module_name": "Industrial Flow Measurement & Primary Sensing",
			"weight_percentage": 20,
			"topics": [
				"Differential Pressure Meters (Orifice, Venturi, Dall Tube, Pitot Tube)",
				"Variable Area Meters (Rotameters & Tapered Tubes)",
				"Electromagnetic, Ultrasonic (Transit Time & Doppler), and Vortex Flowmeters",
				"Coriolis Mass Flowmeters & Thermal Mass Sensing",
				"Flow Calculations, Discharge Coefficients & Reynolds Number Corrections",
			],
		},
		{
			"module_id": 2,
			"module_name": "Temperature Measurement & Transducers",
			"weight_percentage": 20,
			"topics": [
				"Resistance Temperature Detectors (RTDs, Pt100) & Wheatstone Bridge Circuits",
				"Thermocouples (Types J, K, T, S), Cold Junction Compensation & Extension Leads",
				"Thermistors (NTC/PTC) & Semiconductor Temperature Sensors",
				"Optical & Radiation Pyrometers (Blackbody Radiation & Emissivity)",
				"Thermowells, Response Time Constant, and Dynamic Error Compensation",
			],
		},
		{
			"module_id": 3,
			"module_name": "Automatic Process Control & Final Control Elements",
			"weight_percentage": 20,
			"topics": [
				"Proportional (P), Integral (I), and Derivative (D) Control Modes",
				"Composite Actions (PI, PD, PID) and Offset Elimination",
				"Control Valve Characteristics (Linear, Equal Percentage, Quick Opening)",
				"Control Valve Sizing Equations (Cv Value) & Cavitation/Flashing",
				"Pneumatic Actuators, I/P Converters, and Smart Valve Positioners",
			],
		},
		{
			"module_id": 4,
			"module_name": "Analytical Instrumentation & Gas Analysis",
			"weight_percentage": 20,
			"topics": [
				"pH Measurement (Glass Electrode, Reference Electrode & Nernst Equation)",
				"Conductivity Measurement & Temperature Compensation",
				"Gas Chromatography (Carrier Gas, Columns, TCD & FID Detectors)",
				"Infrared Gas Analyzers (NDIR) & Oxygen Analyzers (Zirconia Cell)",
				"Viscosity and Density Measurement Techniques",
			],
		},
		{
			"module_id": 5,
			"module_name": "Signal Conditioning, Telemetry & Intrinsic Safety",
			"weight_percentage": 20,
			"topics": [
				"4-20mA Two-Wire Current Loops & Live Zero Advantages",
				"HART Communication Protocol & Digital Signal Modulation",
				"Hazardous Area Classifications (Zone 0, 1, 2) & Explosion-Proof Enclosures",
				"Intrinsic Safety Barriers (Zener Barriers & Galvanic Isolators)",
				"Analog-to-Digital (A/D) Conversion & Noise Rejection",
			],
		},
	],
}

curriculum_dir = os.path.join("data", "dhet_curriculum")
os.makedirs(curriculum_dir, exist_ok=True)

with open(os.path.join(curriculum_dir, "instrumentation_n5.json"), "w") as f:
	json.dump(n5_payload, f, indent=2)

# 2. Rebuild curriculum.db
curr_db_path = os.path.join("data", "databases", "curriculum.db")
os.makedirs(os.path.dirname(curr_db_path), exist_ok=True)

conn_c = sqlite3.connect(curr_db_path)
cur_c = conn_c.cursor()

cur_c.execute("CREATE TABLE IF NOT EXISTS subjects (subject_code TEXT PRIMARY KEY, subject_name TEXT NOT NULL, level TEXT NOT NULL)")
cur_c.execute("CREATE TABLE IF NOT EXISTS modules (module_id INTEGER, subject_code TEXT, module_name TEXT NOT NULL, weight_percentage REAL, PRIMARY KEY (module_id, subject_code))")
cur_c.execute("CREATE TABLE IF NOT EXISTS topics (topic_id INTEGER PRIMARY KEY AUTOINCREMENT, module_id INTEGER, subject_code TEXT, topic_name TEXT NOT NULL)")

cur_c.execute("DELETE FROM topics")
cur_c.execute("DELETE FROM modules")
cur_c.execute("DELETE FROM subjects")

cur_c.execute("INSERT INTO subjects VALUES (?, ?, ?)", (n5_payload["subject_code"], n5_payload["subject_name"], n5_payload["level"]))
for mod in n5_payload["modules"]:
	cur_c.execute("INSERT INTO modules VALUES (?, ?, ?, ?)", (mod["module_id"], n5_payload["subject_code"], mod["module_name"], mod["weight_percentage"]))
	for top in mod["topics"]:
		cur_c.execute("INSERT INTO topics (module_id, subject_code, topic_name) VALUES (?, ?, ?)", (mod["module_id"], n5_payload["subject_code"], top))

conn_c.commit()

cur_c.execute("SELECT COUNT(*) FROM topics")
top_count = cur_c.fetchone()[0]
conn_c.close()

# 3. Rebuild mastery.db
mastery_db_path = os.path.join("data", "databases", "mastery.db")
if os.path.exists(mastery_db_path):
	os.remove(mastery_db_path)

conn_m = sqlite3.connect(mastery_db_path)
cur_m = conn_m.cursor()

cur_m.execute("""
CREATE TABLE topic_mastery (
	topic_id INTEGER PRIMARY KEY,
	subject_code TEXT NOT NULL,
	module_id INTEGER NOT NULL,
	topic_name TEXT NOT NULL,
	mastery_score REAL DEFAULT 0.0,
	repetition_count INTEGER DEFAULT 0,
	interval_days INTEGER DEFAULT 0,
	ease_factor REAL DEFAULT 2.5,
	last_reviewed TEXT,
	next_review_due TEXT
)
""")

cur_m.execute("""
CREATE TABLE study_logs (
	log_id INTEGER PRIMARY KEY AUTOINCREMENT,
	topic_id INTEGER,
	session_date TEXT NOT NULL,
	duration_minutes INTEGER NOT NULL,
	performance_rating INTEGER NOT NULL,
	notes TEXT
)
""")

conn_c = sqlite3.connect(curr_db_path)
cur_c = conn_c.cursor()
cur_c.execute("SELECT topic_id, subject_code, module_id, topic_name FROM topics")
all_topics = cur_c.fetchall()
conn_c.close()

today_str = datetime.now().strftime("%Y-%m-%d")
for t in all_topics:
	cur_m.execute("INSERT INTO topic_mastery VALUES (?, ?, ?, ?, 0.0, 0, 0, 2.5, NULL, ?)", (t[0], t[1], t[2], t[3], today_str))

conn_m.commit()

cur_m.execute("SELECT COUNT(*) FROM topic_mastery")
mastery_count = cur_m.fetchone()[0]
conn_m.close()

print(f"[SUCCESS] Curriculum DB updated: {top_count} topics populated.")
print(f"[SUCCESS] Mastery DB initialized: {mastery_count} N5 topics tracked.")
