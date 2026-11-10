"""Circuit models shared by lessons, question walkthroughs and fault cases."""

from math import cos, pi, sin

from ui.diagram_lib import BL, CY, DK, GR, LG, OR, RD, ST, box, cyl, flow, param, readout, spec, sphere, text, torus, wire
from ui.diagram_registry import reg


def _component(name, position, size, color, explanation):
    return box(position, size, color, label=name, lp=[0, size[1] / 2 + 0.32, 0.45], lsize=0.26, info=explanation)


def _banded_resistor(y, parameter, name):
    colours = "['#17202c','#76472d','#e84546','#f59025','#f4d447','#48b477','#3f7bdf','#a461db','#9ca3af','#f8fafc']"
    value = f"p.{parameter}"
    digits = f"({value}>=1000?floor({value}/100):floor({value}/10))"
    separated = [0, y * 0.22, 0.95]
    parts = [
        cyl([0, y, 0], 0.28, 1.65, "#d6ab72", axis="x", label=name,
            lp=[0, 0.48, 0.38], lsize=0.28, explode=separated,
            info="Axial resistor. The colour bands update with the selected resistance."),
        cyl([-0.94, y, 0], 0.065, 0.32, LG, axis="x", metal=0.65, explode=separated),
        cyl([0.94, y, 0], 0.065, 0.32, LG, axis="x", metal=0.65, explode=separated),
        cyl([0.55, y, 0], 0.283, 0.095, "#d4af37", axis="x", explode=separated),
    ]
    for x, band in ((-0.52, f"floor({digits}/10)"), (-0.24, f"{digits}%10"),
                    (0.04, f"{value}>=1000?2:1")):
        parts.append(cyl([x, y, 0], 0.283, 0.108, ST, axis="x",
                         explode=separated, bind={"color": f"{colours}[{band}]"}))
    return parts


@reg("dc_resistor_network", "DC circuit · series and parallel resistor network")
def dc_resistor_network():
    supply = _component("DC supply", [-5, 0, 0], [1.35, 1.6, 0.65], DK, "Sets the voltage across the complete network.")
    objects = [
        supply, *_banded_resistor(1.65, "r1", "Resistor R1"), *_banded_resistor(-1.65, "r2", "Resistor R2"),
        text([-5, 0.38, 0.42], "+", RD, 0.36), text([-5, -0.38, 0.42], "−", CY, 0.36),
        wire([[-5, 0.8, 0], [-5, 1.65, 0], [-1.1, 1.65, 0]], OR, 0.07),
        wire([[1.1, 1.65, 0], [3, 1.65, 0], [3, -1.65, 0], [1.1, -1.65, 0]], CY, 0.07),
        wire([[-1.1, -1.65, 0], [-3.5, -1.65, 0], [-3.5, -0.8, 0], [-5, -0.8, 0]],
             CY, 0.07, bind={"visible": "!p.parallel"}),
        wire([[-1.1, -1.65, 0], [-3.5, -1.65, 0], [-3.5, 1.65, 0]],
             OR, 0.07, bind={"visible": "p.parallel"}),
        wire([[3, -1.65, 0], [3, -2.95, 0], [-5, -2.95, 0], [-5, -0.8, 0]],
             CY, 0.07, bind={"visible": "p.parallel"}),
        sphere([-3.5, 1.65, 0], 0.11, OR, bind={"visible": "p.parallel"}),
        sphere([3, -1.65, 0], 0.11, CY, bind={"visible": "p.parallel"}),
    ]
    resistance = "(p.parallel?p.r1*p.r2/(p.r1+p.r2):p.r1+p.r2)"
    series_current = "p.volts/(p.r1+p.r2)"
    current_1 = f"(p.parallel?p.volts/p.r1:{series_current})"
    current_2 = f"(p.parallel?p.volts/p.r2:{series_current})"
    return spec(
        "DC resistor network", objects, "Trace both paths and compare what stays the same in series and parallel.",
        [param("parallel", "Wiring", 0, 1, 0, 1, names=["Series", "Parallel"]),
         param("volts", "Supply", 1, 24, 12, 1, "V"),
         param("r1", "R1", 100, 1000, 100, 50, "Ω"),
         param("r2", "R2", 100, 1000, 200, 50, "Ω")],
        [readout("Equivalent resistance (Ω)", resistance),
         readout("Supply current (mA)", f"1000*p.volts/{resistance}"),
         readout("R1 current (mA)", f"1000*{current_1}"), readout("R2 current (mA)", f"1000*{current_2}"),
         readout("Voltage across R1 (V)", f"p.r1*{current_1}"), readout("Voltage across R2 (V)", f"p.r2*{current_2}")],
        cam=(-0.45, 5, 15.5), target=(-0.9, -0.3, 0),
    )


