"""Interactive teaching models for the expanded N6 laboratory."""

from math import cos, pi, sin

from ui.diagram_lib import (
    BL, CY, DK, GR, LG, OR, RD, ST, YL,
    box, cyl, flow, param, plot, prism, readout, spec, sphere, text, vec, wire,
)
from ui.diagram_registry import reg


@reg("transformer_turns_3d", "Transformer · turns ratio and reflected load")
def transformer_turns():
    objects = [
        box([0, 1.38, 0], [5.6, 0.52, 0.66], ST, metal=0.55, label="Laminated core",
            info="The core provides a low-reluctance path for the shared alternating flux."),
        box([0, -1.38, 0], [5.6, 0.52, 0.66], ST, metal=0.55),
    ]
    for x, color, label, count in ((-2.28, OR, "Primary", 10), (2.28, CY, "Secondary", 16)):
        objects.append(box([x, 0, 0], [0.68, 2.8, 0.66], ST, metal=0.55))
        for turn in range(count):
            y = -0.98 + 0.127 * turn
            objects.append(wire([[x-0.57, y, -0.49], [x+0.57, y, -0.49],
                                 [x+0.57, y, 0.51], [x-0.57, y, 0.51], [x-0.57, y, -0.49]],
                                color, 0.052, bind={"visible": f"{turn}<round(p.ns/25)"} if x > 0 else None))
        objects.append(text([x, -2.04, 0.1], label, color, 0.36))
    objects.append(flow([[-1.92, 1.38, 0.37], [2.1, 1.38, 0.37], [2.28, -1.38, 0.37],
                         [-2.28, -1.38, 0.37], [-1.92, 1.38, 0.37]], YL,
                        speed="2.5*sin(2*t)", size=0.055))
    voltage = "(p.vp*p.ns/250)"
    return spec(
        "Ideal single-phase transformer", objects,
        "The primary has 250 turns. Change the secondary turns and compare the output voltage, current and reflected resistance.",
        [param("ns", "Secondary turns", 50, 400, 200, 25),
         param("vp", "Primary RMS voltage", 20, 240, 100, 10, "V"),
         param("load", "Secondary load", 10, 100, 40, 5, "Ω")],
        [readout("Secondary RMS voltage (V)", voltage), readout("Secondary RMS current (A)", f"{voltage}/p.load"),
         readout("Primary RMS current (A)", f"{voltage}*p.ns/(p.load*250)"),
         readout("Reflected load (Ω)", "p.load*(250/p.ns)**2")],
        cam=(4.6, 3.7, 10.5),
    )


@reg("four_stroke_3d", "Four-stroke engine · piston and crank position")
def four_stroke():
    # With 1 unit of crank radius and 2.6 of rod length, this is slider-crank geometry.
    angle = "(p.phase*PI/180)"
    pin_x = f"sin({angle})"
    pin_y = f"(-1.4+cos({angle}))"
    piston_y = f"({pin_y}+sqrt(2.6**2-({pin_x})**2))"
    stroke = "p.phase<180?'Intake':p.phase<360?'Compression':p.phase<540?'Power':'Exhaust'"
    objects = [
        cyl([0, 1.5, 0], 0.82, 3.2, CY, open=True, opacity=0.18, label="Cylinder wall",
            lp=[1.27, 0.7, 0], info="The transparent wall exposes the piston and connecting rod."),
        cyl([0, 3.12, 0], 0.89, 0.17, ST, metal=0.55),
        cyl([0, -1.4, -0.25], 1.11, 0.24, DK, axis="z", label="Crankshaft",
            lp=[1.65, -0.6, 0], info="Two crankshaft turns complete one four-stroke cycle."),
        vec([0, -1.4, 0.12], [pin_x, pin_y, 0.12], OR, r=0.072),
        vec([pin_x, pin_y, 0.12], [0, piston_y, 0.12], LG, r=0.08),
        sphere([0, 0, 0.12], 0.13, OR, bind={"pos.x": pin_x, "pos.y": pin_y}),
        cyl([0, 1.5, 0], 0.73, 0.46, LG, metal=0.55, label="Piston",
            lp=[1.07, 0.18, 0], bind={"pos.y": piston_y}),
        cyl([-0.42, 3.35, 0], 0.13, 0.52, CY, label="Inlet",
            bind={"pos.y": "p.phase<180?3.17:3.35"}),
        cyl([0.42, 3.35, 0], 0.13, 0.52, OR, label="Exhaust",
            bind={"pos.y": "p.phase>=540?3.17:3.35"}),
    ]
    return spec(
        "Four-stroke engine cycle", objects,
        "Scrub through 720° of crank rotation. Valve events are idealised at stroke boundaries.",
        [param("phase", "Crank angle", 0, 719, 30, 1, "°")],
        [readout("Stroke", stroke), readout("Travel from top dead centre (% of stroke)", f"50*(2.2-{piston_y})")],
        cam=(4.4, 2.4, 12), target=(0, 0.55, 0),
    )


