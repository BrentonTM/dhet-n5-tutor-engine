"""A small, genuine gate-wiring lab with exhaustive truth-table feedback."""

from itertools import product
from typing import Callable

import streamlit as st


GATE_TYPES = ("AND", "OR", "NOT")
LEVELS = (
    {
        "id": 1, "tag": "Two conditions", "title": "Safe start",
        "description": "A is the start request. B is the safety guard closed. The motor Q may run only when both are true.",
        "inputs": ("A", "B"), "gate_count": 1,
        "hint": "Which gate outputs 1 only when both of its inputs are 1?",
    },
    {
        "id": 2, "tag": "Interlock", "title": "Pump interlock",
        "description": "A is tank level high. B is motor overload. The pump Q may run only when the tank is high and there is no overload.",
        "inputs": ("A", "B"), "gate_count": 2,
        "hint": "First turn overload B into a permission signal. Then combine that permission with tank level A.",
    },
    {
        "id": 3, "tag": "Three inputs", "title": "Alarm with maintenance inhibit",
        "description": "A is high temperature. B is high pressure. C is maintenance mode. Alarm Q must activate for either fault, except while maintenance mode is on.",
        "inputs": ("A", "B", "C"), "gate_count": 3,
        "hint": "Combine the two faults first. Make a separate signal for maintenance being off, then decide when the alarm is allowed.",
    },
    {
        "id": 4, "tag": "Combine your gates", "title": "One request at a time",
        "description": "A and B are requests from two operators. Output Q must be 1 when exactly one operator requests a run. Two simultaneous requests must give 0.",
        "inputs": ("A", "B"), "gate_count": 4,
        "hint": "You need at least one request, but never both together. Build those two conditions separately and combine them.",
    },
)


def get_level(level_id: int) -> dict:
    if type(level_id) is not int or not 1 <= level_id <= len(LEVELS):
        raise ValueError("Choose a Logic Builder level from 1 to 4.")
    return LEVELS[level_id - 1]


def initial_circuit(level_id: int) -> dict:
    level = get_level(level_id)
    return {
        "gates": [{"type": "OR", "a": "A", "b": "B"} for _ in range(level["gate_count"])],
        "output": f"G{level['gate_count']}",
    }


def evaluate_circuit(gates: list[dict], inputs: dict, output: str) -> tuple[int, dict]:
    """Evaluate only feed-forward gates; never execute a learner's expression."""
    if not isinstance(gates, list) or not 1 <= len(gates) <= 6:
        raise ValueError("A circuit needs between one and six gates.")
    if not isinstance(inputs, dict) or not inputs or set(inputs) - {"A", "B", "C"}:
        raise ValueError("Circuit inputs must be A, B or C.")
    if any(type(value) is not int or value not in (0, 1) for value in inputs.values()):
        raise ValueError("Every input must be 0 or 1.")
    signals = dict(inputs)
    trace = {}
    for number, gate in enumerate(gates, 1):
        name = f"G{number}"
        if not isinstance(gate, dict) or gate.get("type") not in GATE_TYPES:
            raise ValueError(f"{name} must be an AND, OR or NOT gate.")
        operation = gate["type"]
        left, right = gate.get("a"), gate.get("b")
        if not isinstance(left, str) or left not in signals or (operation != "NOT" and (not isinstance(right, str) or right not in signals)):
            raise ValueError(f"{name} can use an input or an earlier gate only. Feedback loops are not allowed.")
        a = signals[left]
        if operation == "NOT":
            result = 1 - a
        elif operation == "AND":
            result = a & signals[right]
        else:
            result = a | signals[right]
        trace[name] = result
        signals[name] = result
    if not isinstance(output, str) or output not in signals:
        raise ValueError("Choose an available input or gate for output Q.")
    return signals[output], trace


def target_output(level_id: int, inputs: dict) -> int:
    get_level(level_id)
    a, b = inputs["A"], inputs["B"]
    if level_id == 1:
        return a & b
    if level_id == 2:
        return a & (1 - b)
    if level_id == 3:
        return (a | b) & (1 - inputs["C"])
    return int(a != b)


