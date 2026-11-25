"""Dependency graph: which part of a family must be configured before which.

A node is a *family part*: the instances of one family section that address one
kind of device object (``interfaces.config:ont`` is the ``ont:`` entries of the
interfaces family, ``interfaces.config:vlan_port`` its ``vlan-port:`` entries).
An edge ``before -> after`` says the device accepts ``after`` only once
``before`` is configured, and why:

* ``creates``    ``before`` is the command that creates the object ``after``
                 configures (``equipment_onts.interfaces`` creates the ONT).
* ``contains``   ``after`` addresses an object inside the one ``before``
                 addresses (ONT slot inside ONT, VLAN port on bridge port).
* ``references`` ``after`` names definitions of ``before`` (QoS/xDSL profiles).
* ``requires``   a requirement the family declares, with its evidence.

Nothing here is a table of its own: the edges follow from what the families
declare in relations/<family>.py and from the containment in objects.py. The
graph is built for a concrete configuration (a change set, or everything read
from an MSAN), because the kind of object an instance addresses is decoded from
its identity. What cannot be placed is reported (or refused), never guessed.

The write order is one topological order of this graph; removal is its reverse.
"""

import heapq

from ..relations import FAMILIES
from ..targeted import TARGETED_GATHER
from . import export_catalog
from .identity import UnknownIdentity, decode


class UnorderedWrite(ValueError):
    """The catalog cannot place this configuration in the dependency graph."""


def node_id(resource, section, kind):
    return "%s.%s:%s" % (resource, section, kind)


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


def _identity(instance, field):
    if isinstance(field, list):
        values = tuple(instance.get(name) for name in field)
        return values if all(value not in (None, "") for value in values) else None
    value = instance.get(field)
    return value if value not in (None, "") else None


def place(families, catalog, strict=True):
    """Sort the instances of a configuration into family parts.

    families: {resource: config} in the modules' canonical form (a list for
    single-section families, {section: [instances]} otherwise).
    Returns (parts, unplaced). parts: {(resource, section, kind): {"role",
    "rank", "instances"}}. With strict, the first thing that cannot be placed
    raises UnorderedWrite; otherwise it is listed in unplaced with its reason.
    """
    if not isinstance(families, dict) or not families:
        raise UnorderedWrite("families must be a non-empty mapping")
    depths = _depths(catalog["objects"])
    bindings = {(b["resource"], b["section"]): b for b in catalog["bindings"]}
    models = catalog["section_models"]
    required = {(r["target_resource"], r["target_section"]) for r in catalog["requires"]}
    self_created = {(c["resource"], c["section"], c["object"]) for c in catalog["created_with"]}
    parts, unplaced, addressed = {}, [], []

    def refuse(reason, resource, section=None, identity=None):
        if strict:
            raise UnorderedWrite(reason)
        unplaced.append({"resource": resource, "section": section, "identity": identity, "reason": reason})

    def add(resource, section, kind, role, rank, instance):
        part = parts.setdefault((resource, section, kind), {"role": role, "rank": rank, "instances": []})
        part["instances"].append(instance)

    for resource, config in families.items():
        if resource not in TARGETED_GATHER:
            refuse("No write order known for family %s" % resource, resource)
            continue
        sections: dict = TARGETED_GATHER[resource]  # type: ignore[assignment]
        if isinstance(config, list):
            if list(sections) != ["config"]:
                refuse("%s has sections %s; a list is not its canonical form" % (resource, sorted(sections)), resource)
                continue
            by_section = {"config": config}
        elif isinstance(config, dict):
            outside = sorted(key for key in config if key not in sections)
            if outside:
                refuse("Settings of %s outside its instance lists cannot be ordered: %s" % (resource, outside), resource)
            by_section = {key: value for key, value in config.items() if key in sections}
        else:
            refuse("Malformed configuration for %s" % resource, resource)
            continue
        for section, instances in by_section.items():
            key = "%s.%s" % (resource, section)
            if not isinstance(instances, list):
                refuse("%s must be a list of instances" % key, resource, section)
                continue
            if not instances:
                continue
            model = models.get(key, {})
            binding = bindings.get((resource, section))
            if model.get("scope") == "shared_profile":
                for instance in instances:
                    add(resource, section, "definition", "definition", 1, instance)
                continue
            if model.get("model") == "device_settings":
                if (resource, section) not in required:
                    refuse("No write order evidence for device settings %s" % key, resource, section)
                    continue
                for instance in instances:
                    add(resource, section, "device_settings", "device_settings", 0, instance)
                continue
            if not binding:
                refuse("No object binding for %s" % key, resource, section)
                continue
            for instance in instances:
                if not isinstance(instance, dict):
                    refuse("%s instances must be mappings" % key, resource, section)
                    continue
                identity = _identity(instance, binding["identity"])
                if identity is None:
                    refuse("%s instance without its identity %s" % (key, binding["identity"]), resource, section)
                    continue
                addressed.append((resource, section, binding["decoder"], identity, instance))

    # Several kinds of object share a bare port address (line, Ethernet port,
    # bonding group, LAG). Such an address is only resolved from an object the
    # same configuration identifies unambiguously, exactly as the graph does.
    known_ports = set()
    for resource, section, decoder, identity, instance in addressed:
        try:
            known_ports.add(decode(decoder, identity))
        except UnknownIdentity:
            pass
    for resource, section, decoder, identity, instance in addressed:
        key = "%s.%s" % (resource, section)
        try:
            kind = decode(decoder, identity, known_ports)[0]
        except UnknownIdentity as exc:
            refuse("%s %s: %s" % (key, identity, exc), resource, section, identity)
            continue
        if kind not in depths:
            refuse("Object kind %s has no place in the containment tree" % kind, resource, section, identity)
            continue
        if catalog["creates"].get(kind) == {"resource": resource, "section": section}:
            role = "creates"
        elif (resource, section, kind) in self_created:
            role = "created_with"
        else:
            role = "configures"
        add(resource, section, kind, role, 2 + depths[kind], instance)
    return parts, unplaced


