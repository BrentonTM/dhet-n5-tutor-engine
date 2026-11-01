"""Interactive 3D digital-electronics learning diagrams.

Digital Electronics N5 is offered here as a visualization preview only; its
programme syllabus map remains unverified in the curriculum catalogue.
"""

from ui.diagram_lib import *
from ui.diagram_registry import reg


BOARD = "#142235"
CHIP = "#263449"
COPPER = "#B87935"
LOW = "#475569"
HIGH = "#10B981"


def _board(title, size=(14, 9, 0.35)):
    return [
        box([0, 0, -0.75], list(size), BOARD, metal=0.35, rough=0.65,
            label="Insulated circuit board", lp=[-5.4, -size[1] / 2 + 0.35, 0.25],
            info="The board supports the components. Rotate the scene to inspect its depth and wiring."),
        line([[-size[0] / 2 + 0.3, -size[1] / 2 + 0.3, -0.55],
              [size[0] / 2 - 0.3, -size[1] / 2 + 0.3, -0.55]], "#3B536F", 0.02),
    ]


def _switch(name, x, y, parameter, color=OR):
    expr = f"p.{parameter}>0.5?'#10B981':'#475569'"
    return [
        box([x, y, 0.0], [1.0, 0.75, 0.55], CHIP, label=f"Input {name}",
            lp=[0, 0.67, 0.1], lsize=0.25,
            info=f"Click this 3D switch or use its slider to toggle logic input {name}.",
            click={parameter: f"1-p.{parameter}"}),
        cyl([x, y, 0.35], 0.20, 0.12, color, axis="z", bind={"color": expr, "emissive": f"p.{parameter}*0.65"},
            label=f"{name} input indicator", lp=[-0.45, -0.45, 0.15], lsize=0.22),
        box([x, y + 0.08, 0.52], [0.10, 0.42, 0.12], color,
            bind={"rot.z": f"p.{parameter}*28-14", "color": expr}),
    ]


def _gate_poly(kind):
    if kind == "AND":
        return [[-0.7, -0.45], [-0.12, -0.45], [0.20, -0.38], [0.43, -0.2],
                [0.5, 0], [0.43, 0.2], [0.20, 0.38], [-0.12, 0.45], [-0.7, 0.45]]
    if kind == "OR":
        return [[-0.65, -0.45], [-0.3, -0.45], [0.1, -0.32], [0.42, -0.12],
                [0.55, 0], [0.42, 0.12], [0.1, 0.32], [-0.3, 0.45], [-0.65, 0.45],
                [-0.45, 0], [-0.65, -0.45]]
    # XOR and NAND use the same extruded OR/AND body with a distinct name/bubble.
    return _gate_poly("OR" if kind == "XOR" else "AND")


@reg("logic_gate_board", "3D logic-gate board – click A and B")
def logic_gate_board():
    rows = [("AND", 2.7, "p.A*p.B", CY),
            ("OR", 0.9, "max(p.A,p.B)", VI),
            ("XOR", -0.9, "abs(p.A-p.B)", OR),
            ("NAND", -2.7, "1-p.A*p.B", "#F59E0B")]
    o = _board()
    o += _switch("A", -5.6, 3.15, "A", CY)
    o += _switch("B", -5.6, -3.15, "B", VI)
    o += [text([-5.9, 4.05, 0.2], "Click switches or adjust inputs below", WH, 0.23)]

    for name, y, expression, color in rows:
        o += [
            # Two labelled input traces feed each gate body.
            wire([[-5.0, 3.15, 0.3], [-4.4, 3.15, 0.3], [-4.4, y + 0.20, 0.3], [-1.5, y + 0.20, 0.3]],
                 COPPER, 0.055, bind={"color": f"p.A>0.5?'{HIGH}':'{LOW}'"}, label=f"A → {name}", lsize=0.20),
            wire([[-5.0, -3.15, 0.3], [-4.0, -3.15, 0.3], [-4.0, y - 0.20, 0.3], [-1.5, y - 0.20, 0.3]],
                 COPPER, 0.055, bind={"color": f"p.B>0.5?'{HIGH}':'{LOW}'"}, label=f"B → {name}", lsize=0.20),
            prism([-0.8, y, 0.15], _gate_poly(name), 0.55, color, label=f"{name} gate",
                  la=[-0.1, 0.72, 0.2], lsize=0.25,
                  info=f"3D {name} gate symbol. Inputs A and B determine the output shown by the LED."),
            wire([[-0.3, y, 0.48], [1.3, y, 0.48], [2.0, y, 0.48]], color, 0.06,
                 bind={"color": f"({expression})>0.5?'{HIGH}':'{LOW}'"}, label=f"{name} output", lsize=0.20),
            sphere([2.25, y, 0.48], 0.22, LOW,
                   bind={"color": f"({expression})>0.5?'{HIGH}':'{LOW}'",
                         "emissive": f"({expression})*0.8"},
                   label=f"{name} output LED", lp=[0.55, 0.0, 0.1], lsize=0.20,
                   info="Green means logic 1; dark means logic 0."),
            text([3.25, y, 0.3], f"Y = {name}", color, 0.25),
        ]

    return spec(
        "Digital Electronics N4 – interactive logic gates",
        o,
        "Toggle A and B. Green traces/LEDs represent logic 1; dark traces/LEDs represent logic 0.",
        [param("A", "Input A", 0, 1, 0, 1, toggle=True), param("B", "Input B", 0, 1, 0, 1, toggle=True)],
        [readout("Current truth-table row A, B", "Math.round(p.A)+', '+Math.round(p.B)"),
         readout("AND, OR, XOR, NAND outputs", "Math.round(p.A*p.B)+', '+Math.round(max(p.A,p.B))+', '+Math.round(abs(p.A-p.B))+', '+Math.round(1-p.A*p.B)"),
         readout("Boolean relations", "'AND = A·B   OR = A+B   XOR = A⊕B   NAND = ¬(A·B)'"),
         readout("Learning check", "p.A*p.B>0.5?'Both inputs are HIGH: AND is 1 and NAND is 0.':(p.A+p.B>0.5?'At least one input is HIGH.':'Both inputs are LOW.')")],
        cam=(0.5, 8.4, 17), target=(-0.5, 0, 0), grid_y=-4.6,
    )


