import os
import json
import sqlite3
import yaml

def load_config():
    config_path = os.path.join("config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Sample rich instructional content payload
sample_payloads = {
    "MATH-N5": {
        "subject_code": "MATH-N5",
        "subject_name": "Mathematics N5",
        "modules": [
            {
                "module_id": 1,
                "module_name": "Limits and Continuity",
                "topics": [
                    {
                        "topic_name": "L'Hôpital's Rule & Indeterminate Forms",
                        "summary": "Application of derivatives to evaluate limits yielding 0/0 or ±∞/∞.",
                        "key_formulas": ["\\lim_{x \\to a} \\frac{f(x)}{g(x)} = \\lim_{x \\to a} \\frac{f'(x)}{g'(x)}"],
                        "worked_example": "Evaluate \\lim_{x \\to 0} \\frac{\\sin(3x)}{x}.\nSolution: Direct substitution gives 0/0. Differentiate numerator (3\\cos(3x)) and denominator (1). \\lim_{x \\to 0} \\frac{3\\cos(3x)}{1} = 3(1) = 3."
                    }
                ]
            },
            {
                "module_id": 5,
                "module_name": "Differential Equations",
                "topics": [
                    {
                        "topic_name": "Linear Differential Equations & Integrating Factors",
                        "summary": "First-order equations of the form dy/dx + P(x)y = Q(x).",
                        "key_formulas": ["I(x) = e^{\\int P(x) dx}", "y \\cdot I(x) = \\int Q(x) \\cdot I(x) dx + C"],
                        "worked_example": "Solve dy/dx + 2y = e^{-x}.\nP(x) = 2, so I(x) = e^{\\int 2 dx} = e^{2x}.\nMultiply: e^{2x} \\frac{dy}{dx} + 2e^{2x}y = e^x \\implies \\frac{d}{dx}[y e^{2x}] = e^x.\nIntegrate: y e^{2x} = e^x + C \\implies y = e^{-x} + C e^{-2x}."
                    }
                ]
            }
        ]
    },
    "DIGI-N4": {
        "subject_code": "DIGI-N4",
        "subject_name": "Digital Electronics N4",
        "modules": [
            {
                "module_id": 2,
                "module_name": "Logic Gates & Boolean Algebra",
                "topics": [
                    {
                        "topic_name": "Simplification using Karnaugh Maps (K-Maps)",
                        "summary": "Graphical method to simplify Boolean expressions up to 4 variables.",
                        "key_formulas": ["Gray Code Order: 00, 01, 11, 10", "Group size must be powers of 2 (1, 2, 4, 8, 16)"],
                        "worked_example": "Minimize F(A,B,C) = \\sum m(1, 3, 5, 7).\nGrouping all four ones gives a 2x2 quad covering C=1 across all A and B combinations.\nSimplified Result: F = C."
                    }
                ]
            }
        ]
    }
}

def ingest_rich_content():
    config = load_config()
    db_path = config["databases"]["curriculum_db"]
    curr_dir = os.path.join("data", "dhet_curriculum")
    os.makedirs(curr_dir, exist_ok=True)

    # Save initial rich payloads to data/dhet_curriculum/
    for sub_code, payload in sample_payloads.items():
        file_path = os.path.join(curr_dir, f"{sub_code}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add content storage columns if they don't exist
    try:
        cursor.execute("ALTER TABLE topics ADD COLUMN summary TEXT")
        cursor.execute("ALTER TABLE topics ADD COLUMN key_formulas TEXT")
        cursor.execute("ALTER TABLE topics ADD COLUMN worked_example TEXT")
    except sqlite3.OperationalError:
        pass

    ingested_files = 0
    for filename in os.listdir(curr_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(curr_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            subject_code = data.get("subject_code", "")
            for mod in data.get("modules", []):
                for top in mod.get("topics", []):
                    # Handle topic as a string or dictionary
                    if isinstance(top, str):
                        topic_name = top
                        summary = ""
                        formulas = json.dumps([])
                        example = ""
                    elif isinstance(top, dict):
                        topic_name = top.get("topic_name", "")
                        summary = top.get("summary", "")
                        formulas = json.dumps(top.get("key_formulas", []))
                        example = top.get("worked_example", "")
                    else:
                        continue

                    cursor.execute("""
                        UPDATE topics
                        SET summary = ?, key_formulas = ?, worked_example = ?
                        WHERE subject_code = ? AND topic_name = ?
                    """, (summary, formulas, example, subject_code, topic_name))
            ingested_files += 1

    conn.commit()
    conn.close()
    print("=================================================================")
    print("     RICH CURRICULUM TEXT INGESTION COMPLETE                     ")
    print("=================================================================")
    print(f" -> Processed JSON files in 'data/dhet_curriculum/': {ingested_files}")

if __name__ == "__main__":
    ingest_rich_content()