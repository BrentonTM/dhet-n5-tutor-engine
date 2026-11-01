"""Device-local first-use guide and study reminders for the Streamlit app."""

import streamlit as st


_DEVICE_SUPPORT_HTML = r"""
<style>
#trentox-device-support {
  color: #dceaf3;
  font: 0.86rem/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
  margin: .15rem 0 .85rem;
}
#trentox-device-support details {
  border: 1px solid rgba(111, 173, 197, .3);
  border-radius: 12px;
  background: linear-gradient(145deg, rgba(17, 42, 59, .96), rgba(8, 23, 35, .98));
  overflow: hidden;
}
#trentox-device-support summary {
  cursor: pointer;
  padding: .72rem .8rem;
  color: #f0c96c;
  font-weight: 700;
  list-style-position: inside;
}
#trentox-device-support .tx-reminder-body {
  padding: .1rem .8rem .8rem;
}
#trentox-device-support label {
  display: block;
  margin: .55rem 0 .25rem;
  color: #bdd0dc;
  font-size: .78rem;
}
#trentox-device-support input,
#trentox-device-support select {
  box-sizing: border-box;
  width: 100%;
  min-height: 2.35rem;
  border: 1px solid #345568;
  border-radius: 8px;
  background: #0c1b27;
  color: #edf6fa;
  padding: .4rem .55rem;
  font: inherit;
}
#trentox-device-support button {
  width: 100%;
  min-height: 2.35rem;
  margin-top: .55rem;
  border: 1px solid #317c88;
  border-radius: 8px;
  background: #123545;
  color: #effcff;
  cursor: pointer;
  font: inherit;
  font-weight: 650;
}
#trentox-device-support button:hover {
  border-color: #4bd3dc;
  background: #174656;
}
#trentox-device-support #tx-reminder-calendar {
  border-color: #8e702d;
  background: #302919;
}
#trentox-device-support #tx-reminder-off {
  border-color: #70484d;
  background: #352328;
}
#trentox-device-support .tx-device-note,
#trentox-device-support #tx-reminder-status {
  display: block;
  margin: .55rem 0 0;
  color: #a9beca;
  font-size: .73rem;
}
#trentox-device-guide {
  position: fixed;
  inset: 0;
  z-index: 2147483000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(2, 8, 13, .78);
  backdrop-filter: blur(7px);
}
#trentox-device-guide.tx-open { display: flex; }
#trentox-device-guide .tx-guide-card {
  box-sizing: border-box;
  width: min(560px, 100%);
  border: 1px solid rgba(93, 207, 221, .48);
  border-radius: 20px;
  padding: clamp(1.15rem, 4vw, 2rem);
  background:
    radial-gradient(circle at 94% 2%, rgba(36, 147, 163, .20), transparent 34%),
    linear-gradient(145deg, #102637, #08131d 70%);
  color: #eaf4f8;
  box-shadow: 0 24px 90px rgba(0,0,0,.55);
  font: 1rem/1.55 system-ui, -apple-system, "Segoe UI", sans-serif;
}
#trentox-device-guide .tx-guide-brand {
  color: #f0c96c;
  font-size: .76rem;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
}
#trentox-device-guide .tx-guide-step {
  margin-top: 1rem;
  color: #58dce8;
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
}
#trentox-device-guide h2 {
  margin: .45rem 0 .6rem;
  color: #fff;
  font-size: clamp(1.45rem, 4vw, 2rem);
  line-height: 1.18;
}
#trentox-device-guide p { margin: .5rem 0; color: #c3d6e0; }
#trentox-device-guide .tx-guide-tip {
  margin-top: 1rem;
  border-left: 3px solid #f0b85d;
  border-radius: 0 8px 8px 0;
  padding: .65rem .8rem;
  background: rgba(245, 184, 93, .09);
  color: #f1dfba;
  font-size: .88rem;
}
#trentox-device-guide .tx-guide-progress {
  height: 5px;
  margin: 1.25rem 0 .35rem;
  border-radius: 8px;
  background: #203949;
  overflow: hidden;
}
#trentox-device-guide .tx-guide-progress span {
  display: block;
  width: 25%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #49d6e2, #f0bd5e);
  transition: width .2s ease;
}
#trentox-device-guide .tx-guide-count {
  color: #91aebb;
  font-size: .77rem;
}
#trentox-device-guide .tx-guide-actions {
  display: flex;
  gap: .6rem;
  align-items: center;
  margin-top: 1.1rem;
}
#trentox-device-guide button {
  min-height: 2.65rem;
  border: 1px solid #426173;
  border-radius: 9px;
  padding: .55rem .9rem;
  background: #102a3a;
  color: #eaf4f8;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}
#trentox-device-guide button:focus-visible,
#trentox-device-support button:focus-visible,
#trentox-device-support input:focus-visible,
#trentox-device-support select:focus-visible {
  outline: 3px solid #5ce0e8;
  outline-offset: 2px;
}
#trentox-device-guide #tx-guide-next {
  margin-left: auto;
  border-color: #32aeb8;
  background: linear-gradient(110deg, #106779, #187985);
}
@media (max-width: 540px) {
  #trentox-device-guide { padding: .65rem; }
  #trentox-device-guide .tx-guide-card { border-radius: 15px; }
  #trentox-device-guide .tx-guide-actions { flex-wrap: wrap; }
}
@media (prefers-reduced-motion: reduce) {
  #trentox-device-guide .tx-guide-progress span { transition: none; }
}
</style>

<div id="trentox-device-support">
  <details id="tx-reminder-details">
    <summary>🔔 Study reminders</summary>
    <div class="tx-reminder-body">
      <label for="tx-reminder-time">Reminder time (this device)</label>
      <input id="tx-reminder-time" type="time" value="18:00" aria-label="Study reminder time">
      <label for="tx-reminder-frequency">Repeat</label>
      <select id="tx-reminder-frequency" aria-label="Study reminder frequency">
        <option value="daily">Every day</option>
        <option value="weekdays">Weekdays</option>
      </select>
      <button id="tx-reminder-enable" type="button">Save &amp; enable browser reminder</button>
      <button id="tx-reminder-off" type="button" hidden>Turn browser reminder off</button>
      <button id="tx-reminder-calendar" type="button">Add recurring reminder to calendar (.ics)</button>
      <p id="tx-reminder-status" role="status" aria-live="polite">Choose a time and save the reminder on this device.</p>
      <small class="tx-device-note">Browser notifications need your permission and this app open. The calendar file can remind you after you close the app. Settings stay in this browser on this device.</small>
      <button id="tx-guide-replay" type="button">📘 Replay the app guide</button>
    </div>
  </details>
</div>

<script>
(function () {
  "use strict";

  const reminderKey = "trentox_study_reminder_v1";
  const tourKey = "trentox_first_use_guide_v1";
  const tourDismissKey = "trentox_first_use_guide_dismissed_session";
  const timeInput = document.getElementById("tx-reminder-time");
  const frequencyInput = document.getElementById("tx-reminder-frequency");
  const enableButton = document.getElementById("tx-reminder-enable");
  const offButton = document.getElementById("tx-reminder-off");
  const calendarButton = document.getElementById("tx-reminder-calendar");
  const statusLine = document.getElementById("tx-reminder-status");
  const replayButton = document.getElementById("tx-guide-replay");

  if (!timeInput || !frequencyInput || !enableButton || !offButton || !calendarButton || !statusLine || !replayButton) {
    return;
  }

  function readStore(key, fallback) {
    try {
      const value = window.localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function writeStore(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      return false;
    }
  }

  let reminder = readStore(reminderKey, { time: "18:00", frequency: "daily", enabled: false, lastSent: "" });
  if (!reminder || typeof reminder !== "object") {
    reminder = { time: "18:00", frequency: "daily", enabled: false, lastSent: "" };
  }
  timeInput.value = typeof reminder.time === "string" ? reminder.time : "18:00";
  frequencyInput.value = reminder.frequency === "weekdays" ? "weekdays" : "daily";

  function notificationSupported() {
    return typeof window.Notification !== "undefined" && window.isSecureContext;
  }

  function updateReminderUI(message) {
    const active = Boolean(reminder.enabled && notificationSupported() && Notification.permission === "granted");
    offButton.hidden = !active;
    enableButton.textContent = active ? "Save reminder settings" : "Save & enable browser reminder";
    if (message) {
      statusLine.textContent = message;
    } else if (!notificationSupported()) {
      statusLine.textContent = "Browser notifications are unavailable here. You can still add the recurring calendar reminder.";
    } else if (reminder.enabled && Notification.permission === "granted") {
      statusLine.textContent = "Reminder saved for " + reminder.time + " (" +
        (reminder.frequency === "weekdays" ? "weekdays" : "every day") +
        "). It will appear while this app is open.";
    } else if (Notification.permission === "denied") {
      statusLine.textContent = "Notifications are blocked for this site. Allow them in browser settings, or use the calendar reminder.";
    } else {
      statusLine.textContent = "Choose a time and save the reminder on this device.";
    }
  }

  enableButton.addEventListener("click", async function () {
    const chosenTime = timeInput.value || "18:00";
    const chosenFrequency = frequencyInput.value === "weekdays" ? "weekdays" : "daily";
    if (!notificationSupported()) {
      reminder = { time: chosenTime, frequency: chosenFrequency, enabled: false, lastSent: reminder.lastSent || "" };
      writeStore(reminderKey, reminder);
      updateReminderUI("Browser notifications are unavailable here. Use the calendar reminder for alerts when the app is closed.");
      return;
    }

    let permission = Notification.permission;
    if (permission === "default") {
      try {
        permission = await Notification.requestPermission();
      } catch (error) {
        permission = "denied";
      }
    }

    if (permission === "granted") {
      reminder = { time: chosenTime, frequency: chosenFrequency, enabled: true, lastSent: reminder.lastSent || "" };
      const saved = writeStore(reminderKey, reminder);
      updateReminderUI(saved
        ? "Reminder enabled for " + chosenTime + ". It will notify you while this app is open."
        : "Browser storage is unavailable. Keep this tab open and use the calendar reminder as a backup.");
      checkReminder();
    } else {
      reminder = { time: chosenTime, frequency: chosenFrequency, enabled: false, lastSent: reminder.lastSent || "" };
      writeStore(reminderKey, reminder);
      updateReminderUI(permission === "denied"
        ? "Permission was not granted. Allow notifications in browser settings or add the calendar reminder."
        : "Notification permission was not completed. You can try again or add the calendar reminder.");
    }
  });

  offButton.addEventListener("click", function () {
    reminder = {
      time: timeInput.value || reminder.time || "18:00",
      frequency: frequencyInput.value === "weekdays" ? "weekdays" : "daily",
      enabled: false,
      lastSent: reminder.lastSent || ""
    };
    writeStore(reminderKey, reminder);
    updateReminderUI("Browser reminder turned off. Any calendar reminder you imported must be removed from your calendar separately.");
  });

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function localDateKey(date) {
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate());
  }

  function checkReminder() {
    reminder = readStore(reminderKey, reminder);
    if (!reminder || !reminder.enabled || !notificationSupported() || Notification.permission !== "granted") {
      return;
    }
    const now = new Date();
    const currentTime = pad(now.getHours()) + ":" + pad(now.getMinutes());
    const today = localDateKey(now);
    if (currentTime !== reminder.time || reminder.lastSent === today) {
      return;
    }
    if (reminder.frequency === "weekdays" && (now.getDay() === 0 || now.getDay() === 6)) {
      return;
    }

    reminder.lastSent = today;
    writeStore(reminderKey, reminder);
    try {
      const notice = new Notification("Trentox Tutor AI · Study time", {
        body: "Take a focused study block, then check one topic from your course.",
        tag: "trentox-study-" + today,
        renotify: false
      });
      notice.onclick = function () {
        window.focus();
        notice.close();
      };
    } catch (error) {
      updateReminderUI("The browser could not show this notification. Use the recurring calendar reminder instead.");
    }
  }

  if (window.__trentoxReminderTimer) {
    window.clearInterval(window.__trentoxReminderTimer);
  }
  updateReminderUI();
  checkReminder();
  window.__trentoxReminderTimer = window.setInterval(checkReminder, 15000);

  function escapeIcs(value) {
    return String(value).replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
  }

  function buildStudyCalendar() {
    const timeText = timeInput.value || "18:00";
    const parts = timeText.split(":");
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(),
      Number(parts[0]) || 18, Number(parts[1]) || 0, 0, 0);
    while (start.getTime() <= now.getTime() ||
      (frequencyInput.value === "weekdays" && (start.getDay() === 0 || start.getDay() === 6))) {
      start.setDate(start.getDate() + 1);
    }
    const end = new Date(start.getTime() + 20 * 60 * 1000);
    function stamp(date) {
      return date.getFullYear() + pad(date.getMonth() + 1) + pad(date.getDate()) + "T" +
        pad(date.getHours()) + pad(date.getMinutes()) + pad(date.getSeconds());
    }
    const nowUtc = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
    const rule = frequencyInput.value === "weekdays"
      ? "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"
      : "RRULE:FREQ=DAILY";
    const lines = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Trentox Tutor AI//Study Reminders//EN",
      "CALSCALE:GREGORIAN",
      "X-WR-CALNAME:Trentox Tutor AI Study Reminders",
      "BEGIN:VEVENT",
      "UID:" + Date.now() + "@trentox-tutor-ai",
      "DTSTAMP:" + nowUtc,
      "DTSTART:" + stamp(start),
      "DTEND:" + stamp(end),
      "SUMMARY:Trentox Tutor AI study session",
      "DESCRIPTION:" + escapeIcs("A planned 20-minute study block. Open Trentox Tutor AI, choose one topic, then complete its topic check."),
      rule,
      "BEGIN:VALARM",
      "ACTION:DISPLAY",
      "TRIGGER:PT0S",
      "DESCRIPTION:Your Trentox study session is starting.",
      "END:VALARM",
      "END:VEVENT",
      "END:VCALENDAR"
    ];
    return lines.join("\r\n") + "\r\n";
  }

  calendarButton.addEventListener("click", function () {
    try {
      const file = new Blob([buildStudyCalendar()], { type: "text/calendar;charset=utf-8" });
      const url = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = url;
      link.download = "trentox-study-reminder.ics";
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      updateReminderUI("Calendar file downloaded for " + (timeInput.value || "18:00") +
        ". Open it and save the recurring reminder in your device calendar.");
    } catch (error) {
      updateReminderUI("The calendar file could not be created in this browser. Try a supported desktop browser.");
    }
  });

  const steps = [
    {
      label: "1 · SET YOUR STUDY PATH",
      title: "Choose what you are learning",
      body: "Use Study path in the sidebar to select your programme, N-level and subject. The lessons, practice and examples then follow that selection.",
      tip: "You can change the course selection whenever you need."
    },
    {
      label: "2 · LEARN IN SHORT CYCLES",
      title: "Study one topic, then check it",
      body: "Open Lessons in Tutor & lab. Choose a comfortable focus block, work through the explanation and example, then answer the short topic quiz.",
      tip: "Missed concepts feed your progress view and review reminders."
    },
    {
      label: "3 · MAKE THE THEORY VISIBLE",
      title: "Explore the 3D engineering lab",
      body: "Open 3D lab to rotate and inspect a model or practise a circuit. Follow the on-screen operating tips and use the controls beside each model.",
      tip: "Drag to rotate and scroll to zoom where the model supports it."
    },
    {
      label: "4 · PRACTISE AND RETURN",
      title: "Ask, practise and review",
      body: "Use Quick AI tutor for Socratic hints, upload worked answers for feedback, and try Exam practice. Progress shows topics to revisit.",
      tip: "Set a study reminder in the sidebar; export a calendar reminder if you want alerts when the app is closed."
    }
  ];

  let tourOverlay = document.getElementById("trentox-device-guide");
  if (tourOverlay) {
    tourOverlay.remove();
  }
  tourOverlay = document.createElement("div");
  tourOverlay.id = "trentox-device-guide";
  tourOverlay.innerHTML =
    '<section class="tx-guide-card" role="dialog" aria-modal="true" aria-labelledby="tx-guide-title" aria-describedby="tx-guide-body">' +
      '<div class="tx-guide-brand">Trentox Tutor AI · First-use guide</div>' +
      '<div id="tx-guide-step" class="tx-guide-step"></div>' +
      '<h2 id="tx-guide-title"></h2>' +
      '<p id="tx-guide-body"></p>' +
      '<div id="tx-guide-tip" class="tx-guide-tip"></div>' +
      '<div class="tx-guide-progress" aria-hidden="true"><span id="tx-guide-bar"></span></div>' +
      '<div id="tx-guide-count" class="tx-guide-count" aria-live="polite"></div>' +
      '<div class="tx-guide-actions">' +
        '<button id="tx-guide-later" type="button">Not now</button>' +
        '<button id="tx-guide-back" type="button">Back</button>' +
        '<button id="tx-guide-next" type="button">Next</button>' +
      '</div>' +
    '</section>';
  document.body.appendChild(tourOverlay);

  let tourState = readStore(tourKey, { done: false, step: 0 });
  if (!tourState || typeof tourState !== "object") {
    tourState = { done: false, step: 0 };
  }
  let tourStep = Math.min(Math.max(Number(tourState.step) || 0, 0), steps.length - 1);

  function updateTour() {
    const step = steps[tourStep];
    document.getElementById("tx-guide-step").textContent = step.label;
    document.getElementById("tx-guide-title").textContent = step.title;
    document.getElementById("tx-guide-body").textContent = step.body;
    document.getElementById("tx-guide-tip").textContent = step.tip;
    document.getElementById("tx-guide-count").textContent = "Step " + (tourStep + 1) + " of " + steps.length;
    document.getElementById("tx-guide-bar").style.width = (((tourStep + 1) / steps.length) * 100) + "%";
    document.getElementById("tx-guide-back").disabled = tourStep === 0;
    document.getElementById("tx-guide-next").textContent = tourStep === steps.length - 1 ? "Finish guide" : "Next";
    writeStore(tourKey, { done: false, step: tourStep });
  }

  function closeTourForNow() {
    tourOverlay.classList.remove("tx-open");
    try {
      window.sessionStorage.setItem(tourDismissKey, "1");
    } catch (error) {
      /* The replay button remains available even when session storage is blocked. */
    }
  }

  function finishTour() {
    writeStore(tourKey, { done: true, step: 0 });
    tourOverlay.classList.remove("tx-open");
  }

  function openTour(replay) {
    if (replay) {
      tourStep = 0;
      writeStore(tourKey, { done: false, step: 0 });
    } else {
      const saved = readStore(tourKey, { done: false, step: 0 });
      tourStep = Math.min(Math.max(Number(saved.step) || 0, 0), steps.length - 1);
    }
    updateTour();
    tourOverlay.classList.add("tx-open");
    window.setTimeout(function () { document.getElementById("tx-guide-next").focus(); }, 0);
  }

  document.getElementById("tx-guide-back").addEventListener("click", function () {
    if (tourStep > 0) {
      tourStep -= 1;
      updateTour();
    }
  });
  document.getElementById("tx-guide-next").addEventListener("click", function () {
    if (tourStep < steps.length - 1) {
      tourStep += 1;
      updateTour();
    } else {
      finishTour();
    }
  });
  document.getElementById("tx-guide-later").addEventListener("click", closeTourForNow);
  replayButton.addEventListener("click", function () { openTour(true); });

  updateReminderUI();
  let dismissed = false;
  try {
    dismissed = window.sessionStorage.getItem(tourDismissKey) === "1";
  } catch (error) {
    dismissed = false;
  }
  if (!tourState.done && !dismissed) {
    openTour(false);
  }
})();
</script>
"""


def render_device_guide_and_reminders():
    """Render a device-local guide and notification/calendar reminder controls."""
    st.html(_DEVICE_SUPPORT_HTML, unsafe_allow_javascript=True)
