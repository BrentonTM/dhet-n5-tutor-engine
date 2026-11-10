"""Syllabus and exam links for the selected Report 191 subject and level."""

import streamlit as st


def render_curriculum(course, policy_url):
    st.markdown("#### Curriculum")
    st.caption(f"DHET examination subject code {course['code']}")
    if course.get("syllabus"):
        st.link_button("Open the official DHET syllabus", course["syllabus"], icon=":material/description:")
        st.caption(f"Implementation shown in the syllabus: {course['implementation']}.")
        st.markdown("\n".join(f"{number}. {topic}" for number, topic in enumerate(course["modules"], 1)))
        if course.get("source_note"):
            st.caption(course["source_note"])
    else:
        st.caption("DHET lists this subject in Report 191. A full DHET syllabus is still needed for a verified module outline.")
        st.link_button("Open DHET Report 191 subject listings", policy_url, icon=":material/description:")


def render_exam_resources(course):
    st.markdown("#### Past papers and marking memos")
    pairs = course.get("pairs", [])
    if pairs:
        st.caption("Paired using the subject, level and sitting printed on the documents.")
        sessions = {pair["session"]: pair for pair in pairs}
        sitting = st.selectbox("Exam sitting", sessions, key=f"linked_exam_sitting_{course['code']}")
        with st.container(horizontal=True):
            st.link_button("Open question paper", sessions[sitting]["paper"], icon=":material/description:")
            st.link_button("Open matching memo", sessions[sitting]["memo"], icon=":material/fact_check:")
        if note := sessions[sitting].get("note"):
            st.caption(note)
    elif course.get("archive_pairs"):
        st.caption("The archive lists these papers and memos for the same sitting. Check the covers before marking your work.")
        sessions = {pair["session"]: pair for pair in course["archive_pairs"]}
        sitting = st.selectbox("Archive sitting", sessions, key=f"archive_exam_sitting_{course['code']}")
        with st.container(horizontal=True):
            st.link_button("Preview question paper", sessions[sitting]["paper"], icon=":material/description:")
            st.link_button("Preview listed memo", sessions[sitting]["memo"], icon=":material/fact_check:")
        st.caption("EduCoast asks for an account to download files.")
    with st.container(horizontal=True):
        for archive in course.get("archives", ()):
            st.link_button(archive["label"], archive["url"], icon=":material/open_in_new:")
    if not pairs and not course.get("archive_pairs") and not course.get("archives"):
        st.caption("An exam archive for this subject and level is still being checked.")
    st.caption("For older papers, compare the topics and instructions with the syllabus your college uses.")
