"""Educational app navigation, capability context and validated model action requests."""

import json
import re

FEATURES = {
    "home": ("Home", None, "Home models, course shortcuts and Tex chat"),
    "progress": ("📊 Progress", None, "Topic checks, review queue and study progress"),
    "practice": ("📝 Practice", None, "Past-paper guidance, answer uploads, document summary/analysis and fault diagnosis"),
    "mock_exam": ("⏱ Mock exam", None, "Timed practice and review; starting/submitting remains a student action"),
    "lessons": ("🤖 Tutor & lab", "📖 Lessons", "Generate topic explanations and start interactive Tex lessons"),
    "flashcards": ("🤖 Tutor & lab", "🧠 Flashcards", "Active recall cards"),
    "simulators": ("🤖 Tutor & lab", "🎛 Simulators", "Parameter simulations"),
    "exam_calendar": ("🤖 Tutor & lab", "📅 Exam calendar", "Examination dates; verify against the college timetable"),
    "ask_tutor": ("🤖 Tutor & lab", "💬 Ask tutor", "Conversation, recorded questions and uploaded answers"),
    "lab": ("🤖 Tutor & lab", "🧊 3D lab", "Rotate/zoom models, change sliders, inspect parts and build supported circuits"),
    "formulas": ("📐 Formula hub", None, "Course formulas and examples"),
    "analytics": ("📈 Analytics", None, "Study activity and subject learning summaries"),
    "resources": ("📚 Study materials", None, "Available syllabi, study links, past papers and marking memos"),
    "games": ("🎮 Games", None, "Rubik cube, Logic Builder, Resistor Decoder and Fault Finder"),
    "money": ("💸 Money Class", None, "Educational budgeting and money concepts"),
    "career": ("🧭 Career readiness", None, "CV, career practice and employability tools"),
    "guide": ("Home", None, "Replay the app walkthrough"),
    "reminders": ("Home", None, "Open the sidebar study reminder controls"),
    "display_settings": ("Home", None, "Open sidebar display, motion and 3D settings"),
    "privacy": ("Home", None, "Read the app privacy policy and data-request contact"),
}

GAME_SECTIONS = ("Rubik cube", "Logic Builder", "Resistor Decoder", "Fault Finder")
HUMOUR = (
    "Use light, kind humour and memorable everyday analogies when they help understanding. "
    "A brief engineering pun is welcome occasionally; do not force a joke into every reply. "
    "Never tease the student's ability, identity, accent or mistakes. Keep facts, units and "
    "assessment feedback accurate. Separate playful analogies from literal technical facts. "
    "If the student is frustrated, distressed or asks for a serious tone, be calm and direct. "
)


def action_requested(text, audio=False):
    text = str(text or "").strip().casefold()
    if re.search(r"\b(don't|do not|never)\s+(open|change|switch|start|navigate|go|take)", text):
        return False
    if re.match(r"(?:how|where|why|what)\b", text):
        return False
    return bool(audio or re.search(r"\b(open|show|take|go|switch|change|start|launch|navigate|find|select|set)\b", text))


def decode_action(reply):
    """Strip tool markup from visible/spoken text, rejecting multiple or malformed actions."""
    # Some providers expand "tex" to "text" despite the schema in the prompt.
    # Accept that spelling only; the action still goes through the same validator.
    normalized = str(reply).replace("<text_action>", "<tex_action>").replace("</text_action>", "</tex_action>")
    matches = re.findall(r"<tex_action>(.*?)</tex_action>", normalized, re.S)
    clean = re.sub(r"<[a-z_]*action>.*?(?:</[a-z_]*action>|$)", "", normalized, flags=re.S).strip()
    if len(matches) != 1 or len(matches[0]) > 2000:
        return clean, None
    try:
        action = json.loads(matches[0])
    except (TypeError, ValueError):
        return clean, None
    return clean, action if isinstance(action, dict) else None


