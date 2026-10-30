"""Render diagrams to standalone HTML files for quick browser/headless checks.

Usage:  python preview_diagrams.py venturi pid_loop      (specific diagrams)
        python preview_diagrams.py --all                  (every diagram)
        python preview_diagrams.py --validate             (structure check, no files)
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from ui import diagram_registry as reg  # noqa: E402
from ui.diagram_engine import build_html  # noqa: E402

OUT = os.path.join(BASE, "_preview")


def validate(spec_id):
    spec = reg.get_spec(spec_id)
    problems = []
    json.dumps(spec)
    ids = {p["id"] for p in spec.get("params", [])}
    for o in spec["objects"]:
        if "type" not in o:
            problems.append("object without type")
    for rd in spec.get("readouts", []):
        if "expr" not in rd:
            problems.append("readout without expr")
    return spec, problems, ids


def main():
    args = sys.argv[1:]
    all_ids = reg.available()
    if "--validate" in args:
        bad = 0
        for i in all_ids:
            try:
                spec, probs, _ = validate(i)
                print(f"OK   {i:18s} objects={len(spec['objects']):3d} params={len(spec['params'])} readouts={len(spec['readouts'])}" + (" PROBLEMS: " + "; ".join(probs) if probs else ""))
            except Exception as exc:  # noqa: BLE001
                bad += 1
                print(f"FAIL {i}: {exc!r}")
        print(f"{len(all_ids)} diagrams, {bad} failed")
        return
    ids = all_ids if "--all" in args or not args else args
    os.makedirs(OUT, exist_ok=True)
    for i in ids:
        spec = reg.get_spec(i)
        if spec is None:
            print("unknown:", i)
            continue
        path = os.path.join(OUT, i + ".html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_html(spec))
        print("wrote", path)


if __name__ == "__main__":
    main()