def truth_table(level_id: int, circuit: dict) -> list[dict]:
    level = get_level(level_id)
    rows = []
    for values in product((0, 1), repeat=len(level["inputs"])):
        inputs = dict(zip(level["inputs"], values))
        actual, trace = evaluate_circuit(circuit["gates"], inputs, circuit["output"])
        target = target_output(level_id, inputs)
        rows.append({"inputs": inputs, "target": target, "actual": actual, "trace": trace, "matches": target == actual})
    return rows


def counterexample_feedback(row: dict) -> str:
    inputs = ", ".join(f"{name}={value}" for name, value in row["inputs"].items())
    if row["matches"]:
        return f"Row {inputs} matches: Q={row['actual']}. Now check the rows that still differ."
    return (
        f"Row {inputs} should give Q={row['target']}, but your circuit gives {row['actual']}. "
        "Trace this row through the gates. Where does the signal first go wrong?"
    )


def _store_gate(level_id: int, number: int, field: str, widget_key: str) -> None:
    state = st.session_state["logic_builder_state"]
    state["circuits"][level_id]["gates"][number][field] = st.session_state[widget_key]


def _store_output(level_id: int, widget_key: str) -> None:
    st.session_state["logic_builder_state"]["circuits"][level_id]["output"] = st.session_state[widget_key]


def _select_row(level_id: int, row_index: int) -> None:
    st.session_state["logic_builder_state"]["selected_rows"][level_id] = row_index


def _next_level(level_id: int) -> None:
    st.session_state["logic_builder_state"]["active_level"] = level_id + 1
    st.session_state["logic_builder_level"] = level_id + 1


def _store_level() -> None:
    st.session_state["logic_builder_state"]["active_level"] = st.session_state["logic_builder_level"]


def _reset_level(level_id: int) -> None:
    state = st.session_state["logic_builder_state"]
    state["circuits"][level_id] = initial_circuit(level_id)
    state["selected_rows"][level_id] = 0
    state["hints"].pop(level_id, None)
    if level_id in state["solved"]:
        state["solved"].remove(level_id)
    prefix = f"logic_{level_id}_"
    for key in list(st.session_state):
        if key.startswith(prefix):
            del st.session_state[key]


