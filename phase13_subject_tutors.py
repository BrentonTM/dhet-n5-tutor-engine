import os
import sqlite3

class SubjectTutorSkill:
	"""Specialized tutor engine providing subject-specific hints, formulas, and topic frameworks."""
    
	FORMULA_SHEETS = {
		"INST-N5": {
			"Process Control": "PID Control: u(t) = K_p * e(t) + K_i * ∫e(t)dt + K_d * (de/dt)",
			"Flow Measurement": "Differential Pressure Flow: Q = C * √(ΔP / ρ)",
			"Temperature Sensing": "RTD Resistance: R_T = R_0 * (1 + α * T)",
			"Pressure Transmitters": "Span = Upper Range Value (URV) - Lower Range Value (LRV)"
		},
		"MATH-N5": {
			"Integration": "Integration by Parts: ∫u dv = uv - ∫v du",
			"Differential Equations": "First-Order Linear: dy/dx + P(x)y = Q(x) => I.F. = e^(∫P(x)dx)",
			"Taylor / Maclaurin": "f(x) = f(0) + f'(0)x + (f''(0)/2!)x^2 + ...",
			"Partial Fractions": "A/(ax+b) + (Bx+C)/(ax^2+bx+c)"
		},
		"IE-N5": {
			"Operational Amplifiers": "Inverting Gain: A_v = -R_f / R_in | Non-Inverting: A_v = 1 + (R_f / R_in)",
			"Power Electronics": "SCR Triggering: V_T = V_G + I_G * R_G",
			"Transducers": "Wheatstone Bridge Balance: R1 / R2 = R3 / R4"
		},
		"DIGI-N4": {
			"Number Systems": "2's Complement = 1's Complement + 1",
			"Boolean Algebra": "De Morgan's Laws: NOT(A AND B) = NOT A OR NOT B",
			"K-Maps": "Group sizes must be powers of 2 (1, 2, 4, 8, 16)"
		},
		"DIGI-N5": {
			"Counters": "Modulus N Counter requires n flip-flops where 2^n >= N",
			"ADC/DAC Conversion": "DAC Resolution = V_ref / (2^n - 1)",
			"Memory Systems": "Address Lines = log2(Memory Capacity in Words)"
		}
	}

	def __init__(self, active_subject="INST-N5"):
		self.active_subject = active_subject

	def get_subject_formulas(self):
		"""Returns reference formulas for the active subject module."""
		formulas = self.FORMULA_SHEETS.get(self.active_subject, {})
		if not formulas:
			# Fallback for base subjects
			base_key = self.active_subject.split("-")[0] if "-" in self.active_subject else self.active_subject
			formulas = next((v for k, v in self.FORMULA_SHEETS.items() if base_key in k), {})
		return formulas

	def generate_socratic_hint(self, topic_name, question_text):
		"""Generates structured subject guidance to help break down past paper questions."""
		base_sub = self.active_subject.split("-")[0] if "-" in self.active_subject else self.active_subject

		hints = {
			"INST": [
				"1. Identify whether the question involves Open-Loop or Closed-Loop control.",
				"2. Check unit conversions for pressure (bar to Pa) or temperature (°C to K).",
				"3. Draw the block diagram before attempting calculations."
			],
			"MATH": [
				"1. Check if substitution (u-du) simplifies the integral before trying integration by parts.",
				"2. Express second-order linear ODEs in auxiliary equation form: m^2 + pm + q = 0.",
				"3. Verify boundary conditions carefully when evaluating integration constants."
			],
			"IE": [
				"1. Assume ideal Op-Amp conditions: Infinite input impedance, zero input current (V+ = V-).",
				"2. Determine firing angle (α) phase relationships for SCR / Triac circuits.",
				"3. Calculate RMS and DC average values carefully."
			],
			"DIGI": [
				"1. Construct truth tables step-by-step for combinational logic circuits.",
				"2. Check flip-flop clock triggering conditions (edge-triggered vs level-triggered).",
				"3. Use K-Maps for minimal SOP (Sum of Products) expressions."
			]
		}

		return hints.get(base_sub, [
			"1. Read the key terminology in the question prompt.",
			"2. Note down all known parameters and required units.",
			"3. State the governing equation before substituting values."
		])
