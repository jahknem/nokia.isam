"""Fresh child-enumeration results for the semantic graph.

This module never executes commands.  A facts adapter supplies the response for
one collection-owned discovery command; the adapter records the command, scope,
outcome and timestamp.  A successful enumeration is evidence only for that one
direct-neighbor relation, never for the whole recursive subtree.

The ISAM has no scoped "list the children of X" command for PON->ONT or
ONT->slot.  The smallest source that contains those children is device-wide
(``show equipment ont interface``) or family-wide (``info configure equipment
ont flat``).  Discovery therefore reads that whole source and filters by the
parent identity, and records ``read_scope`` honestly so callers know the read
also touched siblings.  This is the documented enumeration method, not a hidden
fallback to a wider read than requested.

Unknown/unsupported enumeration is a gap, not an empty child list.  A successful
empty filter is different: it is confirmed absence of children for that parent
within the enumerated source.
"""

from datetime import datetime, timezone
import math
import re

from . import SCHEMA_VERSION
from .graph import node_key
from .identity import DEPTHS, UnknownIdentity, _vlan_suffix, decode, numeric, parent_of

DISCOVERY_VERSION = 1

# relation -> (command template, read_scope).  read_scope is the true breadth of
# the source read: "device" (whole MSAN) or "family" (whole resource family).
# There is no "scoped" enumeration command for these relations on this platform.
ENUMERATION = {
    ("pon", "ont"): ("show equipment ont interface", "device"),
    ("ont", "ont_slot"): ("info configure equipment ont flat", "family"),
}

