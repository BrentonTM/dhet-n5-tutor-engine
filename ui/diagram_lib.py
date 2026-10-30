"""Tiny helpers for describing 3D diagrams as data (see diagram_engine.py)."""

CY = "#22D3EE"   # cyan
OR = "#FF7A1A"   # orange
VI = "#8B5CF6"   # violet
GR = "#10B981"   # green
RD = "#EF4444"   # red
YL = "#FACC15"   # yellow
BL = "#3B82F6"   # blue
ST = "#6B7A8F"   # steel
LG = "#9CA3AF"   # light grey
WH = "#E6EDF3"   # text white
DK = "#1F2937"   # dark panel


def _o(type_, **kw):
    d = {"type": type_}
    d.update({k: v for k, v in kw.items() if v is not None})
    return d


def box(p, s, color=ST, **kw):
    return _o("box", p=p, s=s, color=color, **kw)


def sphere(p, r, color=CY, **kw):
    return _o("sphere", p=p, r=r, color=color, **kw)


def cyl(p, r, h, color=ST, axis="y", rt=None, **kw):
    return _o("cyl", p=p, r=r, h=h, color=color, axis=axis, rt=rt, **kw)


def cone(p, r, h, color=ST, axis="y", **kw):
    return _o("cone", p=p, r=r, h=h, color=color, axis=axis, **kw)


def torus(p, r, tube, color=ST, arc=None, **kw):
    return _o("torus", p=p, r=r, tube=tube, color=color, arc=arc, **kw)


def lathe(p, profile, color=ST, **kw):
    return _o("lathe", p=p, profile=profile, color=color, **kw)


def wire(pts, color=OR, r=0.04, **kw):
    return _o("wire", pts=pts, color=color, r=r, **kw)


def line(pts, color=ST, r=0.015, **kw):
    return _o("line", pts=pts, color=color, r=r, **kw)


def arrow(a, b, color=OR, r=0.045, **kw):
    d = _o("arrow", color=color, r=r, **kw)
    d["from"] = a
    d["to"] = b
    return d


def text(p, s, color=WH, size=0.4, **kw):
    return _o("text", p=p, text=s, color=color, size=size, **kw)


def flow(path, color=CY, n=18, speed=1.5, size=0.13, jit=0.0, **kw):
    return _o("flow", path=path, color=color, n=n, speed=speed, size=size, jit=jit, **kw)


def plot(expr, x0, x1, p, sx, sy, color=CY, n=160, r=0.035, **kw):
    return _o("plot", expr=expr, x0=x0, x1=x1, p=p, sx=sx, sy=sy, color=color, n=n, r=r, **kw)


def bars(expr, x0, x1, n, p, sx, sy, color=CY, depth=0.5, **kw):
    return _o("bars", expr=expr, x0=x0, x1=x1, n=n, p=p, sx=sx, sy=sy, color=color, depth=depth, **kw)


def revolve(expr, x0, x1, p, sx, sy, color=CY, n=60, **kw):
    return _o("revolve", expr=expr, x0=x0, x1=x1, p=p, sx=sx, sy=sy, color=color, n=n, **kw)


def pt(x, f, x0, p, sx, sy, color=OR, r=0.13, **kw):
    return _o("pt", x=x, f=f, x0=x0, p=p, sx=sx, sy=sy, color=color, r=r, **kw)


def tangent(x, f, x0, p, sx, sy, color=YL, length=2.0, **kw):
    return _o("tangent", x=x, f=f, x0=x0, p=p, sx=sx, sy=sy, color=color, len=length, **kw)


def arc(c, R, a0, a1, r=0.1, color=OR, **kw):
    return _o("arc", c=c, R=R, a0=a0, a1=a1, r=r, color=color, **kw)


def axes(p, w, h_up, h_down=0.0, xl="x", yl="y", color="#4B5563", z=0.0):
    """Two arrows (x and y axes) with labels, centred on origin p."""
    x0, y0 = p[0], p[1]
    objs = [
        arrow([x0 - 0.1, y0, z], [x0 + w, y0, z], color, r=0.02),
        arrow([x0, y0 - h_down, z], [x0, y0 + h_up, z], color, r=0.02),
        text([x0 + w + 0.35, y0 - 0.05, z], xl, "#8B949E", 0.34),
        text([x0 + 0.05, y0 + h_up + 0.3, z], yl, "#8B949E", 0.34),
    ]
    return objs


def vec(a, b, color=OR, r=0.05, **kw):
    """Dynamic arrow whose end points may be expression strings (e.g. phasors)."""
    d = _o("vec", color=color, r=r, **kw)
    d["from"] = a
    d["to"] = b
    return d


def prism(p, poly, depth, color=ST, **kw):
    """Extruded 2D polygon (poly in local x,y; extruded along z)."""
    return _o("prism", p=p, poly=poly, depth=depth, color=color, **kw)


def param(id, label, lo, hi, val, step=None, unit="", toggle=False, hidden=False, names=None):
    d = {"id": id, "label": label, "min": lo, "max": hi, "value": val}
    if step is not None:
        d["step"] = step
    if unit:
        d["unit"] = unit
    if toggle:
        d["toggle"] = True
    if hidden:
        d["hidden"] = True
    if names:
        d["names"] = names
    return d


def readout(label, expr):
    return {"label": label, "expr": expr}


def spec(title, objects, subtitle="", params=None, readouts=None, cam=(7, 4.5, 10), target=(0, 0, 0),
         hint=None, auto=False, grid_y=-3.2, grid=True):
    d = {
        "title": title,
        "subtitle": subtitle,
        "objects": objects,
        "params": params or [],
        "readouts": readouts or [],
        "camera": {"pos": list(cam), "target": list(target)},
        "auto": auto,
        "gridY": grid_y,
        "grid": grid,
    }
    if hint:
        d["hint"] = hint
    return d
