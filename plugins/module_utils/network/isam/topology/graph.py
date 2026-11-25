"""Build an evidence graph from canonical resources; never execute commands.

An observed graph is not a discovery certificate. Known read requirements can be
exported, but incomplete discovery/mapping blocks a claim of recursive coverage.
Only identities are retained; descriptions, serials and credentials are not.
"""

import json

from . import SCHEMA_VERSION, export_catalog
from .identity import UnknownIdentity, _valid_vlan, candidate_owners, decode, parent_of


def node_key(kind, identity):
    return json.dumps([kind, identity], separators=(",", ":"), ensure_ascii=True)


def _rows(data, section):
    if section == "config":
        return data if isinstance(data, list) else []
    for part in section.split("."):
        if not isinstance(data, dict):
            return []
        data = data.get(part)
    return data if isinstance(data, list) else []


def _references(value, fields):
    if isinstance(value, list):
        for item in value:
            yield from _references(item, fields)
    elif isinstance(value, dict):
        for field, item in value.items():
            if isinstance(item, str) and item.startswith("name:"):
                yield fields.get(field.replace("-", "_")), item[5:], field
            elif isinstance(item, (list, dict)):
                yield from _references(item, fields)


def _has_unmapped_settings(data, sections, path=()):
    """Detect settings outside instance lists without exporting their values."""
    if path in sections:
        return False
    if not isinstance(data, dict):
        return data not in (None, [], {})
    for key, value in data.items():
        child = path + (key,)
        if any(section[:len(child)] == child for section in sections):
            if _has_unmapped_settings(value, sections, child):
                return True
        elif value not in (None, [], {}):
            return True
    return False


def _path_present(data, path):
    for part in path.split("."):
        if not isinstance(data, dict) or part not in data:
            return False
        data = data[part]
    return True


