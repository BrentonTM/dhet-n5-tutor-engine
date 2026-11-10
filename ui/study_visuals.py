"""Match specific study topics to trusted models and render them on demand."""

import re

import streamlit as st

from ui import diagrams_study  # Registers the additional circuit models.
from ui.diagram_engine import build_html
from ui.diagram_lib import CY, OR, ST, cyl, param
from ui.diagram_registry import get_spec, title_of


# Put specific circuit names ahead of broader related terms.
MATCHES = {
    "DIGI": (
        ("full_adder_3d", r"full adders?|carry in"),
        ("kmap4", r"k maps?|karnaugh maps?|minterms?"),
        ("ripple_counter_3d", r"ripple counters?|asynchronous counters?|mod(?:ulo)? [0-9]+ counters?"),
        ("weighted_dac_3d", r"dacs?|d a converters?|digital to analo[gu]+e? converters?|weighted resistor"),
        ("flash_adc_3d", r"flash adcs?|flash (?:a d )?converters?|comparator ladder"),
        ("logic_gate_board", r"logic gates?|truth tables?|boolean algebra|xor|nand|logic gate board"),
    ),
    "IE": (
        ("bridge_rectifier_3d", r"bridge rectifier|bridge rectifies|four diode bridge|graetz"),
        ("rectifier", r"rectifiers?|rectification|reservoir capacitors?|ripple voltage"),
        ("opamp_noninv", r"non ?inverting (?:amplifier|op amp|operational amplifier)|op amp non ?inverting"),
        ("opamp_inv", r"(?<!non )(?<!non)inverting (?:amplifier|op amp|operational amplifier)|op amp inverting"),
        ("dc_resistor_network", r"direct current theory|dc resistor network|voltage dividers?|resistors? in (?:series|parallel)|(?:series|parallel) resistors?"),
        ("phasor", r"phasors?|series r ?l ?c circuits?|series r l circuits?|series r c circuits?|inductive reactance|capacitive reactance"),
        ("rc_response", r"rc differentiator|rc integrator|rc time constant"),
        ("load_line", r"load lines?|q points?|quiescent points?"),
        ("bjt_structure", r"common emitter|bjt|npn transistor|transistor amplifier"),
        ("scr_waveform", r"firing angles?|phase control|half wave controller"),
        ("scr_structure", r"scr|thyristors?|holding current"),
        ("wheatstone", r"wheatstone bridges?|strain gauges?"),
        ("lvdt", r"lvdts?|linear variable differential transformers?"),
        ("timer555", r"555 timers?|ne555|astable multivibrators?"),
        ("lc_tank", r"lc tanks?|lc oscillators?|lc resonance"),
        ("cro", r"oscilloscopes?|cathode ray tubes?|cro"),
        ("lcd_cell", r"liquid crystal displays?|lcds?"),
    ),
    "INST": (
        ("current_loop_3d", r"4 (?:to )?20 ma|current loops?|live zero|250 (?:ohm|ω)"),
        ("rotameter", r"rotameters?|variable area flow"),
        ("venturi", r"venturi|bernoulli"),
        ("orifice", r"orifice plates?|orifice meters?"),
        ("weir", r"v notch|weirs?"),
        ("target_flow", r"target (?:flow )?meters?|drag plates?"),
        ("manometer", r"manometers?|u tube"),
        ("bourdon", r"bourdon|mechanical pressure gauges?"),
        ("strain_gauge", r"strain gauges?"),
        ("rtd_tc", r"rtds?|pt100|thermocouples?|thermowells?|resistance temperature detectors?"),
        ("tank_level", r"tank level|ultrasonic level|hydrostatic level"),
        ("ph_probe", r"ph|glass electrodes?|reference electrodes?"),
        ("step_response", r"step responses?|overshoot|damping ratio"),
        ("pid_loop", r"pid|closed loop control|proportional integral derivative"),
    ),
    "MATH": (
        ("unit_circle", r"unit circle|trigonometry"),
        ("derivative", r"differentiation|differential calculus|derivatives?|tangent"),
        ("riemann", r"definite integrals?|integral calculus|riemann"),
        ("revolve", r"volumes? of revolution|rotat(?:e|ed|ing) about"),
        ("second_moment", r"second moments? of area"),
        ("ode_decay", r"first order differential equations?"),
    ),
}

