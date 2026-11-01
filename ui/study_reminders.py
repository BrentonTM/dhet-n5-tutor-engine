"""Native study reminder controls and an importable recurring calendar event."""

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st

SOUTH_AFRICA = ZoneInfo("Africa/Johannesburg")


def _escape_ics(value):
    return str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def build_study_calendar_ics(study_time, repeat):
    """Build a recurring calendar event at the selected South African local time."""
    now = datetime.now(SOUTH_AFRICA)
    start = datetime.combine(now.date(), study_time, tzinfo=SOUTH_AFRICA)
    weekdays_only = repeat == "Weekdays"
    while start <= now or (weekdays_only and start.weekday() >= 5):
        start += timedelta(days=1)
    end = start + timedelta(minutes=20)
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rule = (
        "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"
        if weekdays_only
        else "RRULE:FREQ=DAILY"
    )
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Trentox Tutor AI//Study Reminders//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Trentox Tutor AI Study Reminders",
        "BEGIN:VTIMEZONE",
        "TZID:Africa/Johannesburg",
        "X-LIC-LOCATION:Africa/Johannesburg",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0200",
        "TZOFFSETTO:+0200",
        "TZNAME:SAST",
        "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VEVENT",
        "UID:trentox-study-reminder@trentox-tutor-ai",
        "SEQUENCE:0",
        "DTSTAMP:" + dtstamp,
        "DTSTART;TZID=Africa/Johannesburg:" + start.strftime("%Y%m%dT%H%M%S"),
        "DTEND;TZID=Africa/Johannesburg:" + end.strftime("%Y%m%dT%H%M%S"),
        "SUMMARY:Trentox Tutor AI study session",
        "DESCRIPTION:" + _escape_ics(
            "A planned 20-minute study block. Open Trentox Tutor AI, choose one topic, then complete its topic check."
        ),
        rule,
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "TRIGGER:PT0S",
        "DESCRIPTION:Your Trentox study session is starting.",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"


def open_exam_calendar_workspace():
    """Select the exam calendar nested tab from a sidebar or home shortcut."""
    st.session_state["learning_workspace"] = "🤖 Tutor & lab"
    st.session_state["tutor_section"] = "📅 Exam calendar"


def _save_study_reminder(study_time, repeat):
    st.session_state["study_reminder"] = {
        "time": study_time.strftime("%H:%M"),
        "repeat": repeat,
        "enabled": True,
    }
    st.session_state["study_reminder_last_sent"] = ""
    st.session_state["study_reminder_pending"] = False


def render_study_reminders():
    """Render session-based in-app alerts, calendar download, and exam-calendar shortcut."""
    saved = st.session_state.get("study_reminder", {})
    default_time = time.fromisoformat(saved.get("time", "18:00"))
    default_repeat = saved.get("repeat", "Every day")

    with st.expander("🔔 Study reminders", expanded=False):
        st.caption(
            "The in-app alert appears while this app is open. Download the calendar event "
            "and open it from your browser's Downloads to keep reminders after closing the app."
        )
        study_time = st.time_input(
            "Reminder time (South African time)",
            value=default_time,
            key="study_reminder_time",
        )
        repeat = st.selectbox(
            "Repeat",
            options=["Every day", "Weekdays"],
            index=1 if default_repeat == "Weekdays" else 0,
            key="study_reminder_repeat",
        )
        if st.button(
            "Save & enable in-app reminder",
            key="save_study_reminder",
            use_container_width=True,
            type="primary",
        ):
            _save_study_reminder(study_time, repeat)
            saved = st.session_state["study_reminder"]
            st.success(
                "Reminder set for " + saved["time"] + " (" + saved["repeat"].lower() + ")."
            )

        saved = st.session_state.get("study_reminder", {})
        if saved.get("enabled"):
            if st.button(
                "Turn off in-app reminder",
                key="disable_study_reminder",
                use_container_width=True,
            ):
                saved["enabled"] = False
                st.session_state["study_reminder"] = saved
                st.session_state["study_reminder_pending"] = False
                st.success("In-app study reminder turned off.")

        st.download_button(
            "📆 Download recurring study reminder (.ics)",
            data=build_study_calendar_ics(study_time, repeat),
            file_name="trentox-study-reminder.ics",
            mime="text/calendar",
            help="Open the downloaded file and add it to Google Calendar, Outlook, Apple Calendar, or Windows Calendar.",
            use_container_width=True,
            key="download_study_reminder_calendar",
        )
        st.caption("The calendar copy continues after the app closes. Remove the old calendar event if you change its time.")

    st.button(
        "📅 Open exam calendar",
        key="open_exam_calendar_sidebar",
        on_click=open_exam_calendar_workspace,
        use_container_width=True,
    )

    current = st.session_state.get("study_reminder", {})
    interval = "30s" if current.get("enabled") else None

    @st.fragment(run_every=interval)
    def _check_study_reminder():
        config = st.session_state.get("study_reminder", {})
        if not config.get("enabled"):
            return
        now = datetime.now(SOUTH_AFRICA)
        today = now.date().isoformat()
        target = time.fromisoformat(config.get("time", "18:00"))
        due = (now.hour * 60 + now.minute) >= (target.hour * 60 + target.minute)
        weekday_ok = config.get("repeat") != "Weekdays" or now.weekday() < 5
        if due and weekday_ok and st.session_state.get("study_reminder_last_sent") != today:
            st.session_state["study_reminder_last_sent"] = today
            st.session_state["study_reminder_pending"] = True
            st.toast("Time for a focused study block.", icon="🔔")

        if st.session_state.get("study_reminder_pending"):
            st.sidebar.info("🔔 Your study reminder is due. Choose one topic and complete its short check.")
            if st.sidebar.button("Dismiss study reminder", key="dismiss_study_reminder_notice"):
                st.session_state["study_reminder_pending"] = False

    _check_study_reminder()
