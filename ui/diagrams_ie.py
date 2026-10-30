"""Industrial Electronics N5 – 3D diagrams."""
import math

from ui.diagram_lib import *
from ui.diagram_registry import reg


# ------------------------------------------------------------------ Module 1: AC theory
@reg("phasor", "Series RLC impedance and phasor diagram")
def phasor():
    k, ox, oy = 0.05, -3.2, -0.2
    X = "(p.XL-p.XC)"
    Z = "sqrt(p.R*p.R+" + X + "*" + X + ")"
    ex = f"{ox}+{k}*p.R"
    o = [
        line([[ox - 0.3, oy, 0], [ox + 6.2, oy, 0]], "#4B5563"), line([[ox, oy - 3, 0], [ox, oy + 4.3, 0]], "#4B5563"),
        text([ox + 6.5, oy - 0.3, 0], "R", "#8B949E", 0.3), text([ox + 0.3, oy + 4.5, 0], "+j", "#8B949E", 0.3),
        vec([ox, oy, 0], [ex, oy, 0], GR, 0.05, label="R", lp=[0, -0.45, 0], info="Resistance: voltage in phase with current (along the real axis)."),
        vec([ex, oy, 0], [ex, f"{oy}+{k}*p.XL", 0], VI, 0.05, label="XL", lp=[0.5, 0, 0], info="Inductive reactance XL = 2πfL. Voltage leads current by 90° (+j)."),
        vec([ex, f"{oy}+{k}*p.XL", 0], [ex, f"{oy}+{k}*{X}", 0], BL, 0.05, label="XC", lp=[0.5, 0, 0], info="Capacitive reactance XC = 1/(2πfC). Voltage lags current by 90° (−j). It subtracts from XL."),
        vec([ox, oy, 0], [ex, f"{oy}+{k}*{X}", 0], OR, 0.065, label="Z", lp=[-0.5, 0.4, 0], info="Impedance Z = R + j(XL − XC). Its length is |Z| and its angle is the phase angle θ."),
        arc([ox, oy, 0], 1.0, 0, "atan2(" + X + ",p.R)*180/PI", 0.03, YL, label="θ", la=[ox + 1.3, oy + 0.25, 0]),
        text([ox + 2.5, oy + 3.4, 0], "RESONANCE: XL = XC", YL, 0.4, bind={"visible": "abs(" + X + ")<1.5"}),
    ]
    for i, (nm, col, e) in enumerate((("R", GR, "p.R"), ("XL", VI, "p.XL"), ("XC", BL, "p.XC"))):
        x = 3.0 + i * 1.1
        h = f"(0.035*{e}+0.05)"
        o.append(box([x, -2.0, 0], [0.6, 1, 0.6], col, bind={"scale.y": h, "pos.y": f"-2.4+{h}/2"}))
        o.append(text([x, -2.75, 0], nm, col, 0.3))
    return spec("Series RLC – impedance triangle", o, "Z = R + j(XL − XC),   |Z| = √(R² + X²),   θ = tan⁻¹(X/R)",
                [param("R", "Resistance R", 10, 100, 40, 1, "Ω"), param("XL", "Inductive reactance XL", 0, 100, 80, 1, "Ω"),
                 param("XC", "Capacitive reactance XC", 0, 100, 50, 1, "Ω"), param("V", "Supply voltage V", 10, 240, 100, 5, "V")],
                [readout("Net reactance X = XL − XC", X + ".toFixed(1)+' Ω'"), readout("Impedance |Z|", Z + ".toFixed(2)+' Ω'"),
                 readout("Phase angle θ", "(atan2(" + X + ",p.R)*180/PI).toFixed(1)+'°'"),
                 readout("Current I = V/Z", "(p.V/" + Z + ").toFixed(3)+' A'"),
                 readout("Power factor cos θ = R/Z", "(p.R/" + Z + ").toFixed(3)"),
                 readout("Circuit is", "abs(" + X + ")<1.5?'resistive (resonance)':(" + X + ">0?'inductive (I lags V)':'capacitive (I leads V)')")],
                cam=(0.5, 1.2, 12.5), target=(0.3, 0.2, 0))


@reg("rc_response", "RC differentiator and integrator")
def rc_response():
    body = ("var tau=p.tau,a=exp(-0.5/tau),VH=1/(1+a),VL=a/(1+a),u=x-floor(x);"
            "var vc=u<0.5?1-(1-VL)*exp(-u/tau):VH*exp(-(u-0.5)/tau);"
            "return p.mode>0.5?vc:((u<0.5?1:0)-vc);")
    o = [
        line([[-4.2, 1.0, 0], [4.2, 1.0, 0]], "#4B5563"), line([[-4.2, -1.9, 0], [4.2, -1.9, 0]], "#4B5563"),
        plot("(x-floor(x))<0.5?1:0", 0, 3, [-4, 1.0, 0], 2.6, 1.5, CY, 360, 0.04, label="Vin (square wave)", la=[-3.4, 3.0, 0], lsize=0.28),
        plot(body, 0, 3, [-4, -1.9, 0], 2.6, 1.4, OR, 360, 0.04, label="Vout", la=[-3.4, -0.2, 0], lsize=0.28,
             info="Integrator: output across C (rounded edges). Differentiator: output across R = Vin − Vc (spikes)."),
        text([4.6, 1.0, 0], "0", "#8B949E", 0.26), text([4.7, -1.9, 0], "0", "#8B949E", 0.26),
    ]
    return spec("RC wave-shaping (T = 1 period)", o, "Integrator: τ = RC ≫ T.   Differentiator: τ = RC ≪ T.",
                [param("tau", "Time constant τ = RC (in periods T)", 0.02, 5, 0.5, 0.01),
                 param("mode", "Integrator (ON) / Differentiator (OFF)", 0, 1, 1, 1, toggle=True)],
                [readout("τ / T", "p.tau.toFixed(2)"),
                 readout("Behaviour", "p.mode>0.5?(p.tau>2?'Good integrator (triangle wave)':(p.tau<0.1?'Output just follows input':'Partial integration (rounded edges)')):(p.tau<0.1?'Good differentiator (sharp spikes)':(p.tau>2?'Output ≈ input (no differentiation)':'Partial differentiation (tilted tops)'))"),
                 readout("Rule of thumb", "'Differentiator: τ ≤ T/10   Integrator: τ ≥ 10T'")],
                cam=(0, 0.5, 13), target=(0, -0.3, 0), grid_y=-3.6)