# Validation provenance for the ENUMERATION adapters (both live-verified on
# DS-LIN-TEST-01). See SOURCES evidence below for the convention.
ENUMERATION_EVIDENCE = {
    ("pon", "ont"): "live_verified",
    ("ont", "ont_slot"): "live_verified",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def result(kind, identity, child_kind, status, children=(), command=None,
           collected_at=None, error=None, source="collection", read_scope=None):
    """One direct-neighbor enumeration result, JSON-compatible and fail-closed."""
    if kind in ("bridge_port", "vlan_port") and isinstance(identity, (tuple, list)):
        identity = tuple(identity)
    _validate_parent(kind, identity)
    # A child source existing somewhere is not evidence that any parent can
    # enumerate it. Reject invalid relations even when their result is empty.
    from . import export_catalog
    if child_kind not in export_catalog()["objects"].get(kind, {}).get("children", []):
        raise UnknownIdentity("Unsupported discovery relation: %s -> %s" % (kind, child_kind))
    if status not in ("ok", "unsupported", "error"):
        raise ValueError("Discovery status must be ok, unsupported or error")
    if status != "ok" and children:
        raise ValueError("A failed enumeration cannot report children")
    if status == "ok" and not command:
        raise ValueError("A successful enumeration must name its read command")
    if status == "ok" and read_scope not in ("device", "family", "scoped"):
        raise ValueError("A successful enumeration must record its read scope")
    if status != "ok" and not error:
        raise ValueError("A failed enumeration must report its reason")
    identities = []
    for child in children:
        if child_kind in ("vlan_port", "bridge_port"):
            # These identities are tuples: (port kind, port identity[, vlan]).
            child_identity = tuple(child) if isinstance(child, (tuple, list)) else child
            expected = 3 if child_kind == "vlan_port" else 2
            if not isinstance(child_identity, tuple) or len(child_identity) != expected:
                raise UnknownIdentity("%s child identity has the wrong shape" % child_kind)
        else:
            child_identity = child[1] if isinstance(child, (tuple, list)) and len(child) == 2 else child
            if not isinstance(child_identity, str):
                raise UnknownIdentity("Child identities must be strings")
        try:
            decoded = decode(child_kind, child_identity)
        except UnknownIdentity:
            raise UnknownIdentity("Child does not match the declared %s identity" % child_kind)
        if parent_of(*decoded) != (kind, identity):
            raise UnknownIdentity("Child %s does not belong to %s %s" % (child_identity, kind, identity))
        identities.append(child_identity)
    return {
        "schema_version": SCHEMA_VERSION,
        "discovery_version": DISCOVERY_VERSION,
        "parent": node_key(kind, identity),
        "child_kind": child_kind,
        "status": status,
        "children": sorted(set(identities)),
        "command": command,
        "read_scope": read_scope,
        "collected_at": collected_at or utc_now(),
        "error": error,
        "source": source,
    }


def parse_ont_serials(output, pon):
    """Children of one PON from the device-wide ``show equipment ont interface``.

    The command is a compact configured-ONT index, not an operational-status
    requirement: an admin-down or offline ONT is still a child.  Rows for other
    PONs are filtered out (the source is device-wide); a row whose identity does
    not parse as an ONT under some PON is a malformed source, not a child.
    """
    if not numeric(pon, DEPTHS["pon"]):
        raise UnknownIdentity("Expected a four-component PON identity")
    from ansible_collections.nokia.isam.plugins.module_utils.tables import parse_status_table

    if not isinstance(output, str) or not any(
            "ont-idx" in line and "|" in line for line in output.splitlines()):
        raise UnknownIdentity("ONT enumeration has no recognized table header")
    rows = parse_status_table(output)
    counts = re.findall(r"(?m)^\s*interface count\s*:\s*(\d+)\s*$", output)
    if len(counts) != 1 or int(counts[0]) != len(rows):
        raise UnknownIdentity("ONT enumeration table count does not match parsed rows")
    children = []
    for row in rows:
        identity = row.get("ont_idx")
        if not identity:
            raise UnknownIdentity("ONT index table row has no ont_idx")
        try:
            decode("ont", identity)
        except UnknownIdentity:
            raise UnknownIdentity("ONT index table row is not a valid ONT identity: %s" % identity)
        if parent_of("ont", identity) == ("pon", pon):
            children.append(identity)
    return result("pon", pon, "ont", "ok", children,
                  command="show equipment ont interface", read_scope="device")


def parse_ont_slots(output, ont):
    """Children of one ONT from the family-wide ``info configure equipment ont flat``.

    Only slot lines under the requested ONT are kept; slots of other ONTs in the
    family-wide source are filtered out.  A non-slot line is ignored (the source
    also contains interface/sw-ctrl/loop/pm-collect nodes).
    """
    if not numeric(ont, DEPTHS["ont"]):
        raise UnknownIdentity("Expected a five-component ONT identity")
    children = {identity for identity in _config_identities(
        output, "configure equipment ont slot ", "ont_slot", "configure equipment ont ")
                if parent_of("ont_slot", identity) == ("ont", ont)}
    return result("ont", ont, "ont_slot", "ok", sorted(children),
                  command="info configure equipment ont flat", read_scope="family")


# --- Source-driven enumeration -------------------------------------------------
# Each child kind is enumerated from one whole source (the ISAM has no scoped
# "list children" command).  A source declares its command, true read_scope, and
# how to extract child identities from the response.  Discovery filters those
# identities by the requested parent.  read_scope is recorded honestly.
#
# kind: "table" (parse_status_table, identity in a column) or "config" (flat
# configure lines, identity is the token after a fixed CLI prefix).
SOURCES = {
    "uni": {
        "parents": ("ont_slot",),
        "command": "info configure ethernet ont flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure ethernet ont ",
    },
    "pon": {
        "parents": ("card",),
        "command": "info configure pon interface flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure pon interface ",
    },
    "xdsl_line": {
        "parents": ("card",),
        "command": "info configure xdsl line flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure xdsl line ",
    },
    "ethernet_port": {
        "parents": ("card",),
        "command": "info configure ethernet line flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure ethernet line ",
    },
    "cage": {
        "parents": ("card",),
        "command": "info configure interface cage flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure interface cage ",
    },
    "bonding_group": {
        "parents": ("card",),
        "command": "info configure interface port flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure interface port bonding:",
        "family_prefix": "configure interface port ",
    },
    "lag": {
        "parents": ("card",),
        "command": "info configure link-agg flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure link-agg group ",
        "family_prefix": "configure link-agg ",
    },
    "rack": {
        "parents": ("msan",),
        "command": "info configure equipment flat",
        "read_scope": "family",
        "kind": "equipment_racks",
        "prefix": "configure equipment rack ",
        "family_prefix": "configure equipment ",
    },
    "shelf": {
        "parents": ("rack",),
        "command": "info configure equipment flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure equipment shelf ",
        "family_prefix": "configure equipment ",
    },
    "card": {
        "parents": ("msan", "shelf"),
        "command": "info configure equipment flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure equipment slot ",
        "family_prefix": "configure equipment ",
    },
    "applique": {
        "parents": ("msan",),
        "command": "info configure equipment flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure equipment applique ",
        "family_prefix": "configure equipment ",
    },
    "channel_pair": {
        "parents": ("card",),
        "command": "info configure channel-pair interface flat",
        "read_scope": "family",
        "kind": "config",
        "prefix": "configure channel-pair interface ",
        "family_prefix": "configure channel-pair ",
    },
    # Physical cage inventory, including empty cages. Live-verified on
    # DS-LIN-TEST-01: header "transceiver-inventory table", identity column
    # "index", footer "transceiver-inventory count : N".
    "transceiver": {
        "parents": ("card", "applique"),
        "command": "show equipment transceiver-inventory",
        "read_scope": "device",
        "kind": "table",
        "column": "index",
        "count_label": "transceiver-inventory count",
    },
    "uplink": {
        "parents": ("card", "applique"),
        "command": "show port",
        "read_scope": "device",
        "kind": "ihub_optical_ports",
    },
    # Bridge ports and VLAN ports are interface-stack layers. The device's own
    # stack table gives typed higher/lower pairs, so attachment is evidenced,
    # not guessed: bridge-port:X stacks on la-group:X / ethernet-line:X / uni:X,
    # and vlan-port:X:V stacks on bridge-port:X (same address). Live-verified
    # across the whole lab device (1103 rows, matching footer).
    "bridge_port": {
        "parents": ("uni", "xdsl_line", "ethernet_port", "lag"),
        "command": "show interface stack",
        "read_scope": "device",
        "kind": "stack_bridge",
    },
    "vlan_port": {
        "parents": ("bridge_port",),
        "command": "show interface stack",
        "read_scope": "device",
        "kind": "stack_vlans",
    },
}

# Validation provenance per source. Every adapter here was exercised read-only
# on DS-LIN-TEST-01 except the channel-pair source, which the non-NGPON2 lab
# firmware rejects (documented-only; needs an NGPON2-capable device). A new
# adapter MUST be listed as documented until it is live-verified. This is
# metadata about adapter validation, not about a particular read: a fresh
# successful read is real evidence regardless of prior verification.
_LIVE_VERIFIED_SOURCES = {
    "uni", "pon", "xdsl_line", "ethernet_port", "cage", "bonding_group", "lag",
    "rack", "shelf", "card", "applique", "transceiver", "bridge_port", "vlan_port", "uplink",
}
for _name, _source in SOURCES.items():
    _source["evidence"] = "live_verified" if _name in _LIVE_VERIFIED_SOURCES else "documented"


def _validate_parent(kind, identity):
    if kind == "msan":
        if identity == "":
            return
    elif kind in DEPTHS or kind in ("card", "applique", "bridge_port"):
        decode(kind, identity)
        return
    raise UnknownIdentity("Unsupported discovery parent identity: %s" % kind)


def adapter_for(kind, child_kind):
    """The exact relation capability; never promote a child-only match."""
    if (kind, child_kind) in ENUMERATION:
        command, read_scope = ENUMERATION[(kind, child_kind)]
        return {"command": command, "read_scope": read_scope}
    source = SOURCES.get(child_kind)
    if source is not None and kind in source["parents"]:
        return source
    raise UnknownIdentity("No enumeration adapter for %s -> %s" % (kind, child_kind))


def evidence_for(kind, child_kind):
    """Validation provenance of a relation's adapter, or None if unimplemented.

    "live_verified" means exercised read-only on a reference device;
    "documented" means derived from the CLI reference but not yet live-verified.
    """
    if (kind, child_kind) in ENUMERATION:
        return ENUMERATION_EVIDENCE.get((kind, child_kind), "documented")
    source = SOURCES.get(child_kind)
    if source is not None and kind in source["parents"]:
        return source.get("evidence", "documented")
    return None


# The device closes every flat 'info configure ... flat' reply with a delimiter
# line (tests/fixtures/bridges/targeted-present, equipment/slot-flat-detail),
# also when the family is empty. It is the flat counterpart of a table's count
# footer: without it a reply may be cut short, so it cannot confirm absence.
_FLAT_TERMINATOR = re.compile(r"#-{10,}")


def _config_identities(output, prefix, child_kind, family_prefix=None):
    """Child identities from flat configure lines under a fixed CLI prefix.

    The reply must end with the device's terminal delimiter; a reply without it
    (truncated, comment/echo-only) is not a complete source. A line whose identity
    does not parse as the child kind is a malformed source (rejected), not silently
    skipped; lines under other prefixes of the same family are ignored.
    """
    if not isinstance(output, str) or not output.strip():
        raise UnknownIdentity("Enumeration source is blank; absence is not confirmed")
    if not _FLAT_TERMINATOR.fullmatch(output.strip().splitlines()[-1].strip()):
        raise UnknownIdentity("Enumeration source has no terminal delimiter; the reply may be truncated")
    family_prefix = family_prefix or prefix
    identities = set()
    for raw_line in (output or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "echo ")):
            continue
        if not line.startswith(family_prefix):
            raise UnknownIdentity("Enumeration source contains an unexpected line")
        if line == prefix.rstrip():
            raise UnknownIdentity("Enumeration source has a missing identity")
        if not line.startswith(prefix):
            continue
        tokens = line[len(prefix):].split()
        if not tokens:
            raise UnknownIdentity("Enumeration source has a missing identity")
        identity = tokens[0]
        try:
            decode(child_kind, identity)
        except UnknownIdentity:
            raise UnknownIdentity("%s line is not a valid %s identity: %s" % (prefix.strip(), child_kind, identity))
        identities.add(identity)
    return sorted(identities)


