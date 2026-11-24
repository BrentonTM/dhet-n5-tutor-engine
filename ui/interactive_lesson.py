"""Adaptive, source-grounded lessons with optional keyless conversational voice."""

import hashlib
import json
import streamlit as st
from google.genai import types

from ui.puter_voice import render_puter_voice
from ui.tex_partner import recent_turns
from ui.tex_voice import lesson_instruction


def lesson_key(subject, topic, notes):
    return hashlib.sha256(json.dumps([subject, topic, notes], ensure_ascii=False).encode()).hexdigest()[:20]


def submit_lesson_turn(state, text, audio, *, call_model, instruction):
    """Keep pending work after provider failure; retry without duplicate user turns."""
    if text or audio:
        if audio and len(audio) > 8 * 1024 * 1024:
            state["error"] = "Record a shorter answer (up to 8 MB)."
            return
        state["messages"].append({"role": "user", "content": str(text or "My spoken answer")[:6000], "audio": audio})
    if not state["messages"] or state["messages"][-1]["role"] != "user":
        return
    contents = []
    for message in recent_turns(state["messages"]):
        parts = [types.Part.from_text(text=message["content"])]
        if message.get("audio"):
            parts.append(types.Part.from_bytes(data=message["audio"], mime_type="audio/wav"))
        contents.append(types.Content(role="model" if message["role"] == "assistant" else "user", parts=parts))
    reply, error = call_model(contents, system_instruction=instruction)
    if reply:
        state["messages"].append({"role": "assistant", "content": reply})
        state["error"] = None
    else:
        state["error"] = error or "Tex could not answer. Your work is still here."
    del state["messages"][:-20]
    for message in state["messages"][:-4]:
        message.pop("audio", None)


def render_interactive_lesson(subject, topic, notes, sources, call_model):
    scope = lesson_key(subject, topic, notes)
    st.subheader("Learn interactively with Tex", anchor=False)
    st.caption("Tex teaches one step, waits for your answer and adapts. Ask for a slower explanation, a worked example or a quiz. This conversation stays in your current study session.")
    sessions = st.session_state.setdefault("interactive_lessons", {})
    if scope not in sessions:
        # Keep only a small number of active lesson conversations in this session.
        while len(sessions) >= 4:
            sessions.pop(next(iter(sessions)))
        sessions[scope] = {"messages": [], "error": None, "seen_utterance": None}
    state = sessions[scope]
    instruction = lesson_instruction(subject, topic, notes, sources) + (
        "\nFor this interactive turn, use at most 180 words, plain conversational text, "
        "and one focused check question. Do not read the entire lesson at once. "
        "When the student requests an explanation or example, provide it before checking understanding."
    )

    def ask(text="", audio=None):
        with st.spinner("Tex is preparing the next learning step…"):
            submit_lesson_turn(state, text, audio, call_model=call_model, instruction=instruction)
        st.rerun()

    if not state["messages"]:
        if st.button("Start interactive lesson", key=f"tex_lesson_start_{scope}"):
            ask("Start this lesson with a short introduction and ask me one question about what I already know.")
        return

    for message in state["messages"][-12:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    latest = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "assistant"), "")
    voice = render_puter_voice(latest, key=f"tex_lesson_voice_{scope}")
    utterance = getattr(voice, "utterance", None)
    if isinstance(utterance, dict) and utterance.get("id") != state["seen_utterance"]:
        state["seen_utterance"] = utterance.get("id")
        text = utterance.get("text")
        if isinstance(text, str) and text.strip():
            ask(text)

    pending = bool(state["messages"] and state["messages"][-1]["role"] == "user")
    if state["error"]:
        st.error(state["error"])
        if st.button("Retry my last lesson message", key=f"tex_lesson_retry_{scope}"):
            ask()
    with st.container(horizontal=True):
        for label, prompt in [("Give me a hint", "Give me one hint for the current question."),
                              ("Explain differently", "Explain the current concept in a different, simpler way with an example."),
                              ("Quiz me", "Ask one application question about what we have covered."),
                              ("Recap this lesson", "Summarize what we discussed and what my answers demonstrate. Suggest what to practise next.")]:
            if st.button(label, key=f"{scope}_{label}", disabled=pending):
                ask(prompt)
    st.caption("Typed messages, recordings and recent lesson context go to Google Gemini when submitted.")
    answer = st.chat_input("Answer Tex or ask a question about this lesson", accept_audio=True,
                           max_upload_size=8, max_chars=6000, key=f"tex_lesson_answer_{scope}",
                           disabled=pending)
    if answer:
        if isinstance(answer, str):
            ask(answer)
        else:
            ask(answer.text, answer.audio.getvalue() if answer.audio else None)
    st.download_button("Download lesson conversation", data="\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in state["messages"]),
        file_name="tex-lesson-conversation.txt", mime="text/plain", key=f"tex_lesson_export_{scope}")
    if st.button("End and clear this lesson conversation", key=f"tex_lesson_end_{scope}"):
        sessions.pop(scope, None)
        st.rerun()
