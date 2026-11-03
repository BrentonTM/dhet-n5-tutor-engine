import unittest

from streamlit.testing.v1 import AppTest

from ui.logic_builder import (
    LEVELS, counterexample_feedback, evaluate_circuit, get_level,
    initial_circuit, target_output, truth_table,
)


def gate(kind, a, b="A"):
    return {"type": kind, "a": a, "b": b}


SOLUTIONS = {
    1: {"gates": [gate("AND", "A", "B")], "output": "G1"},
    2: {"gates": [gate("NOT", "B"), gate("AND", "A", "G1")], "output": "G2"},
    3: {"gates": [gate("OR", "A", "B"), gate("NOT", "C"), gate("AND", "G1", "G2")], "output": "G3"},
    4: {"gates": [gate("OR", "A", "B"), gate("AND", "A", "B"), gate("NOT", "G2"), gate("AND", "G1", "G3")], "output": "G4"},
}


class LogicBuilderTests(unittest.TestCase):
    def test_every_level_has_a_complete_solution(self):
        for level in LEVELS:
            with self.subTest(level=level["id"]):
                rows = truth_table(level["id"], SOLUTIONS[level["id"]])
                self.assertEqual(len(rows), 2 ** len(level["inputs"]))
                self.assertTrue(all(row["matches"] for row in rows))

    def test_interlock_matches_reference_and_blocks_overload(self):
        rows = truth_table(2, initial_circuit(2))
        self.assertEqual(sum(row["matches"] for row in rows), 2)
        failure = rows[1]
        self.assertEqual(failure["inputs"], {"A": 0, "B": 1})
        self.assertEqual((failure["target"], failure["actual"]), (0, 1))
        self.assertIn("A=0, B=1", counterexample_feedback(failure))
        for a in (0, 1):
            self.assertEqual(target_output(2, {"A": a, "B": 1}), 0)

    def test_gate_trace_uses_actual_wiring(self):
        output, trace = evaluate_circuit(SOLUTIONS[3]["gates"], {"A": 0, "B": 1, "C": 1}, "G3")
        self.assertEqual(trace, {"G1": 1, "G2": 0, "G3": 0})
        self.assertEqual(output, 0)
        self.assertEqual(evaluate_circuit([gate("NOT", "A")], {"A": 0}, "G1")[0], 1)

    def test_cycles_forward_references_and_bad_signals_are_rejected(self):
        for gates, output in (
            ([gate("AND", "G1", "A")], "G1"),
            ([gate("OR", "A", "G2"), gate("NOT", "G1")], "G2"),
            ([gate("OR", "A", "missing")], "G1"),
            ([gate("XOR", "A", "B")], "G1"),
            ([gate("OR", "A", "B")], "G8"),
        ):
            with self.subTest(gates=gates), self.assertRaises(ValueError):
                evaluate_circuit(gates, {"A": 0, "B": 1}, output)
        with self.assertRaises(ValueError):
            evaluate_circuit([gate("OR", "A", "B")], {"A": 2, "B": 1}, "G1")
        with self.assertRaises(ValueError):
            get_level(True)

    def test_maintenance_blocks_every_fault_combination(self):
        for a in (0, 1):
            for b in (0, 1):
                self.assertEqual(target_output(3, {"A": a, "B": b, "C": 1}), 0)

    def test_ui_wiring_solves_advances_resets_and_retains_other_level(self):
        app = AppTest.from_string(
            "import streamlit as st\n"
            "from ui.logic_builder import render_logic_builder\n"
            "if st.toggle('Show Logic Builder', value=True, key='show_logic'):\n"
            "    render_logic_builder('Breezy')\n"
        ).run()
        self.assertEqual(len(app.exception), 0)
        app.selectbox(key="logic_1_G1_type").select("AND").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Level complete" in message.value for message in app.success))
        self.assertIn(1, app.session_state["logic_builder_state"]["solved"])
        app.button(key="logic_next_1").click().run()
        self.assertEqual(app.session_state["logic_builder_level"], 2)
        app.selectbox(key="logic_2_G1_type").select("NOT").run()
        app.selectbox(key="logic_2_G1_a").select("B").run()
        app.selectbox(key="logic_2_G2_type").select("AND").run()
        app.selectbox(key="logic_2_G2_b").select("G1").run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn(2, app.session_state["logic_builder_state"]["solved"])
        app.button(key="logic_reset_2").click().run()
        self.assertEqual(len(app.exception), 0)
        state = app.session_state["logic_builder_state"]
        self.assertEqual(state["circuits"][2], initial_circuit(2))
        self.assertIn(1, state["solved"])
        self.assertNotIn(2, state["solved"])
        app.selectbox(key="logic_2_G1_type").select("NOT").run()
        app.selectbox(key="logic_2_G1_a").select("B").run()
        app.button(key="logic_row_2_2").click().run()
        app.button(key="logic_hint_2").click().run()
        app.toggle(key="show_logic").set_value(False).run()
        self.assertEqual(len(app.selectbox), 0)
        app.toggle(key="show_logic").set_value(True).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["logic_builder_level"], 2)
        self.assertEqual(app.selectbox(key="logic_2_G1_type").value, "NOT")
        self.assertEqual(app.selectbox(key="logic_2_G1_a").value, "B")
        self.assertEqual(app.session_state["logic_builder_state"]["selected_rows"][2], 2)
        self.assertTrue(app.session_state["logic_builder_state"]["hints"][2])


if __name__ == "__main__":
    unittest.main()