# ------------------------------------------------------------------ Module 2: power supplies
@reg("rectifier", "Rectifier and capacitor filter")
def rectifier():
    body = ("var s=sin(x);var rect=p.full>0.5?abs(s):max(s,0);if(p.tau<0.3)return rect;"
            "var per=p.full>0.5?PI:2*PI;var ang=((x-PI/2)%per+per)%per;return max(rect,exp(-ang/p.tau));")
    scan = ("var per=p.full>0.5?PI:2*PI;var mn=1,sum=0;for(var i=0;i<=400;i++){var x=PI/2+per*i/400;var s=sin(x);var rect=p.full>0.5?abs(s):max(s,0);"
            "var ang=((x-PI/2)%per+per)%per;var o=p.tau<0.3?rect:max(rect,exp(-ang/p.tau));if(o<mn)mn=o;sum+=o;}")
    names = ("Transformer", "Rectifier", "Filter", "Regulator", "Load")
    cols = (BL, OR, VI, GR, YL)
    info = ("Steps the mains down to the required AC level and isolates the supply.", "Diodes convert AC to pulsating DC.",
            "A reservoir capacitor (or LC/π filter) smooths the pulsations; ripple depends on C and the load current.",
            "Zener / series regulator / 78xx IC keeps the output constant against load and mains changes.", "The circuit being powered.")
    o = []
    for i, (n, c, f) in enumerate(zip(names, cols, info)):
        x = -6 + i * 3.0
        o.append(box([x, 3.0, 0], [2.0, 1.0, 0.6], c, label=n, lp=[0, 0.85, 0], info=f))
        if i < 4:
            o.append(arrow([x + 1.1, 3.0, 0], [x + 1.9, 3.0, 0], WH, 0.03))
    o += [
        line([[-4, -2.2, 0], [4.2, -2.2, 0]], "#4B5563"), line([[-4, -2.4, 0], [-4, 0.2, 0]], "#4B5563"),
        plot("sin(x)", 0, 4 * math.pi, [-4, -2.2, 0], 0.6, 2.0, "#5B6B8C", 200, 0.02, label="AC input", la=[-3.2, 0.0, 0], lsize=0.26),
        plot(body, 0, 4 * math.pi, [-4, -2.2, 0], 0.6, 2.0, OR, 400, 0.045, label="Output", la=[3.4, -0.6, 0], lsize=0.28),
    ]
    return spec("Power supply chain", o, "Ripple: Vr(p-p) ≈ I_dc / (f_r·C)   (f_r = 50 Hz half-wave, 100 Hz full-wave)",
                [param("full", "Full-wave (ON) / Half-wave (OFF)", 0, 1, 1, 1, toggle=True),
                 param("tau", "Filter size τ = R_L·C (in rad of supply)", 0, 30, 8, 0.5)],
                [readout("Ripple Vr(p-p)", scan + "return p.tau<0.3?'no filter (100 % ripple)':((1-mn)*100).toFixed(1)+' % of Vm';"),
                 readout("Average DC (÷ Vm)", scan + "return (sum/401).toFixed(3);"),
                 readout("Ideal unfiltered Vdc", "p.full>0.5?'2Vm/π = 0.637 Vm':'Vm/π = 0.318 Vm'"),
                 readout("Ripple frequency", "p.full>0.5?'2 × mains (100 Hz)':'mains (50 Hz)'")],
                cam=(0, 0.8, 14.5), target=(0, 0.2, 0), grid_y=-3.6)


# ------------------------------------------------------------------ Module 3: amplifiers
@reg("bjt_structure", "NPN transistor – how it works")
def bjt_structure():
    lbl = dict(lsize=0.3)
    o = [
        box([-2.6, 0, 0], [2.4, 2.4, 2.0], BL, opacity=0.8, label="Emitter (N, heavily doped)", lp=[0, -1.9, 0],
            info="Heavily doped so it emits many electrons into the base."),
        box([-0.9, 0, 0], [1.0, 2.4, 2.0], "#F87171", opacity=0.85, label="Base (P, thin)", lp=[0.2, -1.9, 0],
            info="Very thin and lightly doped. Most electrons pass straight through to the collector; only a few recombine (the small base current IB)."),
        box([1.1, 0, 0], [3.0, 2.4, 2.0], BL, opacity=0.8, label="Collector (N, large)", lp=[0.4, -1.9, 0],
            info="Large area collects the electrons and dissipates the heat."),
        box([-1.4, 0, 0], [0.4, 2.45, 2.05], YL, opacity=0.55, emissive=0.4, label="J(BE)", la=[-1.4, 1.9, 0],
            bind={"scale.x": "p.vbe>0.5?0.15:1.0"}, info="Base–emitter junction. Forward biased (≈0.7 V) its depletion region shrinks and electrons flow."),
        box([-0.4, 0, 0], [0.4, 2.45, 2.05], YL, opacity=0.55, emissive=0.4, label="J(BC)", la=[-0.1, 1.9, 0],
            bind={"scale.x": "p.vce>0.5?1.6:0.6"}, info="Base–collector junction. Reverse biased: wide depletion region with a strong field that sweeps electrons into the collector."),
        wire([[-3.8, 0, 0], [-5.2, 0, 0]], OR, 0.06, label="Emitter (E)", la=[-5.4, 0.5, 0]),
        wire([[-0.9, 1.2, 0], [-0.9, 2.8, 0]], OR, 0.06, label="Base (B)", la=[-0.9, 3.2, 0]),
        wire([[2.6, 0, 0], [4.2, 0, 0]], OR, 0.06, label="Collector (C)", la=[4.4, 0.5, 0]),
        flow([[-3.8, 0.3, 0], [-0.9, 0.3, 0], [2.6, 0.3, 0]], CY, 16, 2.0, 0.12, 0.05, bind={"visible": "p.vbe>0.5&&p.vce>0.5"}),
        flow([[-3.0, -0.6, 0], [-0.9, -0.6, 0], [-0.9, 1.2, 0], [-0.9, 2.8, 0]], "#F87171", 4, 0.6, 0.12, bind={"visible": "p.vbe>0.5"}),
    ]
    return spec("NPN bipolar junction transistor", o, "IE = IC + IB      IC = β·IB      α = IC/IE ≈ 0.99",
                [param("vbe", "Base–emitter forward biased (≈ 0.7 V)", 0, 1, 1, 1, toggle=True),
                 param("vce", "Collector supply connected", 0, 1, 1, 1, toggle=True)],
                [readout("State", "!p.vbe?'CUT-OFF: IB = 0, IC ≈ 0 (switch OFF)':(p.vce>0.5?'ACTIVE: most electrons reach C, IC = β·IB (amplifier)':'No collector supply → no IC')"),
                 readout("Example β = 100, IB = 40 µA", "p.vbe>0.5&&p.vce>0.5?'IC = 4 mA, IE = 4.04 mA':'IC = 0'")],
                cam=(0.5, 2.5, 10.5), target=(0, 0.2, 0))