@reg("ripple_counter_3d", "4-bit ripple counter · clock, stages and reset")
def ripple_counter():
    positions = [-3.4, -0.95, 1.5, 3.95]
    objects = [
        box([0, 0.08, -0.65], [13.25, 4.8, 0.25], "#194238"),
        _component("Clock input", [-5.65, 0, 0], [1.15, 0.88, 0.56], OR,
                   "Only the first stage receives the external clock."),
        wire([[-5.075, 0, 0], [-4.25, 0, 0]], OR, 0.06),
        wire([[-5, -1.45, 0], [3.95, -1.45, 0]], RD, 0.045),
        _component("Reset input", [-5.65, -1.45, 0], [1.15, 0.6, 0.55], RD,
                   "The reset line clears every stage. A decoded reset can shorten the count sequence."),
        wire([[-5.075, -1.45, 0], [-5, -1.45, 0]], RD, 0.045),
    ]
    for x in (-6.25, 6.25):
        for y in (-2.05, 2.22):
            objects.append(cyl([x, y, -0.46], 0.16, 0.13, LG, axis="z", metal=0.65))
    count = "(p.pulses%p.modulus)"
    for bit, x in enumerate(positions):
        output = f"(floor({count}/{2 ** bit})%2)"
        binding = {"color": f"{output}?'#10B981':'#475569'"}
        offset = [x * 0.15, 0.03, 0.85]
        objects += [
            dict(_component(f"Stage Q{bit}", [x, 0, 0], [1.7, 0.9, 0.65], DK,
                            f"Toggle stage {bit}. The settled output repeats every {2 ** (bit + 1)} input clocks at modulus 16."),
                 explode=offset),
            wire([[x, -1.45, 0], [x, -0.45, 0]], RD, 0.04),
            wire([[x + 0.85, 0, 0], [x + 1.04, 0, 0], [x + 1.04, 1.2, 0]], ST, 0.055, bind=binding),
            sphere([x + 1.04, 1.4, 0], 0.22, LG, label=f"Q{bit} output", lp=[0, 0.45, 0.12], lsize=0.24,
                   info=f"Bit weight {2 ** bit}. Green means HIGH.", bind=binding),
        ]
        for pin in (-0.43, -0.14, 0.14, 0.43):
            for side in (-1, 1):
                objects.append(box([x + pin, side * 0.47, 0.04], [0.13, 0.25, 0.15], LG,
                                   metal=0.65, explode=offset))
        if bit < len(positions) - 1:
            objects.append(wire([[x + 1.04, 0, 0], [positions[bit + 1] - 0.85, 0, 0]], ST, 0.055, bind=binding))
    return spec(
        "Four-bit asynchronous counter", objects,
        "A falling edge at one stage clocks the next. Read the settled state after each pulse. Propagation delays are omitted.",
        [param("pulses", "Clock pulses since reset", 0, 32, 0, 1), param("modulus", "States before decoded reset", 2, 16, 16, 1)],
        [readout("Binary Q3 Q2 Q1 Q0", f"{count}.toString(2).padStart(4,'0')"),
         readout("Settled decimal count", count)],
        cam=(0, 5.8, 16.7), target=(-0.2, 0, 0), grid=False,
    )


