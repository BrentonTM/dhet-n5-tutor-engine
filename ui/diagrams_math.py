"""Mathematics N5 – 3D diagrams."""
import math

from ui.diagram_lib import *
from ui.diagram_registry import reg

TAU = 2 * math.pi


@reg("unit_circle", "Unit circle – sine and cosine waves")
def unit_circle():
    cx = -3.5
    a = "(p.a*PI/180)"
    xp = f"({cx}+2*cos{a})"
    xw = f"(-0.8+{a})"
    o = [
        torus([cx, 0, 0], 2, 0.03, "#4B5563"),
        line([[cx - 2.4, 0, 0], [cx + 2.4, 0, 0]], "#4B5563"), line([[cx, -2.4, 0], [cx, 2.4, 0]], "#4B5563"),
        line([[-0.8, 0, 0], [6.1, 0, 0]], "#4B5563"), line([[-0.8, -2.3, 0], [-0.8, 2.4, 0]], "#4B5563"),
        text([5.7, -0.4, 0], "θ (rad)", "#8B949E", 0.3), text([math.pi - 0.8, -0.4, 0], "π", "#8B949E", 0.3),
        text([TAU - 0.8, -0.4, 0], "2π", "#8B949E", 0.3),
        text([2.6, 2.6, 0], "sin θ", CY, 0.38), text([2.6, 2.6, -2.2], "cos θ", OR, 0.38),
        cyl([cx + 1, 0, 0], 0.025, 2, YL, bind={"pos.x": f"{cx}+cos{a}", "pos.y": f"sin{a}", "rot.z": "p.a-90"}),
        sphere([cx + 2, 0, 0], 0.14, OR, bind={"pos.x": xp, "pos.y": f"2*sin{a}"}, label="P(cos θ, sin θ)", lp=[0.2, 0.5, 0],
               info="Point on the unit circle. Its height is sin θ and its horizontal distance is cos θ."),
        cyl([cx + 2, 1, 0], 0.025, 1, CY, bind={"pos.x": xp, "pos.y": f"sin{a}", "scale.y": f"abs(2*sin{a})"}),
        cyl([cx + 1, 0, 0], 0.025, 1, OR, axis="x", bind={"pos.x": f"{cx}+cos{a}", "scale.x": f"abs(2*cos{a})"}),
        plot("sin(x)", 0, TAU, [-0.8, 0, 0], 1.0, 2.0, CY, 200),
        plot("cos(x)", 0, TAU, [-0.8, 0, -2.2], 1.0, 2.0, OR, 200),
        pt("p.a*PI/180", "sin(x)", 0, [-0.8, 0, 0], 1.0, 2.0, CY, 0.13),
        pt("p.a*PI/180", "cos(x)", 0, [-0.8, 0, -2.2], 1.0, 2.0, OR, 0.13),
        cyl([0, 0, 0], 0.012, 1, YL, axis="x", opacity=0.6, bind={"pos.x": f"({xp}+{xw})/2", "pos.y": f"2*sin{a}", "scale.x": f"abs({xw}-{xp})+0.001"}),
    ]
    return spec("Unit circle ⇄ waves", o, "Radius 1: sin θ = height, cos θ = horizontal distance. Unrolling θ draws the waves.",
                [param("a", "Angle θ", 0, 360, 40, 1, "°")],
                [readout("sin θ", "Math.sin(p.a*PI/180).toFixed(3)"), readout("cos θ", "Math.cos(p.a*PI/180).toFixed(3)"),
                 readout("tan θ = sin θ / cos θ", "Math.abs(Math.cos(p.a*PI/180))<0.001?'undefined':Math.tan(p.a*PI/180).toFixed(3)"),
                 readout("sin²θ + cos²θ", "(pow(sin(p.a*PI/180),2)+pow(cos(p.a*PI/180),2)).toFixed(3)")],
                cam=(-0.5, 3.5, 13), target=(-0.5, 0, -1))