@reg("load_line", "Transistor load line and Q-point")
def load_line():
    base = [-4, -2.2, 0]
    o = [
        line([[-4.2, -2.2, 0], [4.0, -2.2, 0]], "#4B5563"), line([[-4, -2.4, 0], [-4, 2.6, 0]], "#4B5563"),
        text([4.4, -2.5, 0], "VCE (V)", "#8B949E", 0.3), text([-3.2, 2.9, 0], "IC (mA)", "#8B949E", 0.3),
        plot("(12-x)/2", 0, 12, base, 0.6, 0.75, OR, 30, 0.05, label="Load line (Vcc = 12 V, RC = 2 kΩ)", la=[1.2, 1.9, 0], lsize=0.26,
             info="From (VCE = Vcc, IC = 0) cut-off to (VCE = 0, IC = Vcc/RC) saturation."),
        pt("12-2*Math.min(0.1*p.Ib,5.9)", "(12-x)/2", 0, base, 0.6, 0.75, YL, 0.17, label="Q-point", lp=[0.4, 0.5, 0],
           info="Operating (quiescent) point set by the base bias current IB."),
        text([-3.4, -1.9, 0], "cut-off", "#8B949E", 0.26), text([2.9, -1.9, 0], "cut-off end", "#8B949E", 0.0001),
    ]
    for ib in (20, 40, 60, 80, 100):
        o.append(plot(f"0.1*{ib}*(1-exp(-x/0.25))", 0, 12, base, 0.6, 0.75, "#5B6B8C", 60, 0.018, label=f"IB = {ib} µA", la=[3.9 if ib < 100 else 3.9, -2.2 + 0.075 * ib * 0.75 + 0.1, 0], lsize=0.2))
    return spec("Output characteristics and load line", o, "Vce = Vcc − IC·RC      IC = β·IB",
                [param("Ib", "Base current IB", 0, 100, 40, 1, "µA")],
                [readout("IC = β·IB (β = 100)", "Math.min(0.1*p.Ib,5.9).toFixed(2)+' mA'"),
                 readout("VCE = Vcc − IC·RC", "(12-2*Math.min(0.1*p.Ib,5.9)).toFixed(2)+' V'"),
                 readout("Region", "p.Ib<1?'CUT-OFF (OFF)':(0.1*p.Ib>=5.9?'SATURATION (ON, VCE ≈ 0.2 V)':'ACTIVE (amplifier)')")],
                cam=(0, 0.5, 13), target=(0, 0.1, 0), grid_y=-3.2)