@reg("kmap4", "4-variable Karnaugh map – click cells to set minterms")
def kmap4():
    gray = ["00", "01", "11", "10"]
    o = _board((11, 10, 0.35))
    o += [text([-4.6, 3.7, 0.25], "CD →", CY, 0.25),
          text([-5.15, 0.0, 0.25], "AB ↓", CY, 0.25),
          text([3.3, -4.2, 0.25], "Yellow = 1   ·   dark = 0", YL, 0.22),
          text([3.3, -4.65, 0.25], "Adjacent cells can be grouped in powers of 2", WH, 0.20)]

    minterms = []
    for row, ab in enumerate(gray):
        y = 2.6 - row * 1.55
        o.append(text([-3.85, y, 0.28], ab, WH, 0.23))
        for col, cd in enumerate(gray):
            x = -2.45 + col * 1.55
            if row == 0:
                o.append(text([x, 3.35, 0.28], cd, CY, 0.22))
            m = int(ab + cd, 2)
            key = f"m{m}"
            minterms.append(m)
            o.append(box([x, y, 0.1], [1.16, 1.05, 0.55], LOW,
                         bind={"color": f"p.{key}>0.5?'#FACC15':'#334155'",
                               "emissive": f"p.{key}*0.45"},
                         label=f"m{m}", la=[x, y + 0.12, 0.5], lsize=0.25,
                         click={key: f"1-p.{key}"},
                         info=f"Minterm m{m}: AB={ab}, CD={cd}. Click to toggle the truth-table output F for this input combination."))
    params = [param(f"m{i}", f"Minterm m{i}", 0, 1, 0, 1, hidden=True) for i in range(16)]
    minterm_expr = "var m=[];" + "".join(f"if(p.m{i}>0.5)m.push('m{i}');" for i in minterms) + "return m.length?m.join(', '):'none';"
    return spec(
        "Digital Electronics N4 – clickable 4-variable Karnaugh map",
        o,
        "Gray-code order on both axes: 00, 01, 11, 10. Toggle cells to set F=1, then group adjacent 1s; wraparound edges are adjacent.",
        params,
        [readout("Minterms set to 1", minterm_expr),
         readout("Number of 1-cells", "+".join(f"Math.round(p.m{i})" for i in minterms)),
         readout("Grouping rule", "'Use the largest adjacent groups of 1, 2, 4, 8, or 16 cells; groups may overlap.'")],
        cam=(0, 8.8, 16), target=(-0.2, 0, 0), grid_y=-5.0,
    )