@reg("pascal", "Pascal's triangle and the binomial theorem")
def pascal():
    cols = [CY, "#38BDF8", BL, VI, "#C084FC", OR, YL]
    o = []
    for r in range(7):
        c = 1
        for k in range(r + 1):
            if k:
                c = c * (r - k + 1) // k
            x, y = (k - r / 2) * 1.4, (3 - r) * 1.15
            o.append(sphere([x, y, 0], 0.46, cols[r], bind={"emissive": f"Math.round(p.n)=={r}?0.9:0.08"},
                            click={"n": str(r)}, label=None, info=f"Row n = {r}: the coefficients of (a + b)^{r}. Click to select this row."))
            o.append(text([x, y, 0.55], str(c), "#0A0D12" if r in (0, 6) else WH, 0.36))
        o.append(text([-r / 2 * 1.4 - 1.4, (3 - r) * 1.15, 0], f"n={r}", "#8B949E", 0.3))
    return spec("Pascal's triangle", o, "Each number is the sum of the two above it:  C(n,k) = C(n−1,k−1) + C(n−1,k)",
                [param("n", "Row n (or click a row)", 0, 6, 4, 1)],
                [readout("(a + b)ⁿ coefficients", "var n=Math.round(p.n),c=1,s=[];for(var k=0;k<=n;k++){if(k>0)c=c*(n-k+1)/k;s.push(c);}return s.join(',  ');"),
                 readout("Sum of row = 2ⁿ", "pow(2,Math.round(p.n))"),
                 readout("General term", "'T(k+1) = C('+Math.round(p.n)+',k)·a^('+Math.round(p.n)+'−k)·b^k'")],
                cam=(0, 0.5, 11), target=(0, 0, 0), grid=False)


F_CUBIC = "x*x*x/3-x"


@reg("derivative", "Derivative: tangent and secant")
def derivative():
    base = [-3.6, 0, 0]
    sec = ("var f=function(u){return u*u*u/3-u;};return f(p.a)+((f(p.a+p.h)-f(p.a))/p.h)*(x-p.a);")
    o = [
        line([[-3.9, 0, 0], [3.9, 0, 0]], "#4B5563"), line([[0, -2.6, 0], [0, 2.7, 0]], "#4B5563"),
        text([4.2, -0.35, 0], "x", "#8B949E", 0.34), text([0.35, 2.9, 0], "y", "#8B949E", 0.34),
        plot(F_CUBIC, -2.4, 2.4, base, 1.5, 1.0, OR, 200, 0.045, label="y = f(x) = x³/3 − x", la=[3, 2.2, 0], lp=[0, 0.4, 0]),
        plot(sec, "p.a-1.2", "p.a+1.6", base, 1.5, 1.0, VI, 40, 0.025, xr=-2.4, label="Secant", la=[-3.3, -2.3, 0], lsize=0.28),
        tangent("p.a", F_CUBIC, -2.4, base, 1.5, 1.0, YL, 1.4),
        pt("p.a", F_CUBIC, -2.4, base, 1.5, 1.0, OR, 0.14, label="(a, f(a))", lp=[0.2, 0.55, 0],
           info="The tangent at this point has slope f′(a). As h → 0 the secant becomes the tangent."),
        sphere([1.5, 1 / 3 - 1, 0], 0.1, GR, label="f′(x) = 0", lp=[0.2, -0.5, 0], info="Turning point (local minimum): the tangent is horizontal."),
        sphere([-1.5, 1 - 1 / 3, 0], 0.1, GR, label="f′(x) = 0", lp=[-0.2, 0.5, 0], info="Turning point (local maximum): the tangent is horizontal."),
    ]
    return spec("Derivative as a limit", o, "f′(a) = lim (h→0) [f(a+h) − f(a)] / h — shrink h and the secant becomes the tangent",
                [param("a", "Point x = a", -2.2, 2.2, 1.5, 0.05), param("h", "Step h (secant width)", 0.05, 2, 1.0, 0.05)],
                [readout("f(a)", "(p.a*p.a*p.a/3-p.a).toFixed(3)"),
                 readout("Exact slope f′(a) = a² − 1", "(p.a*p.a-1).toFixed(3)"),
                 readout("Secant slope", "(((pow(p.a+p.h,3)/3-(p.a+p.h))-(p.a*p.a*p.a/3-p.a))/p.h).toFixed(3)")],
                cam=(0, 1, 13), target=(0, 0, 0))