LESSON_TOPICS = {
    "DIGI": {
        "logic gates boolean algebra and k maps": ("logic_gate_board", "kmap4"),
        "combinational circuits": ("full_adder_3d",),
        "counters and shift registers": ("ripple_counter_3d",),
        "counter design": ("ripple_counter_3d",),
        "a d and d a conversion": ("flash_adc_3d", "weighted_dac_3d"),
        "digital to analog and analog to digital converters": ("weighted_dac_3d", "flash_adc_3d"),
        "k maps and code converters": ("kmap4",),
        "boolean algebra xor and xnor": ("logic_gate_board",),
    },
    "IE": {
        "alternating current theory": ("phasor", "rc_response"),
        "power supplies": ("bridge_rectifier_3d", "rectifier"),
        "amplifiers": ("bjt_structure", "load_line", "opamp_inv", "opamp_noninv"),
        "electronic power control": ("scr_waveform", "scr_structure"),
        "electronic phase control": ("scr_waveform", "scr_structure"),
        "integrated circuits and transducers": ("wheatstone", "lvdt"),
        "transducers and electronic testing equipment": ("wheatstone", "lvdt", "cro"),
        "measuring instruments": ("cro", "wheatstone"),
        "oscillators": ("timer555", "lc_tank"),
    },
    "INST": {
        "general instrumentation concepts and terminology": ("current_loop_3d", "bourdon", "rtd_tc"),
        "flow measurement": ("orifice", "venturi", "rotameter", "weir", "target_flow"),
        "density humidity and viscosity measurement": ("manometer",),
        "ph and conductivity measurement": ("ph_probe",),
        "automatic control": ("pid_loop", "step_response"),
    },
    "MATH": {
        "integration techniques": ("riemann",),
        "areas and volumes": ("riemann", "revolve"),
        "differential equations": ("ode_decay",),
    },
}

TRY_THIS = {
    "logic_gate_board": "Set A and B to 1. Compare the AND, XOR and NAND traces.",
    "full_adder_3d": "Set A = B = 1 and change carry-in. Trace which gate drives each output.",
    "kmap4": "Turn on all four corner cells. Trace how adjacency wraps around the edges.",
    "ripple_counter_3d": "Step the clock count from 7 to 8, then set the reset modulus to 6 and repeat.",
    "weighted_dac_3d": "Flip the most significant bit and then the least significant bit. Compare their changes in output.",
    "flash_adc_3d": "Move the input slowly across a threshold. Watch which comparator and output bits change.",
    "dc_resistor_network": "Leave the supply fixed and change from series to parallel. Compare the branch voltages and currents.",
    "bridge_rectifier_3d": "Move through both AC half-cycles. Follow the lit diode pair and check the output polarity.",
    "rectifier": "Compare the input with the rectified waveform. Change the filtering and watch the ripple.",
    "opamp_inv": "Raise the input amplitude. Compare the calculated gain with the output as it reaches a rail.",
    "opamp_noninv": "Adjust Rf, then compare the gain and the output waveform before and after clipping.",
    "current_loop_3d": "Set the process to 0%, then open the junction. Compare 4 mA and 0 mA at the receiver.",
    "orifice": "Change the flow setting and compare the pressure at the two tapping points.",
    "venturi": "Change the inlet velocity and compare the inlet and throat readings.",
    "rotameter": "Raise the flow. Follow the float and look at the space between it and the tube.",
    "pid_loop": "Change one controller setting and trace the signal from setpoint to the valve and back through feedback.",
    "rtd_tc": "Change the temperature. Compare the resistance and thermocouple readings.",
}

