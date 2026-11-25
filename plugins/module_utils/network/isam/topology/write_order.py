"""Write order: in which order resource families are created and removed.

The ISAM accepts configuration only once what it attaches to exists (an ONT
before its slot, a UNI before its bridge port, a bridge port before its VLAN
ports, a profile before the interface using it) and removes it only in the
reverse order. One module call cannot reorder another, so callers need this
order. It is derived from what the families declare in relations/<family>.py
and from the containment of the objects (objects.py); there is no order table:

1. ``contains``: an instance is written after every object kind above it
   (catalog objects and their parents; the kind is decoded per instance, so a
   ``vlan:`` QoS instance belongs to the VLAN port, ``ont:`` to the ONT).
2. ``references``: shared definitions (QoS profiles, xDSL profiles, ...) come
   before the configuration referencing them, and inside a definition family
   a referenced definition comes before its referrer.
3. ``creates``: of the families configuring one object kind, the one whose
   command creates the object comes first (``equipment ont interface``
   creates the ONT; its ANI, NTP and QoS settings follow) and goes last.
4. ``requires``: a device-wide section another section declares it needs
   (a bridge port requires the VLANs) comes before every object family. Any
   other device-wide family is refused: its position is not known.

Removal is the exact reverse of creation. A family, section, instance or
setting the catalog cannot place is refused, never guessed; the order is only
as complete as the families it accepts (``exhaustive: False``).

Relation to live evidence: the upstream-queue bandwidth profile of a UNI must
exist before a VLAN is attached to its bridge port (device error 277, live
apply 2026-11-19). That is rule 1 (UNI above bridge port), not a special case.
Within one module call the module orders its own commands (e.g. admin-state
alone, ``docs/live-apply-regressions-2026-11-19.md``).
"""

from ..targeted import TARGETED_GATHER
from . import export_catalog
from .identity import UnknownIdentity, decode

PHASES = ("create", "delete")

class UnorderedWrite(ValueError):
    """The catalog cannot place this configuration in a write order."""


def _depths(objects):
    """Object kind -> length of its longest parent chain (msan = 0)."""
    depths = {}

    def depth(kind, seen=()):
        if kind in depths:
            return depths[kind]
        if kind in seen:
            raise UnorderedWrite("Containment cycle at object kind %s" % kind)
        parents = objects.get(kind, {}).get("parents", [])
        depths[kind] = 0 if not parents else 1 + max(depth(parent, seen + (kind,)) for parent in parents)
        return depths[kind]

    for kind in objects:
        depth(kind)
    return depths


def _sections(resource):
    """Section name -> identity field(s) of a family, as TARGETED_GATHER declares them."""
    sections: dict = TARGETED_GATHER[resource]  # type: ignore[assignment]
    return sections


def _identity(instance, field):
    if isinstance(field, list):
        values = tuple(instance.get(name) for name in field)
        return values if all(value not in (None, "") for value in values) else None
    value = instance.get(field)
    return value if value not in (None, "") else None


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
    Consecutive units of the same resource form one step (one module call).
    Raises UnorderedWrite for anything the catalog cannot place.
    """
    if phase not in PHASES:
        raise UnorderedWrite("phase must be create or delete")
    if not isinstance(families, dict) or not families:
        raise UnorderedWrite("families must be a non-empty mapping")
    catalog = export_catalog() if catalog is None else catalog
    depths = _depths(catalog["objects"])
    bindings = {(b["resource"], b["section"]): b for b in catalog["bindings"]}
    models = catalog["section_models"]
    required = {(r["target_resource"], r["target_section"]) for r in catalog["requires"]}

    units = {}  # (rank, creator first, resource, section, kind) -> instances
    for resource, config in families.items():
        if resource not in TARGETED_GATHER:
            raise UnorderedWrite("No write order known for family %s" % resource)
        sections = _sections(resource)
        if isinstance(config, list):
            if list(sections) != ["config"]:
                raise UnorderedWrite("%s has sections %s; a list is not its canonical form" % (resource, sorted(sections)))
            parts = {"config": config}
        elif isinstance(config, dict):
            unplaced = sorted(key for key in config if key not in sections)
            if unplaced:
                raise UnorderedWrite("Settings of %s outside its instance lists cannot be ordered: %s" % (resource, unplaced))
            parts = config
        else:
            raise UnorderedWrite("Malformed configuration for %s" % resource)
        for section, instances in parts.items():
            if not isinstance(instances, list):
                raise UnorderedWrite("%s.%s must be a list of instances" % (resource, section))
            if not instances:
                continue
            key = "%s.%s" % (resource, section)
            model = models.get(key, {})
            binding = bindings.get((resource, section))
            if model.get("scope") == "shared_profile":
                fields = catalog["profile_references"].get(resource, {})
                ordered = _ordered_definitions(instances, fields) if resource == "qos_profiles" else list(instances)
                units[(1, 0, resource, section, "definition")] = ordered
                continue
            if model.get("model") == "device_settings":
                if (resource, section) not in required:
                    raise UnorderedWrite("No write order evidence for device settings %s" % key)
                units[(0, 0, resource, section, "device_settings")] = list(instances)
                continue
            if not binding:
                raise UnorderedWrite("No object binding for %s" % key)
            for instance in instances:
                if not isinstance(instance, dict):
                    raise UnorderedWrite("%s instances must be mappings" % key)
                identity = _identity(instance, binding["identity"])
                if identity is None:
                    raise UnorderedWrite("%s instance without its identity %s" % (key, binding["identity"]))
                try:
                    kind = decode(binding["decoder"], identity)[0]
                except UnknownIdentity as exc:
                    raise UnorderedWrite("%s %s: %s" % (key, identity, exc)) from None
                if kind not in depths:
                    raise UnorderedWrite("Object kind %s has no place in the containment tree" % kind)
                creates = catalog["creates"].get(kind) == {"resource": resource, "section": section}
                units.setdefault((2 + depths[kind], 0 if creates else 1, resource, section, kind), []).append(instance)

    ordered = sorted(units)
    if phase == "delete":
        ordered.reverse()
    steps = []
    for unit in ordered:
        _, _, resource, section, kind = unit
        instances = units[unit]
        if phase == "delete":
            instances = list(reversed(instances))
        single = list(_sections(resource)) == ["config"]
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