@reg("beam_point_load_3d", "Simply supported beam · load, reactions and deflection")
def beam_point_load():
    # Pin and roller at x = 0 and 6 m. Deflection in mm with constant EI = 9000 kN m².
    left = "(p.load*(6-p.a)/6)"
    right = "(p.load*p.a/6)"
    a = "p.a"
    b = "(6-p.a)"
    deflection = (
        f"x<={a}?{left}*x*(36-{b}**2-x*x)/54:"
        f"{right}*(6-x)*(36-{a}**2-(6-x)**2)/54"
    )
    objects = [
        box([0, 0, 0], [6.25, 0.24, 0.64], ST, label="Beam", lp=[-0.6, 0.45, 0.42]),
        prism([-3, -0.6, 0], [[0, 0.45], [-0.4, -0.24], [0.4, -0.24]], 0.66, BL,
              label="Pin support", lp=[-0.44, -0.5, 0.3]),
        prism([3, -0.6, 0], [[0, 0.45], [-0.4, -0.24], [0.4, -0.24]], 0.66, CY,
              label="Roller support", lp=[0.52, -0.55, 0.3]),
        cyl([2.81, -0.96, 0], 0.12, 0.66, LG, axis="z"),
        cyl([3.19, -0.96, 0], 0.12, 0.66, LG, axis="z"),
        vec(["p.a-3", "0.65+p.load/17", 0.18], ["p.a-3", 0.19, 0.18], OR, r=0.06),
        sphere([0, 0.17, 0.18], 0.09, OR, label="Point load", lp=[0, 0.76, 0.24], bind={"pos.x": "p.a-3"}),
        vec([-3, f"-1.03-{left}/20", 0.4], [-3, -0.87, 0.4], BL, r=0.043),
        vec([3, f"-1.03-{right}/20", 0.4], [3, -0.87, 0.4], CY, r=0.043),
        plot(f"-({deflection})", 0, 6, [-3, 0, 0.49], 1, 0.065, YL, r=0.032),
        text([0, -1.4, 0.6], "Yellow: exaggerated deflection", YL, 0.28),
    ]
    return spec(
        "Point-loaded beam", objects,
        "Slide the load along a 6 m span. The arrows show the support reactions. The yellow curve exaggerates elastic deflection.",
        [param("a", "Load distance from the left support", 0.5, 5.5, 2, 0.1, "m"),
         param("load", "Downward load", 5, 35, 20, 1, "kN")],
        [readout("Left reaction (kN)", left), readout("Right reaction (kN)", right),
         readout("Moment under the load (kN·m)", f"{left}*p.a"),
         readout("Deflection under the load (mm)", f"p.load*{a}**2*{b}**2/162")],
        cam=(3.1, 3.4, 11), target=(0, -0.35, 0),
    )