@reg("riemann", "Integration as area (Riemann sum)")
def riemann():
    base = [-3.8, -1.6, 0]
    o = [
        line([[-4.1, -1.6, 0], [4.2, -1.6, 0]], "#4B5563"), line([[-3.8, -1.9, 0], [-3.8, 3.0, 0]], "#4B5563"),
        text([4.5, -1.9, 0], "x", "#8B949E", 0.34), text([-3.4, 3.2, 0], "y", "#8B949E", 0.34),
        bars("0.25*x*x+1", 0, "p.b", "p.n", base, 1.9, 0.8, CY, 0.6, opacity=0.6, label="Strips", la=[-2.2, 1.0, 0.5],
             info="Each strip has width Δx and height f(x). Adding their areas approximates ∫f(x)dx."),
        plot("0.25*x*x+1", 0, 4, base, 1.9, 0.8, OR, 120, 0.05, label="y = f(x) = ¼x² + 1", la=[2.8, 2.5, 0]),
    ]
    s = "var n=Math.round(p.n),w=p.b/n,s=0;for(var i=0;i<n;i++){var xm=(i+0.5)*w;s+=(0.25*xm*xm+1)*w;}"
    exact = "(p.b*p.b*p.b/12+p.b)"
    return spec("Area under a curve", o, "A = ∫ₐᵇ f(x) dx = limit of the sum Σ f(x)·Δx as strips → ∞",
                [param("n", "Number of strips n", 2, 40, 6, 1), param("b", "Upper limit b", 1, 4, 4, 0.1)],
                [readout("Strip sum (midpoint)", s + "return s.toFixed(4);"),
                 readout("Exact ∫₀ᵇ (¼x²+1) dx = b³/12 + b", exact + ".toFixed(4)"),
                 readout("Error", s + "return Math.abs(s-" + exact + ").toFixed(5);")],
                cam=(0, 1.5, 13), target=(0, 0.3, 0))


@reg("revolve", "Volume of revolution")
def revolve_solid():
    base = [-3.4, 0, 0]
    o = [
        line([[-3.8, 0, 0], [3.4, 0, 0]], "#6B7A8F", 0.02, label="Axis of revolution (x-axis)", la=[1.5, -3.3, 0], lsize=0.26),
        revolve("sqrt(x)", 0, "p.b", base, 1.4, 1.4, CY, 60, opacity=0.5, mesh=CY, label="Solid", la=[-0.6, 2.7, 0.5],
                info="Rotating y = √x about the x-axis sweeps out a solid. V = π ∫ y² dx."),
        plot("sqrt(x)", 0, "p.b", base, 1.4, 1.4, OR, 80, 0.055),
        cyl([-3.4, 0, 0], 1, 0.08, YL, axis="x", opacity=0.85, label="Thin disc", lp=[0, 0.5, 0],
            info="One disc of radius y and thickness dx has volume π·y²·dx. Integrating all discs gives the volume.",
            bind={"pos.x": "-3.4+p.s*1.4", "scale.y": "sqrt(p.s)*1.4", "scale.z": "sqrt(p.s)*1.4", "visible": "p.s<=p.b"}),
    ]
    return spec("Solid of revolution", o, "V = π ∫ₐᵇ y² dx   (rotation about the x-axis)",
                [param("b", "Upper limit b", 1, 4, 3, 0.1), param("s", "Slice position x", 0.1, 4, 1.5, 0.05)],
                [readout("Volume V = π∫₀ᵇ x dx = πb²/2", "(PI*p.b*p.b/2).toFixed(3)+' units³'"),
                 readout("Disc radius y = √x", "Math.sqrt(p.s).toFixed(3)"),
                 readout("Disc volume π·y²·dx (dx = 1)", "(PI*p.s).toFixed(3)")],
                cam=(1, 3.5, 12), target=(0, 0, 0))