def _table_identities(output, source, child_kind):
    """Identities from a recognized status table with a matching footer count.

    A blank/garbled reply or a missing/mismatched footer cannot confirm absence.
    An identity form the catalog does not decode rejects the whole source: a
    partially understood inventory is not a certificate.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.tables import parse_status_table

    column = source["column"]
    if not isinstance(output, str) or not any(
            column in line and "|" in line for line in output.splitlines()):
        raise UnknownIdentity("Enumeration table has no recognized header")
    rows = parse_status_table(output)
    counts = re.findall(r"(?m)^\s*%s\s*:\s*(\d+)\s*$" % re.escape(source["count_label"]), output)
    if len(counts) != 1 or int(counts[0]) != len(rows):
        raise UnknownIdentity("Enumeration table count does not match parsed rows")
    identities = set()
    for row in rows:
        identity = row.get(column)
        if not identity:
            raise UnknownIdentity("Enumeration table row has no %s" % column)
        decode(child_kind, identity)
        identities.add(identity)
    return sorted(identities)


def _stack_pairs(output):
    """Typed (higher, lower) pairs from the device interface-stack table.

    Requires the recognized header and a matching ``stack count`` footer; a
    blank/truncated/garbled reply cannot confirm absence.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.tables import parse_status_table

    if not isinstance(output, str) or not any(
            "higher" in line and "lower" in line and "|" in line for line in output.splitlines()):
        raise UnknownIdentity("Interface stack table has no recognized header")
    rows = parse_status_table(output)
    counts = re.findall(r"(?m)^\s*stack count\s*:\s*(\d+)\s*$", output)
    if len(counts) != 1 or int(counts[0]) != len(rows):
        raise UnknownIdentity("Interface stack count does not match parsed rows")
    pairs = []
    for row in rows:
        higher, lower = row.get("higher"), row.get("lower")
        if not higher or not lower:
            raise UnknownIdentity("Interface stack row has no higher/lower identity")
        pairs.append((higher, lower))
    return pairs


