"""Trentox study material for DHET Industrial Electronics N6 (8080186)."""

import ipaddress
import random
from dataclasses import dataclass
from pathlib import Path


CODE = "IE-N6"
NAME = "Industrial Electronics N6"
SYLLABUS = (
    "https://www.dhet.gov.za/Revised%20Report%20191%20Nated%20Syllabus/"
    "Engineering%20Studies/2025-2026/N6%20Industrial%20Electronics.pdf"
)
ICASS_URL = (
    "https://www.dhet.gov.za/Technical%20and%20Vocational%20Education%20and%20Training%20Co/"
    "2026%20REPORT%20191%20ICASS%20Guidelines%20January.pdf"
)
ICASS_ARCHIVE = "2020 ICASS Guidelines for REPORT 191.pdf"


@dataclass(frozen=True)
class Module:
    title: str
    filename: str
    weight: int
    notes: tuple[str, ...]
    formula: str
    models: tuple[str, ...]
    questions: tuple[tuple[str, str, int], ...]


MODULES = (
    Module(
        "Transients", "Module 1 Transients.pdf", 10,
        (
            "At a switching instant, ideal capacitor voltage and inductor current cannot jump. Use that fact to find the starting value, then replace C with an open circuit and L with a short circuit to find the long-time DC value.",
            "For a first-order circuit, find the resistance seen by the storage element with independent sources deactivated. Use RC for a capacitor and L/R for an inductor. After one time constant the response has travelled about 63% of the way from its initial to its final value.",
            "In a series RLC circuit, compare R with 2√(L/C). Below this resistance the response rings; at the threshold it is critically damped; above it the response is overdamped. On a sketch, mark the final value and the shrinking oscillation peaks.",
        ),
        r"\tau_{RC}=RC,\quad \tau_{RL}=\frac{L}{R},\quad x(t)=x_\infty+(x_0-x_\infty)e^{-t/\tau}",
        ("rc_response",),
        (
            ("A 100 µF capacitor starts uncharged and is connected to 12 V through 20 kΩ. Find the time constant, the capacitor voltage after one time constant, and the initial charging current.",
             "Convert µF and kΩ to SI units. τ = 20,000 × 0.0001 = 2.0 s. At t = τ, Vc = 12(1 − e⁻¹) ≈ 7.59 V. Initially Vc = 0 V, so I = 12/20,000 = 0.60 mA. (1 mark for τ, 2 for Vc, 1 for I.)", 4),
            ("A series RLC circuit has L = 10 mH and C = 1 µF. Find the critical resistance and classify the response with R = 150 Ω.",
             "Rcrit = 2√(L/C) = 2√(0.010/0.000001) = 200 Ω. Since 150 Ω is below 200 Ω, the circuit is underdamped and can ring after a step. (2 marks for Rcrit, 1 for classification, 1 for the behaviour.)", 4),
        ),
    ),
    Module(
        "Transducers", "Module 2 Transducers.pdf", 10,
        (
            "Trace the measurement chain: physical quantity → sensor → signal conditioning → analogue-to-digital converter → record or display. An actuator works in the other direction, using a command to produce an action.",
            "A thermocouple generates a small voltage from a temperature difference. An RTD changes resistance and needs excitation to be read. Check range, accuracy, response time and compatibility with the input before choosing a sensor.",
            "Condition the sensor signal before digitising it. An amplifier changes span, an offset shifts zero, a filter limits unwanted frequencies, and linearisation compensates for a curved response. Feedback resistors set the gain of an op-amp circuit.",
        ),
        r"A_{v,\mathrm{inv}}=-\frac{R_f}{R_{\rm in}},\qquad A_{v,\mathrm{noninv}}=1+\frac{R_f}{R_g}",
        ("wheatstone", "rtd_tc", "opamp_inv"),
        (
            ("A sensor produces 0.25–1.25 V across its operating range. You need 0–5 V at the ADC. Write an ideal transfer equation and explain the two conditioning operations.",
             "Subtract 0.25 V to set the zero, then multiply by 5 to expand the 1 V span to 5 V. Vout = 5(Vin − 0.25 V). The endpoints give 0 V and 5 V. (1 mark for offset, 1 for gain, 1 for the equation, 1 for checking endpoints.)", 4),
            ("A bridge produces a +40 mV signal relative to its reference. An ideal inverting stage uses 10 kΩ input resistance and 100 kΩ feedback. Find the output and give one reason to check it against the ADC input range.",
             "Gain = −100/10 = −10. Output = −10 × 40 mV = −0.40 V. An ADC that only accepts non-negative voltages cannot measure it correctly without a compatible stage or level shift. (1 mark for gain, 1 for the sign, 1 for the value, 1 for the ADC constraint.)", 4),
        ),
    ),
    Module(
        "Ultrasonics, X-rays and radioactivity", "Module 3 Ultrasonics, X-rays and radioactivity.pdf", 15,
        (
            "Ultrasound is a mechanical wave and needs a medium. A piezoelectric element can generate a pulse and detect its echo; magnetostriction can also generate vibration. In pulse-echo inspection, halve the travelled distance to find one-way thickness.",
            "Compare the use of ultrasound for cleaning, joining, machining and inspection. Cavitation helps dislodge dirt in a cleaning bath, while a thickness gauge uses the delay between an emitted pulse and its return.",
            "X-rays are electromagnetic radiation. An X-ray tube accelerates electrons into a target; slowing the electrons produces a broad spectrum and atomic transitions add characteristic lines. Radioactive decay, by contrast, originates in unstable nuclei. Compare alpha, beta and gamma emissions and how half-life changes activity over time.",
        ),
        r"d=\frac{vt}{2},\qquad \lambda_{\min}=\frac{hc}{eV},\qquad A=A_0\,2^{-t/T_{1/2}}",
        ("pulse_echo_3d",),
        (
            ("In a virtual steel inspection, a back-wall echo returns after 8.0 µs. Wave speed is 5,900 m/s. Estimate the plate thickness and explain the factor of two.",
             "The echo travels to the back wall and returns. d = 5,900 × 8.0 × 10⁻⁶ / 2 = 0.0236 m = 23.6 mm. (1 mark for time conversion, 2 for the thickness, 1 for explaining the round trip.)", 4),
            ("A simulated X-ray tube runs at 50 kV. Using hc ≈ 1,240 eV·nm, find the shortest wavelength and state whether a lower voltage would make it longer or shorter.",
             "The largest photon energy is eV = 50,000 eV. λmin = 1,240/50,000 ≈ 0.0248 nm. Lower voltage reduces the maximum photon energy, so the minimum wavelength becomes longer. (1 mark for energy, 2 for the wavelength, 1 for the trend.)", 4),
        ),
    ),
    Module(
        "Automatic inspection, testing and NDT", "Module 4 Automatic inspection, testing and NDT.pdf", 10,
        (
            "Break an inspection line into part detection, measurement, a decision against limits, sorting and a confirmation that the part reached the intended lane. A check of the reject mechanism catches faults the inspection sensor alone cannot detect.",
            "A two-way sorter makes a pass/reject decision. A three-way sorter can distinguish undersize, acceptable and oversize parts. Put the boundary values and equality rules on your block diagram.",
            "Non-destructive testing checks a part without making it unusable. Insulation resistance and dielectric withstand are different electrical production tests: one measures resistance, the other verifies the insulation withstands a specified test stress. Review these with drawings and simulations.",
        ),
        "",
        ("pulse_echo_3d",),
        (
            ("A three-way sorter accepts parts from 19.8 to 20.2 mm, inclusive. Route readings of 19.78, 20.20 and 20.24 mm. Give one feedback signal that could detect a stuck diverter.",
             "19.78 mm: undersize. 20.20 mm: accept, because the boundary is included. 20.24 mm: oversize. An end-position switch on the diverter, or a presence sensor in the commanded lane, can confirm the move. (1 mark for each routing decision and 1 for a valid confirmation signal.)", 4),
            ("A metal detector signals reject, yet the parts still reach the accepted bin. Divide the line into three blocks to locate the fault and state what the detector signal already tells you.",
             "The detection decision was generated. Trace the decision/output command, the diverter actuator and its motion, then the downstream routing or confirmation sensor. Comparing command, motion and actual path separates a logic/output fault from a mechanical fault. (1 mark for each block and 1 for interpreting the detector signal.)", 4),
        ),
    ),
    Module(
        "Electronic safety devices", "Module 5 Electronic safety devices.pdf", 10,
        (
            "Identify the hazard, the safe state and how the design responds to a failed component. A light curtain detects entry into a zone; a guard interlock detects guard position. Both depend on a safety control function to stop or inhibit hazardous motion.",
            "In a safety circuit, a missing healthy signal should be treated as a fault. Think through a blocked beam, a broken conductor, loss of supply and restoration of the signal. A reset and a start are separate actions.",
            "A photoelectric smoke detector can sense light scattered by smoke particles; an ionisation type senses a change in a small ion current. A flame-failure system monitors evidence of flame and signals the burner controller when it is lost.",
            "Intrinsic safety limits available electrical and thermal energy in a hazardous atmosphere. Stored energy in field devices and cables matters alongside supply voltage and current. Use a simulated system to distinguish an energy-limiting barrier from an ordinary signal conditioner.",
        ),
        "",
        ("plc_interlock_3d", "logic_gate_board"),
        (
            ("A light curtain clears after an operator leaves a machine's protected zone. What should the safety logic permit at that moment, and why should it avoid automatic motion?",
             "The cleared signal is one prerequisite for a reset. Verify other protective inputs and require the designated reset/start sequence before motion can resume. A person could remain beyond the beam or another unsafe condition could exist. (1 mark for the cleared input, 1 for other checks, 1 for no automatic restart, 1 for the reason.)", 4),
            ("In a simulation, a guard circuit normally reports healthy when its monitored loop is closed. What should happen when a conductor breaks? How would a controller distinguish guard open from a cable fault?",
             "The broken conductor removes the healthy signal, so the system must enter or maintain its safe state. A single ordinary binary contact cannot distinguish the two on its own; use appropriate monitored channels and diagnostics to provide more evidence. (2 marks for the safe-state reasoning, 2 for the diagnostic limitation and remedy.)", 4),
        ),
    ),
    Module(
        "Electronic power control", "Module 6 Electronic power control.pdf", 10,
        (
            "An open-loop controller commands an output without measuring the result. A closed-loop controller compares the measured value with the setpoint and adjusts the actuator using the error.",
            "Distinguish a regulator, which holds a value despite disturbances, from a follow-up system, which tracks a changing command. Trace setpoint → comparator → controller → power actuator → process → sensor.",
            "For a feedback problem, identify the setpoint, measured variable, manipulated variable and disturbance separately. If the output saturates at a limit, the controller cannot remove every error even when the feedback direction is correct.",
            "A servomechanism follows a position or speed command. Sequential control coordinates events in a defined order. A CNC machine interprets programmed motion commands; CAD describes the part and CAM helps turn the design into manufacturing instructions.",
        ),
        r"e(t)=r(t)-y_{\rm measured}(t)",
        ("pid_loop", "step_response"),
        (
            ("An oven setpoint is 180 °C and the sensor reports 165 °C just after the door opens. Find the error using setpoint minus measurement, name the disturbance and predict the controller's action.",
             "e = 180 − 165 = +15 °C. The open door increases heat loss. With correctly signed heating control and available actuator capacity, heater power should increase. (1 mark for the definition, 1 for error and sign, 1 for the disturbance, 1 for the direction.)", 4),
            ("A conveyor must stay at 1.5 m/s when boxes are added. Describe a closed-loop design by naming the sensor, manipulated variable, disturbance and controlled variable.",
             "Use an encoder or tachometer to measure belt or motor speed. Adjust motor drive output as the manipulated variable. The added load is the disturbance and belt speed is the controlled variable. (1 mark per correct identification.)", 4),
        ),
    ),
    Module(
        "Thyristor devices and SCR speed control", "Module 7 Thyristor devices and SCR Speed Control.pdf", 15,
        (
            "A forward-biased SCR can turn on after a gate pulse. Once latched, removing the gate pulse does not turn it off; anode current must fall below the holding current long enough for recovery. Contrast AC line commutation with forced commutation in a DC circuit.",
            "A firing angle delays the conduction interval. In the ideal half-wave SCR circuit with a resistive load, conduction runs from α to π; an inductive motor load can behave differently. Always identify the circuit topology before using an average-voltage formula.",
            "Changing average armature voltage can change DC motor speed. Follow the current path during each conduction interval and distinguish freewheeling, dynamic braking and regenerative braking before interpreting a waveform.",
            "In an SCR thermal calculation, estimate power loss and track the heat path from junction to case, heatsink and ambient. Latching current immediately after triggering and holding current after conduction is established are different ratings.",
        ),
        r"V_{\rm avg}=\frac{V_m}{2\pi}(1+\cos\alpha)\quad\text{(ideal half-wave, resistive load)}",
        ("scr_structure", "scr_waveform", "bridge_rectifier_3d"),
        (
            ("An ideal half-wave SCR controller supplies a resistor from a sinusoid with peak 100 V. It fires at 60°. Calculate the average output over a full cycle.",
             "For a resistive load the SCR conducts from 60° to 180°. Vavg = 100(1 + cos 60°)/(2π) = 150/(2π) ≈ 23.9 V. (1 mark for the conduction interval, 1 for the half-wave formula, 1 for substitution, 1 for the result.)", 4),
            ("In a DC bench simulation, the SCR stays on after its gate signal returns to zero. Explain what keeps it on, and what the commutation circuit must do.",
             "After turn-on, anode current above the holding current keeps the SCR conducting. A DC commutation circuit must interrupt or divert current to bring it below holding current for the device's turn-off interval. The gate alone does not normally turn an ordinary SCR off. (2 marks for latching and holding current, 2 for commutation and recovery.)", 4),
        ),
    ),
    Module(
        "Programmable logic controllers", "Module 8 PROGRAMMABLE LOGIC CONTROLLERS.pdf", 10,
        (
            "Trace the PLC chain from field input to input module, CPU scan and output module. A typical scan reads inputs, evaluates logic and updates outputs; a short pulse can be missed unless the hardware or program is designed to capture it.",
            "Read ladder rungs from left to right. Series tests are an AND condition, parallel branches are OR conditions, and a timer or counter represents state that spans scans. A seal-in contact can maintain a run command after the start button is released.",
            "Separate physical wiring from the ladder instruction that tests a bit. Trace normal start, stop, broken-wire and power-restoration cases. Safety functions require appropriate safety hardware and design; a standard PLC rung is useful for learning the logic.",
        ),
        "",
        ("plc_interlock_3d", "logic_gate_board"),
        (
            ("A PLC starts a pump only when the tank level is low, supply pressure is healthy and the Auto selector is on. Write the logic and describe its ladder arrangement.",
             "Run = LevelLow AND PressureHealthy AND Auto. Put three tests for the healthy or desired input states in series before the run output. One false test prevents the output. (1 mark for the equation, 2 for the series rung, 1 for the false-input behaviour.)", 4),
            ("Write the Boolean update for a virtual seal-in circuit using a momentary Start, a StopHealthy bit and the previous Run bit. What happens if StopHealthy becomes false while Start is held?",
             "Run_next = StopHealthy AND (Start OR Run_previous). In a rung, the Start and Run branches are parallel, with StopHealthy in series. If StopHealthy is false, the output drops even when Start is held. (2 marks for the update, 1 for the branches, 1 for stop priority.)", 4),
        ),
    ),
    Module(
        "Robotics", "Module 09 Robotics.pdf", 10,
        (
            "A robot uses a controller to turn a task into commands, a drive and actuators to produce motion, and sensors to measure the robot or surroundings. Separate the command path from the feedback path.",
            "An H-bridge reverses motor current by selecting opposite output polarities. For an enabled L293D channel, opposite logic inputs produce opposite directions; disabling that channel makes its outputs high impedance. Distinguish the logic supply from the motor supply.",
            "In closed-loop motion, the controller compares target position or speed with the measured value. Trace a stall by asking whether the command reached the driver, whether the motor responded, and whether feedback matches the actual motion.",
        ),
        "",
        ("h_bridge_3d",),
        (
            ("One L293D bridge is enabled. The inputs change from (1, 0) to (0, 1). What changes at the motor and what happens at the driver outputs when enable goes low?",
             "The output polarity reverses, so the commanded motor direction reverses. With enable low, the two driver outputs are high impedance. The motor's physical direction depends on which way it was wired. (2 marks for polarity and direction, 1 for high impedance, 1 for the wiring distinction.)", 4),
            ("A robot joint is commanded to move to 60°, but its encoder reports 43° and the motor does not move. Name one check on the command path, one on the drive and one on the feedback path.",
             "Check that the controller issued a motion command, that the driver is enabled and producing the expected output, and that the encoder reading agrees with actual joint position. The target error is 17°; the mismatch alone does not identify the failed block. (1 mark per valid check and 1 for the error or interpreting it.)", 4),
        ),
    ),
)