@reg("full_adder_3d", "Full-adder circuit – interactive A, B and carry-in")
def full_adder_3d():
    o = _board((15, 8.5, 0.35))
    for name, x, y, key, color in (("A", -5.5, 2.65, "A", CY),
                                    ("B", -5.5, 0.5, "B", VI),
                                    ("Cin", -5.5, -1.65, "Cin", OR)):
        o += _switch(name, x, y, key, color)

    # The board-level circuit uses two XOR, two AND and one OR gate.
    chips = [("XOR₁", -1.9, 2.2, VI), ("XOR₂", 1.25, 1.25, VI),
             ("AND₁", -1.9, -0.1, CY), ("AND₂", 1.25, -1.35, CY),
             ("OR", 4.0, -0.2, OR)]
    for name, x, y, color in chips:
        o += [box([x, y, 0.05], [2.05, 1.05, 0.65], CHIP, label=f"{name} IC",
                  lp=[0, 0.68, 0.1], lsize=0.24,
                  info=f"{name} logic stage in the full-adder network."),
              text([x, y, 0.42], name, color, 0.33)]

    # Interconnects are routed as visible, raised 3D copper traces.
    nets = [
        ("A to XOR₁", [[-4.9, 2.65, 0.25], [-3.5, 2.65, 0.25], [-3.5, 2.42, 0.25], [-2.95, 2.42, 0.25]], "p.A"),
        ("B to XOR₁", [[-4.9, 0.5, 0.25], [-3.2, 0.5, 0.25], [-3.2, 2.0, 0.25], [-2.95, 2.0, 0.25]], "p.B"),
        ("XOR₁ to XOR₂", [[-0.88, 2.2, 0.25], [0.15, 2.2, 0.25], [0.15, 1.47, 0.25], [0.22, 1.47, 0.25]], "abs(p.A-p.B)"),
        ("Cin to XOR₂", [[-4.9, -1.65, 0.25], [-2.8, -1.65, 0.25], [-2.8, 1.02, 0.25], [0.22, 1.02, 0.25]], "p.Cin"),
        ("A·B to OR", [[-4.9, 2.65, 0.5], [-3.9, 2.65, 0.5], [-3.9, 0.15, 0.5], [-2.95, 0.15, 0.5], [-0.88, -0.1, 0.25], [3.0, -0.1, 0.25]], "p.A*p.B"),
        ("Cin·(A⊕B) to OR", [[-4.9, -1.65, 0.5], [-3.6, -1.65, 0.5], [-3.6, -0.45, 0.5], [-2.95, -0.45, 0.5], [-0.88, -1.35, 0.25], [3.0, -0.45, 0.25]], "p.Cin*abs(p.A-p.B)"),
        ("XOR₂ to Sum", [[2.28, 1.25, 0.25], [5.5, 1.25, 0.25]], "abs(abs(p.A-p.B)-p.Cin)"),
        ("OR to Carry", [[5.03, -0.2, 0.25], [5.5, -0.2, 0.25]], "p.A*p.B+p.Cin*abs(p.A-p.B)"),
    ]
    for name, pts, expression in nets:
        o.append(wire(pts, COPPER, 0.05, label=name, lsize=0.19,
                      bind={"color": f"({expression})>0.5?'#10B981':'#475569'"}))

    sum_expr = "abs(abs(p.A-p.B)-p.Cin)"
    carry_expr = "p.A*p.B+p.Cin*abs(p.A-p.B)"
    for y, name, expression in ((1.25, "SUM", sum_expr), (-0.2, "CARRY", carry_expr)):
        o += [sphere([5.8, y, 0.35], 0.26, LOW,
                     bind={"color": f"({expression})>0.5?'#10B981':'#475569'",
                           "emissive": f"({expression})*0.75"},
                     label=f"{name} output", lp=[0.65, 0, 0.15], lsize=0.23)]

    return spec(
        "Digital Electronics N4 – full-adder circuit",
        o,
        "Two XOR gates generate SUM; two AND gates and one OR gate generate CARRY. Toggle inputs or click each switch.",
        [param("A", "Input A", 0, 1, 0, 1, toggle=True),
         param("B", "Input B", 0, 1, 0, 1, toggle=True),
         param("Cin", "Carry-in Cin", 0, 1, 0, 1, toggle=True)],
        [readout("SUM = A ⊕ B ⊕ Cin", sum_expr),
         readout("CARRY = AB + Cin(A ⊕ B)", carry_expr),
         readout("Three-bit addition", "Math.round(p.A)+Math.round(p.B)+Math.round(p.Cin)+' = '+(Math.round(p.A)+Math.round(p.B)+Math.round(p.Cin))")],
        cam=(0.2, 8.5, 17), target=(0, 0, 0), grid_y=-4.6,
    )


