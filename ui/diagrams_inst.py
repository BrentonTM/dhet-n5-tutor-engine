"""Instrumentation N5 – 3D diagrams."""
import math

from ui.diagram_lib import *
from ui.diagram_registry import reg

GLASS = "#E6EDF3"


def _tube(x, y0, y1, **kw):
    return cyl([x, (y0 + y1) / 2, 0], 0.13, y1 - y0, GLASS, open=True, opacity=0.25, **kw)


# --------------------------------------------------------------------------- flow
@reg("venturi", "Venturi meter – Bernoulli & differential pressure")
def venturi():
    R, r2 = 1.0, 2 / 3
    drop = "clamp(0.28*(p.v1*p.v1*(2.25*2.25-1))/19.62,0,1.8)"
    o = [
        lathe([0, 0, 0], [[R, -6], [R, -3], [r2, -1.2], [r2, 0.8], [R, 3.2], [R, 6]], CY, opacity=0.28,
              rot=[0, 0, -90], label="Venturi tube", la=[3.6, -1.5, 0], lp=[0, 0, 0],
              info="Converging inlet cone, narrow throat, gradual diffuser. Speed rises in the throat so static pressure falls (Bernoulli). Pressure is mostly recovered in the diffuser."),
        _tube(-3.6, 1.0, 3.4), _tube(-0.2, 0.667, 3.4),
        cyl([-3.6, 2.0, 0], 0.09, 2.0, BL, emissive=0.25, label="P₁", lp=[0, 1.5, 0],
            info="Static pressure head at the inlet (high pressure, low velocity)."),
        cyl([-0.2, 2.0, 0], 0.09, 1.0, BL, emissive=0.25, label="P₂", lp=[0, 1.9, 0],
            info="Static pressure head at the throat. It drops as velocity rises. The height difference is the differential pressure ΔP.",
            bind={"scale.y": "3.0-" + drop + "-0.667", "pos.y": "0.667+(3.0-" + drop + "-0.667)/2"}),
        line([[-3.6, 3.0, 0], [-0.2, 3.0, 0]], "#8B949E"),
        text([0.5, 2.6, 0], "Δh", YL, 0.42, bind={"pos.y": "3.0-" + drop + "/2"}),
        arrow([-6.8, 0, 0], [-5.9, 0, 0], OR), text([-6.9, 0.5, 0], "Flow", OR, 0.36),
        sphere([-4.8, 1.25, 0], 0.1, OR, label="Inlet (A₁)", lp=[0, 0.45, 0], info="Full pipe diameter D₁ = 100 mm. Velocity V₁."),
        sphere([-0.2, -0.95, 0], 0.1, OR, label="Throat (A₂)", lp=[0, -0.5, 0], info="Throat diameter D₂ ≈ 67 mm so A₁/A₂ = 2.25. V₂ = 2.25 × V₁."),
        sphere([2.2, 1.25, 0], 0.1, OR, label="Diffuser", lp=[0, 0.45, 0], info="Gradual 7°–15° expansion that recovers most of the pressure and keeps permanent loss small."),
    ]
    for yo in (-0.35, 0.0, 0.35):
        o.append(flow([[-5.8, yo, 0], [-1.4, yo, 0]], CY, 7, "p.v1*0.6", 0.12))
        o.append(flow([[-1.4, yo, 0], [-1.2, yo * 0.667, 0], [0.9, yo * 0.667, 0]], OR, 4, "p.v1*2.25*0.6", 0.12))
        o.append(flow([[0.9, yo * 0.667, 0], [3.4, yo, 0], [5.8, yo, 0]], CY, 5, "p.v1*0.6", 0.12))
    return spec("Venturi meter", o, "Continuity A₁V₁ = A₂V₂ and Bernoulli: P₁ + ½ρV₁² = P₂ + ½ρV₂²",
                [param("v1", "Inlet velocity V₁", 1, 5, 2, 0.1, "m/s")],
                [readout("Throat velocity V₂ = V₁·A₁/A₂", "(p.v1*2.25).toFixed(2)+' m/s'"),
                 readout("ΔP = ½ρ(V₂² − V₁²)", "(0.5*(p.v1*p.v1*(2.25*2.25-1))).toFixed(2)+' kPa (water)'"),
                 readout("Flow Q = A₁V₁ (D₁ = 100 mm)", "(7.854*p.v1).toFixed(2)+' L/s'")],
                cam=(2.5, 3.2, 12.5), target=(-0.5, 0.8, 0))