def build_graph(resources, msan):
    """resources is ansible_network_resources, with canonical facts names.

    All node keys are local to this MSAN. NOC supplies the device identity and
    owns cross-device NVT membership. Missing/ambiguous ownership is a gap, never
    a guessed edge to a plausible parent. Implied ancestors are marked observed
    only if a resource actually identifies them.
    """
    if not isinstance(resources, dict) or not isinstance(msan, str) or not msan:
        raise ValueError("A resource dictionary and nonempty MSAN identity are required")
    catalog = export_catalog()
    nodes, edges, gaps = {}, set(), []
    known_ports = set()

    def obj(kind, identity, observed=False):
        key = node_key(kind, identity)
        if key not in nodes:
            nodes[key] = {"key": key, "kind": kind, "identity": json.loads(json.dumps(identity)), "observed": observed}
            parent = parent_of(kind, identity)
            if parent:
                edges.add((obj(*parent), "contains", key))
            elif kind in ("qos_profile", "shared_profile", "device_settings", "ihub_virtual_port", "ihub_lag", "ihub_service", "ihub_customer"):
                # Device ownership is not physical containment. Shared catalogs
                # must not become child-enumeration requirements of the chassis.
                edges.add((node_key("msan", ""), "owns", key))
        elif observed:
            nodes[key]["observed"] = True
        return key

    obj("msan", "", True)

    def config_node(resource, section, identity, read_scope=None):
        key = node_key("configuration", (resource, section, identity))
        nodes[key] = {"key": key, "kind": "configuration", "resource": resource,
                      "section": section, "identity": json.loads(json.dumps(identity)), "observed": True}
        if read_scope:
            nodes[key]["read_scope"] = read_scope
        return key

    records = []
    for binding in catalog["bindings"]:
        resource, section = binding["resource"], binding["section"]
        fields = binding["identity"]
        fields = fields if isinstance(fields, list) else [fields]
        for row in _rows(resources.get(resource), section):
            if not isinstance(row, dict) or any(field not in row for field in fields):
                gaps.append({"reason": "missing_identity", "resource": resource, "section": section})
                continue
            values = tuple(row[field] for field in fields)
            if any(not isinstance(v, (str, int)) or isinstance(v, bool) for v in values):
                gaps.append({"reason": "invalid_identity", "resource": resource, "section": section})
                continue
            identity = values if len(fields) > 1 else values[0]
            key = config_node(resource, section, identity, binding.get("read_scope"))
            records.append((binding, row, identity, key))

    # Typed primary resources first; ambiguous bare service ports can only use
    # exact evidence from those objects, regardless of input dictionary order.
    for binding, row, identity, key in records:
        try:
            owner = decode(binding["decoder"], identity)
        except UnknownIdentity:
            continue
        known_ports.add(owner)
        edges.add((key, "configures", obj(owner[0], owner[1], observed=True)))
        if binding["resource"] == "link_agg" and binding["section"] == "groups":
            for member in row.get("ports") or []:
                try:
                    member_owner = decode("ethernet_port", member)
                except UnknownIdentity:
                    gaps.append({"reason": "unknown_member", "node": key})
                    continue
                # Membership is neither containment nor an instruction to read
                # the other members' entire configuration recursively.
                edges.add((obj(*member_owner), "member_of", obj(*owner)))

    for binding, row, identity, key in records:
        try:
            owner = decode(binding["decoder"], identity, known_ports)
        except UnknownIdentity:
            # Several object kinds can share one bare address (line / Ethernet
            # port / bonding group / LAG). Keep the configuration reachable from
            # every candidate instead of dropping it, but report ownership as
            # unresolved rather than asserting a guessed owner.
            owner = None
            candidates = candidate_owners(binding["decoder"], identity, known_ports)
            if candidates:
                for kind, ident in candidates:
                    edges.add((key, "candidate_owner", obj(kind, ident, observed=True)))
                gaps.append({"reason": "ambiguous_owner", "resource": binding["resource"],
                             "section": binding["section"], "node": key,
                             "candidates": [list(c) for c in candidates]})
            else:
                gaps.append({"reason": "unknown_owner", "resource": binding["resource"],
                             "section": binding["section"], "node": key})
        if owner is not None:
            edges.add((key, "configures", obj(owner[0], owner[1], observed=True)))
            if binding["resource"] in ("ihub_lags", "ihub_services"):
                from .ihub import sap_endpoint
                if binding["resource"] == "ihub_lags":
                    for member in row.get("ports") or []:
                        try:
                            member_owner = decode("ihub_port", member)
                            edges.add((obj(*member_owner), "member_of", obj(*owner)))
                        except UnknownIdentity:
                            gaps.append({"reason": "unknown_member", "node": key})
                elif binding["section"] == "services":
                    try:
                        customer = decode("ihub_customer", row.get("customer_id"))
                        edges.add((key, "references", obj(*customer)))
                    except UnknownIdentity:
                        gaps.append({"reason": "unknown_reference", "node": key, "field": "customer_id"})
                    saps = list(row.get("saps") or [])
                    for interface in row.get("interfaces") or []:
                        saps.extend(interface.get("saps") or [])
                    for sap in saps:
                        try:
                            edges.add((key, "references", obj(*sap_endpoint(sap.get("id")))))
                        except UnknownIdentity:
                            gaps.append({"reason": "unknown_reference", "node": key, "field": "saps.id"})
            # VLAN membership is explicit data on a bridge instance, not inferred
            # from an arbitrary nested field or string suffix.
            if binding["resource"] == "bridges":
                for vlan in row.get("vlan_id") or []:
                    vid = str(vlan.get("id", "")) if isinstance(vlan, dict) else ""
                    if vid.startswith("stacked:"):
                        parts = vid.split(":")
                        valid = len(parts) == 3 and _valid_vlan(parts[1]) and _valid_vlan(parts[2])
                    else:
                        valid = _valid_vlan(vid)
                    if valid:
                        # owner is ("bridge_port", (port kind, port identity)); the
                        # VLAN port stacks on that bridge port at the same address.
                        vlan_key = obj("vlan_port", (owner[1][0], owner[1][1], vid), observed=True)
                        # A bridge-port read is the collection's smallest read
                        # unit and also supplies each nested VLAN's configuration.
                        edges.add((key, "configures", vlan_key))
                    else:
                        gaps.append({"reason": "invalid_vlan", "node": key})
        # Profile/service references are independent of ownership resolution: an
        # unresolved (candidate-owned) instance still depends on its profiles.
        fields = catalog["profile_references"].get(binding["resource"])
        if fields:
            for kind, name, field in _references(row, fields):
                if kind and name:
                    edges.add((key, "references", obj("qos_profile", (kind, name))))
                else:
                    gaps.append({"reason": "unknown_reference", "node": key, "field": field})
        for reference in catalog.get("typed_references", []):
            if reference["resource"] != binding["resource"] or reference["section"] != binding["section"]:
                continue
            value = row.get(reference["field"])
            if value is None or value in ("none", "not-applicable"):
                continue
            if not isinstance(value, (str, int)) or isinstance(value, bool):
                gaps.append({"reason": "invalid_reference", "node": key, "field": reference["field"]})
                continue
            target = obj("shared_profile", (reference["target_resource"], reference["target_section"], str(value)))
            edges.add((key, "references", target))

    mapped = {(b["resource"], b["section"]) for b in catalog["bindings"]}
    section_scope = catalog.get("section_scopes", {})
    from ..targeted import TARGETED_GATHER

    def global_config(resource):
        # A single full-resource read is required for device-wide settings.
        # Do not copy credential-valued identities (e.g. SNMP communities) into
        # the graph: only its family read unit and ownership are needed here.
        key = config_node(resource, "all", None, "all")
        edges.add((key, "configures", obj("device_settings", resource, True)))

    for resource, data in resources.items():
        sections = TARGETED_GATHER.get(resource)
        if sections is None:
            if resource in {binding["resource"] for binding in catalog["bindings"]}:
                continue  # explicit whole-family bindings outside TARGETED_GATHER
            if resource in catalog.get("global_resources", []):
                global_config(resource)
            else:
                gaps.append({"reason": "unmapped_resource", "resource": resource})
        else:
            for section in sections:
                if (resource, section) not in mapped and _rows(data, section):
                    scope = section_scope.get("%s.%s" % (resource, section))
                    if scope == "device_global":
                        global_config(resource)
                    elif scope == "shared_profile":
                        identity_field = sections[section]
                        if not isinstance(identity_field, str):
                            gaps.append({"reason": "profile_identity_unmodeled", "resource": resource, "section": section})
                            continue
                        for row in _rows(data, section):
                            identity = row.get(identity_field) if isinstance(row, dict) else None
                            if not isinstance(identity, (str, int)) or isinstance(identity, bool):
                                gaps.append({"reason": "missing_identity", "resource": resource, "section": section})
                                continue
                            key = config_node(resource, section, identity)
                            edges.add((key, "configures", obj("shared_profile", (resource, section, str(identity)), True)))
                    else:
                        gap = {"reason": "unmapped_section", "resource": resource, "section": section}
                        if scope:
                            gap["scope"] = scope
                        gaps.append(gap)
            if isinstance(data, dict):
                global_fields = catalog.get("global_settings", {}).get(resource, ())
                if any(_path_present(data, field) for field in global_fields):
                    global_config(resource)
                claimed_paths = {tuple(s.split(".")) for s in sections} | {tuple(field.split(".")) for field in global_fields}
                if _has_unmapped_settings(data, claimed_paths):
                    gaps.append({"reason": "unmapped_settings", "resource": resource})
    return {"schema_version": SCHEMA_VERSION, "msan": msan,
            "nodes": sorted(nodes.values(), key=lambda n: n["key"]),
            "edges": [{"source": source, "relation": relation, "target": target}
                      for source, relation, target in sorted(edges)],
            "gaps": sorted(gaps, key=lambda g: json.dumps(g, sort_keys=True))}


