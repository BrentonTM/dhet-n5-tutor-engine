"""Interactive models for curriculum topics without an existing study diagram."""

from ui.diagram_lib import CY, DK, GR, LG, OR, YL, box, cyl, line, param, plot, pt, readout, spec, sphere, text
from ui.diagram_registry import reg


@reg("determinant_area", "2×2 determinant · area and orientation")
def determinant_area():
    objects = [line([[-0.5, 0, 0], [4.5, 0, 0]], LG), line([[0, -0.5, 0], [0, 4.5, 0]], LG)]
    for colour, x, y, offset_x, offset_y, label in (
        (CY, "p.a", "1", "1", "p.d", "u = (a, 1)"),
        (OR, "1", "p.d", "p.a", "1", "v = (1, d)"),
    ):
        objects.append(sphere([0, 0, 0], 0.15, colour, label=label,
                              bind={"pos.x": x, "pos.y": y}))
        objects.append(plot(f"x*({y})/({x})", 0, 1, [0, 0, 0], 1, 1, colour,
                            bind={"scale.x": x, "scale.y": x}))
        objects.append(plot(f"x*({y})/({x})", 0, 1, [0, 0, 0], 1, 1, colour,
                            bind={"scale.x": x, "scale.y": x, "pos.x": offset_x, "pos.y": offset_y}))
    # The opposite endpoints move with the sum of the column vectors.
    objects.append(sphere([0, 0, 0], 0.17, YL, label="u + v",
                          bind={"pos.x": "p.a+1", "pos.y": "p.d+1"}))
    return spec("Determinant and orientation", objects,
                "The signed determinant is ad − 1. Its absolute value is the parallelogram area.",
                [param("a", "a", 0.25, 3, 2, 0.25), param("d", "d", 0.25, 3, 2, 0.25)],
                [readout("Determinant", "p.a*p.d-1"), readout("Area", "abs(p.a*p.d-1)")])


@reg("complex_plane", "Complex plane · modulus and argument")
def complex_plane():
    objects = [
        line([[-4, 0, 0], [4, 0, 0]], LG), line([[0, -4, 0], [0, 4, 0]], LG),
        text([4, 0.4, 0], "Real"), text([0.5, 4, 0], "Imaginary"),
        sphere([0, 0, 0], 0.2, CY, label="z", bind={"pos.x": "p.a", "pos.y": "p.b"}),
        sphere([0, 0, 0], 0.16, OR, label="Conjugate", bind={"pos.x": "p.a", "pos.y": "-p.b"}),
    ]
    return spec("Complex plane", objects, "Move z across the axes and compare its conjugate.",
                [param("a", "Real part", -4, 4, -3, 0.25), param("b", "Imaginary part", -4, 4, 3, 0.25)],
                [readout("Modulus", "sqrt(p.a*p.a+p.b*p.b)"),
                 readout("Argument in degrees", "p.a||p.b?Math.atan2(p.b,p.a)*180/PI:'undefined'")])


@reg("parabola_transform", "Parabola · turning point and intercepts")
def parabola_transform():
    curve = "p.a*(x-p.h)*(x-p.h)+p.k"
    return spec("Parabola transformations", [
        line([[-5, 0, 0], [5, 0, 0]], LG), line([[0, -3, 0], [0, 5, 0]], LG),
        plot(curve, -4, 4, [0, 0, 0], 1, 1, CY),
        pt("p.h", curve, 0, [0, 0, 0], 1, 1, OR, label="Turning point"),
    ], "Change h and k to move the turning point. Compare positive and negative a.",
        [param("a", "a", -0.5, 0.5, 0.25, 0.05), param("h", "h", -2, 2, 1, 0.25),
         param("k", "k", -2, 2, -1, 0.25)],
        [readout("Turning point", "p.a?'('+p.h+', '+p.k+')':'constant function'"),
         readout("Axis of symmetry", "p.a?p.h:'no unique axis'")], cam=(1, 3, 14))


@reg("removable_limit", "Limits · approaching a hole")
def removable_limit():
    curve = "x+1"
    return spec("A removable discontinuity", [
        line([[-3, 0, 0], [3, 0, 0]], LG), line([[0, -2, 0], [0, 4, 0]], LG),
        plot(curve, -2.5, 0.91, [0, 0, 0], 1, 1, CY),
        plot(curve, 1.09, 2.5, [0, 0, 0], 1, 1, CY),
        sphere([1, 2, 0], 0.12, LG, opacity=0.25, label="Hole at (1, 2)"),
        pt("1-p.d", curve, 0, [0, 0, 0], 1, 1, OR, label="Left"),
        pt("1+p.d", curve, 0, [0, 0, 0], 1, 1, GR, label="Right"),
    ], "For x ≠ 1, (x² − 1)/(x − 1) simplifies to x + 1. At x = 1 the original expression is undefined.",
        [param("d", "Distance from 1", 0.02, 1.5, 0.8, 0.02)],
        [readout("Left value", "2-p.d"), readout("Right value", "2+p.d"), readout("Two-sided limit", "2")])


def _bit_cells(expression, width, y, colour):
    cells = []
    for bit in range(width):
        x = (width / 2 - bit - 0.5) * 1.25
        state = f"floor(({expression})/{2 ** bit})%2"
        cells.extend([
            box([x, y, 0], [0.88, 0.72, 0.55], DK,
                bind={"color": f"{state}?'{colour}':'#475569'"}),
            text([x, y - 0.57, 0.2], str(2 ** bit), LG, 0.24),
        ])
    return cells