@reg("orifice", "Orifice plate flow meter")
def orifice():
    drop = "0.018*p.Q*p.Q"
    o = [
        cyl([0, 0, 0], 1.0, 12, CY, axis="x", open=True, opacity=0.2, label="Pipe", lp=[-3.5, -1.5, 0]),
        lathe([0, 0, 0], [[0.45, -0.09], [1.0, -0.09], [1.0, 0.09], [0.45, 0.09]], ST, rot=[0, 0, 90],
              label="Orifice plate", lp=[0, -1.6, 0],
              info="A thin plate with a sharp-edged hole. The stream contracts to the vena contracta just after the plate where velocity is highest and pressure lowest."),
        _tube(-0.9, 1.0, 3.4), _tube(0.9, 1.0, 3.4),
        cyl([-0.9, 2.0, 0], 0.09, 2.0, BL, emissive=0.25, label="P₁ (upstream)", lp=[-0.2, 1.5, 0], info="Upstream tapping: higher pressure."),
        cyl([0.9, 2.0, 0], 0.09, 1.0, BL, emissive=0.25, label="P₂ (downstream)", lp=[0.3, 1.9, 0],
            info="Downstream tapping: lower pressure. ΔP = P₁ − P₂ is proportional to Q².",
            bind={"scale.y": "2.0-" + drop, "pos.y": "1.0+(2.0-" + drop + ")/2"}),
        arrow([-6.8, 0, 0], [-5.9, 0, 0], OR), text([-6.9, 0.5, 0], "Flow", OR, 0.36),
    ]
    for yo in (-0.6, -0.3, 0, 0.3, 0.6):
        o.append(flow([[-5.8, yo, 0], [-0.6, yo, 0], [0.25, yo * 0.45, 0], [1.6, yo * 0.45, 0], [3.2, yo, 0], [5.8, yo, 0]],
                      CY, 14, "p.Q*0.5", 0.1))
    return spec("Orifice plate meter", o, "Q = Cd·A₂·√(2ΔP / ρ(1 − β⁴)) – square-root relationship",
                [param("Q", "Flow rate Q", 1, 10, 4, 0.1, "L/s")],
                [readout("Differential pressure ΔP", "(0.316*p.Q*p.Q).toFixed(2)+' kPa'"),
                 readout("Velocity in pipe V₁ (D = 100 mm)", "(p.Q/7.854).toFixed(2)+' m/s'"),
                 readout("Velocity through hole V₂ (d = 50 mm)", "(p.Q/1.9635).toFixed(2)+' m/s'"),
                 readout("Rule", "'Q ∝ √ΔP  (ΔP ∝ Q²)'")],
                cam=(2, 3, 12.5), target=(0, 0.8, 0))


@reg("weir", "V-notch weir (open-channel flow)")
def weir():
    notch = [[-3, 0], [3, 0], [3, 3], [1.6, 3], [0, 1.4], [-1.6, 3], [-3, 3]]
    o = [
        box([-1.5, -0.1, 0], [15, 0.2, 6.2], DK),
        {"type": "prism", "poly": notch, "depth": 0.3, "p": [0, 0, 0], "rot": [0, 90, 0], "color": ST,
         "label": "V-notch plate", "lp": [0.5, 3.5, 0],
         "info": "Thin plate with a 90° V-notch. Water spills through the notch; the head H above the notch apex sets the flow Q ∝ H^2.5."},
        box([-4.5, 0.7, 0], [9, 1, 6], BL, opacity=0.4, label="Upstream water", lp=[-3, 3.5, 0],
            info="Still water behind the weir. Measure H at least 3H upstream of the notch.",
            bind={"scale.y": "1.4+4*p.H", "pos.y": "(1.4+4*p.H)/2"}),
        box([2.6, 0.1, 0], [4, 0.15, 6], BL, opacity=0.35),
        cyl([-0.6, 1.4, 0], 0.035, 1.0, YL, label="H", lp=[-0.5, 0, 0], info="Head H measured from the notch apex to the water surface.",
            bind={"scale.y": "4*p.H", "pos.y": "1.4+2*p.H"}),
        sphere([0, 1.4, 0], 0.09, OR, label="Notch apex", lp=[0.2, -0.4, 0.8], info="Zero reference for the head H."),
    ]
    for z in (-0.7, 0, 0.7):
        o.append(flow([[0.0, 1.55, z * 0.5], [0.8, 1.45, z], [1.8, 0.6, z * 1.4], [2.6, 0.15, z * 1.7]], CY, 8, "1.2+p.H*4", 0.1))
    return spec("V-notch weir", o, "Q = (8/15)·Cd·tan(θ/2)·√(2g)·H^2.5   (θ = notch angle)",
                [param("H", "Head H above notch apex", 0.05, 0.4, 0.2, 0.01, "m")],
                [readout("Flow Q (θ = 90°, Cd = 0.6)", "(1417.4*pow(p.H,2.5)).toFixed(1)+' L/s'"),
                 readout("If H doubles, Q increases by", "pow(2,2.5).toFixed(2)+' ×'")],
                cam=(-5, 5, 12), target=(0, 1.2, 0))