@reg("gear_pair_3d", "Spur gear pair · speed, direction and ratio")
def gear_pair():
    objects = []
    for cx, teeth, radius, color, motion, label in (
        (-1.5, 12, 0.86, OR, "t*p.speed*6/20", "12-tooth driver"),
        (1.2, 24, 1.76, CY, "-t*p.speed*3/20+7.5", "24-tooth driven gear"),
    ):
        objects += [
            cyl([cx, 0, 0], radius, 0.42, color, axis="z", metal=0.35, label=label,
                lp=[0, 1.06 if teeth == 12 else 2.03, 0.32]),
            cyl([cx, 0, 0.12], 0.3, 1.2, ST, axis="z", metal=0.55),
            wire([[cx, 0, -0.38], [cx, 0, -1]], ST, 0.18),
        ]
        for tooth in range(teeth):
            rad = 2 * pi * tooth / teeth
            angle = f"({rad}+({motion})*PI/180)"
            reach = radius + 0.085
            objects.append(box([cx+reach*cos(rad), reach*sin(rad), 0],
                               [0.22, 0.205, 0.42], color, metal=0.35,
                               bind={"pos.x": f"{cx}+{reach}*cos({angle})",
                                     "pos.y": f"{reach}*sin({angle})", "rot.z": f"{tooth*360/teeth}+({motion})"}))
        phase = f"({motion})*PI/180"
        objects.append(sphere([cx+radius*0.7, 0, 0.26], 0.095, YL,
                              bind={"pos.x": f"{cx}+{radius*0.7}*cos({phase})",
                                    "pos.y": f"{radius*0.7}*sin({phase})"}))
    return spec(
        "External spur gears", objects,
        "Two external gears turn in opposite directions. Tooth shapes are simplified and rotation is slowed for viewing.",
        [param("speed", "Driver speed", -240, 240, 100, 10, "rpm")],
        [readout("Speed reduction", "'2:1'"), readout("Driven gear speed (rpm)", "-p.speed/2")],
        cam=(3.6, 4, 11), target=(0, 0.2, 0),
    )


@reg("survey_sight_3d", "Surveying · line of sight and elevation difference")
def survey_sight():
    far_x = "(-3.1+0.047*p.distance)"
    height = "(p.distance*tan(p.angle*PI/180))"
    sight_y = f"(0.6+0.067*{height})"
    objects = [
        box([0.1, -1.2, 0], [8.4, 0.18, 2.8], DK),
        box([-3.1, 0.6, 0], [0.46, 0.26, 0.32], OR, label="Instrument",
            bind={"rot.z": "p.angle"}, info="The angle is measured from the horizontal through the instrument."),
        wire([[-3.1, 0.46, 0], [-3.48, -1.1, 0.52]], LG, 0.042),
        wire([[-3.1, 0.46, 0], [-2.7, -1.1, 0.48]], LG, 0.042),
        wire([[-3.1, 0.46, 0], [-3.1, -1.1, -0.52]], LG, 0.042),
        box([0, 0.55, 0], [0.14, 3.5, 0.16], ST, label="Target staff",
            lp=[0.23, 1.87, 0.16], bind={"pos.x": far_x}),
        vec([-3.1, 0.6, 0], [far_x, sight_y, 0], CY, r=0.03),
        vec([-3.1, 0.6, 0.06], [far_x, 0.6, 0.06], LG, r=0.018),
        sphere([0, 0, 0.1], 0.12, YL, bind={"pos.x": far_x, "pos.y": sight_y}, label="Sight point"),
    ]
    return spec(
        "Trigonometric levelling", objects,
        "Vary the horizontal distance and signed vertical angle. Vertical and horizontal scales are schematic.",
        [param("distance", "Horizontal distance", 20, 135, 95, 5, "m"),
         param("angle", "Vertical angle", -10, 10, 5, 0.5, "°"),
         param("setup", "Instrument height above station", 1, 2.5, 1.5, 0.05, "m"),
         param("target", "Target height above station", 1, 2.5, 1.5, 0.05, "m")],
        [readout("Sight rise or fall (m)", height), readout("Target station minus instrument station (m)", f"p.setup+{height}-p.target")],
        cam=(3.6, 4.2, 11.8), target=(0.2, 0.2, 0),
    )