def plan_known_reads(graph, kind, identity):
    """Observed subtree + referenced profile closure, NOT a complete refresh.

    Requests name TARGETED_GATHER sections (not NOC's older scope aliases).
    Never broadens a scoped request into whole-family/MSAN reads. The caller
    must obtain fresh, successful child-discovery certificates before execution
    can be advertised as a recursive refresh. This first version blocks it.
    """
    if not isinstance(graph, dict) or graph.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported topology graph version")
    root = node_key(kind, identity)
    nodes = {n["key"]: n for n in graph["nodes"]}
    if root not in nodes:
        raise ValueError("The requested root is not known")
    children, configs, refs, candidates = {}, {}, {}, {}
    for edge in graph["edges"]:
        source, relation, target = edge["source"], edge["relation"], edge["target"]
        if relation == "contains" or (relation == "owns" and kind == "msan"):
            children.setdefault(source, set()).add(target)
        elif relation == "configures":
            configs.setdefault(target, set()).add(source)
        elif relation == "candidate_owner":
            # Unresolved ownership: include the configuration when refreshing any
            # candidate object, but never walk back to the other candidates.
            candidates.setdefault(target, set()).add(source)
        elif relation == "references":
            refs.setdefault(source, set()).add(target)
    selected, pending = set(), [root]
    while pending:
        key = pending.pop()
        if key not in selected:
            selected.add(key)
            pending.extend(children.get(key, ()))
    pending = list(selected)
    # Follow profile dependencies only forwards. Never traverse their other
    # consumers, or the profile's parent (the entire MSAN). Candidate-owned
    # configuration is pulled in the same direction (object -> config), so a
    # shared QoS entry is read once without selecting its other candidate owners.
    while pending:
        key = pending.pop()
        for target in configs.get(key, set()) | candidates.get(key, set()) | refs.get(key, set()):
            if target not in selected:
                selected.add(target)
                pending.append(target)
    reads = {}
    global_reads = set()
    for key in sorted(selected):
        node = nodes[key]
        if node["kind"] == "configuration":
            if node.get("read_scope") == "all":
                global_reads.add(node["resource"])
            else:
                reads.setdefault((node["resource"], node["section"]), []).append(node["identity"])
    from .discovery import coverage
    discovery = coverage(graph, kind, identity)
    missing = [{"node": key, "reason": "referenced_definition_missing"}
               for key in sorted(selected) if nodes[key]["kind"] in ("qos_profile", "shared_profile") and not configs.get(key)]
    # Unowned configuration cannot safely be assigned to, OR excluded from, this
    # subtree. Retain all mapping gaps conservatively until the catalog covers it.
    gaps = list(graph["gaps"]) + discovery["missing"] + discovery["unimplemented"] + discovery["failed"] + missing
    catalog = export_catalog()
    unmodeled = {kind for kind, spec in catalog["objects"].items()
                 if spec.get("configuration_status") == "unmodeled"}
    gaps += [{"node": key, "reason": "configuration_coverage_unmodeled"}
             for key in sorted(selected)
             if nodes[key]["kind"] in unmodeled]
    partial = {kind for kind, spec in catalog["objects"].items() if spec.get("configuration_status") == "partial"}
    gaps += [{"node": key, "reason": "configuration_coverage_partial"}
             for key in sorted(selected) if nodes[key]["kind"] in partial]
    if kind == "msan":
        gaps += [{"domain": domain, "reason": "configuration_domain_unmodeled"}
                 for domain in catalog.get("unmodeled_configuration_domains", [])]
    unresolved = sorted({g["node"] for g in graph["gaps"]
                         if g.get("reason") == "ambiguous_owner" and g.get("node") in selected})
    return {"schema_version": SCHEMA_VERSION, "msan": graph["msan"], "root": root,
            "nodes": sorted(selected), "reads": [
                {"resource": resource, "section": section, "ids": ids}
                for (resource, section), ids in sorted(reads.items()) if resource not in global_reads] + [
                    {"resource": resource, "section": "all", "ids": []} for resource in sorted(global_reads)],
            "complete": False, "executable": False, "physical_discovery": discovery,
            "unresolved_ownership": unresolved,
            "gaps": gaps, "reason": "observed_graph_is_not_complete_discovery"}
