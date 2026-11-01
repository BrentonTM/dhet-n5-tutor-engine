import streamlit as st


def inject_industrial_theme():
    """Apply the Trentox engineering-lab design system and display controls."""
    with st.sidebar.expander("Display & 3D settings", expanded=False):
        st.caption("Adjust the visual load for your device.")
        fx_mode = st.selectbox(
            "3D scene quality",
            [
                "High — full interactive scenes",
                "Low — lighter visual mode",
                "Off — static view",
            ],
            index=0,
            help="Choose a lighter mode if 3D scenes feel slow on this device.",
        )
        st.session_state["fx_mode"] = fx_mode.split(" ")[0].lower()

    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --tx-bg: #08131e;
            --tx-panel: #0d1d2b;
            --tx-panel-raised: #122638;
            --tx-line: rgba(135, 170, 194, .18);
            --tx-text: #edf5fa;
            --tx-muted: #a0b4c2;
            --tx-cyan: #43d3e5;
            --tx-orange: #ffad5b;
            --tx-green: #6fddb2;
        }

        .stApp {
            background:
                radial-gradient(ellipse at 78% 0%, rgba(25, 112, 145, .18), transparent 42%),
                radial-gradient(ellipse at 5% 28%, rgba(209, 112, 48, .08), transparent 34%),
                var(--tx-bg);
            color: var(--tx-text);
        }
        [data-testid="stAppViewContainer"] > .main { background: transparent; }
        [data-testid="stMainBlockContainer"] {
            max-width: 1540px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }
        [data-testid="stHeader"] { background: rgba(8, 19, 30, .78); }
        [data-testid="stIFrame"] {
            border: 1px solid var(--tx-line);
            border-radius: 14px;
            background: #091724;
            box-shadow: 0 14px 34px rgba(0, 0, 0, .24);
            overflow: hidden;
        }

        h1, h2, h3, h4 {
            color: var(--tx-text) !important;
            font-family: "Segoe UI", Inter, system-ui, sans-serif !important;
            letter-spacing: -.025em !important;
            text-shadow: none !important;
        }
        h1 { font-size: clamp(2rem, 4vw, 3.1rem) !important; font-weight: 750 !important; }
        h2 { font-size: clamp(1.45rem, 2.4vw, 2rem) !important; font-weight: 700 !important; }
        p, label, [data-testid="stCaptionContainer"] { color: var(--tx-muted); }
        code, pre, .stCodeBlock { font-family: "Cascadia Code", Consolas, monospace !important; }

        [data-testid="stSidebar"] {
            background: #091724;
            border-right: 1px solid var(--tx-line);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            letter-spacing: -.02em !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid var(--tx-line);
            border-radius: 12px;
            background: rgba(18, 38, 56, .45);
        }

        [data-testid="stTabs"] [role="tablist"] {
            display: flex;
            gap: .4rem;
            overflow-x: auto;
            padding: .38rem .35rem;
            border: 1px solid var(--tx-line);
            border-radius: 13px;
            background: rgba(10, 25, 38, .92);
            scrollbar-width: thin;
        }
        [data-testid="stTabs"] [role="tab"] {
            flex: 0 0 auto;
            min-height: 42px;
            padding: .55rem .85rem;
            border: 1px solid transparent;
            border-radius: 9px;
            color: var(--tx-muted);
            font-size: .9rem;
            font-weight: 650;
            white-space: nowrap;
            transition: background .16s ease, color .16s ease, border-color .16s ease;
        }
        [data-testid="stTabs"] [role="tab"]:hover {
            color: var(--tx-text);
            background: rgba(67, 211, 229, .08);
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            color: #e8fbff !important;
            background: rgba(34, 156, 181, .22) !important;
            border-color: rgba(67, 211, 229, .42) !important;
            box-shadow: inset 0 -2px 0 var(--tx-cyan);
        }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }
        [data-testid="stTabs"] [role="tabpanel"] { padding-top: 1.1rem; }

        [data-testid="stMetric"] {
            min-height: 112px;
            padding: 1rem 1.1rem;
            border: 1px solid var(--tx-line);
            border-radius: 14px;
            background: linear-gradient(145deg, rgba(18, 38, 56, .96), rgba(11, 27, 41, .96));
            box-shadow: 0 12px 28px rgba(0, 0, 0, .18);
        }
        [data-testid="stMetricLabel"] { color: var(--tx-muted); }
        [data-testid="stMetricValue"] { color: var(--tx-text); font-weight: 720; }

        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            border-color: var(--tx-line);
            border-radius: 10px;
            background: #0c1d2b;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
            border-color: var(--tx-cyan);
            box-shadow: 0 0 0 1px rgba(67, 211, 229, .28);
        }
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button {
            min-height: 42px;
            border: 1px solid rgba(67, 211, 229, .32);
            border-radius: 10px;
            color: var(--tx-text);
            background: linear-gradient(135deg, rgba(19, 117, 143, .92), rgba(17, 72, 96, .96));
            font-weight: 650;
            box-shadow: 0 5px 16px rgba(0, 0, 0, .16);
            transition: border-color .16s ease, transform .16s ease, filter .16s ease;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {
            border-color: var(--tx-cyan);
            filter: brightness(1.12);
            transform: translateY(-1px);
        }
        [data-testid="stExpander"] {
            border-color: var(--tx-line);
            border-radius: 12px;
            background: rgba(13, 29, 43, .72);
        }
        [data-testid="stAlert"] { border-radius: 12px; }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--tx-line);
            border-radius: 12px;
            overflow: hidden;
        }
        hr { border-color: var(--tx-line); }

        .tx-eyebrow {
            margin: 0 0 .45rem;
            color: var(--tx-cyan);
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .15em;
            text-transform: uppercase;
        }
        .tx-brand-title {
            margin: .12rem 0 .45rem;
            color: #f3f8fb;
            font-size: clamp(2.55rem, 5vw, 4rem);
            font-weight: 850;
            letter-spacing: -.06em;
            line-height: 1.04;
            text-shadow: 0 1px 0 #b5c5cf, 0 2px 0 #788c99, 0 4px 0 #405461, 0 9px 22px rgba(0, 0, 0, .58);
            transform: perspective(900px) rotateX(2deg);
        }
        .tx-brand-title strong {
            color: #62d8e7;
            font-weight: 850;
            text-shadow: 0 1px 0 #2398a8, 0 3px 0 #176171, 0 8px 18px rgba(0, 0, 0, .55);
        }
        .tx-brand-subtitle {
            max-width: 54rem;
            margin: 0 0 1rem;
            color: var(--tx-muted);
            font-size: 1.04rem;
            line-height: 1.6;
        }
        .tx-monogram {
            position: fixed;
            right: 22px;
            bottom: 82px;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .02em;
            width: 132px;
            height: 86px;
            perspective: 520px;
            transform-style: preserve-3d;
            filter: drop-shadow(0 10px 11px rgba(0, 0, 0, .62));
            animation: tx-monogram-rotate 7s ease-in-out infinite;
            pointer-events: none;
        }
        .tx-monogram svg {
            width: 132px;
            height: 90px;
            overflow: visible;
            transform: translateZ(12px) rotateX(4deg) rotateY(-7deg);
            transform-style: preserve-3d;
        }
        .tx-extrusion text {
            fill: #67470d;
            stroke: #3d2b0b;
            stroke-width: 1.4;
            stroke-linejoin: round;
            font-family: "Arial Black", "Segoe UI Black", sans-serif;
            font-size: 82px;
            font-weight: 900;
            letter-spacing: -5px;
        }
        .tx-face-t,
        .tx-face-x {
            stroke: #fff0a1;
            stroke-width: 1.2;
            stroke-linejoin: round;
            font-family: "Arial Black", "Segoe UI Black", sans-serif;
            font-size: 82px;
            font-weight: 900;
            letter-spacing: -5px;
        }
        .tx-face-t {
            fill: url(#tx-gold-t);
        }
        .tx-face-x {
            fill: url(#tx-gold-x);
        }
        @keyframes tx-monogram-rotate {
            0% { transform: rotateY(-12deg) rotateX(6deg) rotateZ(-1deg); }
            50% { transform: rotateY(12deg) rotateX(6deg) rotateZ(1deg); }
            100% { transform: rotateY(-12deg) rotateX(6deg) rotateZ(-1deg); }
        }
        .tx-hero-copy {
            padding: .5rem 0 .75rem;
        }
        .tx-hero-copy p {
            max-width: 48rem;
            font-size: 1.05rem;
            line-height: 1.65;
        }
        .tx-visual-label {
            margin: .35rem .2rem .25rem;
            color: var(--tx-muted);
            font-size: .68rem;
            font-weight: 750;
            letter-spacing: .13em;
            text-transform: uppercase;
        }
        .tx-hero-chip-row-label { margin: .8rem 0 .3rem; color: var(--tx-muted); font-size: .65rem; font-weight: 750; letter-spacing: .13em; }
        .st-key-hero_course_button button,
        .st-key-hero_ai_button button,
        .st-key-hero_lab_button button,
        .st-key-hero_exam_button button {
            min-height: 40px;
            border-color: rgba(107, 172, 198, .24);
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(16, 42, 60, .96), rgba(13, 32, 47, .96));
            font-size: .78rem;
        }
        .st-key-hero_course_button button { border-color: rgba(111, 221, 178, .36); }
        .st-key-hero_ai_button button { border-color: rgba(245, 200, 75, .48); color: #fff2bf; }
        .tx-chip {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            padding: .4rem .65rem;
            border: 1px solid var(--tx-line);
            border-radius: 999px;
            color: #d4e4ed;
            background: rgba(16, 37, 54, .8);
            font-size: .78rem;
            font-weight: 600;
        }
        .tx-chip-dot {
            width: .42rem;
            height: .42rem;
            border-radius: 50%;
            background: var(--tx-green);
            box-shadow: 0 0 8px rgba(111, 221, 178, .45);
        }
        .tx-course-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: .25rem 0 1.1rem;
            padding: .85rem 1rem;
            border: 1px solid var(--tx-line);
            border-left: 3px solid var(--tx-orange);
            border-radius: 12px;
            background: linear-gradient(100deg, rgba(18, 38, 56, .94), rgba(12, 29, 43, .8));
        }
        .tx-course-label { color: var(--tx-muted); font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
        .tx-course-name { color: var(--tx-text); font-size: 1rem; font-weight: 720; }
        .tx-course-state {
            flex: 0 0 auto;
            padding: .32rem .55rem;
            border: 1px solid rgba(111, 221, 178, .3);
            border-radius: 999px;
            color: #a8f0d1;
            background: rgba(42, 125, 91, .16);
            font-size: .74rem;
            font-weight: 700;
        }

        @media (max-width: 720px) {
            [data-testid="stMainBlockContainer"] { padding: 1rem .8rem 2rem; }
            [data-testid="stTabs"] [role="tab"] { padding: .48rem .65rem; font-size: .82rem; }
            .tx-course-bar { align-items: flex-start; flex-direction: column; gap: .45rem; }
            .tx-monogram { right: 8px; bottom: 72px; width: 98px; height: 62px; }
            .tx-monogram svg { width: 98px; height: 66px; }
            .tx-extrusion text,
            .tx-face-t,
            .tx-face-x { font-size: 82px; }
        }
        @media (prefers-reduced-motion: reduce) {
            .tx-monogram { animation: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

