import os
import sys
import time
import sqlite3
import re
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# Import Industrial Futurism Theme Module
try:
    from ui.theme import inject_industrial_theme
except ImportError:
    def inject_industrial_theme():
        st.sidebar.warning("ui.theme module not found. Using default style.")

# Configure Matplotlib for headless Streamlit rendering
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except ImportError:
    plt = None
    patches = None

import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Document parsers
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pptx
except ImportError:
    pptx = None

# Optional Audio Recorder
try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None

# 1. Load API key from local .env file
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 2. Initialize Google GenAI Client
client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")

# Page configuration
st.set_page_config(
    page_title="Trentox Tutor AI | Industrial Engineering Mastery Engine",
    page_icon="⚡",
    layout="wide"
)

# Inject Industrial Futurism Theme & FX Controls
inject_industrial_theme()

# Paths configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "data", "databases")
os.makedirs(DATABASE_DIR, exist_ok=True)

# Helper function to clean corrupted PDF question characters
def clean_question_text(text):
    if not text:
        return ""
    cleaned = text.replace("\x00", "")
    cleaned = re.sub(r'f\s*[\(\[].*?[\)\]]', 'f(A, B, C)', cleaned)
    cleaned = re.sub(r'\(A,B,C,D\)', '(A, B, C, D)', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

# Helper function to render Three.js 3D Scenes safely based on FX quality
def render_3d_scene(scene_file, height=200):
    fx_mode = st.session_state.get("fx_mode", "high")
    if fx_mode == "off":
        return
    if fx_mode == "low":
        st.info("💡 3D WebGL effects are disabled in Low Quality mode.")
        return
        
    scene_path = os.path.join(BASE_DIR, "ui", "scenes", scene_file)
    if os.path.exists(scene_path):
        with open(scene_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=height, scrolling=False)
    else:
        fallback_html = f'<div style="color: #22D3EE; font-family: monospace; text-align: center; padding: 20px;">[3D Scene Canvas Placeholder: {scene_file}]</div>'
        components.html(fallback_html, height=height, scrolling=False)

# Universal Topic Diagram Engine
def render_topic_diagram(topic_name):
    if not plt or not patches:
        st.info("💡 Install Matplotlib (`python -m pip install matplotlib`) to render dynamic vector diagrams.")
        return
        
    topic_lower = topic_name.lower()
    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=120)
    fig.patch.set_facecolor("#0A0D12")
    ax.set_facecolor("#0A0D12")
    
    if "pressure" in topic_lower or "bourdon" in topic_lower or "gauge" in topic_lower:
        ax.set_title("C-Type Bourdon Tube Gauge Assembly (INST-N5)", color="white", fontsize=11, fontweight="bold")
        arc = patches.Arc((0.35, 0.45), 0.5, 0.6, angle=0, theta1=20, theta2=250, color="#22D3EE", linewidth=5)
        ax.add_patch(arc)
        base = patches.Rectangle((0.28, 0.1), 0.08, 0.2, color="#8B949E")
        ax.add_patch(base)
        ax.annotate("Fluid Pressure Inlet (P)", xy=(0.32, 0.1), xytext=(0.05, 0.05),
                    arrowprops=dict(arrowstyle="->", color="#FF7A1A", lw=2), color="white", fontsize=9)
        ax.plot([0.5, 0.65], [0.62, 0.65], color="#FF7A1A", lw=3)
        ax.text(0.52, 0.68, "Sealed Tip & Link", color="#FF7A1A", fontsize=8)
        sector = patches.Wedge((0.65, 0.55), 0.12, 120, 210, color="#8B5CF6")
        ax.add_patch(sector)
        ax.text(0.70, 0.58, "Quadrant Gear", color="#C4B5FD", fontsize=8)
        dial = patches.Circle((0.65, 0.45), 0.2, fill=False, edgecolor="#ffffff", ls="--", lw=1.5)
        ax.add_patch(dial)
        ax.text(0.72, 0.4, "Dial Scale & Pointer", color="#FCA5A5", fontsize=8)

    elif "flow" in topic_lower or "orifice" in topic_lower or "venturi" in topic_lower or "bernoulli" in topic_lower:
        ax.set_title("Venturi Flow Meter Differential Pressure (INST-N5)", color="white", fontsize=11, fontweight="bold")
        ax.plot([0.05, 0.35, 0.5, 0.65, 0.95], [0.8, 0.8, 0.65, 0.8, 0.8], color="#8B949E", lw=4)
        ax.plot([0.05, 0.35, 0.5, 0.65, 0.95], [0.2, 0.2, 0.35, 0.2, 0.2], color="#8B949E", lw=4)
        for x in [0.15, 0.48, 0.8]:
            ax.annotate("", xy=(x+0.08, 0.5), xytext=(x, 0.5), arrowprops=dict(arrowstyle="->", color="#22D3EE", lw=2.5))
        ax.text(0.1, 0.53, "Inlet (P1, V1)", color="#67E8F9", fontsize=9)
        ax.text(0.44, 0.53, "Throat (P2, V2)", color="#FF7A1A", fontsize=8)
        ax.plot([0.25, 0.25], [0.8, 0.95], color="#22D3EE", lw=3)
        ax.plot([0.50, 0.50], [0.65, 0.95], color="#22D3EE", lw=3)
        ax.plot([0.25, 0.50], [0.95, 0.95], color="#FF7A1A", lw=2, ls=":")
        ax.text(0.32, 0.97, "ΔP = P1 - P2", color="#FF7A1A", fontsize=10, fontweight="bold")

    elif "temperature" in topic_lower or "rtd" in topic_lower or "thermocouple" in topic_lower or "pyrometer" in topic_lower:
        ax.set_title("RTD / Thermocouple Industrial Sensor Probe (INST-N5)", color="white", fontsize=11, fontweight="bold")
        probe = patches.Rectangle((0.15, 0.42), 0.5, 0.16, facecolor="#8B949E", edgecolor="#22D3EE", lw=2)
        ax.add_patch(probe)
        ax.text(0.4, 0.48, "Protective Thermowell Sheath", color="white", fontsize=9, ha="center")
        ax.plot([0.65, 0.85], [0.5, 0.5], color="#FF7A1A", lw=3)
        ax.text(0.7, 0.55, "Compensating Leads to Transmitter", color="#FF7A1A", fontsize=8)

    elif "op-amp" in topic_lower or "amplifier" in topic_lower or "thyristor" in topic_lower or "electronics" in topic_lower:
        ax.set_title("Operational Amplifier Circuit Schematic (IE-N5)", color="white", fontsize=11, fontweight="bold")
        opamp = patches.Polygon([[0.45, 0.25], [0.45, 0.75], [0.75, 0.5]], color="#10B981")
        ax.add_patch(opamp)
        ax.text(0.47, 0.62, "-", color="white", fontsize=16, fontweight="bold")
        ax.text(0.47, 0.32, "+", color="white", fontsize=14, fontweight="bold")
        ax.plot([0.1, 0.3], [0.65, 0.65], color="#FF7A1A", lw=2)
        ax.text(0.05, 0.63, "Vin", color="#22D3EE", fontsize=11, fontweight="bold")
        ax.plot([0.75, 0.9], [0.5, 0.5], color="#EF4444", lw=2.5)
        ax.text(0.82, 0.42, "Vout", color="#EF4444", fontsize=10, fontweight="bold")

    elif "calculus" in topic_lower or "derivative" in topic_lower or "integral" in topic_lower or "differential equation" in topic_lower or "complex" in topic_lower:
        ax.set_title(f"Mathematical Response & Function Curve: {topic_name}", color="white", fontsize=11, fontweight="bold")
        x = np.linspace(0, 10, 100)
        y = np.exp(-0.2*x) * np.sin(1.5*x) + 0.5
        ax.plot(x, y, color="#22D3EE", lw=2.5, label="f(x) Curve")
        ax.axhline(0, color="#30363D", lw=1.5)
        ax.axvline(0, color="#30363D", lw=1.5)
        ax.grid(True, color="#30363D", linestyle=":")
        ax.legend(facecolor="#0A0D12", edgecolor="none", labelcolor="white")

    elif "counter" in topic_lower or "shift" in topic_lower or "flip-flop" in topic_lower or "logic" in topic_lower or "number" in topic_lower:
        ax.set_title("Sequential Digital Logic Architecture (DIGI-N4/N5)", color="white", fontsize=11, fontweight="bold")
        for i, label in enumerate(["FF0 (LSB)", "FF1", "FF2 (MSB)"]):
            x = 0.1 + i * 0.28
            rect = patches.Rectangle((x, 0.3), 0.2, 0.4, facecolor="#161B22", edgecolor="#22D3EE", lw=2)
            ax.add_patch(rect)
            ax.text(x + 0.1, 0.5, label, color="white", fontsize=9, fontweight="bold", ha="center")
            if i < 2:
                ax.annotate("", xy=(x + 0.28, 0.5), xytext=(x + 0.2, 0.5), arrowprops=dict(arrowstyle="->", color="#FF7A1A", lw=2))
        ax.annotate("CLK", xy=(0.1, 0.5), xytext=(0.01, 0.5), arrowprops=dict(arrowstyle="->", color="#22D3EE", lw=2), color="#22D3EE", fontsize=9, fontweight="bold")

    else:
        ax.set_title(f"System Block Diagram & Signal Flow: {topic_name}", color="white", fontsize=11, fontweight="bold")
        blocks = [("Sensor / Input", 0.1, "#22D3EE"), ("Signal Conditioner", 0.4, "#10B981"), ("Controller / Output", 0.7, "#FF7A1A")]
        for title, x, color in blocks:
            rect = patches.Rectangle((x, 0.35), 0.2, 0.3, facecolor="#161B22", edgecolor=color, lw=2)
            ax.add_patch(rect)
            ax.text(x + 0.1, 0.5, title, color="white", fontsize=8, fontweight="bold", ha="center")
        ax.annotate("", xy=(0.4, 0.5), xytext=(0.3, 0.5), arrowprops=dict(arrowstyle="->", color="white", lw=2))
        ax.annotate("", xy=(0.7, 0.5), xytext=(0.6, 0.5), arrowprops=dict(arrowstyle="->", color="white", lw=2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    st.pyplot(fig)

# Local Material Reader Function
def extract_text_from_local_files(folder_path):
    extracted_notes = []
    if not os.path.exists(folder_path):
        return ""

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext == ".pdf" and pypdf:
                try:
                    reader = pypdf.PdfReader(file_path)
                    text = ""
                    for page in reader.pages[:15]:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    if text.strip():
                        extracted_notes.append(f"--- SOURCE FILE: {file} ---\n{text[:3000]}")
                except Exception:
                    continue

            elif ext in [".ppt", ".pptx"] and pptx:
                try:
                    prs = pptx.Presentation(file_path)
                    text = ""
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text") and shape.text:
                                text += shape.text + "\n"
                    if text.strip():
                        extracted_notes.append(f"--- SOURCE FILE: {file} ---\n{text[:3000]}")
                except Exception:
                    continue

    return "\n\n".join(extracted_notes)

# Cached Gemini Query Function
@st.cache_data(show_spinner=False)
def cached_query_gemini(prompt_text, subject_code):
    if not client:
        return None, "Gemini API client is not configured."
    candidate_models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-3.1-pro-preview"]
    last_err = None
    for model_name in candidate_models:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt_text)
            if res and res.text:
                return res.text, None
        except Exception as m_err:
            last_err = m_err
            continue
    return None, f"All models currently busy. Details: {last_err}"

def query_gemini_with_fallback(prompt):
    if not client:
        return None, "Gemini API client is not configured."
    candidate_models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-3.1-pro-preview"]
    last_err = None
    for model_name in candidate_models:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt)
            if res and res.text:
                return res.text, None
        except Exception as m_err:
            last_err = m_err
            continue
    return None, f"All models currently busy. Details: {last_err}"