BY_TOPIC = {module.title: module for module in MODULES}
LAB_MODELS = tuple(dict.fromkeys(model for module in MODULES for model in module.models))
FLASHCARDS = dict(zip(BY_TOPIC, (
    (
        ("Which quantities cannot change instantly in an ideal RC or RL switching circuit?",
         "Capacitor voltage and inductor current."),
        ("What changes if you raise R above the critical resistance in a series RLC circuit?",
         "Ringing stops. Above the threshold the response is overdamped and settles more slowly than at critical damping."),
    ),
    (
        ("Which stage changes a sensor’s zero and span before conversion?",
         "Signal conditioning: offset shifts zero and gain changes the span."),
        ("Why can a thermocouple generate a signal without excitation while an RTD needs it?",
         "A thermocouple produces a voltage from a temperature difference; an RTD changes resistance, which needs an electrical measurement."),
    ),
    (
        ("Why divide a pulse-echo flight distance by two?", "The pulse travels to the reflecting surface and back."),
        ("How do X-rays from a tube differ in origin from gamma rays?",
         "Tube X-rays come from accelerated electrons interacting with a target. Gamma rays from radioactive decay originate in the nucleus."),
    ),
    (
        ("How does a three-way sorter improve on a simple pass/reject sorter?",
         "It can separate below-limit, acceptable and above-limit parts, making the reason for rejection visible."),
        ("Why confirm a reject at the output of the sorter?", "A correct reject decision does not prove the actuator sent the part to the reject lane."),
    ),
    (
        ("What is the difference between a guard interlock and a light curtain?",
         "The interlock checks guard position; the light curtain detects interruption of a protected field."),
        ("What does intrinsic safety limit?", "The energy available for a spark or hot surface that could ignite a hazardous atmosphere, including stored energy."),
    ),
    (
        ("What makes a control system closed loop?", "It measures the process output and uses that feedback to adjust the command."),
        ("How does a regulator differ from a follow-up controller?", "A regulator holds a target against disturbances. A follow-up controller tracks a changing target."),
    ),
    (
        ("Can the gate normally switch off a latched SCR?", "No. Anode current must drop below holding current long enough for recovery."),
        ("What does increasing the firing angle do in a resistive half-wave SCR circuit?",
         "It delays turn-on, shortens the conduction interval and lowers average output voltage."),
    ),
    (
        ("What are the three basic steps in a typical PLC scan?", "Read inputs, execute the logic and update outputs."),
        ("What do series and parallel contact tests represent in ladder logic?", "Series tests implement AND; parallel branches implement OR."),
    ),
    (
        ("How does an H-bridge reverse a DC motor?", "It reverses the voltage polarity across the motor."),
        ("What does an encoder contribute to closed-loop motion control?", "It measures position or motion, allowing the controller to compare actual movement with the command."),
    ),
), strict=True))