# ------------------------------------------------------------------ Module 4: ICs & transducers
def _opamp(inverting):
    G = "(-p.Rf/p.R1)" if inverting else "(1+p.Rf/p.R1)"
    tri = [[-1.6, -1.8], [-1.6, 1.8], [1.8, 0]]
    o = [prism([0, 2.2, 0], tri, 0.6, GR, opacity=0.85, label="Operational amplifier", la=[0.3, 0.5, 0.5],
                info="Very high gain, very high input impedance, very low output impedance. With negative feedback: V+ ≈ V− (virtual short)."),
         text([-1.15, 3.1, 0.4], "−" if inverting else "+", WH, 0.5), text([-1.15, 1.3, 0.4], "+" if inverting else "−", WH, 0.5),
         wire([[1.8, 2.2, 0], [4.8, 2.2, 0]], OR, 0.045, label="Vout", la=[5.2, 2.6, 0]),
         box([0.8, 4.5 if inverting else 0.2, 0], [1.2, 0.3, 0.3], "#F59E0B", label="Rf", lp=[0, 0.5 if inverting else -0.5, 0], info="Feedback resistor sets the gain together with R1.")]
    if inverting:
        o += [sphere([-6.2, 3.1, 0], 0.25, CY, label="Vin", lp=[0, 0.5, 0]), wire([[-6.2, 3.1, 0], [-5.2, 3.1, 0]], OR),
              box([-4.6, 3.1, 0], [1.2, 0.3, 0.3], "#F59E0B", label="R1", lp=[0, 0.5, 0], info="Input resistor. Gain = −Rf/R1."),
              wire([[-4.0, 3.1, 0], [-1.6, 3.1, 0]], OR),
              wire([[-3, 3.1, 0], [-3, 4.5, 0], [0.2, 4.5, 0]], OR), wire([[1.4, 4.5, 0], [3.2, 4.5, 0], [3.2, 2.2, 0]], OR),
              wire([[-1.6, 1.3, 0], [-3, 1.3, 0], [-3, 0.7, 0]], OR), box([-3, 0.55, 0], [0.8, 0.06, 0.3], LG, label="0 V", lp=[0.9, 0, 0])]
    else:
        o += [sphere([-6.2, 3.1, 0], 0.25, CY, label="Vin", lp=[0, 0.5, 0]), wire([[-6.2, 3.1, 0], [-1.6, 3.1, 0]], OR),
              wire([[-1.6, 1.3, 0], [-3, 1.3, 0]], OR), box([-4.4, 1.3, 0], [1.2, 0.3, 0.3], "#F59E0B", label="R1", lp=[0, 0.5, 0], info="With Rf sets the gain: 1 + Rf/R1."),
              wire([[-5.0, 1.3, 0], [-5.8, 1.3, 0]], OR), box([-5.9, 1.3, 0], [0.06, 0.8, 0.3], LG, label="0 V", lp=[-0.2, 0.6, 0]),
              wire([[3.2, 2.2, 0], [3.2, 0.2, 0], [1.4, 0.2, 0]], OR), wire([[0.2, 0.2, 0], [-3, 0.2, 0], [-3, 1.3, 0]], OR)]
    o += [line([[-3.2, -2.6, 0], [3.4, -2.6, 0]], "#4B5563"),
          plot("p.vp*sin(x)", 0, 2 * math.pi, [-3.2, -2.6, 0], 1.0, 0.18, CY, 120, 0.04, label="Vin", la=[-3.6, -2.0, 0], lsize=0.26),
          plot("clamp(" + G + "*p.vp*sin(x),-p.vsat,p.vsat)", 0, 2 * math.pi, [-3.2, -2.6, 0], 1.0, 0.18, OR, 160, 0.045, label="Vout", la=[3.8, -2.6, 0], lsize=0.26,
               info="Output follows gain × input but flat-tops (clips) at the supply rails ±Vsat.")]
    ttl = "Inverting amplifier" if inverting else "Non-inverting amplifier"
    sub = "Gain Av = −Rf/R1 (180° phase shift)" if inverting else "Gain Av = 1 + Rf/R1 (in phase)"
    return spec(ttl, o, sub,
                [param("R1", "R1", 1, 50, 10, 1, "kΩ"), param("Rf", "Rf", 10, 200, 50, 1, "kΩ"),
                 param("vp", "Input peak", 0.1, 5, 1, 0.1, "V"), param("vsat", "Supply rails ±Vsat", 5, 15, 12, 1, "V")],
                [readout("Voltage gain Av", G + ".toFixed(2)"),
                 readout("Unclipped Vout peak", "abs(" + G + "*p.vp).toFixed(2)+' V'"),
                 readout("Output", "abs(" + G + "*p.vp)>p.vsat?'CLIPPING at ±'+p.vsat+' V':'Linear (no distortion)'")],
                cam=(0, 0.8, 14), target=(-0.5, 0.3, 0), grid_y=-5.2)


@reg("opamp_inv", "Op-amp: inverting amplifier")
def opamp_inv():
    return _opamp(True)


@reg("opamp_noninv", "Op-amp: non-inverting amplifier")
def opamp_noninv():
    return _opamp(False)


@reg("timer555", "555 timer – astable multivibrator")
def timer555():
    pre = "var tc=(p.RA+p.RB)*p.C,td=p.RB*p.C,th=0.693*tc,tl=0.693*td,Tt=th+tl,u=(x-floor(x))*Tt;"
    pins = [("1 GND", "Ground"), ("2 TRIG", "Trigger: sets the output HIGH when it falls below 1/3 Vcc."), ("3 OUT", "Output (source/sink up to 200 mA)."),
            ("4 RESET", "Active-low reset; tie to Vcc when unused."), ("5 CTRL", "Control voltage (2/3 Vcc); decouple with 10 nF."),
            ("6 THRES", "Threshold: resets the flip-flop when above 2/3 Vcc."), ("7 DISCH", "Discharges the timing capacitor through RB."), ("8 Vcc", "Supply 4.5–16 V.")]
    o = [box([-4.2, 0.2, 0], [2.2, 3.6, 0.6], "#111827", label="NE555", la=[-4.2, 0.2, 0.5], lsize=0.4, info="Two comparators, an SR flip-flop, a discharge transistor and a 3 × 5 kΩ divider (1/3 and 2/3 Vcc).")]
    for i, (n, inf) in enumerate(pins):
        left = i < 4
        y = 1.2 - 0.8 * i if left else -1.2 + 0.8 * (i - 4)
        x = -5.5 if left else -2.9
        o.append(box([x, y + 0.2, 0], [0.6, 0.2, 0.25], LG, label=n, lp=[-0.9 if left else 0.9, 0, 0], lsize=0.22, info=inf))
    o += [line([[-0.3, 1.3, 0], [6.8, 1.3, 0]], "#4B5563"), line([[-0.3, -1.2, 0], [6.8, -1.2, 0]], "#4B5563"),
          line([[-0.3, -1.2 + 1.4 / 3, 0], [6.8, -1.2 + 1.4 / 3, 0]], YL, 0.008), line([[-0.3, -1.2 + 2.8 / 3, 0], [6.8, -1.2 + 2.8 / 3, 0]], YL, 0.008),
          text([7.4, -1.2 + 0.47, 0], "⅓Vcc", YL, 0.24), text([7.4, -1.2 + 0.93, 0], "⅔Vcc", YL, 0.24),
          plot(pre + "return u<th?1:0;", 0, 3, [-0.2, 1.3, 0], 2.3, 1.4, OR, 360, 0.04, label="Output (pin 3)", la=[3.5, 3.0, 0], lsize=0.26),
          plot(pre + "return u<th?1-(2/3)*exp(-u/tc):(2/3)*exp(-(u-th)/td);", 0, 3, [-0.2, -1.2, 0], 2.3, 1.4, CY, 360, 0.04,
               label="Capacitor voltage (pins 2 & 6)", la=[3.5, -2.2, 0], lsize=0.26,
               info="Charges from ⅓Vcc to ⅔Vcc through RA+RB, then discharges through RB back to ⅓Vcc.")]
    return spec("555 astable oscillator", o, "f = 1.443 / ((RA + 2RB)·C)      t_high = 0.693(RA+RB)C      t_low = 0.693·RB·C",
                [param("RA", "RA", 1, 100, 1, 1, "kΩ"), param("RB", "RB", 1, 100, 10, 1, "kΩ"), param("C", "C", 10, 1000, 100, 10, "nF")],
                [readout("Frequency f", "(1.443e6/((p.RA+2*p.RB)*p.C)).toFixed(0)+' Hz'"),
                 readout("t_high = 0.693(RA+RB)C", "(0.693*(p.RA+p.RB)*p.C/1000).toFixed(3)+' ms'"),
                 readout("t_low = 0.693·RB·C", "(0.693*p.RB*p.C/1000).toFixed(3)+' ms'"),
                 readout("Duty cycle (RA+RB)/(RA+2RB)", "(100*(p.RA+p.RB)/(p.RA+2*p.RB)).toFixed(1)+' %'")],
                cam=(1.5, 1.0, 14), target=(1.5, 0.1, 0), grid_y=-3.2)