# The lower-interface spelling of each bridge-port parent kind. An xDSL line's
# bridge port stacks on its ethernet-line (EFM) facet, not on xdsl-line: and
# never on bonding: (live stack evidence).
_STACK_LOWER = {"uni": "uni:", "xdsl_line": "ethernet-line:", "ethernet_port": "ethernet-line:", "lag": "la-group:"}


def _stack_bridge_children(pairs, kind, identity):
    lower_name = _STACK_LOWER[kind] + identity
    children = set()
    for higher, lower in pairs:
        if not higher.startswith("bridge-port:") or lower != lower_name:
            continue
        address = higher[len("bridge-port:"):]
        if address != identity:
            raise UnknownIdentity("Bridge port address does not match its lower interface")
        children.add((kind, identity))
    return sorted(children)


def _stack_vlan_children(pairs, identity):
    port_kind, port_address = identity
    lower_name = "bridge-port:" + port_address
    children = set()
    for higher, lower in pairs:
        if not higher.startswith("vlan-port:") or lower != lower_name:
            continue
        suffix = _vlan_suffix(higher[len("vlan-port:"):])
        if suffix is None:
            raise UnknownIdentity("VLAN port identity is not a supported form: %s" % higher)
        address, vlan = suffix
        if address != port_address:
            raise UnknownIdentity("VLAN port address does not match its bridge port")
        children.add((port_kind, port_address, vlan))
    return sorted(children)


