"""Registry of all 3D diagrams: id -> title + spec builder."""
import importlib

REGISTRY = {}
_loaded = False


def reg(diagram_id, title):
    def deco(fn):
        REGISTRY[diagram_id] = {"title": title, "build": fn}
        return fn
    return deco


def _load():
    global _loaded
    if _loaded:
        return
    for mod in ("diagrams_inst", "diagrams_math", "diagrams_ie", "diagrams_digi"):
        try:
            importlib.import_module("ui." + mod)
        except ModuleNotFoundError as exc:  # allows partial installs while developing
            if mod not in str(exc):
                raise
    _loaded = True


def available():
    _load()
    return list(REGISTRY)


def title_of(diagram_id):
    _load()
    return REGISTRY.get(diagram_id, {}).get("title", diagram_id)


def get_spec(diagram_id):
    _load()
    if diagram_id not in REGISTRY:
        return None
    return REGISTRY[diagram_id]["build"]()