@reg("target_flow", "Target (drag-plate) flow meter")
def target_flow():
    o = [
        cyl([0, 0, 0], 1.2, 12, CY, axis="x", open=True, opacity=0.18),
        cyl([0, 0, 0], 0.6, 0.12, OR, axis="x", bind={"pos.x": "0.03*p.v*p.v"}, label="Target disc", lp=[0, -1.0, 0],
            info="Fluid drag pushes the disc downstream. Force F = Cd·½ρV²·A, so F ∝ V²."),
        cyl([0, 1.7, 0], 0.06, 2.2, ST, bind={"pos.x": "0.03*p.v*p.v"}, label="Rod", lp=[0.7, 0, 0], info="Transfers the drag force to the sensor."),
        box([0, 3.1, 0], [1.2, 0.7, 0.7], GR, label="Force sensor", lp=[0, 0.8, 0],
            info="Strain gauges or a force-balance bridge convert the drag force into an electrical signal."),
        arrow([-6.8, 0, 0], [-5.9, 0, 0], OR), text([-6.9, 0.5, 0], "Flow", OR, 0.36),
    ]
    for yo in (-0.95, -0.7, 0.7, 0.95):
        o.append(flow([[-5.8, yo, 0], [-1.0, yo, 0], [0, yo * 1.1, 0], [1, yo, 0], [5.8, yo, 0]], CY, 12, "p.v*0.8", 0.1))
    return spec("Target flow meter", o, "Good for dirty, viscous or slurry flows – no small orifice to block",
                [param("v", "Fluid velocity v", 0.5, 6, 2, 0.1, "m/s")],
                [readout("Drag force F (Cd 1.15, d = 60 mm, water)", "(1.6255*p.v*p.v).toFixed(2)+' N'"),
                 readout("Rule", "'F ∝ v²  → v ∝ √F'")],
                cam=(3, 3.5, 11), target=(0, 1, 0))


# ------------------------------------------------------------------------ pressure
@reg("manometer", "U-tube manometer (P = ρgh)")
def manometer():
    sg = "(p.f<0.5?1:(p.f<1.5?0.8:13.6))"
    gn = "(p.f<1.5?0.45:6.0)"
    d = "clamp(" + gn + "*p.P/(" + sg + "*9.81)/2,0,1.8)"
    o = [
        cyl([-1.2, 1.1, 0], 0.16, 6.2, GLASS, open=True, opacity=0.22, label="Leg 1 (pressure applied)", lp=[0, 3.8, 0]),
        cyl([1.2, 1.1, 0], 0.16, 6.2, GLASS, open=True, opacity=0.22, label="Leg 2 (open to atmosphere)", lp=[0, 3.8, 0]),
        cyl([0, -2, 0], 0.16, 2.4, GLASS, axis="x", open=True, opacity=0.22),
        cyl([0, -2, 0], 0.1, 2.4, BL, axis="x", emissive=0.25),
        cyl([-1.2, -1, 0], 0.1, 1.0, BL, emissive=0.25, label="Level 1", lp=[-1.0, 0, 0], info="Pushed down by the applied pressure.",
            bind={"scale.y": "2-" + d, "pos.y": "-2+(2-" + d + ")/2"}),
        cyl([1.2, 0, 0], 0.1, 1.0, BL, emissive=0.25, label="Level 2", lp=[1.0, 0, 0], info="Pushed up. The level difference is Δh = P/(ρg).",
            bind={"scale.y": "2+" + d, "pos.y": "-2+(2+" + d + ")/2"}),
        line([[-1.8, 0, 0], [1.8, 0, 0]], "#8B949E"),
        text([2.0, 0.0, 0], "zero", "#8B949E", 0.3),
        arrow([-1.2, 4.6, 0], [-1.2, 3.4, 0], OR), text([-1.2, 5.0, 0], "P applied", OR, 0.36),
    ]
    return spec("U-tube manometer", o, "Gauge pressure P = ρ·g·Δh  (visual scale differs per fluid)",
                [param("P", "Applied gauge pressure", 0, 40, 10, 0.5, "kPa"),
                 param("f", "Manometer fluid", 0, 2, 0, 1, names=["Water (SG 1.0)", "Oil (SG 0.8)", "Mercury (SG 13.6)"])],
                [readout("Level difference Δh = P/(ρg)", "(p.P/(" + sg + "*9.81)*1000).toFixed(0)+' mm'"),
                 readout("Why mercury?", "'Dense fluid → small Δh for large P'")],
                cam=(3, 2.5, 11), target=(0, 0.8, 0))