@reg("binary_place_value", "Binary · place value and two’s complement")
def binary_place_value():
    return spec("Four-bit place value", _bit_cells("p.value", 4, 0.4, CY),
                "Bright blocks are 1. Read the same four bits as unsigned or signed two’s complement.",
                [param("value", "Bit pattern as unsigned value", 0, 15, 11, 1)],
                [readout("Unsigned", "p.value"), readout("Signed", "p.value<8?p.value:p.value-16")])


@reg("binary_decoder", "2-to-4 decoder · select one output")
def binary_decoder():
    value = "2*p.b+p.a"
    objects = _bit_cells(value, 2, 1.8, CY)
    for index in range(4):
        x = (index - 1.5) * 1.25
        objects.append(box([x, -0.3, 0], [0.88, 0.72, 0.55], DK, label=f"Y{index}",
                           bind={"color": f"{value}=={index}?'#10B981':'#475569'"}))
    return spec("Address decoder", objects, "Assume active-high outputs and an enabled decoder.",
                [param("b", "Input B (MSB)", 0, 1, 0, 1), param("a", "Input A (LSB)", 0, 1, 1, 1)],
                [readout("Active output", "'Y'+(2*p.b+p.a)")])


@reg("logic_thresholds", "Logic inputs · low, undefined and high")
def logic_thresholds():
    objects = [
        box([-2.5, 0, 0], [2, 0.55, 0.9], CY, label="LOW"),
        box([-0.5, 0, 0], [2, 0.55, 0.9], OR, label="Undefined"),
        box([1.6, 0, 0], [2.2, 0.55, 0.9], GR, label="HIGH"),
        sphere([-2.5, 0.55, 0], 0.17, YL, label="Input voltage", bind={"pos.x": "p.v-3.5"}),
    ]
    return spec("Example logic thresholds", objects,
                "Illustrative 5 V input thresholds. Actual values depend on the device datasheet.",
                [param("v", "Input", 0, 5, 1, 0.1, "V")],
                [readout("Input interpretation", "p.v<=1?'LOW':p.v>=3?'HIGH':'Undefined'")])


@reg("register_bits", "Register · sample a four-bit input")
def register_bits():
    objects = _bit_cells("p.data", 4, 1.45, CY) + _bit_cells("p.stored", 4, -1, GR)
    objects.extend([
        text([-3.5, 1.45, 0], "Input"), text([-3.5, -1, 0], "Stored"),
        box([3.8, 0.2, 0], [1.35, 0.65, 0.55], OR, label="Clock edge",
            info="Click to capture the input word.", click={"stored": "p.data"}),
    ])
    return spec("Four-bit register", objects,
                "Change the input word, then click Clock edge to capture it.",
                [param("data", "Current input word", 0, 15, 9, 1),
                 param("stored", "Word sampled at last clock edge", 0, 15, 5, 1, hidden=True)],
                [readout("Output word", "p.stored")])


@reg("memory_address", "Memory and I/O · address selection")
def memory_address():
    objects = [
        box([(i - 1.5) * 1.5, 0, 0], [1.12, 1, 0.75], DK, label=f"Address {i}",
            bind={"color": f"p.address=={i}?'#22D3EE':'#475569'"})
        for i in range(4)
    ]
    return spec("Addressed reads", objects,
                "Select one location to read its stored word. The final address illustrates a memory-mapped input.",
                [param("address", "Address", 0, 3, 0, 1), param("switch", "External input", 0, 1, 0, 1)],
                [readout("Read data", "p.address==3?p.switch:[6,9,12][p.address]")])


@reg("switch_bounce", "Contact bounce · raw and debounced signal")
def switch_bounce():
    raw = "x<1?0:x<1+p.span?floor((x-1)*16)%2:1"
    stable = "x<1+p.span+p.delay?0:1"
    return spec("Switch debouncing", [
        plot(raw, 0, 5, [-3, 1, 0], 1.25, 0.75, OR, 256, label="Raw switch"),
        plot(stable, 0, 5, [-3, -1, 0], 1.25, 0.75, GR, 256, label="Debounced output"),
    ], "Illustrative timing model. The output changes after the input is stable for the chosen interval.",
        [param("span", "Bounce duration", 0.1, 1.5, 0.75, 0.05),
         param("delay", "Required stable interval", 0.1, 1.5, 0.4, 0.05)],
        [readout("Accepted transition time", "1+p.span+p.delay")])


@reg("conductivity_cell", "Conductivity cell · electrode geometry and conductance")
def conductivity_cell():
    objects = [
        box([0, -0.15, 0], [6, 2.1, 2.6], CY, opacity=0.18, label="Sample"),
        box([-1, 0, 0], [0.18, 2.4, 1.35], LG, label="Electrode A",
            bind={"pos.x": "-p.gap/2"}),
        box([1, 0, 0], [0.18, 2.4, 1.35], LG, label="Electrode B",
            bind={"pos.x": "p.gap/2"}),
        cyl([0, 0, 0], 0.045, 1, YL, axis="x", bind={"scale.x": "p.gap"}),
    ]
    return spec("Ideal conductivity cell", objects,
                "Parallel electrodes with area 1 cm². For this ideal geometry, G = conductivity × area / spacing.",
                [param("gap", "Electrode spacing", 0.5, 4, 2, 0.1, "cm"),
                 param("k", "Conductivity", 0.2, 8, 2, 0.1, "mS/cm")],
                [readout("Cell constant (cm⁻¹)", "p.gap"), readout("Conductance (mS)", "p.k/p.gap")])
