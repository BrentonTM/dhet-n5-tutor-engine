"""Render the plant fault bench and keep case evidence separate from learner answers."""

import json

import streamlit as st

from ui.diagram_lib import BL, OR, ST, box, cyl, param, readout, wire
from ui.diagram_registry import get_spec
from ui.plant_fault_cases import FAULT_CASES, SUBJECT_FAMILIES
from ui.study_visuals import render_study_model


# A few scenes can show the actual fault state using their existing controls.
CASE_SETTINGS = {
    "loop-open": {"open": 1, "process": 50},
    "orifice-zero": {"Q": 8},
    "rtd-open": {"T": 60},
    "float-sticks": {"Q": 5},
    "level-echo": {"L": 25},
    "supply-ripple": {"Vpk": 17, "C": 100, "f": 50},
    "amp-clipping": {"R1": 10, "Rf": 200, "vp": 1, "vsat": 15},
    "input-b-low": {"A": 1, "B": 0},
    "adder-carry-in": {"A": 0, "B": 0, "Cin": 0},
    "counter-mod-six": {"pulses": 5, "modulus": 6},
    "counter-stage": {"pulses": 1},
    "adc-reference": {"Vin": 2.85},
}


def _add_manifold(objects):
    objects.extend([
        wire([[-0.9, 3.4, 0], [-0.9, 4.35, 0], [-0.35, 4.35, 0]], OR, 0.07),
        wire([[0.9, 3.4, 0], [0.9, 4.35, 0], [0.35, 4.35, 0]], BL, 0.07),
        box([0, 4.35, 0], [0.7, 0.36, 0.45], ST),
        cyl([0, 4.6, 0], 0.2, 0.3, OR, label="Equalising valve", lp=[0.2, 0.48, 0.1], lsize=0.23),
    ])


def fault_scene(case):
    """Add measurement hotspots to the actual circuit or instrument geometry."""
    model = get_spec(case.model)
    if not model:
        return None
    if case.id == "orifice-zero":
        _add_manifold(model["objects"])
        model["camera"] = {"pos": [2, 5, 17], "target": [0, 1.35, 0]}
    probes = {probe.part: index for index, probe in enumerate(case.probes, 1)}
    settings = CASE_SETTINGS.get(case.id, {})
    for control in model["params"]:
        control["value"] = settings.get(control["id"], control["value"])
        control["hidden"] = True
    # Diagnostic measurements belong to the case, not the teaching model's normal readouts.
    for part in model["objects"]:
        part.pop("click", None)
        label = part.get("label")
        if label in probes:
            index = probes[label]
            part.update(probeIndex=index, click={"probePoint": index}, lcolor="#5ee7ff",
                        info="Select this test point to read its case measurement.")
        if case.id == "adc-reference" and label == "C08 output":
            part.pop("bind", None)
            part["color"] = "#475569"
            part["emissive"] = 0
    names = ["Choose a test point", *(probe.part for probe in case.probes)]
    readings = ["Rotate the model and tap a highlighted label’s component, or choose a test point.",
                *(probe.reading for probe in case.probes)]
    model["params"].append(dict(param("probePoint", "Probe", 0, len(names) - 1, 0, 1, names=names), select=True))
    model["readouts"] = [readout("Simulated measurement", f"{json.dumps(readings, ensure_ascii=False)}[p.probePoint]")]
    model.update(probe=True, subtitle="", hint="Tap a cyan-labelled component or use the Probe selector. Drag to rotate.")
    return model


def render_fault_bench(subject):
    st.subheader("Plant Fault Diagnosis", anchor=False)
    st.caption("18 virtual cases. Follow the signal or process path and inspect each test point before choosing a cause.")
    family = SUBJECT_FAMILIES.get(subject.partition("-")[0], "Industrial Instruments")
    groups = list(FAULT_CASES)
    group = st.selectbox("Equipment family", groups, index=groups.index(family), key=f"fault_family_{subject}")
    cases = {case.id: case for case in FAULT_CASES[group]}
    ident = st.selectbox("Diagnosis scenario", list(cases), format_func=lambda key: cases[key].title,
                         key=f"fault_case_{subject}_{group}")
    case = cases[ident]
    st.markdown(f"**Symptom.** {case.symptom}")
    st.caption("Training simulation. Probe readings are provided for the case. Real plant testing requires site procedures and authorised supervision.")
    render_study_model(case.model, fault_scene(case), alt=f"3D diagnostic model: {case.title}", height=570)
    with st.expander("Probe readings as text"):
        point = st.selectbox("Test point", [probe.part for probe in case.probes], index=None,
                             key=f"fault_text_probe_{subject}_{ident}")
        if point:
            st.write(next(probe.reading for probe in case.probes if probe.part == point))
    return case


def render_worked_diagnosis(case):
    st.markdown(f"**Likely cause.** {case.cause}")
    st.markdown("\n".join(f"{i}. {step}" for i, step in enumerate(case.walkthrough, 1)))
