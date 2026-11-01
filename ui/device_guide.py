"""First-use walkthrough built from native Streamlit controls."""

import streamlit as st

_GUIDE_COOKIE = "trentox_tutor_guide_seen_v1"
_GUIDE_COOKIE_SCRIPT = (
    "<script>document.cookie = '" + _GUIDE_COOKIE +
    "=1; Path=/; Max-Age=31536000; SameSite=Lax; Secure';</script>"
)
_GUIDE_STEPS = [
    (
        "Choose what you are learning",
        "Use Study path in the sidebar to select your programme, N-level and subject. "
        "Lessons, practice and examples then follow that selection.",
        "You can change the course selection whenever you need.",
    ),
    (
        "Study one topic, then check it",
        "Open Lessons in Tutor & lab. Choose a comfortable focus block, work through "
        "the explanation and example, then answer the short topic quiz.",
        "Missed concepts appear in your progress view and review queue.",
    ),
    (
        "Make the theory visible",
        "Open 3D lab to rotate and inspect a model or practise a circuit. Follow the "
        "operating tips beside each model.",
        "Drag to rotate and scroll to zoom where the model supports it.",
    ),
    (
        "Ask, practise and review",
        "Use Quick AI tutor for Socratic hints, upload worked answers for feedback, "
        "and try Exam practice. The progress view shows topics to revisit.",
        "Set a study reminder in the sidebar or add one to your device calendar.",
    ),
]


@st.dialog("Welcome to Trentox Tutor AI", width="large")
def _show_guide_dialog():
    step_index = int(st.session_state.get("first_use_guide_step", 0))
    step_index = min(max(step_index, 0), len(_GUIDE_STEPS) - 1)
    title, body, tip = _GUIDE_STEPS[step_index]

    st.caption("FIRST-USE GUIDE · STEP " + str(step_index + 1) + " OF " + str(len(_GUIDE_STEPS)))
    st.progress((step_index + 1) / len(_GUIDE_STEPS))
    st.subheader(title)
    st.write(body)
    st.info("Tip: " + tip)

    back_col, later_col, next_col = st.columns([1, 1, 1])
    with back_col:
        if step_index > 0 and st.button("Back", key="guide_back"):
            st.session_state["first_use_guide_step"] = step_index - 1
            st.rerun()
    with later_col:
        if st.button("Not now", key="guide_later"):
            st.session_state["first_use_guide_open"] = False
            st.session_state["first_use_guide_dismissed"] = True
            st.rerun()
    with next_col:
        label = "Finish guide" if step_index == len(_GUIDE_STEPS) - 1 else "Next"
        if st.button(label, key="guide_next", type="primary"):
            if step_index == len(_GUIDE_STEPS) - 1:
                st.session_state["first_use_guide_open"] = False
                st.session_state["first_use_guide_complete"] = True
            else:
                st.session_state["first_use_guide_step"] = step_index + 1
            st.rerun()


def _cookie_says_guide_is_complete():
    try:
        return st.context.cookies.get(_GUIDE_COOKIE) == "1"
    except (AttributeError, TypeError):
        return False


def render_first_use_guide():
    """Show the guide once per browser profile, with a native replay control."""
    if "first_use_guide_complete" not in st.session_state:
        st.session_state["first_use_guide_complete"] = _cookie_says_guide_is_complete()
    if "first_use_guide_open" not in st.session_state:
        st.session_state["first_use_guide_open"] = not st.session_state["first_use_guide_complete"]
    if "first_use_guide_dismissed" not in st.session_state:
        st.session_state["first_use_guide_dismissed"] = False
    if "first_use_guide_step" not in st.session_state:
        st.session_state["first_use_guide_step"] = 0

    if st.button("📘 Replay the app guide", key="replay_first_use_guide", use_container_width=True):
        st.session_state["first_use_guide_step"] = 0
        st.session_state["first_use_guide_open"] = True
        st.session_state["first_use_guide_dismissed"] = False

    if st.session_state["first_use_guide_open"]:
        _show_guide_dialog()

    if st.session_state["first_use_guide_complete"]:
        st.html(_GUIDE_COOKIE_SCRIPT, unsafe_allow_javascript=True)