@reg("bourdon", "Bourdon tube pressure gauge")
def bourdon():
    o = [cyl([0, 0, 0], 2.3, 0.2, DK, axis="z"), torus([0, 0, 0.1], 2.3, 0.08, LG)]
    for i in range(11):
        a = 225 - 27 * i
        o.append(box([1.95 * math.cos(math.radians(a)), 1.95 * math.sin(math.radians(a)), 0.12], [0.06, 0.22, 0.04], WH, rot=[0, 0, a - 90]))
        if i % 2 == 0:
            o.append(text([1.5 * math.cos(math.radians(a)), 1.5 * math.sin(math.radians(a)), 0.2], str(i * 100), "#8B949E", 0.2))
    tip_a = "(500-0.5*p.P)*PI/180"
    o += [
        arc([0, 0, 0.3], 1.1, 250, "250+250-0.5*p.P", 0.11, OR, label="Bourdon tube", lp=[0, 1.5, 0.5], lsize=0.22,
            info="Flattened, curved (C-shaped) tube sealed at one end. Pressure tries to straighten it; the free end moves in proportion to pressure."),
        sphere([0, 0, 0.3], 0.17, YL, label="Free end", lp=[0.1, 0.45, 0.3], lsize=0.22, info="Free end movement is tiny; the link and sector gear magnify it into needle rotation.",
               bind={"pos.x": "1.1*cos(" + tip_a + ")", "pos.y": "1.1*sin(" + tip_a + ")"}),
        cyl([0, 0, 0.5], 0.035, 1.8, RD, bind={"pos.x": "0.9*cos((225-2.7*p.P)*PI/180)", "pos.y": "0.9*sin((225-2.7*p.P)*PI/180)", "rot.z": "225-2.7*p.P-90"}),
        sphere([0, 0, 0.5], 0.14, ST, label="Pointer", lp=[0.5, -0.3, 0.3], lsize=0.22, info="Driven by link + sector gear + pinion from the tube tip."),
        cyl([-0.376, -1.5, 0.3], 0.22, 0.97, ST, label="Pressure inlet", lp=[-1.2, -0.2, 0.3], lsize=0.22, info="Process pressure enters here. Gauge reads pressure above atmospheric."),
    ]
    return spec("Bourdon tube gauge", o, "Elastic element: tube straightens as pressure rises",
                [param("P", "Pressure (% of range)", 0, 100, 50, 1, "%")],
                [readout("Gauge reading (0–1000 kPa)", "(p.P*10).toFixed(0)+' kPa'"),
                 readout("Tube sweep angle", "(250-0.5*p.P).toFixed(0)+'°'")],
                cam=(1.5, 1.2, 8.5))