@reg("second_moment", "Second moment of area (rectangle)")
def second_moment():
    k = 0.6
    o = [
        box([0, 0, 0], [1, 1, 0.5], BL, opacity=0.55, label="Cross-section b × h", lp=[0, 0, 0.9],
            info="Rectangular cross-section, breadth b and depth h.",
            bind={"scale.x": f"{k}*p.b", "scale.y": f"{k}*p.h", "pos.y": f"-2.4+{k / 2}*p.h"}),
        box([0, 0, 0], [1, 0.12, 0.62], YL, emissive=0.6, label="Strip dA = b·dy", lp=[2.4, 0, 0],
            info="Thin strip at distance y from the base axis. Its contribution to I is y²·dA.",
            bind={"scale.x": f"{k}*p.b+0.05", "pos.y": f"-2.4+{k}*p.s", "visible": "p.s<=p.h"}),
        cyl([0, -2.4, 0], 0.02, 9, OR, axis="x", label="Base axis", la=[-4.2, -2.4, 0], lp=[0, 0.3, 0]),
        cyl([0, 0, 0], 0.02, 9, GR, axis="x", label="Centroidal axis", la=[-4.2, 0, 0], lp=[0, 0.3, 0],
            bind={"pos.y": f"-2.4+{k / 2}*p.h"}),
    ]
    return spec("Second moment of area", o, "I = ∫ y² dA      Parallel-axis theorem: I = I_c + A·d²",
                [param("b", "Breadth b", 2, 8, 4, 0.5, "cm"), param("h", "Depth h", 2, 8, 6, 0.5, "cm"),
                 param("s", "Strip distance y from base", 0, 8, 3, 0.1, "cm")],
                [readout("Area A = b·h", "(p.b*p.h).toFixed(1)+' cm²'"),
                 readout("I about base = bh³/3", "(p.b*pow(p.h,3)/3).toFixed(1)+' cm⁴'"),
                 readout("I about centroid = bh³/12", "(p.b*pow(p.h,3)/12).toFixed(1)+' cm⁴'"),
                 readout("I_c + A·(h/2)²  (= base value)", "(p.b*pow(p.h,3)/12+p.b*p.h*pow(p.h/2,2)).toFixed(1)+' cm⁴'"),
                 readout("Strip contribution y²·b·dy (dy=0.1)", "(p.s*p.s*p.b*0.1).toFixed(2)+' cm⁴'")],
                cam=(3, 2, 11), target=(0, -0.5, 0))


@reg("ode_decay", "First-order differential equation (RC response)")
def ode_decay():
    base = [-4, -1.8, 0]
    o = [
        line([[-4.2, -1.8, 0], [4.2, -1.8, 0]], "#4B5563"), line([[-4, -2.0, 0], [-4, 1.4, 0]], "#4B5563"),
        text([4.6, -2.1, 0], "t (s)", "#8B949E", 0.3), text([-3.4, 1.6, 0], "v / V", "#8B949E", 0.3),
        line([[-4, 0.8, 0], [4.2, 0.8, 0]], GR, 0.015, label="v = V (final value)", la=[2.4, 1.15, 0], lsize=0.26),
        plot("1-exp(-x/p.tau)", 0, 10, base, 0.7, 2.6, OR, 160, 0.05, label="Charging  v = V(1 − e^(−t/τ))", la=[2.2, -0.3, 0], lsize=0.26),
        plot("exp(-x/p.tau)", 0, 10, base, 0.7, 2.6, VI, 160, 0.05, label="Discharging  v = V·e^(−t/τ)", la=[1.8, -1.2, 0], lsize=0.26),
        plot("x/p.tau", 0, "p.tau", base, 0.7, 2.6, YL, 20, 0.025, label="Initial slope V/τ", la=[-2.8, 0.2, 0], lsize=0.26,
             info="The tangent at t = 0 reaches the final value after exactly one time constant τ."),
        pt("p.tau", "1-exp(-x/p.tau)", 0, base, 0.7, 2.6, OR, 0.13, label="t = τ → 63.2 %", lp=[0.3, -0.5, 0]),
        cyl([-4, -1.8 + 0.632 * 1.3, 0], 0.012, 1, YL, opacity=0.5, bind={"pos.x": "-4+p.tau*0.7", "scale.y": "0.632*2.6"}),
    ]
    return spec("dv/dt = (V − v)/τ", o, "Separable ODE: dv/(V−v) = dt/τ  ⇒  v = V(1 − e^(−t/τ))",
                [param("tau", "Time constant τ = RC", 0.3, 4, 1.5, 0.1, "s")],
                [readout("v at t = τ", "'63.2 % of V'"), readout("v at t = 3τ", "'95.0 % of V'"),
                 readout("v at t = 5τ (steady state)", "'99.3 % of V'"), readout("Settling time ≈ 5τ", "(5*p.tau).toFixed(1)+' s'")],
                cam=(0, 1, 13), target=(0, -0.3, 0))