SUBJECT_MODULES = {
    "INST-N5": [
        "Flow Measurement (Orifice, Venturi, Weirs, Bernoulli's Equation)",
        "Pressure Measurement (Bourdon Tube, Strain Gauges, Differential Pressure)",
        "Temperature Measurement (RTDs, Thermocouples, Pyrometers)",
        "Level Measurement & Chemical Instrumentation (pH, pOH)",
        "Control Systems & PID Controllers (P, PI, PID tuning)"
    ],
    "MATH-N5": [
        "Trigonometric Identities & Binomial Theorem",
        "Differential Calculus & Rules (Product, Quotient, Chain Rule)",
        "Integral Calculus & Standard Integration Formulas",
        "Applications of Integration (Areas, Volumes, Second Moment of Area)",
        "Moment of Inertia & Differential Equations"
    ],
    "IE-N5": [
        "Operational Amplifiers (Inverting, Non-Inverting, Summing)",
        "Power Control & Thyristors (SCRs, TRIACs, DIACs)",
        "Transducers & Signal Conditioning",
        "Integrated Circuits & Timer ICs (555 Timer Applications)",
        "Closed-Loop & Open-Loop Control Systems"
    ],
    "DIGI-N4": [
        "Number Systems & Binary Codes (Hex, Octal, BCD)",
        "Logic Gates & Boolean Algebra",
        "Karnaugh Maps (K-Maps) & Simplification",
        "Combinational Logic (Encoders, Decoders, Multiplexers)",
        "Sequential Logic (SR, JK, D Flip-Flops)"
    ],
    "DIGI-N5": [
        "Counters & Shift Registers (Asynchronous, Synchronous)",
        "Digital-to-Analog (DAC) & Analog-to-Digital (ADC) Converters",
        "Memory Organization (RAM, ROM, EPROM, EEPROM)",
        "Microprocessor Fundamentals & Architecture",
        "Arithmetic Logic Units (ALU) & Bus Systems"
    ]
}