@reg("weighted_dac_3d", "4-bit binary-weighted DAC – interactive switch circuit")
def weighted_dac_3d():
    o = _board((15, 8.5, 0.35))
    bits = [("D3", 8, 3.0, CY, "b3"), ("D2", 16, 1.0, VI, "b2"),
            ("D1", 32, -1.0, OR, "b1"), ("D0", 64, -3.0, YL, "b0")]
    for name, resistance, y, color, key in bits:
        o += _switch(name, -5.0, y, key, color)
        o += [wire([[-4.4, y, 0.35], [-3.3, y, 0.35]], color, 0.05,
                   bind={"color": f"p.{key}>0.5?'#10B981':'#475569'"}),
              box([-2.4, y, 0.1], [1.3, 0.5, 0.6], "#C28E53", metal=0.65,
                  label=f"R{resistance} = {resistance}R", lp=[0, 0.48, 0.1], lsize=0.2,
                  info=f"Binary-weighted input resistor: {resistance}R."),
              wire([[-1.75, y, 0.35], [-0.2, y, 0.35], [-0.2, 0, 0.35], [0.55, 0, 0.35]], color, 0.045,
                   bind={"color": f"p.{key}>0.5?'#10B981':'#475569'"}, label=f"{name} contribution", lsize=0.18)]
    o += [
        prism([1.35, 0, 0.1], [[-0.8, -1.2], [0.8, 0], [-0.8, 1.2]], 0.75, GR,
              label="Summing op-amp", la=[0, 1.55, 0.25], lsize=0.24,
              info="The inverting summing amplifier adds the binary-weighted currents. This ideal model uses Rf = 4R."),
        text([0.95, 0.18, 0.7], "−", WH, 0.35), text([0.95, -0.45, 0.7], "+", WH, 0.35),
        wire([[2.15, 0, 0.35], [4.0, 0, 0.35]], OR, 0.06, label="Analog output Vout", lsize=0.2),
        sphere([4.25, 0, 0.35], 0.25, LOW,
               bind={"color": "abs(-5*(p.b3/2+p.b2/4+p.b1/8+p.b0/16))>0.05?'#10B981':'#475569'",
                     "emissive": "abs(-5*(p.b3/2+p.b2/4+p.b1/8+p.b0/16))/5*0.8"},
               label="Vout indicator", lp=[0.55, 0, 0.15], lsize=0.2),
        box([-5.0, 4.0, 0.1], [1.6, 0.6, 0.5], CHIP, label="VREF = 5 V", lp=[0, 0.55, 0.1]),
        text([2.4, -1.4, 0.3], "Ideal inverting binary-weighted DAC", CY, 0.23),
    ]
    return spec(
        "Digital Electronics N5 visualization preview – 4-bit DAC",
        o,
        "Each switch selects VREF or 0 V. A weighted resistor network feeds the virtual-ground summing node; this is a simplified ideal circuit model.",
        [param("b3", "D3 (MSB)", 0, 1, 0, 1, toggle=True),
         param("b2", "D2", 0, 1, 0, 1, toggle=True),
         param("b1", "D1", 0, 1, 0, 1, toggle=True),
         param("b0", "D0 (LSB)", 0, 1, 0, 1, toggle=True)],
        [readout("Digital input code D3D2D1D0", "Math.round(p.b3)+''+Math.round(p.b2)+Math.round(p.b1)+Math.round(p.b0)"),
         readout("Decimal code", "8*Math.round(p.b3)+4*Math.round(p.b2)+2*Math.round(p.b1)+Math.round(p.b0)"),
         readout("Ideal output Vout", "(-5*(p.b3/2+p.b2/4+p.b1/8+p.b0/16)).toFixed(3)+' V'"),
         readout("Range", "'0000 → 0 V; 1111 → −4.6875 V (inverting output)'"),
         readout("Curriculum status", "'Visualization preview; not a verified N5 syllabus map.'")],
        cam=(0.2, 8.5, 18), target=(0, 0, 0), grid_y=-4.6,
    )