@reg("strain_gauge", "Strain gauge on a cantilever beam")
def strain_gauge():
    A = "(p.F*0.6*PI/180)"
    o = [
        box([-0.35, 0, 0], [0.7, 3, 2.5], DK, label="Fixed support", lp=[-0.2, 2.0, 0]),
        box([3, 0, 0], [6, 0.4, 1.2], ST, label="Cantilever beam", lp=[0, 1.1, 0], info="Load bends the beam: top surface stretches (tension), bottom compresses.",
            bind={"pos.x": "3*cos" + A, "pos.y": "-3*sin" + A, "rot.z": "-p.F*0.6"}),
        box([1, 0.23, 0], [1.4, 0.04, 0.9], OR, emissive=0.5, label="Gauge (tension)", lp=[0, 0.55, 0.8],
            info="Foil grid stretched → longer, thinner → resistance rises: ΔR/R = GF·ε.",
            bind={"pos.x": "1.0*cos" + A + "+0.23*sin" + A, "pos.y": "-1.0*sin" + A + "+0.23*cos" + A, "rot.z": "-p.F*0.6"}),
        box([1, -0.23, 0], [1.4, 0.04, 0.9], CY, emissive=0.5, label="Gauge (compression)", lp=[0, -0.55, 0.8],
            info="Gauge on the compressed face – resistance falls. Used in a half bridge to double the output.",
            bind={"pos.x": "1.0*cos" + A + "-0.23*sin" + A, "pos.y": "-1.0*sin" + A + "-0.23*cos" + A, "rot.z": "-p.F*0.6"}),
        arrow([0, 1.8, 0], [0, 0.45, 0], RD, 0.06, label="Load F", lp=[0.8, 1.0, 0],
              bind={"pos.x": "6*cos" + A, "pos.y": "-6*sin" + A}),
    ]
    return spec("Strain gauge", o, "ε = ΔL/L,   ΔR/R = GF·ε,   read with a Wheatstone bridge",
                [param("F", "Load F at the free end", 0, 10, 4, 0.1, "N")],
                [readout("Strain ε at root", "(37.5*p.F).toFixed(0)+' µε'"),
                 readout("ΔR (R = 120 Ω, GF = 2.1)", "(9.45*p.F).toFixed(1)+' mΩ'"),
                 readout("Quarter-bridge output (Vs = 5 V)", "(0.0984*p.F).toFixed(3)+' mV'")],
                cam=(3.5, 2.5, 10), target=(3, -0.3, 0))


# ---------------------------------------------------------------------- temperature
@reg("rtd_tc", "RTD and thermocouple in a thermowell")
def rtd_tc():
    coil = []
    for i in range(161):
        ang = i * 2 * math.pi * 8 / 160
        coil.append([-2.5 + 0.14 * math.cos(ang), -0.8 + 1.1 * i / 160, 0.14 * math.sin(ang)])
    bar = "0.1+p.T/500*3.4"
    o = [
        cyl([-2.5, 0, 0], 1.7, 3.4, RD, opacity=0.14, label="Hot process", lp=[-1.9, -2.2, 0],
            bind={"color": "p.T>350?'#EF4444':(p.T>150?'#FF7A1A':'#22D3EE')"}),
        cyl([-2.5, 1.0, 0], 0.28, 3.6, LG, opacity=0.5, label="Thermowell", lp=[-1.0, 1.2, 0], info="Protective sleeve that lets the sensor be replaced without opening the process."),
        {"type": "tube", "pts": coil, "r": 0.025, "color": CY, "label": "RTD element", "lp": [1.6, -0.2, 0],
         "info": "Platinum wire coil (PT100: 100 Ω at 0 °C, α = 0.00385/°C). Resistance rises almost linearly with temperature."},
        sphere([-2.5, -0.95, 0], 0.13, OR, label="TC hot junction", lp=[1.7, -0.8, 0], info="Two dissimilar metals welded together. The Seebeck EMF depends on (T_hot − T_cold)."),
        box([-2.5, 2.95, 0], [1.2, 0.6, 1.0], DK, label="Terminal head", lp=[0, 0.7, 0]),
        wire([[-1.9, 3.0, 0], [1.0, 3.0, 0], [1.0, 2.2, 0]], CY, 0.04),
        wire([[-1.9, 2.8, 0], [3.2, 2.8, 0], [3.2, 2.2, 0]], OR, 0.04),
        box([1.0, 1.7, 0], [1.6, 1.0, 0.7], BL, label="RTD bridge / transmitter", lp=[0, -0.8, 0], info="3-wire bridge cancels lead resistance."),
        box([3.2, 1.7, 0], [1.6, 1.0, 0.7], GR, label="Cold-junction compensation", lp=[0, -0.8, 0], info="Measures the reference temperature and adds its EMF back."),
        box([5.4, -1.7, 0], [0.5, 1, 0.5], OR, label="Temperature", lp=[0, 2.2, 0], bind={"scale.y": bar, "pos.y": "-1.7+(" + bar + ")/2", "color": "p.T>350?'#EF4444':(p.T>150?'#FF7A1A':'#22D3EE')"}),
    ]
    return spec("RTD & thermocouple", o, "RTD: Rₜ = R₀(1 + αΔT)      Thermocouple: E ≈ S·(T_hot − T_cold)",
                [param("T", "Process temperature", 0, 500, 200, 1, "°C"), param("Tref", "Reference (cold) junction", 0, 50, 25, 1, "°C")],
                [readout("PT100 resistance", "(100*(1+0.00385*p.T)).toFixed(2)+' Ω'"),
                 readout("Type-K EMF (≈ 41 µV/°C)", "((p.T-p.Tref)*0.041).toFixed(2)+' mV'"),
                 readout("RTD sensitivity", "'0.385 Ω per °C'")],
                cam=(1.5, 2.5, 12), target=(1.2, 0.6, 0))