@reg("process_mixer_3d", "Mixing tank · total and solute balances")
def process_mixer():
    mixed = "((p.fa*p.ca+p.fb*p.cb)/(p.fa+p.fb))"
    left = [[-4, 1.55, 0], [-1.65, 1.55, 0], [-1.65, 0.5, 0]]
    right = [[4, 1.55, 0], [1.65, 1.55, 0], [1.65, 0.5, 0]]
    outlet = [[0, -0.73, 0], [0, -1.94, 0], [4.2, -1.94, 0]]
    objects = [
        cyl([0, -0.14, 0], 1.7, 2.3, ST, open=True, opacity=0.45, label="Mixing vessel",
            lp=[0, 1.69, 0.65], info="The model assumes steady state, complete mixing, and no reaction."),
        cyl([0, -0.6, 0], 1.65, 1.24, CY, opacity=0.6, bind={"color": f"{mixed}>20?'#3b82f6':'#22d3ee'"}),
        cyl([0, 0.24, 0], 0.1, 2.24, LG, metal=0.55, label="Agitator"),
        box([0, -0.68, 0], [2.27, 0.17, 0.32], OR, metal=0.35, bind={"rot.y": "t*108"}),
        text([-3.2, 2.0, 0], "Feed A", CY, 0.36), text([3.2, 2.0, 0], "Feed B", OR, 0.36),
        text([3, -2.46, 0], "Mixed outlet", GR, 0.36),
    ]
    for path, color, speed in ((left, CY, "p.fa/3"), (right, OR, "p.fb/3"), (outlet, GR, "(p.fa+p.fb)/5")):
        objects.extend([wire(path, ST, 0.155, opacity=0.42), flow(path, color, n=12, speed=speed, size=0.085)])
    return spec(
        "Steady-state mixing tank", objects,
        "Mix two solutions without reaction. Compare total mass flow and solute mass flow before and after the vessel.",
        [param("fa", "Feed A mass flow", 1, 20, 8, 1, "kg/min"), param("ca", "Feed A solute", 0, 45, 10, 1, "%"),
         param("fb", "Feed B mass flow", 1, 20, 12, 1, "kg/min"), param("cb", "Feed B solute", 0, 45, 30, 1, "%")],
        [readout("Outlet flow (kg/min)", "p.fa+p.fb"), readout("Outlet solute concentration (%)", mixed),
         readout("Solute flow (kg/min)", "(p.fa*p.ca+p.fb*p.cb)/100")],
        cam=(4.1, 4.3, 12.8),
    )


@reg("pulse_echo_3d", "Ultrasonic inspection · pulse echo and plate thickness")
def pulse_echo():
    right_x = "(-2.5+p.thickness/16)"
    pulse = "(-2.5+(1-abs(1-2*((t*5*p.speed/p.thickness)%1)))*p.thickness/16)"
    objects = [
        cyl([-3.15, 0, 0], 0.48, 1.12, CY, axis="x", label="Pulse-echo probe",
            lp=[0, 0.87, 0.6], info="The same probe sends a pulse and detects the echo reflected from the back wall."),
        box([0.5, 0, 0], [1, 2.6, 2.5], ST, opacity=0.4,
            bind={"pos.x": "-2.5+p.thickness/32", "scale.x": "p.thickness/16"}),
        box([0, 0, 0], [0.09, 2.6, 2.5], BL, opacity=0.72, label="Back wall",
            lp=[0.18, 1.8, 0.56], bind={"pos.x": right_x}),
        vec([-2.5, 0, 0], [right_x, 0, 0], CY, r=0.035),
        sphere([0, 0, 0], 0.19, OR, emissive=0.65, bind={"pos.x": pulse}),
    ]
    return spec(
        "Pulse-echo thickness gauge", objects,
        "Watch a pulse cross the plate and return from the back wall. The animation is slowed to show both legs.",
        [param("thickness", "Plate thickness", 15, 95, 50, 1, "mm"),
         param("speed", "Wave speed in the material", 2, 7, 5.9, 0.1, "mm/µs")],
        [readout("One-way travel (µs)", "p.thickness/p.speed"), readout("Echo delay (µs)", "2*p.thickness/p.speed")],
        cam=(3.5, 4, 12.3), target=(0, 0.3, 0),
    )