def _sort_key(key, part):
    # Tie-break among parts no edge orders: device settings, definitions, then
    # by depth of the addressed object, the creating part first.
    return (part["rank"], 0 if part["role"] == "creates" else 1) + key


def _edges(parts, catalog):
    edges, seen = [], set()

    def edge(before, after, reason, **more):
        if before != after and (before, after, reason) not in seen:
            seen.add((before, after, reason))
            edges.append(dict({"before": node_id(*before), "after": node_id(*after), "reason": reason}, **more))

    by_kind, by_section = {}, {}
    for key in sorted(parts):
        by_section.setdefault(key[:2], []).append(key)
        if parts[key]["role"] not in ("definition", "device_settings"):
            by_kind.setdefault(key[2], []).append(key)
    parents = {kind: obj["parents"] for kind, obj in catalog["objects"].items()}

    def nearest_present(kind, seen_kinds=()):
        found = []
        for parent in parents.get(kind, ()):
            if parent in seen_kinds:
                continue
            found += [parent] if parent in by_kind else nearest_present(parent, seen_kinds + (kind,))
        return found

    for kind, keys in by_kind.items():
        creators = [key for key in keys if parts[key]["role"] == "creates"]
        for creator in creators:
            for key in keys:
                edge(creator, key, "creates", object=kind)
        # Entering a kind happens through its creating part when there is one.
        heads = creators or keys
        for above in sorted(set(nearest_present(kind))):
            for before in by_kind[above]:
                for head in heads:
                    edge(before, head, "contains", object=kind, inside=above)
    for key in sorted(parts):
        resource, section = key[:2]
        target = FAMILIES[resource].get("profile_references")
        if target and parts[key]["role"] != "definition":
            for definition in (k for k in parts if k[0] == target and parts[k]["role"] == "definition"):
                edge(definition, key, "references")
    for reference in catalog["typed_references"]:
        for after in by_section.get((reference["resource"], reference["section"]), ()):
            for before in by_section.get((reference["target_resource"], reference["target_section"]), ()):
                edge(before, after, "references", option=reference["field"])
    for need in catalog["requires"]:
        for after in by_section.get((need["resource"], need["section"]), ()):
            for before in by_section.get((need["target_resource"], need["target_section"]), ()):
                if need["target_kind"] in (None, before[2]) and need.get("source_kind") in (None, after[2]):
                    edge(before, after, "requires", evidence=need["evidence"])
    return edges


