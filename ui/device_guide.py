"""Once-only onboarding and a replayable tour anchored to the real app controls."""

import json
import logging
from uuid import uuid4

import streamlit as st

from ui.guide_preferences import claim_first_guide, guide_cookie_name
from ui.guide_steps import GUIDE_STEPS
from ui.guide_overlay import render_overlay, read_browser_preference
from ui.tex_app_control import FEATURES

logger = logging.getLogger(__name__)
_NAV_KEYS = ("learning_workspace", "tutor_section", "quick_tex", "tex_sidebar_panel")


def _cookie_seen(name):
    browser_seen = read_browser_preference(name)
    try:
        if st.context.cookies.get(name) == "1":
            return True
    except (AttributeError, TypeError):
        pass
    return browser_seen


def initialize_guide(state, student_id, dsn, cookie_seen, claim=None):
    """Claim before displaying: skipping, closing or finishing all count as seen."""
    if state.get("_guide_profile") == student_id:
        return
    already_seen_here = state.get("_guide_profile") in (None, student_id) and bool(state.get("first_use_guide_complete") or state.get("first_use_guide_dismissed"))
    claim = claim or claim_first_guide
    first = not cookie_seen
    persistence = "browser"
    if dsn:
        try:
            first = claim(dsn, student_id)
            persistence = "account"
        except Exception as exc:
            logger.warning("Guide preference sync failed: %s", type(exc).__name__)
    state["_guide_profile"] = student_id
    state["_guide_persistence"] = persistence
    state["first_use_guide_open"] = first and not already_seen_here
    state["first_use_guide_step"] = 0
    state["first_use_guide_complete"] = not first or already_seen_here
    state["first_use_guide_dismissed"] = False
    state["_guide_cookie"] = guide_cookie_name(student_id)


def end_guide(state):
    state["first_use_guide_open"] = False
    state["first_use_guide_complete"] = True
    state["first_use_guide_dismissed"] = True
    if state.get("_guide_original_navigation") is not None:
        state["_guide_restore_navigation"] = state.pop("_guide_original_navigation")
    state.pop("_guide_route_id", None)
    state.pop("_guide_current_id", None)


def render_first_use_guide(student_id="session", dsn=None):
    cookie = guide_cookie_name(student_id)
    seen = _cookie_seen(cookie)
    if seen is None:
        st.caption("Loading your guide preference…")
        return
    initialize_guide(st.session_state, student_id, dsn, seen)
    if st.button("📘 Replay the app guide", key="replay_first_use_guide", width="stretch"):
        st.session_state["first_use_guide_step"] = 0
        st.session_state["first_use_guide_open"] = True
        st.session_state["first_use_guide_dismissed"] = False
        st.session_state.pop("_guide_route_id", None)
    if st.session_state.get("first_use_guide_open"):
        ids = st.session_state.get("_guide_step_ids", [row["id"] for row in GUIDE_STEPS])
        position = min(max(int(st.session_state.get("first_use_guide_step", 0)), 0), len(ids) - 1)
        current = next(row for row in GUIDE_STEPS if row["id"] == ids[position])
        if current["feature"] in ("reminders", "display_settings"):
            st.session_state["tex_sidebar_panel"] = current["feature"]
        st.caption(f"App guide · step {position + 1} of {len(ids)}")
        if st.button("Close guide", key="close_first_use_guide", width="stretch"):
            end_guide(st.session_state)
            st.rerun()
    if st.session_state.get("first_use_guide_open"):
        st.caption("Guide preference saved to your account." if st.session_state.get("_guide_persistence") == "account" else "Guide preference saved in this browser.")


def available_steps(workspaces, integrated, has_lab, resource_key=""):
    result = []
    for row in GUIDE_STEPS:
        workspace, section, _ = FEATURES[row["feature"]]
        if workspace not in workspaces:
            continue
        if not integrated and row["id"] in ("starters", "tex", "voice"):
            prefix = f"visual_tutor_{resource_key}" if has_lab else f"resources_{resource_key}"
            suffix = {"starters": "starter_prompts", "tex": "chat_input", "voice": "puter"}[row["id"]]
            row = {**row, "feature": "ask_tutor" if has_lab else "resources", "target": f"{prefix}_{suffix}"}
        if not integrated and section not in (None, "📖 Lessons", "💬 Ask tutor", "🧊 3D lab"):
            continue
        if not integrated and row["id"] in ("lessons", "interactive", "quiz"):
            continue
        if row["id"] == "lab" and not has_lab:
            continue
        if row["id"] == "home" and not has_lab:
            row = {**row, "body": "Home shows your selected course and shortcuts to its available study materials. Open the course outline, exam archive or Tex to begin.", "tip": "Available tools follow the programme, level and subject selected in Study path."}
        result.append(row)
    return result


def prepare_feature_guide(workspaces, *, integrated, has_lab, resource_key=""):
    restore = st.session_state.pop("_guide_restore_navigation", None)
    if restore is not None:
        for key in _NAV_KEYS:
            if key in restore:
                st.session_state[key] = restore[key]
            else:
                st.session_state.pop(key, None)
    if not st.session_state.get("first_use_guide_open"):
        return None
    rows = available_steps(workspaces, integrated, has_lab, resource_key)
    st.session_state["_guide_step_ids"] = [row["id"] for row in rows]
    position = min(max(int(st.session_state.get("first_use_guide_step", 0)), 0), len(rows) - 1)
    st.session_state["first_use_guide_step"] = position
    row = rows[position]
    if row["id"] == "finish" and st.session_state.get("_guide_persistence") == "browser":
        row = {**row, "tip": "This browser remembers that you have seen the guide. Replay is always your choice."}
    if "_guide_original_navigation" not in st.session_state:
        st.session_state["_guide_original_navigation"] = {key: st.session_state[key] for key in _NAV_KEYS if key in st.session_state}
    if st.session_state.get("_guide_route_id") != row["id"]:
        workspace, section, _ = FEATURES[row["feature"]]
        st.session_state["learning_workspace"] = workspace
        if section:
            st.session_state["tutor_section"] = section
        st.session_state["quick_tex"] = False
        if row["sidebar"]:
            st.set_page_config(initial_sidebar_state="expanded")
        st.session_state["_guide_route_id"] = row["id"]
    st.session_state["_guide_current_id"] = row["id"]
    return {"step": row, "number": position + 1, "total": len(rows),
            "items": [{"id": item["id"], "title": item["title"]} for item in rows], "token": str(uuid4())}


def apply_guide_action(state, action):
    if not isinstance(action, dict) or action.get("id") == state.get("_guide_last_action"):
        return False
    if not state.get("first_use_guide_open") or action.get("step") != state.get("_guide_current_id"):
        return False
    ids = state.get("_guide_step_ids", [])
    kind = action.get("kind")
    if kind not in ("next", "back", "stop", "jump"):
        return False
    if kind == "jump" and action.get("target") not in ids:
        return False
    state["_guide_last_action"] = action.get("id")
    index = int(state.get("first_use_guide_step", 0))
    if kind == "stop" or (kind == "next" and index == len(ids) - 1):
        end_guide(state)
    elif kind == "jump":
        state["first_use_guide_step"] = ids.index(action["target"])
    else:
        state["first_use_guide_step"] = max(0, min(len(ids) - 1, index + (1 if kind == "next" else -1)))
    return True


def render_feature_guide(data):
    if data is None:
        return
    result = render_overlay(data)
    if apply_guide_action(st.session_state, getattr(result, "action", None)):
        st.rerun()
