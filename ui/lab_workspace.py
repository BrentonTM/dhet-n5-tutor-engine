"""Shared Tutor & lab model picker and renderer."""

import streamlit as st

from ui.diagram_registry import get_spec, title_of
from ui.n4_courses import N4_LAB_TOPICS, N4_NAMES
from ui.study_visuals import render_study_model


BASE_LAB_PROFILES = {
    **{N4_NAMES[code]: tuple(topics) for code, topics in N4_LAB_TOPICS.items()},
    "Mathematics N5": ("derivative", "riemann", "revolve", "second_moment", "ode_decay", "unit_circle", "pascal"),
    "Industrial Electronics N4": ("dc_resistor_network", *N4_LAB_TOPICS["IE-N4"]),
    "Digital Electronics N4": ("logic_gate_board", "kmap4", "full_adder_3d", "ripple_counter_3d", "weighted_dac_3d", "flash_adc_3d"),
    "Digital Electronics N5 — visualization preview": ("weighted_dac_3d", "flash_adc_3d", "ripple_counter_3d"),
    "Industrial Electronics N5": (
        "phasor", "rc_response", "bridge_rectifier_3d", "rectifier", "bjt_structure", "load_line",
        "opamp_inv", "opamp_noninv", "timer555", "wheatstone", "lvdt", "scr_structure", "scr_waveform", "cro", "lc_tank", "lcd_cell",
    ),
    "Industrial Instruments N5": (
        "current_loop_3d", "rotameter", "venturi", "orifice", "weir", "target_flow", "manometer", "bourdon",
        "strain_gauge", "rtd_tc", "tank_level", "ph_probe", "pid_loop", "step_response",
    ),
}


def render_engineering_lab(preferred_profile, n6_profiles):
    st.markdown("### 🧊 Interactive 3D engineering lab")
    st.caption("Drag to rotate, scroll or pinch to zoom, and select a part to inspect it. Change a control to see the model respond.")

    profiles = {**BASE_LAB_PROFILES, **n6_profiles}
    labels = list(profiles)
    lab_key = "interactive_3d_lab_subject"
    lab_subject = st.selectbox("Lab subject:", labels, key=lab_key,
                               index=0 if lab_key in st.session_state else labels.index(preferred_profile))
    if lab_subject == "Digital Electronics N5 — visualization preview":
        st.caption("Interactive study aids for selected digital electronics topics.")
    if lab_subject == "Industrial Electronics N5":
        st.markdown("#### Guided 3D engineering diagrams")

    diagram_id = st.selectbox("Interactive model:", profiles[lab_subject], format_func=title_of,
                              key=f"interactive_3d_lab_diagram_{lab_subject}")
    title = title_of(diagram_id)
    render_study_model(diagram_id, get_spec(diagram_id), height=680, alt=f"3D lab model: {title}")

    if lab_subject == "Industrial Electronics N5":
        st.divider()
        st.markdown("#### 🧰 Build and simulate this topic")
        st.caption(f"Use the interactive {title} model above, then build a matching circuit below. "
                   "Connect breadboard holes and Arduino pins, run the built-in Blink sketch or load a supported .ino sketch, "
                   "and compare your predicted values with the DC meter.")
        from ui.circuit_lab import render_circuit_lab

        render_circuit_lab(height=1030, focus_topic=title)
