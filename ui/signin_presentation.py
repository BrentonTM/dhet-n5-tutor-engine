"""Presentation for the signed-out native Streamlit entry screen only."""

import base64
from functools import lru_cache
from pathlib import Path


WORDMARK_HTML = '<div class="trentox-entry-wordmark" aria-label="Trentox Tutor AI"><span>TRENTOX</span> TUTOR AI</div>'
_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "signin"


@lru_cache(maxsize=1)
def signin_css():
    """Embed the packaged background without an external image dependency."""
    image = base64.b64encode((_ASSETS / "engineering-background.png").read_bytes()).decode("ascii")
    css = (_ASSETS / "entry.css").read_text(encoding="utf-8")
    return "<style>" + css.replace("__BACKGROUND_IMAGE__", "data:image/png;base64," + image) + "</style>"
