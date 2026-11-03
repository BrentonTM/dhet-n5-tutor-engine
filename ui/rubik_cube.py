"""A legal, touch-friendly Rubik cube with session-local state (CCv2)."""

from copy import deepcopy
from pathlib import Path

import streamlit as st


_COMPONENT = st.components.v2.component(
    "trentox_rubik_cube",
    html="""
    <div class="tx-rubik-root"></div>
    """,
    js=(Path(__file__).parent / "components" / "rubik_cube.js").read_text(encoding="utf-8"),
    isolate_styles=True,
)


def render_rubik_cube(*, key: str = "rubik_cube", height="content"):
    """Render a true 3x3 puzzle; moves and view survive ordinary app reruns.

    The return object's ``puzzle`` contains legal move history, selected face,
    view angles and a revision. State belongs to this Streamlit session and key.
    """
    state = st.session_state.get(key, {})
    snapshot_key = f"_{key}_puzzle_snapshot"

    def remember_puzzle():
        current = st.session_state.get(key, {}).get("puzzle")
        if isinstance(current, dict):
            # Keep the puzzle when navigating away removes the component widget.
            st.session_state[snapshot_key] = deepcopy(current)

    return _COMPONENT(
        key=key,
        data={"puzzle": state.get("puzzle") or st.session_state.get(snapshot_key)},
        width="stretch",
        height=height,
        on_puzzle_change=remember_puzzle,
    )