@reg("wheatstone", "Wheatstone bridge (strain gauge / transducer)")
def wheatstone():
    A, B, C, D = (0, 3), (-3, 0), (0, -3), (3, 0)
    vb = "(5*120/(120+120))"
    vd = "(5*(120*(1+p.d/100))/(120+120*(1+p.d/100)))"
    vout = "(" + vb + "-" + vd + ")"
    def res(x, y, rot, name, col, inf, **kw):
        return box([x, y, 0], [1.3, 0.4, 0.4], col, rot=[0, 0, rot], label=name, lp=[0, 0.6, 0], info=inf, **kw)
    o = [
        line([[0, 3, 0], [-3, 0, 0], [0, -3, 0], [3, 0, 0], [0, 3, 0]], "#6B7A8F", 0.04),
        res(-1.5, 1.5, 45, "R1 = 120 Ω", "#F59E0B", "Fixed arm."), res(1.5, 1.5, -45, "R2 = 120 Ω", "#F59E0B", "Fixed arm."),
        res(-1.5, -1.5, -45, "R3 = 120 Ω", "#F59E0B", "Fixed arm."),
        res(1.5, -1.5, 45, "Rx (gauge)", OR, "Active strain gauge: Rx = 120(1 + δ). The bridge goes out of balance when Rx changes.", emissive=0.4),
        line([[-3, 0, 0], [3, 0, 0]], YL, 0.03),
        cyl([0, 0, 0], 0.6, 0.3, DK, axis="z", label="Detector (galvanometer)", lp=[0, -1.0, 0.3], info="Reads the out-of-balance voltage between B and D."),
        cyl([0, 0.25, 0.25], 0.025, 0.9, RD, bind={"rot.z": "-clamp(" + vout + "*1500,-40,40)", "pos.x": "0.25*sin(clamp(" + vout + "*1500,-40,40)*PI/180)", "pos.y": "0.25*cos(clamp(" + vout + "*1500,-40,40)*PI/180)"}),
        wire([[0, 3, 0], [0, 4.3, 0], [-5.5, 4.3, 0], [-5.5, -4.3, 0], [0, -4.3, 0], [0, -3, 0]], OR, 0.04),
        box([-5.5, 0, 0], [0.5, 1.2, 0.5], GR, label="Supply Vs = 5 V", lp=[0.2, 1.3, 0], info="Excitation voltage across A and C."),
    ]
    for nm, (x, y) in (("A", A), ("B", B), ("C", C), ("D", D)):
        o.append(sphere([x, y, 0], 0.16, WH, label=nm, lp=[0.45 if nm == "D" else (-0.45 if nm == "B" else 0), 0.45 if nm == "A" else (-0.45 if nm == "C" else 0), 0]))
    return spec("Wheatstone bridge", o, "Balanced when R1/R3 = R2/Rx.   Quarter-bridge output ≈ Vs·(ΔR/R)/4",
                [param("d", "Change in Rx (strain)", -5, 5, 2, 0.1, "%")],
                [readout("Vb (R3 branch)", vb + ".toFixed(3)+' V'"), readout("Vd (Rx branch)", vd + ".toFixed(4)+' V'"),
                 readout("Out-of-balance Vout = Vb − Vd", "(" + vout + "*1000).toFixed(2)+' mV'"),
                 readout("Approx. Vs·δ/4", "(5*p.d/100/4*1000).toFixed(2)+' mV'"),
                 readout("State", "abs(p.d)<0.05?'BALANCED (detector reads 0)':'OUT OF BALANCE'")],
                cam=(0, 0.5, 13.5), target=(-0.5, 0, 0))


@reg("lvdt", "LVDT displacement transducer")
def lvdt():
    off = "p.x*0.3"
    o = [
        cyl([0, 0, 0], 1.3, 4, LG, axis="x", open=True, opacity=0.12, label="Housing", lp=[0, 1.7, 0]),
        cyl([0, 0, 0], 1.0, 0.9, OR, axis="x", opacity=0.55, label="Primary coil", lp=[0, -1.5, 0], info="Excited with AC (typically 1–10 kHz)."),
        cyl([-1.3, 0, 0], 1.0, 0.9, CY, axis="x", opacity=0.55, label="Secondary 1", lp=[-0.4, 1.5, 0], info="Voltage V1 depends on how much core is inside."),
        cyl([1.3, 0, 0], 1.0, 0.9, CY, axis="x", opacity=0.55, label="Secondary 2", lp=[0.4, 1.5, 0], info="Wound in opposition to secondary 1. Output = V1 − V2."),
        cyl([0, 0, 0], 0.45, 4.4, LG, axis="x", metal=0.7, bind={"pos.x": off}, label="Iron core", lp=[0, -0.9, 0], info="Moves with the measured object. Centre = null position (0 V)."),
        cyl([3.4, 0, 0], 0.08, 3.0, ST, axis="x", bind={"pos.x": "3.2+" + off}, label="Push-rod", lp=[0, 0.5, 0]),
        box([0, -3.0, 0], [1, 0.4, 0.6], YL, label="Vout", lp=[0, -0.6, 0], bind={"scale.x": "abs(p.x)*1.2+0.05", "pos.x": "0.6*p.x"},
            info="Length = output amplitude. Phase (left/right) tells the direction."),
    ]
    return spec("LVDT", o, "Linear variable differential transformer: Vout ∝ core displacement x",
                [param("x", "Core displacement x", -5, 5, 2, 0.1, "mm")],
                [readout("Output (sensitivity 0.5 V/mm)", "(0.5*p.x).toFixed(2)+' V'"),
                 readout("Phase", "abs(p.x)<0.05?'null position – 0 V':(p.x>0?'in phase with primary':'180° out of phase')"),
                 readout("Advantages", "'no contact, high resolution, long life'")],
                cam=(1, 2.5, 11), target=(0.5, -0.5, 0))