def render_logic_builder(username: str = "Student", on_ask_tex: Callable[[str], None] | None = None) -> dict:
    """Render the lab. Optional callback receives a concrete circuit question for Tex."""
    st.session_state.setdefault("logic_builder_state", {
        "circuits": {level["id"]: initial_circuit(level["id"]) for level in LEVELS},
        "solved": [], "selected_rows": {}, "hints": {}, "active_level": 1,
    })
    state = st.session_state["logic_builder_state"]
    st.subheader("Logic Builder", icon=":material/account_tree:")
    progress = st.empty()
    progress.caption(f"{len(state['solved'])} of 4 levels solved in this session")
    st.session_state.setdefault("logic_builder_level", state.get("active_level", 1))
    level_id = st.segmented_control(
        "Choose a level", [1, 2, 3, 4], required=True,
        format_func=lambda value: f"{value} ✓" if value in state["solved"] else str(value),
        key="logic_builder_level", width="stretch", on_change=_store_level,
    )
    if level_id not in (1, 2, 3, 4):
        st.error("Choose a valid level.")
        return {"solved": len(state["solved"])}
    level = get_level(level_id)
    circuit = state["circuits"][level_id]
    with st.container(border=True):
        st.caption(f"LEVEL {level_id} · {level['tag'].upper()}")
        st.markdown(f"### {level['title']}")
        st.write(level["description"])
        st.caption("Parts bin: AND · OR · NOT")
    try:
        rows = truth_table(level_id, circuit)
    except (ValueError, KeyError, TypeError) as exc:
        st.error(f"Check your circuit: {exc}")
        st.button("Reset level", key=f"logic_recover_{level_id}", on_click=_reset_level, args=(level_id,))
        return {"level": level_id, "solved": len(state["solved"])}
    matches = sum(row["matches"] for row in rows)
    solved = matches == len(rows)
    if solved and level_id not in state["solved"]:
        state["solved"].append(level_id)
    progress.caption(f"{len(state['solved'])} of 4 levels solved in this session")
    selected = state["selected_rows"].get(level_id)
    if selected is None or not 0 <= selected < len(rows):
        selected = next((index for index, row in enumerate(rows) if not row["matches"]), 0)
    row = rows[selected]
    with st.chat_message("assistant", avatar=":material/psychology:"):
        st.caption("Tex · circuit coach")
        if solved:
            st.write(f"Every row matches, {username}. Explain why your circuit handles the all-zero and all-one inputs correctly.")
        else:
            st.write(counterexample_feedback(row))
        if state["hints"].get(level_id):
            st.info(level["hint"])
    with st.container(horizontal=True):
        if st.button("Hint", key=f"logic_hint_{level_id}", icon=":material/lightbulb:"):
            state["hints"][level_id] = True
            st.rerun()
        st.button("Reset level", key=f"logic_reset_{level_id}", on_click=_reset_level, args=(level_id,))
        if on_ask_tex is not None and st.button("Discuss with Tex", key=f"logic_discuss_{level_id}", icon=":material/chat:"):
            question = (
                f"Help me reason about Logic Builder level {level_id}: {level['title']}. "
                f"Requirement: {level['description']} My gates: {circuit['gates']}; Q comes from {circuit['output']}. "
                f"Selected row: {row['inputs']}; target {row['target']}, mine {row['actual']}. "
                "Ask me one useful question about my wiring."
            )
            on_ask_tex(question)
    st.markdown("#### Circuit")
    st.caption("Choose a gate and its input signals. Earlier gates can feed later gates; feedback loops are excluded.")
    st.caption("Selected row: " + ", ".join(f"{name}={value}" for name, value in row["inputs"].items()))
    for number, gate in enumerate(circuit["gates"]):
        name = f"G{number + 1}"
        sources = list(level["inputs"]) + [f"G{earlier + 1}" for earlier in range(number)]
        with st.container(border=True):
            st.markdown(f"**{name}** · output **{row['trace'][name]}**")
            columns = st.columns(3)
            for column, field, label, options in (
                (columns[0], "type", "gate type", GATE_TYPES),
                (columns[1], "a", "input 1", sources),
                (columns[2], "b", "input 2", sources),
            ):
                key = f"logic_{level_id}_{name}_{field}"
                st.session_state.setdefault(key, gate[field])
                with column:
                    st.selectbox(
                        f"{name} {label}", options, key=key,
                        disabled=field == "b" and gate["type"] == "NOT",
                        on_change=_store_gate, args=(level_id, number, field, key),
                    )
            if gate["type"] == "NOT":
                st.caption("NOT uses input 1 only.")
    output_key = f"logic_{level_id}_output"
    st.session_state.setdefault(output_key, circuit["output"])
    st.selectbox(
        "Output Q comes from", list(level["inputs"]) + [f"G{i + 1}" for i in range(len(circuit["gates"]))],
        key=output_key, on_change=_store_output, args=(level_id, output_key),
    )
    st.markdown(f"#### Truth table · {matches} of {len(rows)} rows match")
    st.caption("Tap a row to trace its values through the circuit above. Target is the required output; yours is your circuit's output.")
    for index, current in enumerate(rows):
        bits = " · ".join(f"{signal}={value}" for signal, value in current["inputs"].items())
        mark = "✓" if current["matches"] else "✗"
        st.button(
            f"{bits}  |  target {current['target']} · yours {current['actual']}  {mark}",
            key=f"logic_row_{level_id}_{index}", type="primary" if index == selected else "secondary",
            width="stretch", on_click=_select_row, args=(level_id, index),
        )
    if solved:
        st.success("Level complete: every truth-table row matches.")
        if level_id < 4:
            st.button("Next level", key=f"logic_next_{level_id}", type="primary", on_click=_next_level, args=(level_id,))
    else:
        st.caption("Match every row to complete this level. A matching row alone does not prove the whole circuit is correct.")
    return {"level": level_id, "solved": len(state["solved"]), "matches": matches, "total": len(rows)}