EXPLODED_MODELS = {
    "dc_resistor_network", "current_loop_3d", "ripple_counter_3d", "logic_gate_board",
    "full_adder_3d", "bridge_rectifier_3d", "weighted_dac_3d", "flash_adc_3d", "scr_structure",
    "opamp_inv", "opamp_noninv", "timer555", "wheatstone", "lvdt", "rtd_tc", "orifice",
}
SOLID_TYPES = {"box", "cyl", "prism", "sphere", "cone", "lathe", "torus"}


def _normalized(text):
    return re.sub(r"[^\w]+|_", " ", text.casefold()).strip()


def study_models(subject, text, *, lesson=False):
    """Match supported concepts only. Exam questions use their own wording."""
    family = subject.partition("-")[0]
    normalized = _normalized(text)
    if lesson:
        topic = re.sub(r"^m\d+\s+", "", normalized)
        mapped = LESSON_TOPICS.get(family, {}).get(topic)
        if mapped:
            return mapped
    matches = tuple(
        diagram for diagram, pattern in MATCHES.get(family, ())
        if re.search(r"\b(?:" + pattern + r")\b", normalized)
    )
    # The bridge model already includes the reservoir and ripple.
    if "bridge_rectifier_3d" in matches:
        matches = tuple(diagram for diagram in matches if diagram != "rectifier")
    return matches[:4] if lesson else matches[:2]


def decorate_study_model(model_id, model, *, low_quality=False):
    """Use the existing circuit geometry and expose a component separation view."""
    model.update(studyView=True, lowQuality=low_quality, auto=False, bg="#0a1524")
    if model_id == "bridge_rectifier_3d":
        # The shell moves away from a simplified representation of the wound foil.
        shell = next(part for part in model["objects"] if part.get("label") == "Reservoir capacitor C")
        shell["explode"] = [0.75, 0, 1.8]
        model["objects"].extend(
            cyl([2.15, 0, 0.15], radius, height, colour, axis="y", metal=0.45,
                bind={"visible": "p.assembly>0.15"}, label=label, lsize=0.2, lp=[-0.4, 1.25, 0.15])
            for radius, height, colour, label in ((0.32, 1.78, OR, "Wound foil and separator"),
                                                   (0.14, 1.9, ST, None), (0.1, 2.0, CY, None))
        )
    movable = False
    for part in model["objects"]:
        if part["type"] not in SOLID_TYPES:
            continue
        if part.get("opacity", 1) >= 0.75:
            part["outline"] = True
        if model_id not in EXPLODED_MODELS:
            continue
        if ("explode" not in part and part.get("label") and "board" not in part["label"].casefold()
                and part["label"] != "Wound foil and separator"):
            x, y, _ = part["p"]
            part["explode"] = [max(-1.2, min(1.2, x * 0.2)), y * 0.18, 0.8]
        movable = movable or "explode" in part
    if movable:
        model["params"].append(param("assembly", "Component separation", 0, 1, 0, 0.05))
    return model


def render_study_model(model_id, model, *, alt, height=520):
    quality = st.session_state.get("fx_mode", "high")
    if quality == "off":
        st.info("3D visuals are off. Choose High or Low in Study path → Display & 3D settings.")
        return
    if not model:
        st.info("This model is temporarily unavailable.")
        return
    decorate_study_model(model_id, model, low_quality=quality == "low")
    st.iframe(build_html(model), height=height, alt=alt)


def render_study_visual(model_ids, *, key, label="Open interactive 3D demonstration", question=False):
    if not model_ids:
        return
    preview = st.expander(label, key=key, on_change="rerun")
    if preview.open:
        with preview:
            model_id = model_ids[0]
            if len(model_ids) > 1:
                model_id = st.selectbox("Model", model_ids, format_func=title_of, key=f"{key}_model")
            title = title_of(model_id)
            st.markdown(f"**{title}**")
            st.caption(TRY_THIS.get(model_id, "Rotate the model, inspect the labelled parts and change one setting at a time."))
            if question:
                st.caption("Use the question’s own diagram and values for your answer. This model illustrates the underlying principle.")
            render_study_model(model_id, get_spec(model_id), alt=f"Interactive study model: {title}")