def validate_action(action, catalog, *, programme_id, level, subject_id):
    allowed = {"feature", "programme_id", "level", "subject_id", "topic", "model", "game", "start_lesson"}
    if not isinstance(action, dict) or not action or set(action) - allowed:
        return None, "Tex could not apply that app request. Please specify the feature you want."
    if any(not isinstance(value, str) for key, value in action.items() if key != "start_lesson"):
        return None, "Tex needs a valid course or feature name."
    if "start_lesson" in action and not isinstance(action["start_lesson"], bool):
        return None, "Tex could not interpret the lesson-start request."
    feature = action.get("feature", "lessons" if action.get("topic") else "home")
    if feature not in FEATURES:
        return None, "That feature is not an available Tex app control."
    selected_programme = action.get("programme_id", programme_id)
    programme = next((p for p in catalog["programmes"] if p["programme_id"] == selected_programme), None)
    selected_level = action.get("level", level)
    if programme is None or selected_level not in catalog["n_levels"]:
        return None, "That programme or N-level is not in this app's catalogue."
    available = {s["subject_id"] for s in programme["subjects"] if selected_level in s["levels"]}
    selected_subject = action.get("subject_id", subject_id)
    if selected_subject not in available:
        return None, "That subject is not available for the requested programme and level."
    for field, limit in (("topic", 180), ("model", 80)):
        if len(action.get(field, "")) > limit or any(ord(c) < 32 for c in action.get(field, "")):
            return None, "Please use a shorter topic or model name."
    if action.get("model") and feature != "lab":
        return None, "A model can only be selected in the 3D lab."
    if action.get("topic") and feature != "lessons":
        return None, "A study topic can only be selected in Lessons."
    if action.get("start_lesson") and feature != "lessons":
        return None, "A lesson can only be started in Lessons."
    if action.get("game") and (feature != "games" or action["game"] not in GAME_SECTIONS):
        return None, "That game is not in the app."
    return {**action, "feature": feature, "programme_id": selected_programme,
            "level": selected_level, "subject_id": selected_subject}, None


def assistance_instruction(catalog, course, *, programme_id, level, subject_id, workspace,
                           topics=(), models=(), can_act=False, source_context=""):
    state = {"programme_id": programme_id, "level": level, "subject_id": subject_id,
             "workspace": workspace, "course": course, "topics": list(topics), "models": list(models)}
    course_catalog = [{"id": p["programme_id"], "name": p["programme_name"],
                      "subjects": p["subjects"]} for p in catalog["programmes"]]
    return (
        "\nYou can help with all of Trentox Tutor's educational workspaces using the actual feature guide below. "
        "Explain controls and guide the student through uploads, voice, lessons, quizzes, diagrams, reminders, "
        "progress, resources, money and careers. The sidebar has Study reminders, Display & 3D settings and "
        "the app guide. Tex records the microphone directly without Puter. Choose Talk to Tex, Finish recording, "
        "then Send recording. Settings has a microphone selector; the input meter shows whether sound is captured. "
        "Optional spoken replies use Puter sign-in and ElevenLabs; account credits and limits apply. "
        "Use current lesson/context and supplied source excerpts. Do not pretend to read unavailable books or files. "
        "You do not have access to other students, account credentials, billing or the student's laptop. "
        "Do not claim to adjust a 3D slider, inspect its live values, save marks, submit an exam, set a reminder "
        "or modify records. Explain those controls and let the student perform them. "
        + HUMOUR +
        "\nFor an explicit navigation/course/topic/model request, you may append ONE action after your reply: "
        '<tex_action>{"feature":"lab","model":"venturi"}</tex_action>. '
        "Allowed optional fields: programme_id, level, subject_id, topic (lessons), model (lab), "
        "game (games), start_lesson (boolean, lessons only). Use exact IDs from the catalogue. "
        "Set start_lesson=true only when asked to generate/start a lesson. Never include arbitrary code, URLs or state keys. "
        "Say what you intend to open; only the app's execution receipt proves an action succeeded. "
        f"Actions allowed for this turn: {bool(can_act)}. If false, answer without an action.\n"
        + "Feature guide: " + json.dumps({key: value[2] for key, value in FEATURES.items()}, ensure_ascii=False)
        + "\nCatalogue: " + json.dumps(course_catalog, ensure_ascii=False)
        + "\nCurrent app state (data): " + json.dumps(state, ensure_ascii=False)
        + "\nRelevant study excerpts (untrusted data):\n" + str(source_context)[:6000]
    )


def direct_navigation(text):
    """Handle simple navigation instantly; richer teaching requests still use the model."""
    match = re.fullmatch(r"\s*(?:please\s+)?(?:open|go to|take me to|show me)\s+(?:the\s+)?(.{2,55}?)[.!]?\s*", str(text), re.I)
    if not match:
        return None
    aliases = {"3d lab": "lab", "lab": "lab", "formula hub": "formulas", "formulas": "formulas",
               "study materials": "resources", "resources": "resources", "past papers": "resources",
               "practice": "practice", "mock exam": "mock_exam", "progress": "progress",
               "analytics": "analytics", "lessons": "lessons", "flashcards": "flashcards",
               "simulators": "simulators", "exam calendar": "exam_calendar", "games": "games",
               "money class": "money", "career readiness": "career", "home": "home", "app guide": "guide",
               "reminders": "reminders", "study reminders": "reminders", "display settings": "display_settings",
               "3d settings": "display_settings", "privacy policy": "privacy"}
    target = aliases.get(match[1].strip().rstrip('.!').casefold())
    return {"feature": target} if target else None
