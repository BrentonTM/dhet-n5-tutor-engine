"""Curated retrieval cards and course-specific review state."""

import streamlit as st


DIGITAL = {
    "Number systems and codes": (
        ("Convert binary 101101 to decimal.", "32 + 8 + 4 + 1 = 45."),
        ("Write 27₁₀ in binary and hexadecimal.", "27 = 16 + 8 + 2 + 1, so 11011₂ = 1B₁₆."),
        ("How does 8421 BCD represent decimal 59?", "Encode the two decimal digits separately: 0101 1001."),
        ("Which bit makes 1011001 have even parity?", "0. The existing seven bits already contain four 1s."),
    ),
    "Gates and Karnaugh maps": (
        ("When is an XOR output HIGH?", "When its two inputs differ."),
        ("Write the De Morgan equivalent of NOT(A AND B).", "(NOT A) OR (NOT B)."),
        ("How can one NAND gate be used as an inverter?", "Tie both inputs together. NAND(A, A) = NOT A."),
        ("Why can the four corners of a 4-variable K-map form a group?", "Opposite edges wrap in Gray-code order, so the four cells are adjacent as a group of four."),
        ("What should you compare before connecting a TTL output to another logic family?", "Check guaranteed HIGH/LOW output levels against the receiver’s input thresholds, plus current loading and supply limits."),
    ),
    "Combinational circuits": (
        ("What are SUM and CARRY for A = B = 1, Cin = 0?", "SUM = 0 and CARRY = 1. The result is binary 10."),
        ("What is the carry-out expression of a full adder?", "Cout = AB + Cin(A ⊕ B)."),
        ("How many select lines does an 8-to-1 multiplexer need?", "3. Three binary bits address eight inputs."),
        ("What does an enabled 3-to-8 binary decoder normally do?", "Activates the one output addressed by its three input bits. The active level depends on the device."),
    ),
    "Flip-flops and counters": (
        ("What is stored by a rising-edge D flip-flop?", "The D level at the active edge, provided setup and hold requirements are met."),
        ("What does a JK flip-flop do when J = K = 1 at the active edge?", "It toggles the stored output."),
        ("What frequency appears at Q2 of an ideal binary ripple counter?", "One eighth of the input frequency. Q0, Q1 and Q2 divide by 2, 4 and 8 respectively."),
        ("What stable states does an up counter with decoded reset at 6 show?", "0 through 5. Reaching the decoded state 6 triggers the reset."),
        ("What is the role of a serial-in, parallel-out shift register?", "It takes bits one at a time on successive clocks and exposes the stored bits together on its outputs."),
    ),
    "Converters": (
        ("How many codes can an ideal 8-bit ADC produce?", "256, numbered 0 through 255."),
        ("An ideal 8-bit ADC covers a 0–5 V span. What is one quantisation step?", "5 V ÷ 256 ≈ 19.53 mV."),
        ("How many comparators does a conventional 4-bit flash ADC need?", "2⁴ − 1 = 15."),
        ("Which has the larger contribution in a binary-weighted DAC, MSB or LSB?", "The MSB. In a 4-bit ideal binary-weighted DAC its magnitude is eight times the LSB contribution."),
    ),
}
DIGITAL_N5 = {
    "Code arithmetic and memory": (
        ("Write −5 in 8-bit two’s complement.", "00000101 inverted is 11111010. Add 1 to get 11111011."),
        ("Can even parity detect two bits flipped in the same word?", "No. Two flips preserve the parity. Simple parity detects odd numbers of bit errors."),
        ("How many byte locations can 12 address lines select?", "2¹² = 4,096 byte locations if each address identifies one byte."),
        ("Why debounce a mechanical button connected to a clock input?", "One press can produce several rapid transitions. Debouncing gives the counter one clean event per press."),
        ("What prevents two tri-state devices from fighting on a shared bus?", "Enable only the device that should drive the bus. Other outputs must be in high impedance."),
    ),
}
INDUSTRIAL_ELECTRONICS = {
    "DC networks": (
        ("What is the current through 100 Ω and 200 Ω in series on 12 V?", "I = 12 V ÷ 300 Ω = 40 mA through both."),
        ("Two identical 200 Ω resistors are in parallel. What is their equivalent resistance?", "100 Ω."),
        ("Which quantity is the same across parallel branches?", "Voltage. The current in each branch depends on its impedance."),
        ("What is the power dissipated by 200 Ω carrying 40 mA?", "P = I²R = (0.040)² × 200 = 0.32 W."),
    ),
    "AC and phase": (
        ("What is the RMS value of a sine wave with a 10 V peak?", "10 ÷ √2 ≈ 7.07 V."),
        ("Does current lead or lag voltage in an inductive series circuit?", "It lags. Inductive reactance is positive imaginary impedance."),
        ("What happens to capacitive reactance when frequency doubles?", "It halves. Xc = 1/(2πfC)."),
        ("What happens to XL and XC at series resonance?", "Their magnitudes are equal, so their signed reactances cancel and impedance is resistive in the ideal model."),
    ),
    "Power supplies": (
        ("Which way does load current flow on the two AC half-cycles in a bridge rectifier?", "The diode pair changes, but current through the load keeps the same direction."),
        ("What is the ripple frequency after full-wave rectification of 50 Hz?", "100 Hz. The load sees two charging peaks per cycle."),
        ("At the same load current and ripple frequency, what does doubling the reservoir capacitance do?", "It approximately halves peak-to-peak ripple when the ripple is small."),
        ("Why does the reservoir capacitor discharge between peaks?", "The rectifier stops supplying it when source voltage falls below the capacitor voltage plus diode drops. The capacitor continues supplying the load."),
    ),
    "Amplifiers": (
        ("Find the gain of an inverting op-amp with Rin = 10 kΩ and Rf = 47 kΩ.", "Av = −Rf/Rin = −4.7."),
        ("What is the gain of a non-inverting amplifier with Rf = 40 kΩ and R1 = 10 kΩ?", "1 + Rf/R1 = 5."),
        ("Why can an op-amp output clip even when the input is a clean sine wave?", "The output the gain demands exceeds the amplifier’s available voltage swing."),
        ("What is a transistor’s Q-point?", "Its DC operating point before an AC input is added. It is usually described by collector current and collector-emitter voltage."),
    ),
    "Power control and measurement": (
        ("What keeps a latched SCR on after its gate pulse ends?", "Anode current remaining above holding current, with the device in forward conduction."),
        ("How long is one period at 50 Hz?", "20 ms. T = 1/f."),
        ("A waveform spans four divisions at 0.5 ms/div. What is its frequency?", "The period is 2 ms, so the frequency is 500 Hz."),
        ("What is the bridge output when a Wheatstone bridge is balanced?", "Ideally zero differential voltage across the detector."),
        ("What does an LVDT sense?", "Displacement. Two opposing secondary voltages change as the movable core shifts."),
    ),
}
INDUSTRIAL_ELECTRONICS_N5 = {
    "Oscillators and displays": (
        ("What happens to the ideal LC frequency if capacitance increases?", "The frequency falls. f = 1/(2π√(LC))."),
        ("What does an active-low RESET pin do when held low on a 555 timer?", "It overrides timing and forces the output LOW."),
        ("What is the purpose of a polariser in a liquid-crystal display?", "It selects one light polarisation. The liquid crystal controls how much light passes through the polariser pair."),
    ),
}
INSTRUMENTS = {
    "Signals and calibration": (
        ("What does 4 mA represent in a healthy 4–20 mA measurement loop?", "The lower range value. It is called a live zero because current still flows."),
        ("A 0–100 kPa transmitter gives 12 mA. What is the pressure?", "(12 − 4) ÷ 16 = 0.5 of span, so 50 kPa."),
        ("What voltage does 20 mA produce across a 250 Ω shunt?", "5 V. V = 0.020 A × 250 Ω."),
        ("How do accuracy and repeatability differ?", "Accuracy concerns closeness to a reference. Repeatability concerns agreement between repeated readings under the same conditions."),
        ("What causes hysteresis in a calibration plot?", "The reading at the same input differs depending on whether the input was approached from above or below."),
    ),
    "Flow": (
        ("If flow through an orifice meter doubles, what happens to differential pressure at constant density?", "It increases by a factor of four under the square-root model."),
        ("What happens to velocity and static pressure at a Venturi throat?", "Velocity increases and static pressure decreases relative to the upstream section."),
        ("Why does a rotameter float rise as flow increases?", "It moves to a wider part of the tapered tube until the larger flow can pass at a new force balance."),
        ("What does the head H mean in a V-notch weir formula?", "The upstream liquid level above the notch vertex, measured at the specified upstream location."),
    ),
    "Pressure, density and temperature": (
        ("What moves the pointer of a Bourdon pressure gauge?", "The sealed end of the curved tube moves as it tends to straighten. A linkage transfers that movement to the pointer."),
        ("What causes the difference in liquid heights in a U-tube manometer?", "A pressure difference across the columns. In the simple single-liquid case ΔP = ρgΔh."),
        ("If liquid density increases, how does pressure at a fixed depth change?", "It increases. Gauge pressure due to the liquid column is ρgh."),
        ("How does an RTD differ from a thermocouple?", "An RTD measures a change in resistance. A thermocouple generates a voltage related to the temperature difference between junctions."),
        ("What does relative humidity compare?", "The water-vapour partial pressure with the saturation vapour pressure at the same temperature."),
    ),
    "pH and conductivity": (
        ("What happens to hydrogen ion activity when pH falls by one?", "It increases tenfold."),
        ("Why use a high input impedance with a glass pH electrode?", "The glass electrode has a high source resistance. A low input impedance would load it and distort the voltage."),
        ("Why is temperature important when comparing conductivity readings?", "Ion mobility and therefore conductivity change with temperature. Compare at the same temperature or use suitable compensation."),
    ),
    "Automatic control": (
        ("How is control error usually defined in a negative feedback loop?", "Setpoint minus measured process variable."),
        ("Which PID term responds to accumulated error?", "Integral action. It can remove sustained offset when the loop is appropriately configured."),
        ("What is a final control element?", "The device that changes the process input, for example a valve adjusting flow."),
        ("What is overshoot in a step response?", "How far the measured response rises beyond its final value before settling."),
    ),
}
MATH = {
    "Algebra and trigonometry": (
        ("What is the determinant of [[3, 2], [1, 4]]?", "3 × 4 − 2 × 1 = 10."),
        ("What is the modulus of 3 − 4i?", "√(3² + 4²) = 5."),
        ("Which angles from 0° to 360° have cos θ = ½?", "60° and 300°. Cosine is positive in quadrants I and IV."),
        ("Where is the turning point of y = 2(x − 3)² + 4?", "(3, 4). The coefficient is positive, so it is a minimum."),
    ),
    "Calculus": (
        ("Differentiate 3x³ − 4x + 2.", "9x² − 4."),
        ("Find the slope of y = x² at x = 3.", "dy/dx = 2x, so the slope is 6."),
        ("Find the integral of 6x² with respect to x.", "2x³ + C."),
        ("Evaluate the definite integral of 2x from x = 1 to x = 3.", "[x²]₁³ = 9 − 1 = 8."),
        ("What does integrating velocity over time give?", "Displacement. With signed velocity, portions below the time axis subtract."),
    ),
}
MATH_N5 = {
    "Applications of integration": (
        ("What is the second moment of area of a rectangle about its horizontal centroidal axis?", "I = bh³/12, where h is measured perpendicular to the axis."),
        ("What is the order of y″ + 3y′ + y = 0?", "Second order. The highest derivative is y″."),
        ("When can you use integration by parts?", "For a product where differentiating one factor and integrating the other makes the resulting integral easier."),
    ),
}