# ------------------------------------------------------------------- level & chemical
@reg("tank_level", "Tank level: float, DP cell and ultrasonic")
def tank_level():
    o = [
        cyl([-2, 0, 0], 1.6, 4, LG, open=True, opacity=0.18, label="Tank (4 m)", lp=[-1.3, -2.5, 0]),
        cyl([-2, -2.05, 0], 1.6, 0.1, ST),
        cyl([-2, 0, 0], 1.55, 1, BL, opacity=0.5, bind={"scale.y": "4*p.L/100", "pos.y": "-2+2*p.L/100"}, label="Liquid", lp=[0, 0.9, 1.6],
            info="Level h. Hydrostatic pressure at the bottom P = ρgh."),
        sphere([-2, 0, 0], 0.3, OR, bind={"pos.y": "-2+4*p.L/100"}, label="Float", lp=[0.9, 0.3, 0], info="Rises and falls with the surface. Linked mechanically or magnetically to an indicator."),
        cyl([-2, 2.5, 0], 0.35, 0.5, GR, label="Ultrasonic sensor", lp=[1.4, 0.2, 0], info="Sends a pulse down, measures echo time t = 2d/c."),
        cyl([-2, 1, 0], 0.03, 1, CY, opacity=0.5, bind={"scale.y": "4.25-4*p.L/100", "pos.y": "2.25-(4.25-4*p.L/100)/2"}),
        wire([[-0.4, -1.9, 0], [1.6, -1.9, 0]], ST, 0.07),
        box([2.2, -1.9, 0], [1.2, 1.0, 0.9], GR, label="DP transmitter", lp=[0, -1.0, 0], info="High side sees ρgh + tank pressure; low side is vented. Output is proportional to level."),
        wire([[2.2, -1.4, 0], [2.2, -0.6, 0]], ST, 0.05), text([2.2, -0.2, 0], "LP vented", "#8B949E", 0.3),
        box([5, -1, 0], [0.5, 1, 0.5], YL, bind={"scale.y": "0.1+3*p.L/100", "pos.y": "-2+(0.1+3*p.L/100)/2"}, label="4–20 mA", lp=[0, 3.4, 0]),
    ]
    return spec("Level measurement", o, "Hydrostatic head P = ρgh   ·   Ultrasonic: d = ½·c·t",
                [param("L", "Tank level", 0, 100, 60, 1, "%")],
                [readout("Pressure at bottom (water)", "(9.81*4*p.L/100).toFixed(2)+' kPa'"),
                 readout("Transmitter output", "(4+16*p.L/100).toFixed(2)+' mA'"),
                 readout("Ultrasonic echo time", "(2*(4-4*p.L/100)/343*1000).toFixed(2)+' ms'")],
                cam=(2.5, 2, 12), target=(1, 0, 0))