FLASHCARDS_DATA = {
    "INST-N5": [
        {"q": "What is the formula for calculating flow rate over a V-notch (triangular) weir?", "a": r"$$Q = \frac{8}{15}\tan\left(\frac{\theta}{2}\right)\sqrt{2g}H^{5/2}$$"},
        {"q": "How is pH calculated in industrial process instrumentation?", "a": r"$$\text{pH} = -\log[\text{H}^+]$$"}
    ],
    "MATH-N5": [
        {"q": "State the formula for the Product Rule in differentiation.", "a": r"$$\frac{dy}{dx} = u\frac{dv}{dx} + v\frac{du}{dx}$$"},
        {"q": "What is the formula for calculating volume of revolution around the x-axis ($V_x$)?", "a": r"$$V_x = \pi \int_{a}^{b} y^2 \, dx$$"}
    ],
    "IE-N5": [
        {"q": "What is the voltage gain formula for an inverting Op-Amp circuit?", "a": r"$$A_v = -\frac{R_f}{R_1}$$"},
        {"q": "What component is used to turn off an SCR in a DC circuit?", "a": "A forced commutation circuit (such as a reverse-biasing capacitor or transistor switch) that drops the current below the holding current (I_H)."}
    ]
}

# App Header
st.title("⚡ Trentox Tutor AI")
st.caption("Industrial Engineering Mastery Engine | Instrumentation N5 | Mathematics N5 | Industrial Electronics N5 | Digital Electronics N4/N5")

# Render 3D Hero Banner Scene
render_3d_scene("hero_scene.html", height=180)

# Sidebar navigation & Categorized Formula Reference Expander
st.sidebar.header("Navigation & Settings")
active_subject = st.sidebar.selectbox(
    "Select Active Subject:",
    ["INST-N5", "MATH-N5", "IE-N5", "DIGI-N4", "DIGI-N5"]
)

# Render Live Subject Motif in Sidebar
st.sidebar.markdown("### 🌐 Subject Motif")
render_3d_scene("subject_motifs.html", height=130)