def enumerate_children(kind, identity, child_kind, output):
    """Enumerate one parent's children of one kind from a whole-source response.

    Returns a discovery result.  The source must be the one declared for the
    child kind; identities are filtered to those whose physical parent is the
    requested (kind, identity).  A successful empty filter is confirmed absence.
    """
    _validate_parent(kind, identity)
    if kind == "bridge_port" and isinstance(identity, str):
        identity = decode("bridge_port", identity)[1]
    source = adapter_for(kind, child_kind)
    if source["kind"] == "table":
        identities = _table_identities(output, source, child_kind)
        children = [i for i in identities if parent_of(child_kind, i) == (kind, identity)]
    elif source["kind"] == "ihub_optical_ports":
        from .ihub import optical_ports
        children = [i for i in optical_ports(output, owner=identity) if parent_of(child_kind, i) == (kind, identity)]
    elif source["kind"] in ("stack_bridge", "stack_vlans"):
        pairs = _stack_pairs(output)
        if source["kind"] == "stack_bridge":
            children = _stack_bridge_children(pairs, kind, identity)
        else:
            children = _stack_vlan_children(pairs, identity)
    elif source["kind"] in ("config", "equipment_racks"):
        identities = _config_identities(output, source["prefix"], child_kind, source.get("family_prefix"))
        if source["kind"] == "equipment_racks":
            # A shelf's canonical address proves its enclosing rack even when the
            # device omits a default-only rack configuration. No assumed rack 1.
            shelves = _config_identities(output, "configure equipment shelf ", "shelf", source["family_prefix"])
            identities = sorted(set(identities) | {parent_of("shelf", shelf)[1] for shelf in shelves})
        children = [i for i in identities if parent_of(child_kind, i) == (kind, identity)]
    else:
        raise UnknownIdentity("Unsupported source kind: %s" % source["kind"])
    return result(kind, identity, child_kind, "ok", children,
                  command=source["command"], read_scope=source["read_scope"])


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Discovery requires an explicit UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid discovery timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("Discovery timestamp must include its timezone")
    return parsed.astimezone(timezone.utc)


def attach_discovery(graph, results):
    """Attach fresh direct-neighbor evidence to an observed graph.

    Successful results replace the cached child set for exactly that relation;
    failed results leave the old observations visible but mark the relation
    stale.  The graph remains non-executable until every required relation in
    the selected subtree has a successful fresh result.
    """
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported topology graph version")
    nodes = {node["key"]: dict(node) for node in graph["nodes"]}
    edges = {(edge["source"], edge["relation"], edge["target"]) for edge in graph["edges"]}
    evidence = {(item["parent"], item["child_kind"]): item for item in graph.get("discovery", [])}
    incoming = set()
    pending = list(results)
    while pending:
        ready = [item for item in pending if item.get("parent") in nodes]
        if not ready:
            raise ValueError("Discovery parent is not in the graph or this discovery batch")
        for item in ready:
            pending.remove(item)
            _attach_one(item, nodes, edges, evidence, incoming)
    graph = dict(graph)
    graph["nodes"] = sorted(nodes.values(), key=lambda node: node["key"])
    graph["edges"] = [{"source": source, "relation": relation, "target": target}
                      for source, relation, target in sorted(edges)]
    graph["discovery"] = [evidence[key] for key in sorted(evidence)]
    return graph