@reg("plc_interlock_3d", "PLC input and output · conveyor interlock")
def plc_interlock():
    on = "(p.command&&p.guard)"
    belt = [[2.65, 0.27, 0.1], [5.05, 0.27, 0.1]]
    objects = [
        box([-5, 1.08, 0], [1.45, 0.59, 0.56], OR, label="Run request",
            lp=[0, 0.54, 0], click={"command": "1-p.command"}),
        box([-5, -1.08, 0], [1.45, 0.59, 0.56], BL, label="Guard input",
            lp=[0, -0.53, 0], click={"guard": "1-p.guard"}),
        box([-1.2, 0, 0], [2.2, 2.6, 0.62], DK, label="PLC logic",
            lp=[0, 1.66, 0.33], info="In this training model the output is on only when both inputs are true."),
        wire([[-4.28, 1.08, 0], [-2.3, 1.08, 0]], OR, 0.055, bind={"color": f"p.command?'{OR}':'{ST}'"}),
        wire([[-4.28, -1.08, 0], [-2.3, -1.08, 0]], BL, 0.055, bind={"color": f"p.guard?'{CY}':'{ST}'"}),
        wire([[-0.08, 0, 0], [2.65, 0, 0]], GR, 0.06, bind={"color": f"{on}?'{GR}':'{ST}'"}),
        box([3.82, -0.08, 0.03], [2.8, 0.55, 1.04], ST, label="Conveyor drive", lp=[0.24, 1.04, 0.3]),
        cyl([2.6, 0.02, 0.05], 0.24, 1.14, LG, axis="z"),
        cyl([5.02, 0.02, 0.05], 0.24, 1.14, LG, axis="z"),
        flow(belt, GR, n=8, speed="1.7", size=0.093, bind={"visible": on}),
        sphere([-1.2, 0, 0.37], 0.2, GR, bind={"color": f"{on}?'{GR}':'{RD}'"}),
    ]
    return spec(
        "PLC conveyor interlock", objects,
        "Trace each input through the run-permission logic. This simplified model omits safety hardware and restart controls.",
        [param("command", "Run request", 0, 1, 1, 1, toggle=True),
         param("guard", "Guard closed", 0, 1, 1, 1, toggle=True)],
        [readout("Run request AND guard closed", f"{on}?1:0"),
         readout("Conveyor", f"{on}?'Running':'Stopped'")],
        cam=(3.9, 4.8, 15.5),
    )


@reg("h_bridge_3d", "Robot motor · H-bridge current and direction")
def h_bridge():
    objects = [
        cyl([0, 0, 0], 0.76, 0.58, ST, axis="z", label="DC motor",
            lp=[0, 0.98, 0.4], info="Swapping the voltage across the motor reverses its direction."),
        box([0, 0, 0.39], [0.13, 1.23, 0.12], YL, bind={"rot.z": "t*105*p.direction"}),
        text([0, 2.61, 0], "+ supply", OR, 0.35), text([0, -2.61, 0], "Return", BL, 0.35),
        wire([[-2.6, 2.07, 0], [2.6, 2.07, 0]], OR),
        wire([[-2.6, -2.07, 0], [2.6, -2.07, 0]], BL),
        wire([[-2.6, 0, 0], [-0.77, 0, 0]], LG),
        wire([[0.77, 0, 0], [2.6, 0, 0]], LG),
    ]
    for x, y, direction, label in ((-2.6, 1, 1, "Q1"), (2.6, 1, -1, "Q2"),
                                   (-2.6, -1, -1, "Q3"), (2.6, -1, 1, "Q4")):
        objects.extend([
            wire([[x, y*2.07, 0], [x, y*1.29, 0]], LG),
            wire([[x, y*0.71, 0], [x, 0, 0]], LG),
            box([x, y, 0], [0.8, 0.57, 0.48], DK, label=label, lp=[0.63 if x>0 else -0.63, 0, 0.22],
                bind={"color": f"p.direction=={direction}?'{GR}':'{DK}'"}),
        ])
    return spec(
        "H-bridge direction control", objects,
        "A diagonal switch pair drives the motor. Reverse selects the opposite pair. Off opens all four switches.",
        [param("direction", "Direction", -1, 1, 1, 1), param("v", "Supply", 3, 24, 12, 1, "V")],
        [readout("Command", "p.direction>0?'Forward':p.direction<0?'Reverse':'Off (coast)'"),
         readout("Closed switches", "p.direction>0?'Q1 + Q4':p.direction<0?'Q2 + Q3':'None'"),
         readout("Motor terminal voltage", "p.direction?String(p.direction*p.v)+' V':'Disconnected'")],
        cam=(3.6, 3.5, 12),
    )