DECKS = {
    "DIGI-N4": DIGITAL,
    "DIGI-N5": {**DIGITAL, **DIGITAL_N5},
    "IE-N4": INDUSTRIAL_ELECTRONICS,
    "IE-N5": {**INDUSTRIAL_ELECTRONICS, **INDUSTRIAL_ELECTRONICS_N5},
    "INST-N5": INSTRUMENTS,
    "MATH-N4": MATH,
    "MATH-N5": {**MATH, **MATH_N5},
}


def flashcard_groups(subject, original=()):
    groups = dict(DECKS.get(subject, {}))
    if original:
        groups["Course exercises"] = tuple((card["q"], card["a"]) for card in original)
    return groups


def _move(state, delta):
    state["index"] += delta
    state["revealed"] = False


def _mark(state, flagged, question, needs_review):
    if needs_review:
        flagged.add(question)
    else:
        flagged.discard(question)
    _move(state, 1)


def render_flashcards(subject, original):
    groups = flashcard_groups(subject, original)
    if not groups:
        st.info("Flashcards for this subject have not been integrated yet.")
        return

    st.subheader("Active Recall Flashcards", anchor=False)
    all_cards = tuple(card for group in groups.values() for card in group)
    session = st.session_state.setdefault("flashcard_decks", {})
    deck = session.setdefault(subject, {"flagged": set(), "positions": {}})
    flagged = deck["flagged"]
    st.caption(f"{len(all_cards)} cards · {len(flagged)} flagged for review")
    selected = st.selectbox("Flashcard deck", ["All cards", *groups, "Flagged for review"], key=f"flashcard_filter_{subject}")
    if selected == "Flagged for review":
        cards = tuple(card for card in all_cards if card[0] in flagged)
    else:
        cards = groups.get(selected, all_cards)
    if not cards:
        st.info("Cards you mark for review will appear here.")
        return

    state = deck["positions"].setdefault(selected, {"index": 0, "revealed": False})
    index = state["index"] % len(cards)
    question, answer = cards[index]
    key = f"flash_{subject}"
    st.info(f"**Card {index + 1} of {len(cards)}**\n\n{question}")
    with st.container(horizontal=True):
        st.button("Previous", icon=":material/arrow_back:", key=f"{key}_prev", on_click=_move, args=(state, -1))
        if st.button("Hide answer" if state["revealed"] else "Reveal answer", key=f"{key}_reveal"):
            state["revealed"] = not state["revealed"]
            st.rerun()
        st.button("Next", icon=":material/arrow_forward:", key=f"{key}_next", on_click=_move, args=(state, 1))
    if state["revealed"]:
        st.success(answer)
        with st.container(horizontal=True):
            st.button("Got it", key=f"{key}_correct", on_click=_mark, args=(state, flagged, question, False))
            st.button("Review later", key=f"{key}_review", on_click=_mark, args=(state, flagged, question, True))