# ------------------------------------------------------------------ Module 5: phase control
@reg("scr_structure", "Thyristor (SCR) structure")
def scr_structure():
    g = "p.gate>0.5&&p.anode>0.5"
    o = [
        box([-3.3, 0, 0], [1.6, 2.4, 1.6], "#F87171", opacity=0.85, label="P (anode)", lp=[0, -1.8, 0], info="Outer P layer connected to the anode."),
        box([-1.65, 0, 0], [1.7, 2.4, 1.6], BL, opacity=0.85, label="N", lp=[0, -1.8, 0]),
        box([0, 0, 0], [1.6, 2.4, 1.6], "#F87171", opacity=0.85, label="P (gate)", lp=[0, -1.8, 0], info="Gate connects here. A small gate current injects carriers and breaks down J2."),
        box([1.6, 0, 0], [1.6, 2.4, 1.6], BL, opacity=0.85, label="N (cathode)", lp=[0, -1.8, 0]),
        box([-2.5, 0, 0], [0.08, 2.5, 1.7], YL, emissive=0.6, label="J1", la=[-2.5, 1.8, 0]),
        box([-0.8, 0, 0], [0.08, 2.5, 1.7], RD, emissive=0.6, label="J2", la=[-0.8, 1.8, 0], bind={"color": "(" + g + ")?'#10B981':'#EF4444'"},
            info="Reverse-biased centre junction – blocks forward current until the gate triggers it."),
        box([0.8, 0, 0], [0.08, 2.5, 1.7], YL, emissive=0.6, label="J3", la=[0.8, 1.8, 0]),
        box([-0.8, 0, 0], [0.5, 2.4, 1.5], RD, opacity=0.35, bind={"visible": "!(" + g + ")"}, label="Depletion region", lp=[0, 2.4, 0], info="Wide depletion region = blocking state (OFF)."),
        wire([[-4.1, 0, 0], [-5.5, 0, 0]], OR, 0.06, label="Anode (A)", la=[-5.7, 0.5, 0]),
        wire([[2.4, 0, 0], [3.9, 0, 0]], OR, 0.06, label="Cathode (K)", la=[4.2, 0.5, 0]),
        wire([[0, 1.2, 0], [0, 2.8, 0]], GR, 0.06, label="Gate (G)", la=[0.8, 3.0, 0]),
        flow([[-5.5, 0, 0], [3.9, 0, 0]], OR, 22, 2.0, 0.12, bind={"visible": g}),
        flow([[0, 2.8, 0], [0, 1.2, 0]], GR, 4, 0.8, 0.1, bind={"visible": "p.gate>0.5"}),
    ]
    return spec("SCR (thyristor) – four-layer P-N-P-N", o, "Conducts only when the anode is positive AND a gate pulse is applied; then latches ON until IA < I_H",
                [param("anode", "Anode positive with respect to cathode", 0, 1, 1, 1, toggle=True),
                 param("gate", "Gate trigger pulse applied", 0, 1, 0, 1, toggle=True)],
                [readout("State", "p.anode<0.5?'REVERSE BLOCKING (J1, J3 reverse biased)':(p.gate>0.5?'TRIGGERED → conducting (low resistance)':'FORWARD BLOCKING (J2 blocks)')"),
                 readout("After the gate is removed", "'Latches ON until anode current falls below holding current IH'"),
                 readout("Turn-off methods", "'reduce IA < IH, or reverse the anode (commutation)'")],
                cam=(0.5, 2.5, 11.5), target=(-0.3, 0.2, 0))


@reg("scr_waveform", "Phase control – firing angle")
def scr_waveform():
    body = ("var a=p.alpha*PI/180;if(p.full>0.5){var u=x%PI;return u>a?sin(u):0;}else{var u2=x%(2*PI);return (u2>a&&u2<PI)?sin(u2):0;}")
    o = [
        line([[-4, 1.4, 0], [4, 1.4, 0]], "#4B5563"), line([[-4, -2.0, 0], [4, -2.0, 0]], "#4B5563"),
        plot("sin(x)", 0, 4 * math.pi, [-4, 1.4, 0], 0.6, 1.1, "#5B6B8C", 200, 0.03, label="Supply Vin", la=[-3.3, 2.9, 0], lsize=0.26),
        plot(body, 0, 4 * math.pi, [-4, -2.0, 0], 0.6, 1.6, OR, 480, 0.045, label="Load voltage", la=[-3.3, -0.2, 0],
             lsize=0.26, info="The SCR is switched on at the firing angle α and turns itself off at each zero crossing."),
        pt("p.alpha*PI/180", "sin(x)", 0, [-4, 1.4, 0], 0.6, 1.1, YL, 0.14, label="α", lp=[0, 0.5, 0], info="Firing angle: delay from the zero crossing to the gate pulse."),
    ]
    return spec("SCR phase control", o, "Vdc = (Vm/2π)(1 + cos α) half-wave   |   Vdc = (Vm/π)(1 + cos α) full-wave   (Vm = 325 V)",
                [param("alpha", "Firing angle α", 0, 180, 60, 1, "°"), param("full", "Full-wave (ON) / Half-wave (OFF)", 0, 1, 0, 1, toggle=True)],
                [readout("Conduction angle", "(180-p.alpha).toFixed(0)+'°'"),
                 readout("Average output Vdc", "(p.full>0.5?325/PI*(1+cos(p.alpha*PI/180)):325/(2*PI)*(1+cos(p.alpha*PI/180))).toFixed(1)+' V'"),
                 readout("Control", "'Larger α → later firing → lower average power'")],
                cam=(0, 0.2, 14), target=(0, -0.3, 0), grid_y=-3.4)


