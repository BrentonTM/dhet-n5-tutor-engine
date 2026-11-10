"""Career readiness activities and a module-completion meter."""

import streamlit as st

from ui.engineering_games import Round, render_round_game
from ui.money_class import MONEY_MODULES


CAREER_MODULES = {"cv": "CV and cover letter", "scams": "Job scam awareness"}
READINESS_MODULES = {**MONEY_MODULES, **CAREER_MODULES}
SCAM_ROUNDS = (
    Round(
        "A WhatsApp advert promises a paid apprenticeship and wants R250 today to reserve your slot. What should you do?",
        ("Pay to keep the slot", "Decline the fee and find the advert through the employer’s official website", "Send a copy of your ID instead"),
        "Decline the fee and find the advert through the employer’s official website",
        "An upfront fee and deadline pressure are red flags. Verify independently using contact details you find yourself.",
    ),
    Round(
        "A recruiter using a personal email asks for your bank login and a one-time PIN before an interview.",
        ("Share the PIN only", "Share the login after checking the logo", "Keep both private and verify the recruiter through official channels"),
        "Keep both private and verify the recruiter through official channels",
        "An employer can need payroll information during verified onboarding. A recruiter does not need your login, PIN or one-time code.",
    ),
    Round(
        "An advert has a company logo, a vacancy number and no fee. How should you verify it?",
        ("Find the vacancy on the official careers page or call the published switchboard", "Trust the logo", "Reply with ID and banking documents"),
        "Find the vacancy on the official careers page or call the published switchboard",
        "Logos and vacancy numbers can be copied. Check the role and the submission channel before sharing documents.",
    ),
)


def render_employability_meter(completed, topic_history):
    technical = any(
        row["total"] > 0 and row["score"] * 100 >= 70 * row["total"]
        for row in topic_history
    )
    score = len(completed.intersection(READINESS_MODULES)) + int(technical)
    total = len(READINESS_MODULES) + 1
    with st.container(border=True):
        st.subheader("Employability Meter", anchor=False)
        st.progress(score / total, text=f"{score} of {total} milestones complete")
        st.caption("Complete the money and career activities and score at least 70% in an engineering topic check. This meter tracks learning progress.")
        with st.expander("See milestones"):
            for module, label in READINESS_MODULES.items():
                st.write(f"{'✓' if module in completed else '○'} {label}")
            st.write(f"{'✓' if technical else '○'} Engineering topic check at 70% or above")


def build_application(role, training, skills, example):
    cv = (
        "[Full name]\n[Phone] · [Email] · [Town or city]\n\n"
        f"TARGET ROLE\n{role}\n\nTRAINING\n{training}\n\nTECHNICAL SKILLS\n{skills}\n\n"
        f"PRACTICAL PROJECT OR EXPERIENCE\n{example}\n"
    )
    letter = (
        "[Full name]\n[Phone and email]\n[Date]\n\nDear [Hiring manager],\n\n"
        f"I am applying for the {role} position at [employer]. "
        f"My relevant training includes {training.rstrip('.')}.\n\n"
        f"I can bring these skills to the role: {skills.rstrip('.')}. "
        f"One example of my practical work is described here: {example}\n\n"
        "[Add one sentence on why this employer and role interest you.]\n\n"
        "Thank you for considering my application.\n\nKind regards,\n[Full name]\n"
    )
    return cv, letter


def render_cv_builder(complete, ask_tex):
    st.subheader("CV and cover letter builder", anchor=False)
    st.caption("Build a draft for an apprenticeship, learnership or junior trade role. Add contact details after downloading. Use a school or lab project if you are starting out.")
    with st.form("career_application"):
        role = st.text_input("Target role", max_chars=100, placeholder="Instrumentation apprentice")
        training = st.text_input("Relevant training", max_chars=220, placeholder="N5 Industrial Instruments")
        skills = st.text_input("Technical skills", max_chars=280, placeholder="Reading P&IDs, checking a 4–20 mA loop")
        example = st.text_area(
            "One project or work example", max_chars=800,
            placeholder="What did you do, with which tools, and what was the result?",
        )
        submitted = st.form_submit_button("Build my drafts", type="primary")
    if submitted:
        fields = tuple(value.strip() for value in (role, training, skills, example))
        if all(fields):
            st.session_state["career_application_drafts"] = build_application(*fields)
            complete("cv")
        else:
            st.info("Fill in the role, training, skills and example to build your drafts.")
    if "career_application_drafts" in st.session_state:
        cv, letter = st.session_state["career_application_drafts"]
        st.caption("Drafts from your last build. Check them against the job advert and replace the bracketed fields.")
        with st.expander("Preview CV draft", expanded=True):
            st.code(cv, language=None)
        st.download_button("Download CV draft", cv, "trentox-cv-draft.txt", "text/plain")
        with st.expander("Preview cover letter"):
            st.code(letter, language=None)
        st.download_button("Download cover letter", letter, "trentox-cover-letter.txt", "text/plain")
        st.caption("Tex feedback sends the CV draft and chat context to Google Gemini. Check your draft for private details before sending it.")
        st.button(
            "Get CV feedback from Tex", icon=":material/chat:", on_click=ask_tex,
            args=("Give concise feedback on this draft for a South African engineering or trade role. "
                  "Identify weak evidence and suggest a clearer structure. Do not invent experience or qualifications.\n\n" + cv,),
        )


def render_career_tools(complete, ask_tex):
    st.header("Career readiness", anchor=False)
    st.caption("Practise getting hired for engineering and trade roles.")
    meter = st.container()
    tool = st.selectbox("Choose an activity", CAREER_MODULES, format_func=CAREER_MODULES.get, key="career_tool")
    if tool == "cv":
        render_cv_builder(complete, ask_tex)
    else:
        st.subheader("Spot the job scam", anchor=False)
        st.caption("Three fictional adverts and messages. Choose how you would respond.")
        render_round_game("job_scams", SCAM_ROUNDS, complete=lambda: complete("scams"))
        st.markdown(
            "[Department of Employment and Labour guidance](https://www.labour.gov.za/Media-Desk/Media-Statements/Pages/Department-of-Employment-and-Labour-warns-job-seekers-against-a-scam-learnership-on-social-media-platforms.aspx)"
        )
    return meter
