"""Trentox's responsive, code-native engineering wordmark."""

import streamlit as st


WORDMARK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 396 86"
     role="img" aria-label="Trentox Tutor AI">
  <defs>
    <linearGradient id="trentox-metal" x1="0" y1="0" x2="0.8" y2="1">
      <stop offset="0" stop-color="#e6edf8"/>
      <stop offset=".34" stop-color="#83e9ef"/>
      <stop offset=".7" stop-color="#43d3e5"/>
      <stop offset="1" stop-color="#32d6c3"/>
    </linearGradient>
    <linearGradient id="trentox-circuit" x1="0" x2="1">
      <stop stop-color="#43d3e5"/>
      <stop offset="1" stop-color="#6fddb2"/>
    </linearGradient>
  </defs>
  <g aria-hidden="true">
    <path d="M29 10 50 22V46L29 58 8 46V22Z" fill="#121d31"
          stroke="url(#trentox-circuit)" stroke-width="1.6"/>
    <path d="M29 15 45 24V43L29 52 13 43V24Z" fill="none"
          stroke="#32d6c3" stroke-opacity=".22"/>
    <path d="M18 25H40V31H32V44H26V31H18Z" fill="url(#trentox-metal)"/>
    <path d="M0 29H8M0 38H8M50 29H58M50 38H58M29 2V10M29 58V66"
          fill="none" stroke="#43d3e5" stroke-opacity=".65" stroke-width="1.4"/>
    <g fill="#6fddb2">
      <circle cx="1" cy="29" r="1.6"/><circle cx="57" cy="38" r="1.6"/>
      <circle cx="29" cy="2" r="1.6"/><circle cx="29" cy="66" r="1.6"/>
    </g>
    <!-- Angular letterforms stay sharp without a downloaded font. -->
    <g transform="translate(72 12) skewX(-8)" fill="url(#trentox-metal)" fill-rule="evenodd">
      <path d="M0 0H35V8H23V40H12V8H0Z"/>
      <path transform="translate(44)" d="M0 0H27L35 8V19L27 27H23L37 40H23L10 27V40H0ZM10 8V19H23L25 17V10L23 8Z"/>
      <path transform="translate(88)" d="M0 0H34V8H10V16H28V24H10V32H34V40H0Z"/>
      <path transform="translate(132)" d="M0 40V0H10L27 23V0H37V40H27L10 17V40Z"/>
      <path transform="translate(178)" d="M0 0H35V8H23V40H12V8H0Z"/>
      <path transform="translate(222)" d="M8 0H29L37 8V32L29 40H8L0 32V8ZM11 9 9 11V29L11 31H26L28 29V11L26 9Z"/>
      <path transform="translate(267)" d="M0 0H12L20 12L28 0H40L26 20L40 40H28L20 28L12 40H0L14 20Z"/>
    </g>
    <path d="M70 61H132L137 57H339L344 61H376" fill="none"
          stroke="url(#trentox-circuit)" stroke-width="1.2" stroke-opacity=".65"/>
    <path d="M70 61H91" stroke="#6fddb2" stroke-width="2.5"/>
    <circle cx="378" cy="61" r="2" fill="#6fddb2"/>
    <text x="71" y="77" fill="#a0b4c2" font-size="9" font-weight="600"
          font-family="'Cascadia Code', Consolas, monospace" letter-spacing="4.4">TUTOR AI</text>
  </g>
</svg>
"""


def render_wordmark():
    """Show a crisp wordmark that shrinks natively to fit narrow screens."""
    st.image(WORDMARK_SVG.strip(), width=380, alt="Trentox Tutor AI")
