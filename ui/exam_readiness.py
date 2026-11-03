"""Practical exam preparation based on published psychology guidance."""

import streamlit as st


def render_exam_readiness():
    with st.expander("Exam mindset and preparation", icon=":material/psychology:"):
        st.write("Practise a short routine before you start the mock so it feels familiar on exam day.")
        stage = st.segmented_control(
            "When do you want help?", ["Before the exam", "During the exam", "After the exam"],
            default="Before the exam", key="exam_readiness_stage",
        )
        if stage == "Before the exam":
            st.markdown("**Make a plan you can rehearse**")
            st.checkbox("Pick one past-paper question to try under timed conditions.", key="exam_readiness_rehearse")
            st.checkbox("Check the start time, venue and equipment rules.", key="exam_readiness_logistics")
            st.checkbox("Set a stopping time for revision so I can get some sleep.", key="exam_readiness_sleep")
            st.caption("If a thought like ‘I’ll fail’ shows up, try ‘I’m nervous, and I can still take the first step.’")
        elif stage == "During the exam":
            st.markdown("""**If your mind goes blank**

1. Put both feet on the floor. Take a few slow, comfortable breaths. Avoid forcing them.
2. Reread the command word and write one thing you know, such as a given value, unit or formula.
3. If you’re still stuck, mark the question and return to it after answering one you can start.
""")
        elif stage == "After the exam":
            st.markdown("""**Turn the practice into a next step**

Name one thing that helped. Pick one thing to practise next time, then take a break before reviewing the paper.
""")
        st.caption("If exam anxiety regularly disrupts sleep, studying or daily life, consider talking to a counsellor or healthcare professional.")
        st.markdown(
            "[American Psychological Association guidance](https://www.apa.org/ed/schools/primer/anxiety) · "
            "[NHS exam guidance](https://www.healthiertogether.nhs.uk/young-person/exams) · "
            "[NHS breathing exercise](https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/)"
        )