@reg("current_loop_3d", "4–20 mA loop · transmitter, wiring and receiver")
def current_loop():
    upper = [[-4.9, 0.85, 0], [-4.9, 2, 0], [-1.35, 2, 0]]
    outgoing = [[1.35, 2, 0], [2.2, 2, 0], [3.1, 2, 0], [4.8, 2, 0], [4.8, 0.65, 0]]
    lower = [[4.8, -0.65, 0], [4.8, -1.9, 0], [-4.9, -1.9, 0], [-4.9, -0.85, 0]]
    current = "(p.open?0:4+0.16*p.process)"
    cover_offset = [0, 0.85, 1.45]
    objects = [
        _component("24 V supply", [-4.9, 0, 0], [1.6, 1.7, 0.68], DK, "Powers the two-wire loop."),
        cyl([0, 2, -0.14], 0.72, 0.52, "#39667c", axis="z", metal=0.6, label="Field transmitter",
            lp=[0, 0.95, 0.22], lsize=0.3, explode=[0, 0, 0],
            info="Two-wire head. It draws its operating power from the same loop whose current it regulates."),
        cyl([0, 2, 0.23], 0.68, 0.14, "#264853", axis="z", metal=0.5, explode=cover_offset),
        torus([0, 2, 0.32], 0.62, 0.045, CY, metal=0.5, explode=cover_offset),
        box([0, 2.04, 0.33], [0.73, 0.3, 0.07], "#091f2d", explode=cover_offset),
        cyl([0, 2, 0.11], 0.52, 0.055, "#288c66", axis="z",
            bind={"visible": "p.assembly>0.16"}, label="Transmitter PCB", lp=[0, -0.8, 0.05], explode=[0, 0, 0.18],
            info="Signal conditioning and current regulation sit inside the housing."),
        box([0, 2.06, 0.2], [0.42, 0.22, 0.1], DK,
            bind={"visible": "p.assembly>0.16"}, explode=[0, 0, 0.18]),
        _component("Receiver shunt", [4.8, 0, 0], [1.8, 1.3, 0.68], BL,
                   "The PLC measures voltage across this 250 Ω resistor. The current passes through it."),
        wire(upper, OR, 0.065), wire(outgoing[:2], OR, 0.065), wire(outgoing[2:], OR, 0.065), wire(lower, CY, 0.065),
        wire(outgoing[1:3], OR, 0.065, bind={"visible": "!p.open"}),
        sphere([2.2, 2, 0], 0.15, LG, label="Junction terminal", lp=[0.35, -0.52, 0.35], lsize=0.24,
               info="Tap to open or close the junction. An open path stops loop current.", click={"open": "1-p.open"}),
        sphere([3.1, 2, 0], 0.13, LG),
        text([-4.35, 0.9, 0.42], "+", RD, 0.36), text([-4.35, -0.9, 0.42], "−", CY, 0.36),
        box([4.8, 0, 0.38], [1.21, 0.68, 0.1], "#152642", explode=[0.96, 0, 0.8]),
        cyl([4.8, 0.46, 0.44], 0.13, 0.1, LG, axis="z", metal=0.7, explode=[0.96, 0, 0.8]),
        cyl([4.8, -0.46, 0.44], 0.13, 0.1, LG, axis="z", metal=0.7, explode=[0.96, 0, 0.8]),
    ]
    for step in range(8):
        angle = step * pi / 4
        objects.append(cyl([0.55 * cos(angle), 2 + 0.55 * sin(angle), 0.34], 0.065, 0.05,
                           LG, axis="z", seg=6, metal=0.65, explode=cover_offset))
    for side in (-1, 1):
        objects.extend([
            cyl([side * 1.02, 2, 0], 0.16, 0.66, LG, axis="x", metal=0.65),
            cyl([side * 0.91, 2, 0], 0.24, 0.24, DK, axis="x", seg=6),
            cyl([side * 1.26, 2, 0], 0.21, 0.12, ST, axis="x", seg=6, metal=0.6),
        ])
    for slot in range(5):
        objects.append(box([-4.9, -0.51 + 0.14 * slot, 0.36], [0.98, 0.036, 0.038], ST,
                           explode=[-0.98, 0, 0.8]))
    for path in (upper, outgoing, lower):
        objects.append(flow(path, GR, n=10, speed=f"{current}*0.22", size=0.07, bind={"visible": "!p.open"}))
    return spec(
        "Two-wire 4–20 mA instrumentation loop", objects,
        "Current passes through transmitter and shunt. Compare a healthy live zero with an open circuit.",
        [param("process", "Process input", 0, 100, 50, 1, "%"), param("open", "Open junction", 0, 1, 0, 1, toggle=True)],
        [readout("Loop current (mA)", current), readout("PLC input across 250 Ω (V)", f"{current}*0.25"),
         readout("Signal status", "p.open?'Loop open':'Valid process signal'")],
        cam=(0.4, 5.8, 16.5), target=(0, 0.1, 0), grid=False,
    )
