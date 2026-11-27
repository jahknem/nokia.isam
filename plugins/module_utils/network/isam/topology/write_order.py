"""Write order: in which order resource families are created and removed.

The ISAM accepts configuration only once what it attaches to exists (an ONT
before its slot, a UNI before its bridge port, a bridge port before its VLAN
ports, a profile before the interface using it) and removes it only in the
reverse order. One module call cannot reorder another, so callers need this
order.

The order is a topological order of the dependency graph (dependencies.py):
every part of a family comes after all parts it depends on. Among parts no
edge orders, device-wide settings come first, then definitions, then objects
from the outside in, the creating part first. Removal is the exact reverse of
creation. A family, section, instance or setting the catalog cannot place is
refused, never guessed; the order is only as complete as the families it
accepts (``exhaustive: False``).

Within one module call the module orders its own commands (e.g. admin-state
alone, ``docs/live-apply-regressions-2026-11-19.md``).
"""

from ..relations import FAMILIES
from ..targeted import TARGETED_GATHER
from .dependencies import UnorderedWrite, build

PHASES = ("create", "delete")


def _profile_key(instance):
    return (instance.get("profile_type"), instance.get("name"))


def _ordered_definitions(instances, fields):
    """Definitions of one family, every referenced definition before its referrer."""
    by_key = {_profile_key(item): item for item in instances}
    ordered, state = [], {}

    def visit(key, path=()):
        if state.get(key) == "done":
            return
        if state.get(key) == "visiting":
            raise UnorderedWrite("Reference cycle between definitions: %s" % " -> ".join(map(str, path + (key,))))
        state[key] = "visiting"
        for field, value in by_key[key].items():
            kind = fields.get(field.replace("-", "_"))
            if kind and isinstance(value, str) and value.startswith("name:") and (kind, value[5:]) in by_key:
                visit((kind, value[5:]), path + (key,))
        state[key] = "done"
        ordered.append(by_key[key])

    for item in instances:
        visit(_profile_key(item))
    return ordered


def write_steps(families, phase="create", catalog=None):
    """Order the configuration of one MSAN for writing.

    families: {resource: config} in the modules' canonical form (a list for
    single-section families, {section: [instances]} otherwise).
    Returns {"phase", "steps": [{"resource", "config", "kinds"}], "exhaustive": False}.
    Consecutive parts of the same resource form one step (one module call).
    Raises UnorderedWrite for anything the catalog cannot place.
    """
    if phase not in PHASES:
        raise UnorderedWrite("phase must be create or delete")
    parts, graph = build(families, catalog, strict=True)
    by_id = {node["id"]: (node["resource"], node["section"], node["kind"]) for node in graph["nodes"]}
    ordered = [by_id[name] for name in graph["order"]]
    if phase == "delete":
        ordered.reverse()
    steps = []
    for resource, section, kind in ordered:
        instances = list(parts[(resource, section, kind)]["instances"])
        if kind == "definition" and FAMILIES[resource].get("reference_fields"):
            # Definitions of one family that name each other: the named one first.
            instances = _ordered_definitions(instances, FAMILIES[resource]["reference_fields"])
        if phase == "delete":
            instances.reverse()
        sections: dict = TARGETED_GATHER[resource]  # type: ignore[assignment]
        single = list(sections) == ["config"]
        if steps and steps[-1]["resource"] == resource:
            step = steps[-1]
        else:
            step = {"resource": resource, "config": [] if single else {}, "kinds": []}
            steps.append(step)
        if single:
            step["config"].extend(instances)
        else:
            step["config"].setdefault(section, []).extend(instances)
        if kind not in step["kinds"]:
            step["kinds"].append(kind)
    return {"phase": phase, "steps": steps, "exhaustive": False}