@reg("ph_probe", "pH measurement – glass and reference electrodes")
def ph_probe():
    col = "p.pH<3?'#EF4444':(p.pH<6.5?'#FF7A1A':(p.pH<7.5?'#10B981':(p.pH<11?'#3B82F6':'#8B5CF6')))"
    o = [
        cyl([0, -0.5, 0], 1.7, 3, GLASS, open=True, opacity=0.12, label="Sample", lp=[0, -2.3, 0]),
        cyl([0, -1.0, 0], 1.65, 2, BL, opacity=0.5, bind={"color": col}),
        cyl([-0.7, 0.9, 0], 0.2, 3.4, GLASS, opacity=0.35),
        sphere([-0.7, -0.85, 0], 0.3, CY, opacity=0.7, label="Glass bulb", lp=[-1.7, -0.3, 0], info="Thin H⁺-sensitive glass membrane. Develops a potential that depends on the pH difference across it."),
        cyl([0.7, 0.9, 0], 0.18, 3.4, GLASS, opacity=0.35, label="Reference electrode", lp=[1.7, 1.2, 0], info="Ag/AgCl (or calomel) half-cell with constant potential."),
        sphere([0.7, -0.8, 0], 0.1, YL, label="Porous junction", lp=[1.6, -0.2, 0], info="Lets the KCl electrolyte make electrical contact with the sample."),
        line([[-0.7, -0.7, 0], [-0.7, 2.4, 0]], LG, 0.025),
        wire([[-0.7, 2.6, 0], [-0.7, 3.3, 0], [3.0, 3.3, 0], [3.0, 2.8, 0]], CY, 0.04),
        wire([[0.7, 2.6, 0], [0.7, 2.9, 0], [3.8, 2.9, 0], [3.8, 2.8, 0]], OR, 0.04),
        box([3.4, 2.3, 0], [2.4, 1, 0.5], DK, label="pH meter (high impedance)", lp=[0, 1.0, 0], info="Glass electrode impedance is 10–1000 MΩ, so the meter input must be very high impedance."),
        sphere([3.4, 2.2, 0.3], 0.1, YL, bind={"pos.x": "3.4+(p.pH-7)*0.15"}),
    ]
    return spec("pH electrode system", o, "pH = −log₁₀[H⁺]     pH + pOH = 14     Nernst slope ≈ 59.16 mV/pH at 25 °C",
                [param("pH", "Sample pH", 0, 14, 4.4, 0.1), param("T", "Temperature", 0, 60, 25, 1, "°C")],
                [readout("[H⁺]", "pow(10,-p.pH).toExponential(2)+' mol/ℓ'"),
                 readout("pOH", "(14-p.pH).toFixed(1)"),
                 readout("[OH⁻]", "pow(10,p.pH-14).toExponential(2)+' mol/ℓ'"),
                 readout("Electrode EMF", "((7-p.pH)*0.19841*(p.T+273.15)).toFixed(1)+' mV'")],
                cam=(3, 2.5, 11), target=(1, 0.5, 0))


# --------------------------------------------------------------------------- control
@reg("pid_loop", "Closed-loop PID control")
def pid_loop():
    P_ = "p.Kp*p.e"
    I_ = "p.Kp*p.e*5/p.Ti"
    D_ = "p.Kp*p.Td*p.de"
    o = [
        sphere([-7.2, 1.5, 0], 0.35, GR, label="Setpoint (SP)", lp=[0, 0.7, 0], info="The desired value of the process variable."),
        arrow([-6.8, 1.5, 0], [-5.3, 1.5, 0], OR),
        sphere([-4.8, 1.5, 0], 0.45, YL, label="Σ  e = SP − PV", lp=[0, 0.85, 0], info="Comparator: error = setpoint − measured value."),
        arrow([-4.3, 1.5, 0], [-3.5, 1.5, 0], OR),
    ]
    for x, nm, expr, inf in ((-3.0, "P", P_, "Proportional: output ∝ error (Kp·e). Fast response but leaves an offset."),
                             (-2.3, "I", I_, "Integral: removes offset by accumulating error (shown after 5 s)."),
                             (-1.6, "D", D_, "Derivative: reacts to the rate of change of error – damps overshoot.")):
        hh = "clamp(abs(" + expr + ")*0.06,0.05,2.6)"
        o.append(box([x, 0.7, 0], [0.5, 1, 0.5], GR, label=nm, lp=[0, -0.9, 0], info=inf,
                     bind={"scale.y": hh, "pos.y": "0.2+(" + hh + ")/2", "color": "(" + expr + ")>=0?'#10B981':'#EF4444'"}))
    mv = "clamp(50+" + P_ + "+" + I_ + "+" + D_ + ",0,100)"
    o += [
        text([-2.3, 3.2, 0], "PID controller", CY, 0.4),
        arrow([-1.0, 1.5, 0], [0.2, 1.5, 0], OR),
        cone([0.9, 1.5, 0], 0.45, 0.9, OR, axis="x", label="Control valve", lp=[0.4, 0.95, 0], info="Final control element: changes the manipulated variable (flow) according to the controller output."),
        cone([1.5, 1.5, 0], 0.45, 0.9, OR, axis="x", rot=[0, 0, 180]),
        arrow([2.1, 1.5, 0], [3.4, 1.5, 0], OR),
        cyl([4.6, 1.5, 0], 1.0, 2.2, LG, open=True, opacity=0.2, label="Process (tank)", lp=[0, 1.8, 0]),
        cyl([4.6, 1.5, 0], 0.95, 1, BL, opacity=0.5, bind={"scale.y": "2.2*" + mv + "/100", "pos.y": "0.4+1.1*" + mv + "/100"}),
        box([4.6, -1.3, 0], [1.6, 0.8, 0.7], GR, label="Sensor / transmitter", lp=[0, -0.8, 0], info="Measures PV and sends a 4–20 mA signal back to the comparator."),
        wire([[4.6, 0.4, 0], [4.6, -0.9, 0]], ST, 0.05),
        wire([[4.6, -1.7, 0], [4.6, -2.4, 0], [-4.8, -2.4, 0], [-4.8, 1.05, 0]], CY, 0.045, bind={"visible": "p.fb>0.5"}),
        text([0, -2.0, 0], "Feedback path: PV (−)", CY, 0.4, bind={"visible": "p.fb>0.5"}),
        flow([[-7.2, 1.5, 0], [-4.8, 1.5, 0], [-1, 1.5, 0], [0.6, 1.5, 0], [3.6, 1.5, 0]], OR, 16, 1.2, 0.12),
    ]
    return spec("Closed-loop PID control", o, "Output = Kp·[ e + (1/Ti)∫e dt + Td·de/dt ]  + bias",
                [param("fb", "Feedback (closed loop)", 0, 1, 1, 1, toggle=True),
                 param("e", "Error e", -10, 10, 5, 0.5, "%"), param("de", "Error rate de/dt", -5, 5, 0, 0.5, "%/s"),
                 param("Kp", "Proportional gain Kp", 0.5, 5, 2, 0.1), param("Ti", "Integral time Ti", 2, 20, 10, 1, "s"),
                 param("Td", "Derivative time Td", 0, 5, 0.5, 0.1, "s")],
                [readout("P term", "(" + P_ + ").toFixed(1)+' %'"), readout("I term (after 5 s)", "(" + I_ + ").toFixed(1)+' %'"),
                 readout("D term", "(" + D_ + ").toFixed(1)+' %'"),
                 readout("Controller output (50 % bias)", mv + ".toFixed(1)+' %'"),
                 readout("Loop type", "p.fb>0.5?'Closed loop (self-correcting)':'Open loop (no correction!)'")],
                cam=(-1, 3, 15), target=(-1, 0.4, 0))


