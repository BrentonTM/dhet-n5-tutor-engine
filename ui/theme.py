import streamlit as st

def inject_industrial_theme():
    """Injects the Industrial Futurism design system, custom fonts, glassmorphism, and sidebar FX controls."""
    
    # 1. Sidebar Visual Effects Control Toggle
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Visual & 3D Effects Engine")
    fx_mode = st.sidebar.selectbox(
        "Visual Effects Quality:",
        ["High (Full 3D & Shaders)", "Low (CSS Glassmorphism Only)", "Off (Static Minimalist)"],
        index=0,
        help="Controls WebGL 3D scenes and heavy GPU animations for performance tuning."
    )
    st.session_state["fx_mode"] = fx_mode.split(" ")[0].lower() # stores 'high', 'low', or 'off'
    st.sidebar.markdown("---")

    # 2. Comprehensive CSS Injection
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Orbitron:wght@500;700;900&display=swap');

        :root {
            --bg-base: #0A0D12;
            --surface-glass: rgba(22, 27, 34, 0.75);
            --surface-border: rgba(48, 54, 61, 0.6);
            --primary-orange: #FF7A1A;
            --primary-glow: rgba(255, 122, 26, 0.35);
            --secondary-cyan: #22D3EE;
            --secondary-glow: rgba(34, 211, 238, 0.3);
            --accent-violet: #8B5CF6;
            --text-main: #E6EDF3;
            --text-muted: #8B949E;
            --font-display: 'Orbitron', sans-serif;
            --font-body: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        /* Base App Surface */
        .stApp {
            background: radial-gradient(circle at 50% 20%, #121824 0%, var(--bg-base) 100%);
            color: var(--text-main);
            font-family: var(--font-body);
        }

        /* Blueprint Grid Background Overlay */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(rgba(34, 211, 238, 0.03) 1px, transparent 1px),
                linear-gradient(to right, rgba(255,255,255,0.012) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255,255,255,0.012) 1px, transparent 1px);
            background-size: 50px 50px;
            z-index: 0;
            pointer-events: none;
        }

        /* Typography Override */
        h1, h2, h3, h4 {
            font-family: var(--font-display) !important;
            color: var(--text-main);
            letter-spacing: -0.5px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }

        code, pre, .stCodeBlock {
            font-family: var(--font-mono) !important;
        }

        /* Glassmorphism Metric Cards */
        [data-testid="stMetric"] {
            background: var(--surface-glass);
            border: 1px solid var(--surface-border);
            padding: 18px;
            border-radius: 14px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255,255,255,0.05);
            backdrop-filter: blur(12px);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: var(--secondary-cyan);
            box-shadow: 0 12px 40px var(--secondary-glow);
        }

        /* Glass Containers / Expanders */
        .streamlit-expanderHeader, div.stExpander {
            background: var(--surface-glass) !important;
            border: 1px solid var(--surface-border) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px);
        }

        /* Neon Action Buttons */
        .stButton>button {
            background: linear-gradient(135deg, var(--primary-orange) 0%, #E55A00 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 0.65rem 1.4rem;
            font-weight: 600;
            font-family: var(--font-display);
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 20px var(--primary-glow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #FF9138 0%, var(--primary-orange) 100%);
            box-shadow: 0 6px 25px rgba(255, 122, 26, 0.6);
            transform: translateY(-2px);
            border-color: var(--secondary-cyan);
        }

        /* Pill-style Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: rgba(10, 13, 18, 0.6);
            padding: 8px;
            border-radius: 14px;
            border: 1px solid var(--surface-border);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 10px;
            color: var(--text-muted);
            padding: 10px 20px;
            font-weight: 600;
            font-family: var(--font-display);
            font-size: 0.8rem;
            border: 1px solid transparent;
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(255, 122, 26, 0.2) 0%, rgba(34, 211, 238, 0.15) 100%) !important;
            color: var(--secondary-cyan) !important;
            border-color: var(--secondary-cyan) !important;
            box-shadow: 0 0 20px var(--secondary-glow);
        }

        /* Sidebar Glass Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 13, 18, 0.95);
            border-right: 1px solid var(--surface-border);
            backdrop-filter: blur(20px);
        }

        /* Floating 3D Gold/Orange Monogram TX Emblem */
        .trentox-monogram-tx {
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 99999;
            font-size: 22px;
            font-weight: 900;
            font-family: var(--font-display);
            background: linear-gradient(135deg, var(--primary-orange) 0%, var(--secondary-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 25px var(--primary-glow);
            border: 2px solid rgba(255, 122, 26, 0.4);
            padding: 10px 16px;
            border-radius: 12px;
            background-color: var(--surface-glass);
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 1px 2px rgba(255,255,255,0.2);
            animation: pulseEmblem 4s ease-in-out infinite;
            cursor: pointer;
        }
        @keyframes pulseEmblem {
            0%, 100% { transform: scale(1); box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px var(--primary-glow); }
            50% { transform: scale(1.05); box-shadow: 0 15px 35px rgba(0,0,0,0.9), 0 0 25px var(--secondary-glow); }
        }
    </style>
    """, unsafe_allow_html=True)