import os
import json
import sqlite3
import yaml
from datetime import datetime

def load_config():
    config_path = os.path.join("config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Complete syllabus definition for all 5 N4/N5 subjects
full_curriculum = [
    {
        "subject_code": "INST-N5",
        "subject_name": "Instrumentation N5",
        "level": "N5",
        "modules": [
            {"module_id": 1, "module_name": "Industrial Flow Measurement & Primary Sensing", "weight_percentage": 20, "topics": ["Differential Pressure Meters (Orifice, Venturi, Dall Tube)", "Variable Area Meters (Rotameters)", "Electromagnetic & Ultrasonic Flowmeters", "Coriolis Mass Flowmeters", "Flow Calculations & Reynolds Correction"]},
            {"module_id": 2, "module_name": "Temperature Measurement & Transducers", "weight_percentage": 20, "topics": ["RTDs (Pt100) & Wheatstone Bridges", "Thermocouples & Cold Junction Compensation", "Thermistors & Semiconductor Sensors", "Pyrometers & Optical Measurement", "Thermowells & Dynamic Response"]},
            {"module_id": 3, "module_name": "Automatic Process Control & Final Elements", "weight_percentage": 20, "topics": ["P, I, D Control Modes", "Composite Actions (PI, PD, PID)", "Control Valve Characteristics", "Control Valve Sizing (Cv Value)", "Actuators, Positioners & I/P Converters"]},
            {"module_id": 4, "module_name": "Analytical Instrumentation", "weight_percentage": 20, "topics": ["pH Measurement & Nernst Equation", "Conductivity Measurement", "Gas Chromatography (TCD & FID)", "NDIR & Oxygen Analyzers", "Viscosity and Density Measurement"]},
            {"module_id": 5, "module_name": "Telemetry & Intrinsic Safety", "weight_percentage": 20, "topics": ["4-20mA Current Loops & Live Zero", "HART Communication Protocol", "Hazardous Area Classifications (Zones)", "Intrinsic Safety Barriers", "A/D Conversion & Signal Conditioning"]}
        ]
    },
    {
        "subject_code": "MATH-N5",
        "subject_name": "Mathematics N5",
        "level": "N5",
        "modules": [
            {"module_id": 1, "module_name": "Limits and Continuity", "weight_percentage": 15, "topics": ["L'Hôpital's Rule & Indeterminate Forms", "Limits of Trigonometric and Exponential Functions", "Continuity & Discontinuity Evaluation"]},
            {"module_id": 2, "module_name": "Differential Calculus", "weight_percentage": 25, "topics": ["Implicit & Logarithmic Differentiation", "Parametric Equations & Derivatives", "Partial Derivatives & Taylor/Maclaurin Series"]},
            {"module_id": 3, "module_name": "Integral Calculus Techniques", "weight_percentage": 25, "topics": ["Integration by Parts", "Integration by Partial Fractions", "Trigonometric Substitutions"]},
            {"module_id": 4, "module_name": "Applications of Integration", "weight_percentage": 20, "topics": ["Areas Bound by Curves", "Volumes of Solids of Revolution", "Centroids & Moments of Inertia"]},
            {"module_id": 5, "module_name": "Differential Equations", "weight_percentage": 15, "topics": ["First-Order Separable Equations", "Linear Differential Equations & Integrating Factors", "Second-Order Homogeneous Equations"]}
        ]
    },
    {
        "subject_code": "IE-N5",
        "subject_name": "Industrial Electronics N5",
        "level": "N5",
        "modules": [
            {"module_id": 1, "module_name": "Power Semiconductor Devices", "weight_percentage": 20, "topics": ["SCRs, Triacs, and Diacs Characterization", "MOSFETs & IGBT Switching Behaviour", "Power Transistor Protection & Snubber Circuits"]},
            {"module_id": 2, "module_name": "Operational Amplifiers", "weight_percentage": 25, "topics": ["Inverting, Non-Inverting & Summing Amps", "Differential Amplifiers & CMRR", "Integrators, Differentiators & Active Filters"]},
            {"module_id": 3, "module_name": "Converters and Inverters", "weight_percentage": 20, "topics": ["Controlled Rectifiers (Single & 3-Phase)", "DC Choppers & Duty Cycle Control", "Switching Inverters & PWM Control"]},
            {"module_id": 4, "module_name": "Transducers and Signal Processing", "weight_percentage": 15, "topics": ["Strain Gauges & Load Cells", "LVDTs & Capacitive Sensors", "Optocouplers & Isolation Amplifiers"]},
            {"module_id": 5, "module_name": "Closed-Loop Industrial Systems", "weight_percentage": 20, "topics": ["Feedback Control Loops & Stability", "DC Motor Speed Control Circuits", "AC Induction Motor Drives (VFDs)"]}
        ]
    },
    {
        "subject_code": "DIGI-N4",
        "subject_name": "Digital Electronics N4",
        "level": "N4",
        "modules": [
            {"module_id": 1, "module_name": "Number Systems and Codes", "weight_percentage": 20, "topics": ["Binary, Octal, Hexadecimal Conversions", "Binary Arithmetic & 2's Complement", "BCD Code, Gray Code, and ASCII"]},
            {"module_id": 2, "module_name": "Logic Gates & Boolean Algebra", "weight_percentage": 25, "topics": ["Basic Logic Gates (AND, OR, NOT, NAND, NOR, XOR)", "Boolean Theorems & De Morgan's Laws", "Simplification using Karnaugh Maps (K-Maps)"]},
            {"module_id": 3, "module_name": "Combinational Logic Circuits", "weight_percentage": 20, "topics": ["Adders and Subtractors (Half/Full)", "Multiplexers and Demultiplexers", "Encoders and Decoders"]},
            {"module_id": 4, "module_name": "Sequential Logic & Flip-Flops", "weight_percentage": 20, "topics": ["SR, JK, D, and T Flip-Flops", "Edge-Triggering and Clocking", "Master-Slave Flip-Flop Circuits"]},
            {"module_id": 5, "module_name": "Counters and Shift Registers", "weight_percentage": 15, "topics": ["Asynchronous (Ripple) Counters", "Synchronous Counters & Modulo N", "Serial and Parallel Shift Registers"]}
        ]
    },
    {
        "subject_code": "DIGI-N5",
        "subject_name": "Digital Electronics N5",
        "level": "N5",
        "modules": [
            {"module_id": 1, "module_name": "Advanced Logic & Programmable Logic Devices", "weight_percentage": 20, "topics": ["PLDs, PALs, GALs, and FPGAs Architecture", "VHDL/Verilog Fundamentals", "Combinational Logic in PLDs"]},
            {"module_id": 2, "module_name": "Sequential Machine Design", "weight_percentage": 20, "topics": ["Finite State Machines (Mealy & Moore)", "State Diagrams and State Reduction", "Algorithmic State Machines (ASM)"]},
            {"module_id": 3, "module_name": "Data Converters (ADC & DAC)", "weight_percentage": 20, "topics": ["DAC Circuits (R-2R Ladder, Binary Weighted)", "ADC Architectures (SAR, Flash, Dual Slope)", "Conversion Resolution, Speed & Quantization Error"]},
            {"module_id": 4, "module_name": "Memory Devices & Systems", "weight_percentage": 20, "topics": ["RAM (SRAM, DRAM) & ROM Architecture", "EPROM, EEPROM, and Flash Memory", "Memory Addressing, Bus Timing & Expansion"]},
            {"module_id": 5, "module_name": "Microprocessor Architecture Fundamentals", "weight_percentage": 20, "topics": ["ALU, Accumulator, and Register Structures", "Address, Data, and Control Buses", "Fetch-Execute Cycle & Instruction Decoding"]}
        ]
    }
]

def update_database_payloads():
    config = load_config()
    curr_db = config["databases"]["curriculum_db"]
    mast_db = config["databases"]["mastery_db"]

    # 1. Update curriculum.db
    conn_c = sqlite3.connect(curr_db)
    cur_c = conn_c.cursor()

    cur_c.execute("DELETE FROM topics")
    cur_c.execute("DELETE FROM modules")
    cur_c.execute("DELETE FROM subjects")

    total_topics = 0
    total_modules = 0

    for sub in full_curriculum:
        cur_c.execute("INSERT INTO subjects VALUES (?, ?, ?)", (sub["subject_code"], sub["subject_name"], sub["level"]))
        for mod in sub["modules"]:
            cur_c.execute("INSERT INTO modules VALUES (?, ?, ?, ?)", (mod["module_id"], sub["subject_code"], mod["module_name"], mod["weight_percentage"]))
            total_modules += 1
            for top in mod["topics"]:
                cur_c.execute("INSERT INTO topics (module_id, subject_code, topic_name) VALUES (?, ?, ?)", (mod["module_id"], sub["subject_code"], top))
                total_topics += 1

    conn_c.commit()
    conn_c.close()

    # 2. Sync into mastery.db
    if os.path.exists(mast_db):
        os.remove(mast_db)

    conn_m = sqlite3.connect(mast_db)
    cur_m = conn_m.cursor()

    cur_m.execute("""
    CREATE TABLE topic_mastery (
        topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn_c = sqlite3.connect(curr_db)
    cur_c = conn_c.cursor()
    cur_c.execute("SELECT topic_id, subject_code, module_id, topic_name FROM topics")
    all_topics = cur_c.fetchall()
    conn_c.close()

    today_str = datetime.now().strftime("%Y-%m-%d")
    for t in all_topics:
        cur_m.execute("""
            INSERT INTO topic_mastery (topic_id, subject_code, module_id, topic_name, mastery_score, repetition_count, interval_days, ease_factor, next_review_due)
            VALUES (?, ?, ?, ?, 0.0, 0, 0, 2.5, ?)
        """, (t[0], t[1], t[2], t[3], today_str))

    conn_m.commit()
    conn_m.close()

    print("=================================================================")
    print("      MULTI-SUBJECT CURRICULUM & MASTERY INGESTION COMPLETE      ")
    print("=================================================================")
    print(f" -> Total Subjects Registered : {len(full_curriculum)} (INST-N5, MATH-N5, IE-N5, DIGI-N4, DIGI-N5)")
    print(f" -> Total Modules Created     : {total_modules}")
    print(f" -> Total Topics Tracked      : {total_topics}")

if __name__ == "__main__":
    update_database_payloads()