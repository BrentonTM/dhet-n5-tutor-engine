"""Bounded Gemini requests with actionable, credential-free failure messages."""

import logging
import random
import time

logger = logging.getLogger(__name__)
DEFAULT_MODELS = ("gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite")


def configured_models(primary="", fallbacks=""):
    names = [str(primary or "").strip()]
    names += str(fallbacks or "").split(",") if fallbacks else list(DEFAULT_MODELS)
    return tuple(dict.fromkeys(name.strip() for name in names if name.strip()))


def classify_error(exc):
    """Use SDK status codes; inspect messages only for classification, never echo them."""
    code = getattr(exc, "code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = None
    text = str(exc).upper()
    if code == 401 or any(s in text for s in ("API_KEY_INVALID", "API KEY NOT VALID", "API_KEY_EXPIRED")):
        return "key"
    if code == 403 or "PERMISSION_DENIED" in text:
        return "permission"
    if code == 429 or "RESOURCE_EXHAUSTED" in text:
        return "quota"
    if code == 404 or "NOT_FOUND" in text:
        return "model"
    if code in (408, 500, 502, 503, 504) or any(s in text for s in ("UNAVAILABLE", "TIMEOUT", "TIMED OUT")):
        return "service"
    if code == 400:
        return "request"
    return "unknown"


ERROR_MESSAGES = {
    "key": "Google rejected the Gemini API key. The app owner needs to replace the key in Streamlit Cloud Settings → Secrets, then restart the app.",
    "permission": "Google denied this project's access to Gemini (403). The app owner needs to check the key's API restrictions, project eligibility and billing in Google AI Studio.",
    "quota": "Google Gemini's quota or rate limit was reached (429). Wait before trying again. If it persists, the app owner needs to check the project's quota and billing in Google AI Studio.",
    "model": "The configured Gemini models are unavailable to this project (404). The app owner can set GEMINI_MODEL in Streamlit Secrets to a model available in Google AI Studio.",
    "service": "Google Gemini did not respond after limited retries. Please try again shortly; your work is still here.",
    "request": "Google could not accept this request (400). Try a shorter message or smaller upload. If it persists, the app owner needs to check the deployment's Gemini configuration.",
    "empty": "Gemini returned no answer. Try rephrasing your question or providing a clearer upload.",
    "unknown": "ASK TX could not reach Gemini. Please try again. If it persists, the app owner needs to check the app's cloud logs.",
}


def generate_reply(contents, *, api_key, client_factory, models=DEFAULT_MODELS, sleep=time.sleep, system_instruction=None):
    if not api_key:
        return None, "ASK TX needs a Gemini API key in Streamlit Cloud Settings → Secrets (GEMINI_API_KEY or GOOGLE_API_KEY)."
    client = None
    failures = []
    try:
        client = client_factory(
            api_key=api_key,
            http_options={"timeout": 20000, "retry_options": {"attempts": 1}},
        )
        for model in models:
            for attempt in range(2):
                try:
                    options = {"model": model, "contents": contents}
                    if system_instruction:
                        options["config"] = {"system_instruction": system_instruction}
                    response = client.models.generate_content(**options)
                    text = response.text if response else None
                    if text and text.strip():
                        return text, None
                    failures.append("empty")
                    break
                except Exception as exc:
                    category = classify_error(exc)
                    failures.append(category)
                    logger.warning("Gemini request failed: model=%s category=%s", model, category)
                    if category in ("key", "permission", "request"):
                        return None, ERROR_MESSAGES[category]
                    if category in ("quota", "service") and attempt == 0:
                        sleep(1 + random.uniform(0, 0.25))
                        continue
                    break
    except Exception as exc:
        failures.append(classify_error(exc))
        logger.warning("Gemini client failed: category=%s", failures[-1])
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
    # A missing fallback model must not obscure a real quota/service failure.
    priority = ("key", "permission", "quota", "service", "request", "empty", "model", "unknown")
    category = next((kind for kind in priority if kind in failures), "unknown")
    return None, ERROR_MESSAGES[category]
