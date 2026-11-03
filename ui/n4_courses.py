"""DHET module maps and original starter exercises for two N4 courses."""

from urllib.parse import quote

DHET_FOLDER = (
    "https://www.dhet.gov.za/Revised%20Report%20191%20Nated%20Syllabus/"
    "Engineering%20Studies/2025-2026/"
)

# Each row contains a module, one reference equation, and a Trentox exercise.
N4_MODULES = {
    "MATH-N4": (
        ("Determinants", r"D=ad-bc,\quad x=D_x/D",
         "Use Cramer's rule to solve 3x + 2y = 16 and x − y = 2.",
         "D = −5 [1]. Replace the x and y columns in turn to find Dₓ = −20 and Dᵧ = −10 [2]. Divide to get x = 4 and y = 2 [1]."),
        ("Complex numbers", r"|a+bi|=\sqrt{a^2+b^2}",
         "Find the conjugate, modulus and principal argument in degrees of z = −3 + 4i.",
         "Conjugate −3 − 4i [1]. Modulus √(9 + 16) = 5 [1]. Identify quadrant II [1], then 180° − arctan(4/3) = 126.870° [1]."),
        ("Trigonometry", r"\sin^2\theta+\cos^2\theta=1",
         "Find every solution of 2 sin θ = 1 for 0° ≤ θ < 360°.",
         "Isolate sin θ = 0.5 [1]. Reference angle 30° [1]. Sine is positive in quadrants I and II [1], giving 30° and 150° [1]."),
        ("Functions and graphs", r"y=a(x-h)^2+k",
         "For y = (x − 3)² − 4, find the turning point, axis of symmetry and x-intercepts.",
         "Turning point (3, −4) [1]; axis x = 3 [1]. Set y = 0 so x − 3 = ±2 [1], giving intercepts (1, 0) and (5, 0) [1]."),
        ("Differential calculus", r"\frac{d}{dx}x^n=nx^{n-1}",
         "Find the equation of the tangent to y = 2x³ − 5x + 1 at x = 2.",
         "Differentiate to obtain 6x² − 5 [1]. At x = 2 the slope is 19 [1] and y = 7 [1]. Hence y − 7 = 19(x − 2) [1]."),
        ("Integral calculus", r"\int x^n\,dx=\frac{x^{n+1}}{n+1}+C\quad(n\ne-1)",
         "Calculate the area between y = 3x² + 2 and the x-axis from x = 0 to x = 2.",
         "The curve is above the axis [1]. An antiderivative is x³ + 2x [1]. Evaluate at both limits [1] to get 12 square units [1]."),
    ),
    "IE-N4": (
        ("Direct current theory", r"V=IR,\quad P=VI",
         "A 12 V supply feeds 100 Ω and 200 Ω resistors in series. Find the current and power in the 200 Ω resistor.",
         "Rₜ = 300 Ω [1]. I = 12/300 = 0.040 A [1]. Use P = I²R [1] to get 0.320 W [1]."),
        ("Alternating current theory", r"X_L=2\pi fL,\quad |Z|=\sqrt{R^2+(X_L-X_C)^2}",
         "A 10 V RMS source feeds a series R-L circuit with R = 6 Ω and inductive reactance of 8 Ω. Find the impedance magnitude, RMS current and whether current leads or lags.",
         "Use |Z| = √(6² + 8²) [1] = 10 Ω [1]. I = 10/10 = 1 A RMS [1]. The current lags the voltage in this inductive circuit [1]."),
        ("Electronic power control", r"\text{SCR remains on while }I_A\text{ stays above }I_H\text{ after latching}",
         "A forward-biased SCR has latched on in a DC circuit. Its anode current is 60 mA and its holding current is 20 mA. Does removing the gate pulse turn it off? What happens if the anode current is reduced to 10 mA?",
         "Removing the gate pulse does not turn it off [1]; 60 mA exceeds holding current [1]. At 10 mA it is below holding current [1] and turns off if held there long enough to recover [1]."),
        ("Power supplies", r"f_{\mathrm{ripple}}=2f_{\mathrm{line}}\quad\text{(full-wave)}",
         "A full-wave bridge rectifies a 50 Hz supply. Find the ripple frequency and explain the role of a reservoir capacitor across the load.",
         "Both half-cycles contribute [1], so ripple frequency is 100 Hz [1]. The capacitor charges near voltage peaks [1] and supplies load current between peaks, reducing ripple [1]."),
        ("Amplifiers", r"A_v=\frac{v_{\mathrm{out}}}{v_{\mathrm{in}}}",
         "A common-emitter amplifier produces a 2.4 V peak-to-peak output from a 120 mV peak-to-peak input. The output is inverted. Find the signed voltage gain.",
         "Convert 120 mV to 0.120 V [1]. Use the same voltage convention for both signals [1]. Magnitude is 2.4/0.120 = 20 [1]. The inversion gives a signed gain of −20 [1]."),
        ("Transducers and electronic testing equipment", r"f=\frac{1}{T}",
         "An oscilloscope waveform repeats every four horizontal divisions at 0.5 ms per division. Find the period in seconds and the frequency.",
         "Multiply 4 × 0.5 = 2 ms [1]. Convert to 0.002 s [1]. Use f = 1/T [1] to get 500 Hz [1]."),
    ),
}

N4_NAMES = {"MATH-N4": "Mathematics N4", "IE-N4": "Industrial Electronics N4"}
N4_CODES = {"MATH-N4": "16030164", "IE-N4": "8080164"}
N4_LAB_TOPICS = {
    "MATH-N4": {"unit_circle": "Trigonometry", "derivative": "Differential calculus", "riemann": "Integral calculus"},
    "IE-N4": {
        "phasor": "Alternating current theory", "bridge_rectifier_3d": "Power supplies",
        "bjt_structure": "Amplifiers", "scr_waveform": "Electronic power control",
        "cro": "Transducers and electronic testing equipment",
    },
}


def syllabus_url(subject_code):
    name = N4_NAMES[subject_code]
    return DHET_FOLDER + quote("N4 " + name.removesuffix(" N4") + ".pdf")


def starter_questions(subject_code):
    return [
        {
            "id": f"trentox-{subject_code.lower()}-{index}",
            "subject": subject_code,
            "num": f"Trentox {index}",
            "topic": topic,
            "text": question,
            "marking": solution,
            "marks": 4,
            "original_practice": True,
        }
        for index, (topic, _, question, solution) in enumerate(N4_MODULES.get(subject_code, ()), 1)
    ]