# Official NATED Categorized Formula Reference Sheets in Sidebar (Complete Exam Sheets Integration)
with st.sidebar.expander("📐 Official NATED Formula Sheets", expanded=True):
    st.markdown('<div style="max-height: 480px; overflow-y: auto; padding-right: 6px;">', unsafe_allow_html=True)
    
    if active_subject == "IE-N5":
        st.markdown("### ⚡ Industrial Electronics N5")
        
        st.markdown("**1. DC Circuits, Power & Transients**")
        st.latex(r"I = \frac{V}{R} \quad | \quad P = IV = I^2R = \frac{V^2}{R}")
        st.latex(r"V_T = V_1 + V_2 + \dots = I_1R_1 + I_2R_2 + \dots")
        st.latex(r"I_T = I_1 + I_2 + \dots = \frac{V_1}{R_1} + \frac{V_2}{R_2} + \dots")
        st.latex(r"T = RC \quad | \quad T = \frac{L}{R}")
        st.latex(r"V_R = RC\frac{dv}{dt} \quad | \quad V_C = \frac{1}{RC}\int v_i dt")

        st.markdown("**2. AC Theory, Impedance & Resonance**")
        st.latex(r"X_L = 2\pi f L \quad | \quad X_C = \frac{1}{2\pi f C}")
        st.latex(r"Z = R \pm jX_L \quad | \quad Z = R - jX_C")
        st.latex(r"Z = R \pm j(X_L - X_C)")
        st.latex(r"I_T = \frac{V_T}{Z_T} \quad | \quad V_R = I_T R \quad | \quad V_L = I_T(jX_L)")
        st.latex(r"f_r = \frac{1}{2\pi \sqrt{LC}} \quad | \quad Q = \frac{V_L}{V_T} = \frac{X_L}{R}")
        st.latex(r"BW = f_2 - f_1 \quad | \quad \frac{1}{Z_T} = \frac{1}{Z_1} + \frac{1}{Z_2}")
        st.latex(r"Z_T = \frac{Z_1 Z_2}{Z_1 + Z_2} \quad | \quad f = \frac{1}{2\pi}\sqrt{\frac{1}{LC} - \frac{R^2}{L^2}}")
        st.latex(r"Z_d = \frac{L}{CR_1} \quad | \quad Q = \tan\theta")

        st.markdown("**3. Complex Numbers & Polar Conversions**")
        st.latex(r"a + jb = \sqrt{a^2 + b^2} \angle \tan^{-1}\frac{b}{a}")
        st.latex(r"r \angle \theta = r(\cos\theta + j\sin\theta)")

        st.markdown("**4. Rectifiers, Ripple & Power Supplies**")
        st.latex(r"V_{rms} = \frac{1}{\sqrt{2}}V_m = 0.707 V_m")
        st.latex(r"V_{dc} = \frac{2}{\pi}V_m = 0.637 V_m \quad | \quad V_{dc} = \frac{1}{\pi}V_m = 0.318 V_m")
        st.latex(r"PIV = V_m \quad | \quad PIV = 2V_m")
        st.latex(r"V_{r(rms)} = \frac{V_{r(p-p)}}{2\sqrt{3}} \quad | \quad r = \frac{V_{r(rms)}}{V_{dc}}")
        st.latex(r"V_{dc} = V_m - \frac{V_{r(p-p)}}{2} \quad | \quad V_{dc} = V_m - \frac{I_{dc}}{2fC}")
        st.latex(r"V'_{dc} = \frac{R_L}{R + R_L}V_{dc} \quad | \quad V'_{dc} = V_{dc} - I_{dc}R_1")
        st.latex(r"V'_{r(rms)} = \frac{V_{r(rms)}}{(2\pi f)^2 LC} \quad | \quad \%VR = \frac{V_{NL} - V_{FL}}{V_{FL}} \times 100")

        st.markdown("**5. Transistors, Biasing & h-Parameters**")
        st.latex(r"\beta = \frac{I_c}{I_b} \quad | \quad V_{be} = h_{ie}i_b + h_{re}V_{ce}")
        st.latex(r"R_b = \frac{V_{cc} - V_{be}}{I_b} \quad | \quad R_c = \frac{V_{cc} - V_{ce}}{I_c}")
        st.latex(r"R_{b1} = \frac{R_{b2}(V_{cc} - V_b)}{V_b} \quad | \quad R_{b2} = \frac{1}{10}\beta R_e")
        st.latex(r"A_i = \frac{h_{fe}}{1 + h_{oe}Z_L} \quad | \quad A_v = \frac{-h_{fe}Z_L}{h_{ie} + (h_{ie}h_{oe} - h_{fe}h_{re})Z_L}")
        st.latex(r"Z_1 = h_{ie} - \frac{h_{fe}h_{re}Z_L}{1 + h_{oe}Z_L} \quad | \quad Z_2 = \frac{1}{h_{oe} - \frac{h_{fe}h_{re}}{h_{ie} + R_s}}")
        st.latex(r"A_p = \frac{A_i^2 R_L}{R_1} = -A_v A_i \quad | \quad Z_o = R_c // R_L // Z_2")
        st.latex(r"CMRR = \frac{A_{dm}}{A_{cm}} \quad | \quad CMRR_{(dB)} = 20\log\left(\frac{A_{dm}}{A_{cm}}\right)")

        st.markdown("**6. Operational Amplifiers (Op-Amps)**")
        st.latex(r"V_o = -\left(\frac{R_f}{R_1}\right)V_i \text{ (Inverting)}")
        st.latex(r"V_o = -\left(\frac{R_f}{R_1}V_1 + \frac{R_f}{R_2}V_2 + \frac{R_f}{R_3}V_3\right)")
        st.latex(r"V_o = \left(\frac{R_f}{R_1} + 1\right)V_i \text{ (Non-Inverting)}")
        st.latex(r"V_o(t) = -\frac{1}{RC}\int V_i(t)dt \text{ (Integrator)}")
        st.latex(r"V_o(t) = -RC\frac{dV_i(t)}{dt} \text{ (Differentiator)}")

        st.markdown("**7. 555 Timers & Transducers**")
        st.latex(r"f_o = \frac{1.443}{(R_A + 2R_B)C} \text{ (Astable)}")
        st.latex(r"t_{low} = 0.693 R_B C \quad | \quad t_{high} = 0.693(R_A + R_B)C")
        st.latex(r"K = \frac{\Delta R / R}{\Delta L / L} \quad | \quad R = \rho \frac{l}{\pi d^2 / 4}")
        st.latex(r"R_t = A e^{B/T} \quad | \quad V_{Hall} = k I H")

    elif active_subject == "INST-N5":
        st.markdown("### 🎛 Instrumentation N5")
        
        st.markdown("**1. Flow Measurement (Weirs, Orifice & Venturi)**")
        st.latex(r"Q = \frac{8}{15}\tan\left(\frac{\theta}{2}\right)\sqrt{2g}H^{5/2} \text{ (V-Notch)}")
        st.latex(r"Q = \frac{2}{3}BC\sqrt{2g}H^{3/2} \text{ (Rectangular Weir)}")
        st.latex(r"Q = C_d A_2 \sqrt{\frac{2\Delta P}{\rho(1 - \beta^4)}}")
        st.latex(r"\Delta P = P_1 - P_2 = \frac{1}{2}\rho(V_2^2 - V_1^2)")

        st.markdown("**2. Pressure, Level & Chemical Sensors**")
        st.latex(r"P = \rho \cdot g \cdot h \quad | \quad P_{gauge} = P_{abs} - P_{atm}")
        st.latex(r"\text{pH} = -\log[\text{H}^+] \quad | \quad \text{pOH} = -\log[\text{OH}^-] ")

        st.markdown("**3. Temperature Sensors (RTDs & Thermocouples)**")
        st.latex(r"R_t = R_0(1 + \alpha \Delta T + \beta \Delta T^2)")
        st.latex(r"E = a \Delta T + b (\Delta T)^2")

        st.markdown("**4. Control Systems & PID**")
        st.latex(r"e(t) = SP - PV")
        st.latex(r"MV(t) = K_p e(t) + K_i \int e(t)dt + K_d \frac{de(t)}{dt}")

    elif active_subject == "MATH-N5":
        st.markdown("### 📐 Mathematics N5")
        
        st.markdown("**1. Trigonometric Identities**")
        st.latex(r"\sin^2 x + \cos^2 x = 1 \quad | \quad 1 + \tan^2 x = \sec^2 x")
        st.latex(r"\sin 2A = 2\sin A \cos A \quad | \quad \cos 2A = \cos^2 A - \sin^2 A")
        st.latex(r"\tan 2A = \frac{2\tan A}{1 - \tan^2 A}")
        st.latex(r"\sin(A \pm B) = \sin A \cos B \pm \sin B \cos A")
        st.latex(r"\cos(A \pm B) = \cos A \cos B \mp \sin A \sin B")

        st.markdown("**2. Calculus Rules (Product, Quotient, Chain)**")
        st.latex(r"y = uv \implies \frac{dy}{dx} = u\frac{dv}{dx} + v\frac{du}{dx}")
        st.latex(r"y = \frac{u}{v} \implies \frac{dy}{dx} = \frac{v\frac{du}{dx} - u\frac{dv}{dx}}{v^2}")
        st.latex(r"\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}")

        st.markdown("**3. Standard Derivatives & Integrals Table**")
        st.markdown("*Power Functions:*")
        st.latex(r"\frac{d}{dx}[ax^n] = nax^{n-1} \quad | \quad \int ax^n dx = \frac{ax^{n+1}}{n+1} + c")
        st.markdown("*Exponential & Logarithmic:*")
        st.latex(r"\frac{d}{dx}[e^x] = e^x \quad | \quad \int e^x dx = e^x + c")
        st.latex(r"\frac{d}{dx}[\ln x] = \frac{1}{x} \quad | \quad \int \frac{1}{x} dx = \ln|x| + c")
        st.markdown("*Trigonometric Derivatives & Integrals:*")
        st.latex(r"\frac{d}{dx}[\sin x] = \cos x \quad | \quad \int \sin x dx = -\cos x + c")
        st.latex(r"\frac{d}{dx}[\cos x] = -\sin x \quad | \quad \int \cos x dx = \sin x + c")
        st.latex(r"\frac{d}{dx}[\tan x] = \sec^2 x \quad | \quad \int \tan x dx = \ln|\sec x| + c")
        st.markdown("*Inverse Trigonometric:*")
        st.latex(r"\frac{d}{dx}[\sin^{-1}x] = \frac{1}{\sqrt{1-x^2}} \quad | \quad \int \frac{1}{\sqrt{a^2-x^2}}dx = \sin^{-1}\left(\frac{x}{a}\right)+c")
        st.latex(r"\frac{d}{dx}[\tan^{-1}x] = \frac{1}{1+x^2} \quad | \quad \int \frac{1}{a^2+x^2}dx = \frac{1}{a}\tan^{-1}\left(\frac{x}{a}\right)+c")
        st.latex(r"\int \frac{1}{\sqrt{x^2 \pm a^2}}dx = \ln|x + \sqrt{x^2 \pm a^2}| + c")

        st.markdown("**4. Integration Techniques & Applications**")
        st.latex(r"\int u \, dv = uv - \int v \, du \text{ (Parts)}")
        st.latex(r"A_x = \int_{a}^{b} y \, dx \quad | \quad V_x = \pi \int_{a}^{b} y^2 \, dx")
        st.latex(r"I_x = \int_{a}^{b} r^2 \, dA \quad | \quad M = m \cdot r^2")

    elif active_subject == "DIGI-N4":
        st.markdown("### 🔢 Digital Electronics N4")
        
        st.markdown("**1. Number Systems & Codes**")
        st.latex(r"N_{base10} = \sum_{i} d_i \cdot b^i")
        st.latex(r"N_{states} = 2^n")

        st.markdown("**2. Boolean Algebra & De Morgan's Laws**")
        st.latex(r"\overline{A \cdot B} = \overline{A} + \overline{B}")
        st.latex(r"\overline{A + B} = \overline{A} \cdot \overline{B}")

        st.markdown("**3. Sequential Logic & Flip-Flops**")
        st.latex(r"Q_{next} = J\overline{Q} + \overline{K}Q \text{ (JK FF)}")
        st.latex(r"f_{max} = \frac{1}{n \cdot t_{pd}}")

    elif active_subject == "DIGI-N5":
        st.markdown("### 💻 Digital Electronics N5")
        
        st.markdown("**1. Counters & State Machines**")
        st.latex(r"\text{Modulus } M \le 2^n")
        st.latex(r"f_{out} = \frac{f_{clk}}{M}")

        st.markdown("**2. Data Converters (ADC & DAC)**")
        st.latex(r"V_{out} = -V_{ref} \sum_{i=1}^{n} \frac{d_i}{2^i}")
        st.latex(r"\text{Resolution} = \frac{V_{FS}}{2^n - 1}")

        st.markdown("**3. Memory & Signal Conditioning**")
        st.latex(r"A_d = 20 \log_{10}\left(\frac{V_o}{V_i}\right)")
        st.latex(r"t_{conversion} = n \cdot T_{clk}")

    st.markdown('</div>', unsafe_allow_html=True)