# ------------------------------------------------------------------ Module 6: instruments
@reg("cro", "Cathode-ray oscilloscope")
def cro():
    o = [lathe([0, 0, 0], [[0.4, -7], [0.4, -4.2], [0.9, -3.2], [1.9, -1.2], [2.3, 0.3], [2.3, 1.9]], CY, opacity=0.2, rot=[90, 0, 0],
               label="Cathode-ray tube (evacuated)", la=[0, -2.8, 0], lsize=0.28, info="Evacuated glass tube: electron gun, focusing and accelerating anodes, deflection plates, phosphor screen."),
         cyl([0, 0, -6.7], 0.3, 0.8, ST, axis="z", label="Electron gun", lp=[1.3, 0.5, 0], lsize=0.26, info="Heated cathode emits electrons; grid controls brightness; anodes focus and accelerate them."),
         box([0, 0.4, -3.6], [0.9, 0.04, 0.9], OR, label="Y (vertical) plates", lp=[-1.7, 0.7, 0], lsize=0.24, info="The input signal (after the Y-amplifier/attenuator) is applied here and deflects the beam up and down."),
         box([0, -0.4, -3.6], [0.9, 0.04, 0.9], OR),
         box([0.55, 0, -2.6], [0.04, 0.9, 0.9], VI, label="X (horizontal) plates", lp=[1.8, 0.7, 0], lsize=0.24, info="The time-base sawtooth sweeps the beam left to right at a rate set by TIME/DIV."),
         box([-0.55, 0, -2.6], [0.04, 0.9, 0.9], VI),
         line([[0, 0, -6.4], [0, 0, 1.95]], CY, 0.02),
         cyl([0, 0, 1.95], 2.3, 0.06, "#06200F", axis="z", label="Phosphor screen", la=[0, -2.6, 2.0], lsize=0.26, info="Phosphor glows where the electron beam strikes."),
         ]
    for i in range(9):
        o.append(line([[-2.0 + 0.5 * i, -1.5, 1.99], [-2.0 + 0.5 * i, 1.5, 1.99]], "#2F8F4E" if i == 4 else "#1E5B32", 0.012))
    for j in range(7):
        o.append(line([[-2.0, -1.5 + 0.5 * j, 1.99], [2.0, -1.5 + 0.5 * j, 1.99]], "#2F8F4E" if j == 3 else "#1E5B32", 0.012))
    o.append(plot("clamp(p.Vp*sin(2*PI*p.f*x*p.tdiv/1000)/p.vdiv,-3,3)", 0, 8, [-2.0, 0, 2.03], 0.5, 0.5, "#6BFF9A", 300, 0.03, emissive=0.8))
    return spec("Oscilloscope", o, "Screen: 8 horizontal × 6 vertical divisions.  T = (divisions per cycle) × TIME/DIV",
                [param("Vp", "Signal peak voltage", 0.2, 10, 3, 0.1, "V"), param("f", "Signal frequency", 50, 2000, 500, 10, "Hz"),
                 param("tdiv", "TIME/DIV", 0.1, 5, 1, 0.1, "ms"), param("vdiv", "VOLTS/DIV", 0.5, 5, 2, 0.5, "V")],
                [readout("Actual period T = 1/f", "(1000/p.f).toFixed(2)+' ms'"),
                 readout("Divisions per cycle", "(1000/p.f/p.tdiv).toFixed(2)+' div'"),
                 readout("Peak-to-peak on screen", "(2*p.Vp/p.vdiv).toFixed(2)+' div'"),
                 readout("Vpp = div × VOLTS/DIV", "(2*p.Vp).toFixed(1)+' V'"),
                 readout("Screen limit", "2*p.Vp/p.vdiv>6?'Trace clipped – increase VOLTS/DIV':'OK'")],
                cam=(4.5, 2.5, 9.5), target=(0, 0, -1.2))


