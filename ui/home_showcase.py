"""Course-aware live models for the home page, using the existing 3D lab."""

import streamlit as st

from ui.diagram_engine import build_html
from ui.diagram_registry import get_spec, title_of
from ui.n4_courses import N4_LAB_TOPICS, N4_NAMES
from ui.n6_visuals import N6_LAB_MODELS


HOME_MODELS = {
    **{code: tuple(topics) for code, topics in N4_LAB_TOPICS.items()},
    **N6_LAB_MODELS,
    "INST-N5": ("rotameter", "venturi", "bourdon", "pid_loop"),
    "IE-N5": ("bridge_rectifier_3d", "opamp_inv", "bjt_structure"),
    "IE-N6": ("rc_response", "wheatstone", "pulse_echo_3d", "plc_interlock_3d", "h_bridge_3d", "scr_waveform", "pid_loop", "logic_gate_board"),
    "MATH-N5": ("derivative", "riemann", "revolve"),
    "DIGI-N4": ("logic_gate_board", "full_adder_3d", "kmap4"),
    "DIGI-N5": ("weighted_dac_3d", "flash_adc_3d"),
}

LAB_SUBJECTS = {
    **N4_NAMES,
    "INST-N5": "Industrial Instruments N5",
    "IE-N5": "Industrial Electronics N5",
    "IE-N6": "Industrial Electronics N6",
    "MATH-N5": "Mathematics N5",
    "DIGI-N4": "Digital Electronics N4",
    "DIGI-N5": "Digital Electronics N5 — visualization preview",
}


def render_home_model(subject_code, *, height=350):
    """Render a real lab model with rotation, labels, sliders and live readouts."""
    model_id = st.selectbox(
        "Choose a live engineering model",
        HOME_MODELS.get(subject_code, HOME_MODELS["INST-N5"]),
        format_func=title_of,
        key=f"home_live_model_{subject_code}",
        label_visibility="collapsed",
    )
    quality = st.session_state.get("fx_mode", "high")
    if quality == "off":
        st.info("Live models are switched off. Choose High or Low in Study path → Display & 3D settings to show them.")
        return model_id
    model = get_spec(model_id)
    if model is None:
        st.info("This model is temporarily unavailable. Choose another model above.")
        return model_id
    # Specs and expressions come only from the repository's trusted registry.
    model["auto"] = quality == "high"
    model["bg"] = "#0b1524"
    document = build_html(model)
    # The selected title is already shown in the native model picker. Keep the
    # small preview's canvas clear; the full lab retains the detailed heading.
    document = document.replace("</head>", """<style>
    #title{display:none}
    #stage{background:radial-gradient(ellipse at 48% 38%,#173e50 0%,#0a1120 74%)}
    #btns button{padding:5px 6px;font-size:11px}
    #hint{font-size:11px}
    </style></head>""")
    if quality == "low":
        document = document.replace("antialias:true", "antialias:false").replace(
            "Math.min(window.devicePixelRatio||1,2)", "1"
        )
    st.iframe(
        document, height=height,
        alt=f"Live engineering model: {title_of(model_id)}. Drag to rotate, adjust sliders and inspect labelled parts.",
    )
    return model_id


def model_discussion_prompt(subject_name, model_id):
    """Name the model without claiming Tex can see its current slider values."""
    return (
        f"I am exploring the {title_of(model_id)} live model while studying {subject_name}. "
        "Guide me through one prediction, one change to a control, and a short explanation of what I observe. "
        "Start by asking me a prediction question. Ask me to report the settings and readings you need."
    )