def questions_for(module, number):
    return [
        {
            "id": f"trentox-ie-n6-{number}-{index}",
            "subject": CODE,
            "num": f"Trentox {number}.{index}",
            "topic": module.title,
            "text": question,
            "marking": answer,
            "marks": marks,
            "original_practice": True,
        }
        for index, (question, answer, marks) in enumerate(module.questions, 1)
    ]


def question_set(limit, rng=None):
    """Cover a different module per question before choosing second questions."""
    rng = rng or random
    first, second = [], []
    for number, module in enumerate(MODULES, 1):
        choices = questions_for(module, number)
        rng.shuffle(choices)
        first.append(choices[0])
        second.extend(choices[1:])
    rng.shuffle(first)
    rng.shuffle(second)
    return (first + second)[:limit]


def lesson_context(topic):
    module = BY_TOPIC[topic]
    return (
        f"Industrial Electronics N6, DHET subject code 8080186. The learner selected {topic}. "
        f"Trentox study notes: {' '.join(module.notes)} "
        "If the learner asks for a different topic, keep the answer aligned to N6 where possible. "
        "Use simulations for hazardous plant, electrical and radiation examples."
    )


def local_reference(filename, server_address):
    """Return an allowlisted Desktop PDF only when the server binds to loopback."""
    try:
        if not ipaddress.ip_address(server_address or "").is_loopback:
            return None
    except ValueError:
        if server_address != "localhost":
            return None
    if filename != ICASS_ARCHIVE and filename not in {module.filename for module in MODULES}:
        return None
    try:
        directory = (Path.home() / "Desktop" / "attachments").resolve()
        path = (directory / filename).resolve()
        if path.parent == directory and path.is_file():
            return path
    except (OSError, RuntimeError):
        pass
    return None