@reg("step_response", "Controller tuning – step response")
def step_response():
    body = ("var z=p.zeta,w=p.wn,t=x;if(z<0.999){var wd=w*sqrt(1-z*z);return 1-exp(-z*w*t)*(cos(wd*t)+(z/sqrt(1-z*z))*sin(wd*t));}"
            "else if(z<1.001){return 1-exp(-w*t)*(1+w*t);}"
            "else{var s=w*sqrt(z*z-1),s1=-z*w+s,s2=-z*w-s;return 1-(s2*exp(s1*t)-s1*exp(s2*t))/(s2-s1);}")
    o = axes([-4.2, -1.8, 0], 9, 3.6, 0.2, "t (s)", "PV / SP")
    o += [
        plot(body, 0, 10, [-4.2, -1.8, 0], 0.84, 2.4, OR, 220, label="Response", la=[3.5, 0.9, 0], info="Process variable after a step change in setpoint."),
        line([[-4.2, 0.6, 0], [4.2, 0.6, 0]], GR, 0.02, label="Setpoint", la=[4.6, 0.6, 0]),
        line([[-4.2, 0.648, 0], [4.2, 0.648, 0]], YL, 0.01), line([[-4.2, 0.552, 0], [4.2, 0.552, 0]], YL, 0.01),
        text([-3.4, 1.5, 0], "±2 % settling band", YL, 0.3),
        pt("p.zeta<1?PI/(p.wn*sqrt(1-p.zeta*p.zeta)):0", body, 0, [-4.2, -1.8, 0], 0.84, 2.4, RD, 0.12,
           bind={"visible": "p.zeta<0.999"}, label="Peak", lp=[0.5, 0.5, 0], info="Maximum overshoot occurs at tp = π / (ωn√(1−ζ²))."),
    ]
    return spec("Step response vs damping", o, "Low damping → fast but oscillatory.  High damping → slow but safe.",
                [param("zeta", "Damping ratio ζ", 0.1, 2, 0.4, 0.05), param("wn", "Natural frequency ωₙ", 0.5, 3, 1.5, 0.1, "rad/s")],
                [readout("% overshoot", "p.zeta<1?(100*exp(-PI*p.zeta/sqrt(1-p.zeta*p.zeta))).toFixed(1)+' %':'0 %'"),
                 readout("Peak time tp", "p.zeta<1?(PI/(p.wn*sqrt(1-p.zeta*p.zeta))).toFixed(2)+' s':'—'"),
                 readout("Settling time (2 %) ≈ 4/(ζωₙ)", "(4/(p.zeta*p.wn)).toFixed(2)+' s'")],
                cam=(0, 1.5, 12.5), target=(0, 0, 0))