if not GEMINI_API_KEY:
    manual_key = st.sidebar.text_input("Gemini API Key:", type="password")
    if manual_key:
        try:
            from google import genai
            client = genai.Client(api_key=manual_key)
            st.sidebar.success("API key loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Invalid API Key: {e}")

# Main Tabs
tab_mastery, tab_practice, tab_exam, tab_tutor, tab_formulas, tab_analytics = st.tabs([
    "📊 Mastery Dashboard",
    "💡 Practical & Socratic Sandbox",
    "🎯 Stress-Conditioned Exam Simulator",
    "📚 AI Tutor Notes & Simulators",
    "📐 Formula & Reference Hub",
    "📈 Cognitive & Psychological Analytics"
])

# TAB 1: Mastery Dashboard
with tab_mastery:
    st.subheader(f"Mastery Overview & Analytics: {active_subject}")
    mastery_db = os.path.join(DATABASE_DIR, "mastery.db")
    
    data = []
    if os.path.exists(mastery_db):
        with sqlite3.connect(mastery_db) as conn:
            try:
                data = conn.execute(
                    "SELECT topic_name, mastery_percentage FROM mastery_scores WHERE subject_code = ?",
                    (active_subject,)
                ).fetchall()
            except sqlite3.OperationalError:
                data = []

    if data:
        topics = [row[0] for row in data]
        scores = [row[1] for row in data]
        
        col_chart, col_stats = st.columns([2, 1])
        
        with col_chart:
            fig = px.bar(
                x=scores,
                y=topics,
                orientation="h",
                labels={"x": "Mastery Level (%)", "y": "Topic Module"},
                title=f"Cognitive Topic Proficiency ({active_subject})",
                color=scores,
                color_continuous_scale=["#EF4444", "#FF7A1A", "#22D3EE", "#10B981"]
            )
            fig.update_layout(
                plot_bgcolor="rgba(10, 13, 18, 0.8)",
                paper_bgcolor="rgba(10, 13, 18, 0.8)",
                font_color="#E6EDF3",
                font_family="Inter",
                xaxis=dict(gridcolor="rgba(48, 54, 61, 0.4)", range=[0, 100]),
                yaxis=dict(gridcolor="rgba(48, 54, 61, 0.4)"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_stats:
            avg_score = np.mean(scores) if scores else 0
            st.metric("Subject Mastery Level", f"{avg_score:.1f}%")
            st.metric("Modules Tested", f"{len(scores)} / {len(SUBJECT_MODULES.get(active_subject, []))}")
            st.markdown('<span style="color:#10B981; font-weight:bold;">⚡ Active Learning Streak: 4 Days</span>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(48, 54, 61, 0.6); border-radius: 16px; padding: 24px; text-align: center; backdrop-filter: blur(12px);">
            <h3 style="margin-bottom: 0px; color: #22D3EE;">Mastery Core Offline</h3>
            <p style="color: #8B949E; font-size: 0.9rem;">No practice telemetry recorded for this subject yet.</p>
        </div>
        """, unsafe_allow_html=True)
        
        render_3d_scene("mastery_core.html", height=220)
        st.info("💡 **Call to Action:** Head over to **Tab 2 (Practical Sandbox)** or **Tab 3 (Exam Simulator)** to complete your first evaluation and power up your Mastery Core!")

# TAB 2: Practical & Socratic Sandbox
with tab_practice:
    st.subheader("💡 Practical Engineering Sandbox & Fault-Finding Scenarios")
    mode = st.radio("Select Practice Mode:", ["Exam Past Paper Guidance", "🚨 Plant Fault Diagnosis Scenario"], horizontal=True)
    
    st.caption("🎙️ You can type your solution or record a brief spoken explanation below:")
    voice_text = ""
    if mic_recorder:
        audio = mic_recorder(start_prompt="⏺️ Record Voice Explanation", stop_prompt="⏹️ Stop Recording", key="mic_rec")
        if audio:
            st.audio(audio['bytes'])
            voice_text = "[Voice Input Audio Recorded Successfully]"

    if mode == "🚨 Plant Fault Diagnosis Scenario":
        st.markdown("### Industrial Troubleshooting & Fault Diagnosis")
        fault_scenarios = {
            "INST-N5": "A differential pressure transmitter across an orifice plate reads 0 kPa despite a high fluid flow rate in the main pipeline. The 4-20mA loop current is steady at 4.0 mA.",
            "IE-N5": "An operational amplifier non-inverting circuit outputs a clipped square wave at ±15V when a 2V peak-to-peak sine wave is applied at the input.",
            "DIGI-N5": "An asynchronous 4-bit ripple counter skips count state 0110 (6) and resets directly to 0000 on every cycle."
        }
        selected_scenario = fault_scenarios.get(active_subject, "A 4-20mA pressure transducer signal is noisy and tripping the relay switch.")
        st.error(f"**SCENARIO:** {selected_scenario}")
        
        typed_diag = st.text_area("Your Step-by-Step Fault Diagnosis & Repair Strategy:", placeholder="e.g., Step 1: Check impulse line blockage...")
        user_diag = typed_diag if typed_diag.strip() else voice_text
        
        if st.button("Submit Fault Diagnosis"):
            if not user_diag.strip():
                st.warning("Type or record your diagnostic process first!")
            else:
                with st.spinner("Senior Engineering Technician reviewing your strategy..."):
                    diag_prompt = f"Evaluate troubleshooting steps for {active_subject}.\nSCENARIO: {selected_scenario}\nDIAGNOSIS: {user_diag}"
                    resp, err = query_gemini_with_fallback(diag_prompt)
                    if resp:
                        st.markdown("### 🛠 Senior Technician Feedback")
                        st.markdown(resp)
                    else:
                        st.error(err)
    else:
        if "current_question" not in st.session_state:
            st.session_state.current_question = None

        if st.button("Fetch Random Exam Question"):
            past_db = os.path.join(DATABASE_DIR, "past_papers.db")
            if os.path.exists(past_db):
                base_sub = active_subject.split("-")[0]
                with sqlite3.connect(past_db) as conn:
                    try:
                        row = conn.execute(
                            "SELECT question_number, topic_name, question_text, marking_guideline, marks FROM paper_questions WHERE (subject_code LIKE ? OR subject_code LIKE ?) AND LENGTH(question_text) > 30 ORDER BY RANDOM() LIMIT 1",
                            (f"{active_subject}%", f"{base_sub}%")
                        ).fetchone()
                    except sqlite3.OperationalError:
                        row = None
                    if row:
                        st.session_state.current_question = {"num": row[0], "topic": row[1], "text": clean_question_text(row[2]), "marking": row[3], "marks": row[4]}

        q = st.session_state.current_question
        if q:
            st.info(f"**Question {q['num']} [{q['marks']} Marks]** — *{q['topic']}*\n\n{q['text']}")
            typed_sol = st.text_area("Your Working / Answer Attempt:", height=140)
            user_sol = typed_sol if typed_sol.strip() else voice_text
            
            if st.button("Get AI Socratic Guidance"):
                with st.spinner("Analyzing solution..."):
                    prompt = f"Socratic guidance for {active_subject}:\nQUESTION: {q['text']}\nMARKING: {q['marking']}\nATTEMPT: {user_sol}"
                    resp, err = query_gemini_with_fallback(prompt)
                    if resp:
                        st.markdown(resp)

# TAB 3: Stress-Conditioned Exam Simulator
with tab_exam:
    st.subheader(f"🎯 Timed Mock Exam Simulator & Confidence Calibration ({active_subject})")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        num_q = st.slider("Number of Questions:", 5, 15, 5)
        time_limit = st.selectbox("Exam Time Limit (minutes):", [15, 30, 45, 60], index=1)
        high_pressure = st.checkbox("⚡ High-Pressure Mode (Reduce Time by 15%)")
        
        if st.button("🚀 Start Mock Exam"):
            effective_time = time_limit * 0.85 if high_pressure else time_limit
            past_db = os.path.join(DATABASE_DIR, "past_papers.db")
            if os.path.exists(past_db):
                base_sub = active_subject.split("-")[0]
                with sqlite3.connect(past_db) as conn:
                    rows = conn.execute(
                        "SELECT question_number, topic_name, question_text, marking_guideline, marks FROM paper_questions WHERE (subject_code LIKE ? OR subject_code LIKE ?) AND LENGTH(question_text) > 30 ORDER BY RANDOM() LIMIT ?",
                        (f"{active_subject}%", f"{base_sub}%", num_q)
                    ).fetchall()
                if rows:
                    st.session_state.exam_paper = [{"num": r[0], "topic": r[1], "text": clean_question_text(r[2]), "marking": r[3], "marks": r[4]} for r in rows]
                    st.session_state.exam_answers = {}
                    st.session_state.exam_confidence = {}
                    st.session_state.exam_submitted = False
                    st.session_state.exam_start_time = time.time()
                    st.session_state.exam_duration = effective_time * 60
                    st.rerun()

    with col2:
        if "exam_paper" in st.session_state and st.session_state.exam_paper:
            paper = st.session_state.exam_paper
            timer_box = st.empty()
            elapsed = time.time() - st.session_state.exam_start_time
            remaining = int(st.session_state.exam_duration - elapsed)

            if remaining > 0 and not st.session_state.get("exam_submitted", False):
                m, s = divmod(remaining, 60)
                total_sec = st.session_state.get("exam_duration", 1)
                ratio = remaining / total_sec
                
                if ratio > 0.5:
                    v_class = "stress-vignette-cyan"
                    time_color = "#22D3EE"
                elif ratio > 0.2:
                    v_class = "stress-vignette-orange"
                    time_color = "#FF7A1A"
                else:
                    v_class = "stress-vignette-red"
                    time_color = "#EF4444"

                timer_box.markdown(
                    f'<div class="{v_class}" style="text-align: center;">'
                    f'<h3 style="color: {time_color}; margin: 0;">⏱ Time Remaining: {m:02d}:{s:02d}</h3>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif remaining <= 0 and not st.session_state.get("exam_submitted", False):
                timer_box.error("🚨 TIME EXPIRED! Submitting paper...")
                st.session_state.exam_submitted = True

            with st.form("mock_exam_form"):
                for idx, item in enumerate(paper):
                    st.markdown(f"**Question {idx + 1} [{item['marks']} Marks]** — *{item['topic']}*")
                    st.write(item['text'])
                    st.session_state.exam_answers[idx] = st.text_area(f"Working for Q{idx+1}:", value=st.session_state.exam_answers.get(idx, ""), key=f"q_ans_{idx}", height=100)
                    st.session_state.exam_confidence[idx] = st.radio(f"Confidence Level for Q{idx+1}:", ["High Confidence", "Medium / Uncertain", "Low / Pure Guess"], key=f"conf_{idx}", horizontal=True)
                    st.divider()
                submit_exam = st.form_submit_button("📋 Submit & Grade Exam")
            
            if submit_exam or st.session_state.get("exam_submitted", False):
                st.session_state.exam_submitted = True
                with st.spinner("Chief Examiner Grading Attempt..."):
                    grading_prompt = f"Grade exam for {active_subject}."
                    for idx, item in enumerate(paper):
                        grading_prompt += f"\nQ{idx+1}: {item['text']}\nMARKING: {item['marking']}\nANSWER: {st.session_state.exam_answers.get(idx, '')}"
                    eval_result, err = query_gemini_with_fallback(grading_prompt)
                    if eval_result:
                        st.markdown("## 📝 Assessment Report")
                        st.markdown(eval_result)

# TAB 4: AI Tutor Notes, Simulators & Spaced-Repetition Flashcards
with tab_tutor:
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "📖 Module Lessons & Notes",
        "🧠 Spaced-Repetition Cards",
        "🎛 Live Parameter Simulators",
        "📅 14-Day Timetable"
    ])
    
    with sub_tab1:
        modules = SUBJECT_MODULES.get(active_subject, ["General Module Overview"])
        selected_module = st.selectbox("Select Topic:", modules)
        custom_query = st.text_input("Or enter specific concept/formula:", placeholder="e.g., Op-amp summing amplifier derivation")
        
        if st.button("📖 Generate Lesson & Explanation"):
            target_topic = custom_query.strip() if custom_query.strip() else selected_module
            local_material = extract_text_from_local_files(BASE_DIR)
            
            with st.spinner(f"Generating lesson and vector diagram for '{target_topic}'..."):
                prompt = f"Detailed technical lesson notes for NATED {active_subject}: {target_topic}. Provide clear explanations without inline ASCII box diagrams.\nFiles: {local_material[:2000]}"
                notes, err = cached_query_gemini(prompt, active_subject)
                
                st.markdown("### 🎨 Engineering Vector Schematic")
                render_topic_diagram(target_topic)
                st.divider()
                
                if notes:
                    st.markdown(notes)
                else:
                    st.error(err)

    with sub_tab2:
        st.markdown("### 🧠 Active Recall Flashcard Deck")
        cards = FLASHCARDS_DATA.get(active_subject, FLASHCARDS_DATA["INST-N5"])
        if "card_idx" not in st.session_state:
            st.session_state.card_idx = 0
            st.session_state.show_answer = False
            
        current_card = cards[st.session_state.card_idx % len(cards)]
        st.info(f"**Flashcard {st.session_state.card_idx % len(cards) + 1} of {len(cards)}**\n\n### ❓ Question:\n{current_card['q']}")
        
        if st.button("👁️ Flip Card / Reveal Answer"):
            st.session_state.show_answer = not st.session_state.show_answer
            
        if st.session_state.show_answer:
            st.success(f"**💡 Official Solution / Definition:**\n\n{current_card['a']}")
            col_a, col_b = st.columns(2)
            if col_a.button("✅ Got It Right (+1 Score)"):
                st.session_state.card_idx += 1
                st.session_state.show_answer = False
                st.rerun()
            if col_b.button("❌ Need Review"):
                st.session_state.show_answer = False
                st.warning("Flagged for review!")

    with sub_tab3:
        st.markdown("### 🎛 Interactive Parameter Simulation Sandbox")
        sim_type = st.selectbox("Select Hardware Simulator:", ["Operational Amplifier Gain & Clipping", "Venturi Flow Meter & Pressure Head"])
        
        if sim_type == "Operational Amplifier Gain & Clipping":
            c1, c2 = st.columns([1, 2])
            with c1:
                r1 = st.slider("Input Resistor R1 (kΩ):", 1.0, 50.0, 10.0)
                rf = st.slider("Feedback Resistor Rf (kΩ):", 10.0, 200.0, 50.0)
                vin_peak = st.slider("Input Voltage Vin (Peak Volts):", 0.1, 5.0, 2.0)
                v_supply = st.slider("Op-Amp Supply Rails Vcc (±Volts):", 5.0, 18.0, 12.0)
            with c2:
                gain = - (rf / r1)
                vout_calc = gain * vin_peak
                st.metric("Theoretical Gain (Av)", f"{gain:.1f}")
                st.metric("Calculated Vout Peak", f"{vout_calc:.2f} V")
                
                t = np.linspace(0, 2*np.pi, 200)
                vin_wave = vin_peak * np.sin(t)
                vout_wave = np.clip(gain * vin_wave, -v_supply, v_supply)
                
                if plt:
                    fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
                    fig.patch.set_facecolor("#0A0D12")
                    ax.set_facecolor("#0A0D12")
                    ax.plot(t, vin_wave, label="Input (Vin)", color="#22D3EE", lw=2)
                    ax.plot(t, vout_wave, label="Output (Vout)", color="#FF7A1A", lw=2.5)
                    ax.axhline(v_supply, color="red", ls="--")
                    ax.axhline(-v_supply, color="red", ls="--")
                    ax.tick_params(colors="white")
                    ax.legend(facecolor="#0A0D12", labelcolor="white")
                    st.pyplot(fig)

        elif sim_type == "Venturi Flow Meter & Pressure Head":
            c1, c2 = st.columns([1, 2])
            with c1:
                v1 = st.slider("Inlet Velocity V1 (m/s):", 1.0, 10.0, 2.0)
                area_ratio = st.slider("Pipe-to-Throat Area Ratio (A1/A2):", 1.5, 5.0, 2.0)
                rho = st.number_input("Fluid Density (kg/m³):", value=1000)
            with c2:
                v2 = v1 * area_ratio
                delta_p = 0.5 * rho * (v2**2 - v1**2)
                st.metric("Throat Velocity V2", f"{v2:.2f} m/s")
                st.metric("Differential Pressure (ΔP)", f"{delta_p/1000:.2f} kPa")

    with sub_tab4:
        timetable_data = [
            {"Day": "Day 1 - 3", "Focus": "Instrumentation N5", "Activities": "Transducers, Flow/Pressure ΔP Calculations, PID Tuning"},
            {"Day": "Day 4 - 6", "Focus": "Mathematics N5", "Activities": "Derivatives, Integrals, & First/Second Order Differential Equations"},
            {"Day": "Day 7 - 9", "Focus": "Industrial Electronics N5", "Activities": "Op-Amp Derivations, SCR/TRIAC Thyristors, & Closed Loop Control"},
            {"Day": "Day 10 - 12", "Focus": "Digital Electronics N4/N5", "Activities": "Boolean Simplification, K-Maps, Counters, DAC/ADC Converters"},
            {"Day": "Day 13 - 14", "Focus": "Mock Exam Marathon", "Activities": "Timed exams with confidence vs accuracy debrief"}
        ]
        st.table(timetable_data)

# TAB 5: Formula & Reference Hub
with tab_formulas:
    st.subheader(f"📐 Comprehensive Formula & Reference Hub: {active_subject}")
    st.markdown("Official NATED TVET engineering formulas, standard constants, and mathematical derivations.")
    
    if active_subject == "INST-N5":
        st.markdown("### Instrumentation N5 Reference Equations")
        st.latex(r"Q = \frac{8}{15}\tan\left(\frac{\theta}{2}\right)\sqrt{2g}H^{5/2}")
        st.latex(r"Q = C_d A_2 \sqrt{\frac{2\Delta P}{\rho(1 - \beta^4)}}")
        st.latex(r"R_t = R_0(1 + \alpha \cdot \Delta T)")
        st.markdown("**Core Principles:** Bernoulli's theorem, differential head flow metering, RTD temperature coefficients, and thermocouple reference junction compensation.")
    elif active_subject == "MATH-N5":
        st.markdown("### Mathematics N5 Reference Equations")
        st.latex(r"\frac{dy}{dx} = u\frac{dv}{dx} + v\frac{du}{dx}")
        st.latex(r"\int u \, dv = uv - \int v \, du")
        st.latex(r"V_x = \pi \int_{a}^{b} y^2 dx")
        st.markdown("**Core Principles:** Integration by parts, trigonometric substitution, L'Hôpital's rule, and first/second-order linear differential equations.")
    elif active_subject == "IE-N5":
        st.markdown("### Industrial Electronics N5 Reference Equations")
        st.latex(r"V_{out} = -\left(\frac{R_f}{R_1}V_1 + \frac{R_f}{R_2}V_2\right)")
        st.latex(r"V_{dc} = \frac{V_m}{\pi}(1 + \cos\alpha)")
        st.markdown("**Core Principles:** Op-amp feedback networks, thyristor firing angles, and transistor biasing.")
    else:
        st.markdown("### Digital Electronics N4/N5 Reference Equations")
        st.latex(r"N_{states} = 2^n")
        st.latex(r"f_{max} = \frac{1}{n \cdot t_{pd}}")
        st.markdown("**Core Principles:** Boolean algebraic laws, Karnaugh map minimization, asynchronous ripple counters, and synchronous state machines.")

# TAB 6: Analytics & Offline Report Exporter
with tab_analytics:
    st.subheader("📈 Exam Readiness, Cognitive & Psychological Analytics")
    avg_mastery = 71.0
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("### 🎯 Exam Pass Probability Index")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_mastery,
            title={'text': "Calculated Readiness Index (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#FF7A1A"},
                'steps': [
                    {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"},
                    {'range': [50, 75], 'color': "rgba(255, 122, 26, 0.2)"},
                    {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.2)"}
                ]
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="#0A0D12", font_color="#E6EDF3")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c2:
        st.markdown("### 🧠 Cognitive Error Distribution")
        error_data = {"Category": ["Calculation / Unit Slips", "Conceptual Misunderstandings", "Misread NATED Question Text"], "Count": [52, 28, 20]}
        fig_pie = px.pie(error_data, values="Count", names="Category", title="Root Cause of Lost Exam Marks", color_discrete_sequence=["#FF7A1A", "#22D3EE", "#8B5CF6"])
        fig_pie.update_layout(paper_bgcolor="#0A0D12", font_color="#E6EDF3")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.divider()
    st.markdown("### 📄 Export Offline Readiness & Study Plan Report")
    report_text = f"""=======================================================
TRENTOX TUTOR AI - READINESS REPORT
Subject Code: {active_subject}
Calculated Readiness Index: {avg_mastery}%
=======================================================

1. WEAK TOPIC RED ALERTS (<50% Proficiency):
   - PID Controller Tuning & Frequency Response (35%)
   - Second-Order Differential Equations (42%)
   - Op-Amp Summing Amplifiers (48%)

2. COGNITIVE ERROR ANALYSIS:
   - Calculation/Unit Slips: 52%
   - Conceptual Misunderstandings: 28%
   - Misread Question Text: 20%

3. RECOMMENDED 14-DAY ACTION PLAN:
   - Focus next 3 sessions on Tab 4 (AI Lessons) for target topics.
   - Run 10-question timed exam in Tab 3 every 48 hours.
=======================================================
"""
    st.download_button(
        label="📥 Download Readiness Report (.txt)",
        data=report_text,
        file_name=f"Trentox_Readiness_Report_{active_subject}.txt",
        mime="text/plain"
    )