@reg("composite_centroid_3d", "Composite section · area and centroid")
def composite_centroid():
    centroid_x = "(9+(3+2/3)*p.h)/(6+p.h)"
    centroid_y = "(6+p.h**2/3)/(6+p.h)"
    objects = [
        box([-1.5, 1, 0], [3, 2, 0.32], CY, label="3 × 2 rectangle",
            lp=[-0.55, 0.52, 0.21], info="The rectangle's centroid lies at its geometric centre."),
        prism([0, 0, 0], [[0, 0], [2, 0], [0, 1]], 0.32, OR, label="Right triangle",
              lp=[1.14, 0.42, 0.24], bind={"scale.y": "p.h"},
              info="The centroid is one third of the base and one third of the height from its right-angle vertex."),
        sphere([-1.5, 1, 0.24], 0.08, CY),
        sphere([2/3, 0, 0.24], 0.08, OR, bind={"pos.y": "p.h/3"}),
        sphere([0, 0, 0.36], 0.14, YL, label="Composite centroid",
               lp=[0.18, -0.45, 0.3], bind={"pos.x": f"{centroid_x}-3", "pos.y": centroid_y}),
        vec([-3, 0, 0.22], [2.6, 0, 0.22], LG, r=0.018),
        vec([-3, 0, 0.22], [-3, 3.2, 0.22], LG, r=0.018),
        text([2.62, -0.26, 0.26], "x", LG, 0.32),
        text([-3.15, 3.32, 0.26], "y", LG, 0.32),
    ]
    return spec(
        "Area centroid of a composite section", objects,
        "Move the triangle's top vertex. The yellow point weights the two shape centroids by their areas.",
        [param("h", "Triangle height", 0.5, 3, 1.5, 0.1, "m")],
        [readout("Total area (m²)", "6+p.h"), readout("Centroid x (m)", centroid_x),
         readout("Centroid y (m)", centroid_y)],
        cam=(3.1, 4, 11.3), target=(-0.25, 1.1, 0),
    )


@reg("turbine_stage_3d", "Steam turbine · enthalpy drop and shaft power")
def turbine_stage():
    steam_path = [[-4.5, 0, 0.45], [-0.1, 0, 0.45], [4.5, 0, 0.45]]
    power = "(p.mass*p.drop*p.eff/100)"
    objects = [
        cyl([0, 0, 0], 1.56, 4.85, ST, axis="x", open=True, opacity=0.24, label="Turbine casing",
            lp=[0, 1.82, 0.45]),
        cyl([0, 0, 0], 0.27, 7.05, ST, axis="x", metal=0.55, label="Rotor shaft",
            lp=[1.9, -0.71, 0.42]),
        cyl([0, 0, 0], 0.74, 0.33, OR, axis="x", metal=0.55),
        flow(steam_path, CY, n=21, speed="0.55+p.mass/8", size=0.085, jit=0.72),
        text([-3.65, 1.23, 0.48], "Steam in", CY, 0.36),
        text([3.7, 1.23, 0.48], "Steam out", LG, 0.36),
    ]
    for blade in range(12):
        theta = blade*pi/6
        phase = f"({theta}+t*2.3)"
        objects.append(box([0, 1.01*cos(theta), 1.01*sin(theta)], [0.36, 0.61, 0.18], OR,
                           bind={"pos.y": f"1.01*cos({phase})", "pos.z": f"1.01*sin({phase})",
                                 "rot.x": f"{blade*30}+t*2.3*180/PI"}))
    return spec(
        "Steam turbine stage", objects,
        "Compare shaft power at different mass flows and isentropic enthalpy drops. Rotor motion is illustrative.",
        [param("mass", "Steam mass flow", 1, 18, 6, 0.5, "kg/s"),
         param("drop", "Isentropic enthalpy drop", 50, 400, 160, 10, "kJ/kg"),
         param("eff", "Isentropic efficiency", 50, 95, 80, 1, "%")],
        [readout("Actual enthalpy drop (kJ/kg)", "p.drop*p.eff/100"),
         readout("Approximate shaft power (kW)", power)],
        cam=(5.1, 4.1, 10.5),
    )