# ------------------------------------------------------------------ Module 7: oscillators
@reg("lc_tank", "LC tank – oscillation and damping")
def lc_tank():
    coil = []
    N = 140
    for i in range(N + 1):
        a = i * 2 * math.pi * 7 / N
        coil.append([-1.5 + 3.0 * i / N, 2.2 + 0.45 * math.cos(a), 0.45 * math.sin(a)])
    env = "exp(-0.09934*p.R*sqrt(p.C/p.L)*x)"
    o = [
        box([-4.35, 2.2, 0], [0.08, 1.6, 1.2], CY, emissive=0.3, bind={"emissive": "0.9*pow(cos(t*3),2)"}, label="Capacitor C", la=[-4.1, 3.4, 0], info="Stores energy in the electric field."),
        box([-3.85, 2.2, 0], [0.08, 1.6, 1.2], CY, emissive=0.3, bind={"emissive": "0.9*pow(cos(t*3),2)"}),
        {"type": "tube", "pts": coil, "r": 0.04, "color": OR, "emissive": 0.2, "bind": {"emissive": "0.9*pow(sin(t*3),2)"}, "label": "Inductor L", "la": [0, 3.3, 0],
         "info": "Stores energy in the magnetic field. Energy swaps between C and L every half cycle (watch the glow)."},
        wire([[-4.1, 3.0, 0], [-4.1, 3.7, 0], [2.0, 3.7, 0], [2.0, 2.2, 0], [1.5, 2.2, 0]], ST, 0.035),
        wire([[-4.1, 1.4, 0], [-4.1, 0.7, 0], [-2.0, 0.7, 0], [-2.0, 2.2, 0], [-1.5, 2.2, 0]], ST, 0.035),
        line([[-4.2, -1.6, 0], [4.4, -1.6, 0]], "#4B5563"), line([[-4.2, -3.0, 0], [-4.2, -0.2, 0]], "#4B5563"),
        plot("cos(2*PI*x)", 0, 6, [-4.2, -1.6, 0], 1.4, 1.2, "#5B6B8C", 300, 0.015),
        plot(env + "*cos(2*PI*x)", 0, 6, [-4.2, -1.6, 0], 1.4, 1.2, OR, 400, 0.045, label="Voltage across tank", la=[4.4, -0.7, 0], lsize=0.26),
        plot(env, 0, 6, [-4.2, -1.6, 0], 1.4, 1.2, YL, 60, 0.015), plot("-" + env, 0, 6, [-4.2, -1.6, 0], 1.4, 1.2, YL, 60, 0.015),
        text([4.6, -2.6, 0], "cycles", "#8B949E", 0.26),
    ]
    return spec("LC resonant (tank) circuit", o, "f₀ = 1 / (2π√(LC))      Q = (1/R)·√(L/C)      Resistance makes the oscillation die out",
                [param("L", "Inductance L", 1, 100, 10, 1, "mH"), param("C", "Capacitance C", 0.1, 100, 1, 0.1, "µF"), param("R", "Series resistance R", 0, 50, 5, 1, "Ω")],
                [readout("Resonant frequency f₀", "(5032.9/sqrt(p.L*p.C)).toFixed(1)+' Hz'"),
                 readout("Quality factor Q", "p.R<0.01?'∞ (no loss)':(31.623/p.R*sqrt(p.L/p.C)).toFixed(1)"),
                 readout("Oscillation", "p.R<0.01?'sustained (ideal)':'decaying – needs an amplifier to replace the loss'"),
                 readout("Barkhausen criterion", "'loop gain Aβ ≥ 1, phase shift 0° (360°)'")],
                cam=(0, 1.5, 13.5), target=(0, 0.3, 0), grid_y=-3.4)


# ------------------------------------------------------------------ Module 8: LCD
@reg("lcd_cell", "Liquid crystal display cell (twisted nematic)")
def lcd_cell():
    on = "p.V>0.5"
    o = [
        box([-3.2, 0, 0], [0.12, 3.2, 3.2], ST, opacity=0.45, label="Polariser 1 (vertical)", lp=[0, 2.1, 0], lsize=0.26, info="Lets only vertically polarised light through."),
        box([-1.5, 0, 0], [0.12, 3.2, 3.2], CY, opacity=0.2, label="Glass + ITO electrode", lp=[0, 2.1, 0], lsize=0.26, info="Transparent conducting layer (indium tin oxide) applies the electric field."),
        box([1.5, 0, 0], [0.12, 3.2, 3.2], CY, opacity=0.2, label="Glass + ITO electrode", lp=[0, 2.1, 0], lsize=0.26),
        box([3.2, 0, 0], [0.12, 3.2, 3.2], ST, opacity=0.45, label="Polariser 2 (horizontal)", lp=[0, 2.1, 0], lsize=0.26, info="Crossed at 90° to polariser 1."),
        box([5.6, 0, 0], [0.1, 2.0, 2.0], YL, bind={"color": "(" + on + ")?'#111827':'#FDE68A'", "emissive": "(" + on + ")?0:0.9"}, label="Pixel", lp=[0, 1.5, 0], lsize=0.26,
            info="Bright when no voltage is applied (light passes), dark when voltage is applied."),
        flow([[-6, 0, 0], [-3.3, 0, 0]], YL, 10, 2.5, 0.12, 0.5),
        flow([[-3.1, 0, 0], [3.0, 0, 0]], "#FDE68A", 14, 2.5, 0.12),
        flow([[3.3, 0, 0], [5.2, 0, 0]], "#FFFFFF", 8, 2.5, 0.12, bind={"visible": "!(" + on + ")"}),
        text([-4.6, 1.6, 0], "unpolarised light", YL, 0.26),
    ]
    for z in (-0.5, 0.0, 0.5):
        o.append(line([[-3.1, -1.4, z], [-3.1, 1.4, z]], WH, 0.012))
    for y in (-0.8, -0.4, 0, 0.4, 0.8):
        o.append(line([[3.1, y, -1.4], [3.1, y, 1.4]], WH, 0.012))
    for k in range(5):
        for y in (-1.0, 0, 1.0):
            for z in (-1.0, 0, 1.0):
                o.append(cyl([-1.0 + 0.5 * k, y, z], 0.06, 0.8, YL, emissive=0.3,
                              bind={"rot.x": f"({on})?0:{90 * k / 4}", "rot.z": f"({on})?-90:0"},
                              **({"label": "Liquid-crystal molecules", "lp": [0, 1.3, 0], "lsize": 0.26,
                                  "info": "Without voltage they twist 90° layer by layer, rotating the light's polarisation. With voltage they align with the field and no rotation occurs."}
                                 if (k, y, z) == (2, 0, 0) else {})))
    return spec("Twisted-nematic LCD cell", o, "Voltage OFF: twisted 90° → light passes (bright).   Voltage ON: molecules align → blocked (dark).",
                [param("V", "Voltage applied across the cell", 0, 1, 0, 1, toggle=True)],
                [readout("Molecule arrangement", "p.V>0.5?'aligned with the field (no twist)':'twisted 90° (helix)'"),
                 readout("Light after polariser 2", "p.V>0.5?'BLOCKED → pixel DARK':'PASSES → pixel BRIGHT'"),
                 readout("Drive voltage", "'low-frequency AC (DC would damage the cell)'"),
                 readout("LCD advantage", "'very low power; needs ambient or backlight'")],
                cam=(1, 4, 13), target=(0.5, 0, 0))