@reg("flash_adc_3d", "4-bit flash ADC – interactive comparator ladder")
def flash_adc_3d():
    o = _board((16, 9.5, 0.35))
    o += [text([-6.8, 3.75, 0.25], "15 threshold comparators", CY, 0.24),
          text([-6.8, 0.75, 0.25], "Shared analog input Vin", OR, 0.22),
          text([-6.8, -2.15, 0.25], "Equal-resistor reference ladder", VI, 0.22),
          text([0.0, -4.0, 0.25], "4-bit priority encoder", GR, 0.24)]

    # A 16-step ladder generates the 15 flash-comparator thresholds.
    x_left, spacing, ladder_y = -6.5, 0.86, -2.55
    for index in range(16):
        x = x_left + index * spacing
        if index < 15:
            o.append(box([x + spacing / 2, ladder_y, 0.08], [0.46, 0.26, 0.42], "#C28E53",
                         metal=0.6, label=f"R{index + 1}", lp=[0, -0.34, 0.1], lsize=0.16,
                         info="Equal resistor segment in the reference-voltage divider."))
        if index > 0:
            o.append(wire([[x - spacing / 2, ladder_y, 0.28], [x, ladder_y, 0.28]], COPPER, 0.035))
        if index in (0, 15):
            o.append(sphere([x, ladder_y, 0.28], 0.10, YL if index == 15 else BL,
                            label="VREF = 5 V" if index == 15 else "0 V reference",
                            lp=[0, -0.55, 0.1], lsize=0.18))

    # Each comparator changes state when Vin crosses its ladder tap.
    for k in range(1, 16):
        x = x_left + k * spacing
        threshold = 5 * k / 16
        active = f"p.Vin>={threshold:.5f}"
        o += [
            wire([[x, ladder_y + 0.2, 0.28], [x, 1.22, 0.28]], VI, 0.025,
                 label=f"Reference {threshold:.2f} V", lsize=0.17),
            box([x, 1.6, 0.08], [0.58, 0.62, 0.48], CHIP,
                bind={"color": f"{active}?'#10B981':'#334155'"},
                label=f"Comparator C{k:02d}", lp=[0, 0.52, 0.15], lsize=0.17,
                info=f"Comparator C{k:02d} switches HIGH when Vin ≥ {threshold:.3f} V."),
            sphere([x, 2.08, 0.42], 0.11, LOW,
                   bind={"color": f"{active}?'#10B981':'#475569'",
                         "emissive": f"({active})?0.7:0.03"},
                   label=f"C{k:02d} output", lp=[0, 0.27, 0.1], lsize=0.15),
            wire([[x, 0.45, 0.62], [x, 1.25, 0.62]], OR, 0.035,
                 bind={"color": f"p.Vin>={threshold:.5f}?'#10B981':'#475569'"}),
        ]

    # The Vin bus is raised above the comparator reference connections.
    o += [wire([[-7.2, 0.45, 0.62], [7.2, 0.45, 0.62]], OR, 0.06,
               label="Vin bus – shared comparator input", la=[0, 0.68, 0.3], lsize=0.2),
          box([-7.0, 0.45, 0.2], [0.8, 0.85, 0.55], CHIP,
              label="Analog Vin", lp=[0, -0.65, 0.1], lsize=0.18,
              info="Adjust Vin with the slider; the comparator bank forms a thermometer code."),
          box([0, -3.55, 0.08], [2.7, 0.95, 0.62], CHIP,
              label="Priority encoder", lp=[0, -0.68, 0.12], lsize=0.2,
              info="Encodes the highest active comparator into the four-bit binary output."),
          text([0, -3.55, 0.48], "THERMOMETER → BINARY", GR, 0.22)]

    code = "min(15,floor(p.Vin*16/5))"
    for index, weight in enumerate((8, 4, 2, 1)):
        x = 2.6 + index * 1.15
        bit = f"(floor(p.Vin*16/5)&{weight})>0"
        o += [wire([[1.35, -3.55, 0.35], [x - 0.25, -3.55, 0.35]], GR, 0.035),
              sphere([x, -3.55, 0.42], 0.18, LOW,
                     bind={"color": f"{bit}?'#10B981':'#475569'",
                           "emissive": f"({bit})?0.7:0.02"},
                     label=f"B{3-index} (weight {weight})", lp=[0, -0.43, 0.12], lsize=0.17)]

    return spec(
        "Digital Electronics N5 visualization preview – 4-bit flash ADC",
        o,
        "Vin is compared with 15 equal-step thresholds. The thermometer-code pattern is encoded as a 4-bit output; VREF = 5 V.",
        [param("Vin", "Analog input Vin", 0, 5, 2.1, 0.01, "V")],
        [readout("Thermometer-code comparator count", code),
         readout("4-bit output B3 B2 B1 B0", "var n=" + code + ";return ((n>>3)&1)+''+((n>>2)&1)+''+((n>>1)&1)+''+(n&1);"),
         readout("Quantization step Δ", "(5/16).toFixed(4)+' V'"),
         readout("Quantized level", "(5*" + code + "/16).toFixed(3)+' V'"),
         readout("Ideal quantization error", "(p.Vin-5*" + code + "/16).toFixed(3)+' V'"),
         readout("Curriculum status", "'Visualization preview; not a verified N5 syllabus map.'")],
        cam=(0.0, 8.8, 18.5), target=(0, 0, 0), grid_y=-4.9,
    )