def _attach_one(item, nodes, edges, evidence, incoming):
    if item.get("schema_version") != SCHEMA_VERSION or item.get("discovery_version") != DISCOVERY_VERSION:
        raise ValueError("Unsupported discovery result version")
    parent = item["parent"]
    key = (parent, item["child_kind"])
    if key in incoming:
        raise ValueError("Duplicate discovery result for one direct-neighbor relation")
    incoming.add(key)
    _timestamp(item.get("collected_at"))
    parent_node = nodes[parent]
    checked = result(parent_node["kind"], parent_node["identity"], item["child_kind"], item["status"],
                     item["children"], item.get("command"), item["collected_at"], item.get("error"),
                     item.get("source", "collection"), item.get("read_scope"))
    if item["status"] == "ok":
        adapter = adapter_for(parent_node["kind"], item["child_kind"])
        if item["command"] != adapter["command"] or item["read_scope"] != adapter["read_scope"]:
            raise ValueError("Discovery result does not match the declared enumeration source")
    evidence[key] = checked
    if item["status"] == "ok":
        # Retire only this direct-neighbor edge set. Detached observations
        # remain available for audit; this does not delete shared config or
        # another scope's observations.
        removed = {edge for edge in edges if edge[0] == parent and edge[1] == "contains"
                   and nodes[edge[2]]["kind"] == item["child_kind"]}
        edges.difference_update(removed)
        for identity in item["children"]:
            child_key = node_key(item["child_kind"], identity)
            nodes[child_key] = {"key": child_key, "kind": item["child_kind"], "identity": identity, "observed": True}
            edges.add((parent, "contains", child_key))


def coverage(graph, kind, identity, now=None, max_age_seconds=300, collected_since=None):
    """Recursive coverage certificate for one root, based only on fresh evidence.

    Returns a manifest with the relations that succeeded, failed or are missing.
    A missing/failed enumeration never becomes "no children".  Configuration
    read completeness is tracked separately by the caller; this certificate
    covers physical child discovery only.
    """
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported topology graph version")
    if (not isinstance(max_age_seconds, (int, float)) or isinstance(max_age_seconds, bool)
            or not math.isfinite(max_age_seconds) or max_age_seconds < 0):
        raise ValueError("Discovery maximum age must be nonnegative")
    now = _timestamp(now or utc_now())
    since = _timestamp(collected_since) if collected_since is not None else None
    nodes = {node["key"]: node for node in graph["nodes"]}
    root = node_key(kind, identity)
    if root not in nodes:
        raise ValueError("The requested root is not known")
    evidence = {(item["parent"], item["child_kind"]): item for item in graph.get("discovery", [])}
    children = {}
    for edge in graph["edges"]:
        if edge["relation"] == "contains":
            children.setdefault(edge["source"], set()).add(edge["target"])

    from . import export_catalog
    catalog = export_catalog()["objects"]
    required, ok, failed, missing, unimplemented = [], [], [], [], []
    seen = set()
    pending = [root]
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        node = nodes[key]
        spec = catalog.get(node["kind"])
        if spec is None:
            unimplemented.append({"parent": key, "reason": "unknown_object_kind"})
            continue
        for child_kind in spec.get("children", []):
            relation = {"parent": key, "child_kind": child_kind}
            required.append(relation)
            available = spec.get("discovery", {}).get(child_kind, "unimplemented")
            item = evidence.get((key, child_kind))
            if available != "implemented":
                unimplemented.append(dict(relation, reason="discovery_unimplemented"))
            elif item is None:
                missing.append(dict(relation, reason="discovery_missing"))
            elif item["status"] != "ok":
                failed.append(dict(relation, reason=item["status"], error=item.get("error")))
            elif ((now - _timestamp(item["collected_at"])).total_seconds() > max_age_seconds
                  or (_timestamp(item["collected_at"]) - now).total_seconds() > 5
                  or (since is not None and _timestamp(item["collected_at"]) < since)):
                missing.append(dict(relation, reason="discovery_stale"))
            else:
                ok.append(dict(relation, read_scope=item.get("read_scope")))
                for child in item["children"]:
                    pending.append(node_key(child_kind, child))
        # Cached children are traversed for reporting, but without fresh evidence
        # their own required relations remain missing above.
        for child in sorted(children.get(key, ())):
            if child not in seen:
                pending.append(child)
    # Informational: required relations whose adapter is documented-only (not
    # yet live-verified). A fresh successful read still counts as evidence; this
    # only flags that the capability itself rests on documentation, so a
    # completeness claim can carry that caveat. It does not block coverage.
    documented_only = [dict(r, evidence="documented") for r in required
                       if evidence_for(nodes[r["parent"]]["kind"], r["child_kind"]) == "documented"]
    return {
        "schema_version": SCHEMA_VERSION,
        "discovery_version": DISCOVERY_VERSION,
        "msan": graph["msan"],
        "root": root,
        "complete": not failed and not missing and not unimplemented,
        "required": required,
        "ok": ok,
        "failed": failed,
        "missing": missing,
        "unimplemented": unimplemented,
        "documented_only": documented_only,
        "nodes": sorted(seen),
    }
