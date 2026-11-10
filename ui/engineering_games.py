"""Short engineering challenges with feedback and replay."""

from typing import NamedTuple

import streamlit as st


class Round(NamedTuple):
    prompt: str
    choices: tuple[str, ...]
    correct: str
    explanation: str


RESISTOR_ROUNDS = (
    Round("Brown · Black · Red · Gold", ("100 Ω ±5%", "1 kΩ ±5%", "10 kΩ ±10%"),
          "1 kΩ ±5%", "Brown and black give 10. Red multiplies by 100. Gold gives ±5% tolerance."),
    Round("Red · Violet · Orange · Gold", ("270 Ω ±5%", "2.7 kΩ ±5%", "27 kΩ ±5%"),
          "27 kΩ ±5%", "Red and violet give 27. Orange multiplies by 1,000."),
    Round("Yellow · Violet · Brown · Silver", ("470 Ω ±10%", "470 Ω ±5%", "4.7 kΩ ±10%"),
          "470 Ω ±10%", "Yellow and violet give 47. Brown multiplies by 10. Silver gives ±10%."),
    Round("Blue · Grey · Black · Gold", ("680 Ω ±5%", "6.8 Ω ±5%", "68 Ω ±5%"),
          "68 Ω ±5%", "Blue and grey give 68. Black as the multiplier means ×1."),
    Round("Green · Blue · Gold · Gold", ("5.6 Ω ±5%", "56 Ω ±5%", "560 Ω ±5%"),
          "5.6 Ω ±5%", "Green and blue give 56. Gold in the third position multiplies by 0.1."),
)

FAULT_ROUNDS = (
    Round("A 24 V bench circuit has an open switch. What does an ideal meter read across that switch when the load is connected?",
          ("0 V", "12 V", "24 V"), "24 V",
          "With no current, the load has no voltage drop. The open switch has the supply voltage across it."),
    Round("A linear 4–20 mA transmitter measures 0–100 kPa. The loop reads 12 mA. What should the display show?",
          ("50 kPa", "60 kPa", "75 kPa"), "50 kPa",
          "Subtract the 4 mA live zero, then divide by the 16 mA span. 8 ÷ 16 gives half scale."),
    Round("A healthy 220 Ω resistor should have 4.4 V across it. What current would you expect?",
          ("2 mA", "20 mA", "50 mA"), "20 mA",
          "Use I = V ÷ R. 4.4 V ÷ 220 Ω = 0.020 A, or 20 mA."),
    Round("An ideal non-inverting comparator should output HIGH when V+ is 3 V and V− is 2 V. It stays LOW. What should you verify first?",
          ("The power rails and the voltages at the actual input pins", "That the output LED is blue", "That the reference is labelled 2 V"),
          "The power rails and the voltages at the actual input pins",
          "Confirm the supply and measure the real inputs before replacing a component or trusting a label."),
    Round("In a virtual circuit, a 12 V supply collapses to near zero and current reaches the supply limit. What is the strongest clue?",
          ("An open branch", "An inverted meter scale", "A short or excessive load"),
          "A short or excessive load",
          "A current-limited supply reduces its output voltage when a load tries to draw more than the set limit."),
)


def render_round_game(key, rounds, *, complete=None):
    """Show one question at a time and keep the run when the learner changes tabs."""
    answers = st.session_state.setdefault(f"{key}_answers", [])
    cursor_key = f"{key}_cursor"
    cursor = st.session_state.get(cursor_key, 0)
    if cursor == len(rounds):
        score = sum(answer == question.correct for answer, question in zip(answers, rounds))
        st.metric("Final score", f"{score} / {len(rounds)}")
        if complete and score == len(rounds):
            complete()
            st.success("Module complete. Your Employability Meter has been updated.")
        elif complete:
            st.info("Try another round and get each scenario right to complete the module.")
        if st.button("Play again", key=f"{key}_replay"):
            answers.clear()
            st.session_state[cursor_key] = 0
            st.rerun()
        return

    question = rounds[cursor]
    st.progress(cursor / len(rounds), text=f"Round {cursor + 1} of {len(rounds)}")
    st.markdown(f"**{question.prompt}**")
    if cursor < len(answers):
        if answers[cursor] == question.correct:
            st.success(f"Correct. {question.explanation}")
        else:
            st.info(f"Best answer: {question.correct}. {question.explanation}")
        label = "See results" if cursor + 1 == len(rounds) else "Next round"
        if st.button(label, key=f"{key}_next_{cursor}", type="primary"):
            st.session_state[cursor_key] = cursor + 1
            st.rerun()
    else:
        answer = st.radio("Choose an answer", question.choices, index=None, key=f"{key}_answer_{cursor}")
        if st.button("Check answer", key=f"{key}_check_{cursor}", disabled=answer is None, type="primary"):
            answers.append(answer)
            st.rerun()


def render_resistor_decoder():
    st.subheader("Resistor Decoder", anchor=False)
    st.caption("Read the four bands from left to right. The band names are written out so you can play without relying on colour.")
    render_round_game("resistor_game", RESISTOR_ROUNDS)


def render_fault_finder():
    st.subheader("Fault Finder", anchor=False)
    st.caption("Use each simulated reading to work out the most likely answer. All circuits here are virtual.")
    render_round_game("fault_game", FAULT_ROUNDS)