def _order(parts, edges):
    """One topological order of the parts: every edge's before precedes its after."""
    keys = {node_id(*key): key for key in parts}
    waiting = {name: 0 for name in keys}
    followers = {name: [] for name in keys}
    for item in edges:
        waiting[item["after"]] += 1
        followers[item["before"]].append(item["after"])
    ready = [(_sort_key(keys[name], parts[keys[name]]), name) for name, count in waiting.items() if not count]
    heapq.heapify(ready)
    ordered = []
    while ready:
        name = heapq.heappop(ready)[1]
        ordered.append(name)
        for follower in followers[name]:
            waiting[follower] -= 1
            if not waiting[follower]:
                heapq.heappush(ready, (_sort_key(keys[follower], parts[keys[follower]]), follower))
    if len(ordered) != len(keys):
        raise UnorderedWrite("Dependency cycle between %s" % sorted(set(keys) - set(ordered)))
    return ordered


def build(families, catalog=None, strict=True):
    """(parts, graph) for a configuration; see dependency_graph for the graph."""
    catalog = export_catalog() if catalog is None else catalog
    parts, unplaced = place(families, catalog, strict)
    edges = _edges(parts, catalog)
    order = _order(parts, edges)
    nodes = [{"id": node_id(*key), "resource": key[0], "section": key[1], "kind": key[2],
              "role": parts[key]["role"], "instances": len(parts[key]["instances"])}
             for key in sorted(parts, key=lambda key: order.index(node_id(*key)))]
    return parts, {"nodes": nodes, "edges": edges, "order": order, "unplaced": unplaced, "exhaustive": False}


def dependency_graph(families, catalog=None):
    """The dependency graph of a configuration, e.g. of everything read from an MSAN.

    Returns {"nodes": [{id, resource, section, kind, role, instances}],
             "edges": [{before, after, reason, ...}],
             "order": node ids in creation order (removal is the reverse),
             "unplaced": [{resource, section, identity, reason}], "exhaustive": False}.
    role: creates (its command creates the object), created_with (the device
    creates the entry itself with the object), configures, definition,
    device_settings. Instances that cannot be placed are listed, not guessed.
    """
    return build(families, catalog, strict=False)[1]


def to_mermaid(graph):
    """The graph as a Mermaid flowchart: one box per object kind, its family parts inside."""
    names = {node["id"]: "n%d" % index for index, node in enumerate(graph["nodes"])}
    kinds = []
    for node in graph["nodes"]:
        if node["kind"] not in kinds:
            kinds.append(node["kind"])
    marks = {"creates": " (creates it)", "created_with": " (created by the device)"}
    lines = ["flowchart TD"]
    for kind in kinds:
        lines.append('  subgraph %s["%s"]' % (kind, kind.replace("_", " ")))
        for node in graph["nodes"]:
            if node["kind"] == kind:
                lines.append('    %s["%s.%s%s"]' % (names[node["id"]], node["resource"], node["section"], marks.get(node["role"], "")))
        lines.append("  end")
    drawn = set()
    for item in graph["edges"]:
        if item["reason"] == "contains":
            # Drawn once between the boxes: everything of the outer object first.
            pair = (item["inside"], item["object"])
            if pair not in drawn:
                drawn.add(pair)
                lines.append("  %s ==> %s" % pair)
        elif item["reason"] == "creates":
            lines.append("  %s --> %s" % (names[item["before"]], names[item["after"]]))
        else:
            lines.append("  %s -. %s .-> %s" % (names[item["before"]], item["reason"], names[item["after"]]))
    return "\n".join(lines) + "\n"
