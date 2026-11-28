"""Complete refresh of one object subtree (ONT, PON, card): plan and evaluate.

No CLI execution or Ansible dependency. A refresh runs in rounds:

0. ``context_reads(root)`` reads the planned type of the line card that holds the root
   and of the NT slots; ``context_from(results)`` turns the answer into the context the
   other steps take. The card-type rules (cards.py) decide which child kinds and card
   sections apply; without a context, or for an unknown planned type, nothing is
   assumed and the refresh names the gap.
1. ``discovery_requests(root, results, context)`` names the direct-child enumerations still
   needed for the objects known so far: one ``isam_topology_discovery`` call per round
   (``requests``), which reads every source command once for the whole round.
2. ``configuration_reads(objects)`` names every configuration section that can
   configure each object kind (``relations/``), addressed by that object's own
   identity, as ``isam_read`` requests. Sections are read even when the previous
   snapshot had nothing there: only a read establishes absence.
3. ``pending_reference_reads(read_results)`` names the shared definitions (QoS
   profiles, ...) the present configuration refers to and that are not read yet, as
   further ``isam_read`` rounds until it returns nothing.
4. ``evaluate(...)`` classifies every (object, section) and every referenced
   definition as ``present``, ``absent`` (the device confirmed it) or a named gap,
   and every discovery relation as fresh, failed, missing or unimplemented. The
   refresh is ``complete`` only without any gap.

A gap is never interpreted as "empty": an unverified instance, a rejected or failed
read, a relation without an adapter, or an object kind whose identity cannot be
encoded for a section all keep the refresh incomplete and are listed by name.
"""

import json
from copy import deepcopy
from datetime import datetime, timezone

from ..relations import FAMILIES
from ..targeted import TARGETED_GATHER
from .cards import CARD_TYPES, LT_TRANSCEIVER_NOT_APPLICABLE, NT_TYPES, card_of
from .discovery import _timestamp, adapter_for, evidence_for
from .identity import UnknownIdentity, parent_of
from .objects import OBJECTS

REFRESH_VERSION = 1
ROOT_KINDS = ("ont", "pon", "card")

# Object kinds a decoder addresses with the object's own identity, unchanged.
_SAME = {"pon", "ont", "ont_slot", "uni", "xdsl_line", "ethernet_port", "lag", "bonding_group",
         "channel_pair", "card", "cage", "transceiver", "applique", "rack", "shelf"}

# (decoder, object kind) -> section identity. Each form is the inverse of
# identity.decode for that pair; tests check decode(encode(x)) == x.
_PREFIXED = {
    ("interface", "pon"): "pon:", ("interface", "ont"): "ont:", ("interface", "uni"): "uni:",
    ("interface", "xdsl_line"): "xdsl-line:", ("interface", "bonding_group"): "bonding:",
    ("interface", "lag"): "la-group:", ("interface", "channel_pair"): "chpair:",
    ("interface", "ethernet_port"): "ethernet-line:",
    ("qos_interface", "pon"): "pon:", ("qos_interface", "ont"): "ont:",
}
# A bare address: the device accepts no typed form here (QoS, user ports, MSTP
# ports). Which object it names follows the live-verified rules in identity.py.
_BARE = {
    # Not ("qos_interface", "ethernet_port"): the bare QoS index of an Ethernet port is
    # its LAG's (identity._qos_owner), which the refresh reads for the LAG.
    ("qos_interface", "uni"), ("qos_interface", "lag"), ("qos_interface", "xdsl_line"),
    ("user_port", "xdsl_line"), ("user_port", "ethernet_port"), ("user_port", "lag"),
    ("user_port", "bonding_group"),
    ("port_layer", "lag"), ("port_layer", "xdsl_line"), ("port_layer", "ethernet_port"),
}


class NotEncodable(Exception):
    """The object kind has no identity form in that section."""


def encode(decoder, kind, identity):
    """The section identity addressing object (kind, identity) through ``decoder``."""
    if decoder == kind and kind in _SAME:
        return identity
    if decoder == "lt_card" and kind == "card" and isinstance(identity, str) and identity.startswith("lt:"):
        return identity[3:]
    if (decoder, kind) in _PREFIXED:
        return _PREFIXED[(decoder, kind)] + identity
    if (decoder, kind) in _BARE:
        return identity
    if decoder == "bridge_port" and kind == "bridge_port":
        return identity[1]
    if kind == "vlan_port" and decoder in ("interface", "qos_interface"):
        _owner, port, vlan = identity
        return ("vlan-port:" if decoder == "interface" else "vlan:") + port + ":" + vlan
    raise NotEncodable("%s has no %s identity" % (kind, decoder))


def applicable_sections(kind):
    """[(resource, section, decoder)] of every section that can configure ``kind``."""
    out = []
    for resource, family in sorted(FAMILIES.items()):
        if family.get("source") == "ihub":
            continue
        for section, spec in sorted(family["sections"].items()):
            decoder = spec.get("object")
            if not decoder or ("kinds" in spec and kind not in spec["kinds"]):
                continue
            try:
                encode(decoder, kind, _SAMPLE[kind])
            except (NotEncodable, KeyError):
                continue
            out.append((resource, section, decoder))
    return out


# One well-formed identity per kind, only to test whether a decoder has a form for it.
_SAMPLE = {
    "pon": "1/1/1/1", "ont": "1/1/1/1/1", "ont_slot": "1/1/1/1/1/1", "uni": "1/1/1/1/1/1/1",
    "xdsl_line": "1/1/1/1", "ethernet_port": "1/1/1/1", "lag": "1/1/1/1", "bonding_group": "1/1/1/1",
    "channel_pair": "1/1/1/1", "card": "lt:1/1/1", "cage": "lt:1/1/1:cage:1",
    "transceiver": "lt:1/1/1:sfp:1", "bridge_port": ("uni", "1/1/1/1/1/1/1"),
    "vlan_port": ("uni", "1/1/1/1/1/1/1", "100"),
}


# A section an object is also read under: an xDSL line's EFM facet carries its own
# interface settings ('interface port ethernet-line:<line> admin-up' on every NDLT-F
# port of the fleet; stack bridge-port -> ethernet-line -> xdsl-channel -> xdsl-line).
_ALIASES = {("interfaces", "config", "xdsl_line"): ("ethernet-line:",)}


def context_reads(root):
    """The isam_read request for the planned types the card-type rules need."""
    card = card_of(*root)
    ids = ([card] if card else []) + ["nt-a", "nt-b"]
    return [{"kind": "configuration", "resource": "isam_equipment", "section": "slots", "ids": ids,
             "meta": {"refresh": REFRESH_VERSION, "context": True}}]


def context_from(read_results):
    """{"cards": {slot: planned type or None}, "nt": [planned types], "read": bool}.

    "read" is False unless a successful context read answered for every requested slot;
    a slot the device confirmed absent or that has no planned type maps to None.
    """
    context = {"cards": {}, "nt": [], "read": False}
    for result in read_results:
        if not (result.get("meta") or {}).get("context"):
            continue
        if result.get("status") not in ("ok", "partial") or result.get("unverified_ids"):
            # One failed context read: no partial context from the others either.
            return {"cards": {}, "nt": [], "read": False}
        data = result.get("data") or {}
        rows = data.get("slots", []) if isinstance(data, dict) else data
        planned = {row.get("id"): row.get("planned_type") for row in rows if isinstance(row, dict)}
        for slot in result.get("ids") or []:
            if slot.startswith("nt-"):
                if planned.get(slot):
                    context["nt"].append(planned[slot])
            else:
                context["cards"][slot] = planned.get(slot)
        context["read"] = True
    return context


def _rules(context, kind, identity):
    """(card rules or None, NT not-applicable sections) for the object."""
    if not context or not context.get("read"):
        return None, ()
    card = card_of(kind, identity)
    rules = CARD_TYPES.get(context["cards"].get(card)) if card else None
    nt = set()
    for planned in context.get("nt", ()):
        nt.update((NT_TYPES.get(planned) or {}).get("not_applicable", ()))
    return rules, tuple(sorted(nt))


def not_applicable(kind, identity, context):
    """{"resource.section" or child kind: reason} the rules exclude for this object."""
    rules, nt = _rules(context, kind, identity)
    out = {name: "system_not_applicable" for name in nt}
    if kind == "transceiver" and isinstance(identity, str) and identity.startswith("lt:"):
        out.update({name: "lt_transceiver_not_applicable" for name in LT_TRANSCEIVER_NOT_APPLICABLE})
    if rules is None:
        return out
    if kind == "transceiver":
        for name in rules.get("transceiver_not_applicable", ()):
            out.setdefault(name, "card_type_not_applicable")
    if kind == "card":
        for child in OBJECTS["card"]["children"]:
            if child not in rules["children"]:
                out[child] = "card_type_not_applicable"
        for resource, section, _decoder in applicable_sections("card"):
            name = "%s.%s" % (resource, section)
            if name not in rules["sections"]:
                out.setdefault(name, "card_type_not_applicable")
    if kind == "pon":
        for name in rules.get("pon_not_applicable", ()):
            out.setdefault(name, "card_type_not_applicable")
    if kind != "card":
        for name in rules.get("below_not_applicable", ()):
            out.setdefault(name, "card_type_not_applicable")
    return out


def context_gaps(root, context):
    """Gaps because the rules cannot be applied: context not read, or unknown types."""
    card = card_of(*root)
    if not card:
        return []
    if not context or not context.get("read"):
        return [{"kind": "card", "identity": card, "reason": "card_type_not_read"}]
    planned = context["cards"].get(card)
    gaps = []
    if planned not in CARD_TYPES:
        gaps.append({"kind": "card", "identity": card, "planned_type": planned, "reason": "card_type_unknown"})
    for nt in context.get("nt", ()):
        if nt not in NT_TYPES:
            gaps.append({"kind": "card", "identity": "nt", "planned_type": nt, "reason": "nt_type_unknown"})
    return gaps


def descendants(kind):
    """Object kinds below ``kind`` (OBJECTS children), breadth first, without ``kind``."""
    seen, queue = [], list(OBJECTS.get(kind, {}).get("children", []))
    while queue:
        child = queue.pop(0)
        if child not in seen:
            seen.append(child)
            queue.extend(OBJECTS.get(child, {}).get("children", []))
    return seen


def split_fresh(discovery_results, now=None, max_age_seconds=300, collected_since=None):
    """(usable, stale): successful results older than ``max_age_seconds``, dated in the
    future, or before ``collected_since`` (the refresh job's start) are stale and
    cannot establish children; failed results stay usable as failure evidence.
    Same rule as discovery.coverage()."""
    now = now or datetime.now(timezone.utc)
    if isinstance(now, str):
        now = _timestamp(now)
    since = _timestamp(collected_since) if collected_since is not None else None
    usable, stale = [], []
    for item in discovery_results:
        if item.get("status") == "ok":
            at = _timestamp(item.get("collected_at"))
            if ((now - at).total_seconds() > max_age_seconds or (at - now).total_seconds() > 5
                    or (since is not None and at < since)):
                stale.append(item)
                continue
        usable.append(item)
    return usable, stale


def _key(kind, identity):
    return (kind, tuple(identity) if isinstance(identity, list) else identity)


def _parent(item):
    """(kind, identity) of a discovery result's parent (discovery.result stores the
    node key, a JSON list)."""
    parent = item["parent"]
    return _key(*(json.loads(parent) if isinstance(parent, str) else parent))


def known_objects(root, discovery_results):
    """The root and every descendant reached through successful discovery results."""
    objects, frontier = [_key(*root)], [_key(*root)]
    by_parent = {}
    for item in discovery_results:
        if item.get("status") == "ok":
            by_parent.setdefault(_parent(item), []).append(item)
    while frontier:
        parent = frontier.pop(0)
        for item in by_parent.get(parent, ()):
            for child in item.get("children", ()):
                key = _key(item["child_kind"], child)
                if key not in objects:
                    objects.append(key)
                    frontier.append(key)
    return objects


def wanted_sections(sections):
    """None (everything) or the set of "resource.section" names a partial refresh asks for.

    A bare resource name stands for all its sections. Raises ValueError for a name the
    relations do not know.
    """
    if not sections:
        return None
    wanted = set()
    for name in sections:
        resource, _, section = str(name).partition(".")
        family = FAMILIES.get(resource)
        if family is None or (section and section not in family["sections"]):
            raise ValueError("unknown resource section %r" % (name,))
        wanted |= {"%s.%s" % (resource, s) for s in family["sections"]} if not section else {name}
    return wanted


def _traversed_kinds(root_kind, wanted):
    """Child kinds a partial refresh must enumerate: the kinds the wanted sections
    configure, and every kind on the way down to them. None: all."""
    if wanted is None:
        return None
    below = descendants(root_kind)
    targets = {kind for kind in [root_kind] + below
               if any("%s.%s" % (r, s) in wanted for r, s, _d in applicable_sections(kind))}
    return {kind for kind in below if kind in targets or targets & set(descendants(kind))}


def discovery_requests(root, discovery_results, context=None, sections=None):
    """Enumerations still needed for the objects known so far.

    Returns (requests, unimplemented): requests are {"kind", "identity",
    "child_kind", "read_scope"}; a relation without an adapter is listed in
    unimplemented (a capability gap, never an empty child list). A child kind the
    card-type rules exclude is neither (see not_applicable()). With ``sections``
    (a partial refresh) only the kinds those sections configure, and the kinds on
    the way down to them, are enumerated.
    """
    done = {(_parent(item), item["child_kind"]) for item in discovery_results}
    traversed = _traversed_kinds(root[0], wanted_sections(sections))
    requests, unimplemented = [], []
    for kind, identity in known_objects(root, discovery_results):
        excluded = not_applicable(kind, identity, context)
        for child_kind in OBJECTS.get(kind, {}).get("children", []):
            if ((kind, identity), child_kind) in done or child_kind in excluded:
                continue
            if traversed is not None and child_kind not in traversed:
                continue
            try:
                adapter = adapter_for(kind, child_kind, identity)
            except UnknownIdentity:
                unimplemented.append({"kind": kind, "identity": identity, "child_kind": child_kind})
                continue
            requests.append({"kind": kind, "identity": identity, "child_kind": child_kind,
                             "read_scope": adapter.get("read_scope"),
                             "evidence": evidence_for(kind, child_kind, identity)})
    return requests, unimplemented


def configuration_reads(objects, context=None, sections=None):
    """isam_read requests covering every applicable section of every object.

    One request per (resource, section) with the encoded ids; ``meta.objects`` maps
    each id to the objects it addresses (a bare user-port index can address a line
    and a bonding group at once: one read unit, both objects). Sections whose
    identity is composite beyond the object (e.g. a QoS queue) are returned in
    ``needs_enumeration``: they stay gaps until their sub-instances are known. With
    ``sections`` (a partial refresh) only those sections are read.
    """
    wanted = wanted_sections(sections)
    grouped, needs = {}, []
    for kind, identity in objects:
        excluded = not_applicable(kind, identity, context)
        for resource, section, decoder in applicable_sections(kind):
            if "%s.%s" % (resource, section) in excluded:
                continue
            if wanted is not None and "%s.%s" % (resource, section) not in wanted:
                continue
            field = (TARGETED_GATHER.get(resource) or {}).get(section)
            if not isinstance(field, str):
                needs.append({"resource": resource, "section": section, "kind": kind, "identity": identity,
                              "reason": "composite_identity_needs_enumeration"})
                continue
            entry = grouped.setdefault((resource, section), {})
            values = [encode(decoder, kind, identity)]
            values += [prefix + identity for prefix in _ALIASES.get((resource, section, kind), ())]
            for value in values:
                entry.setdefault(value, [])
                if [kind, identity] not in entry[value]:
                    entry[value].append([kind, identity])
    reads = [{"kind": "configuration", "resource": resource, "section": section, "ids": sorted(ids),
              "meta": {"refresh": REFRESH_VERSION, "objects": {value: ids[value] for value in sorted(ids)}}}
             for (resource, section), ids in sorted(grouped.items())]
    return reads, needs


def _profile_fields():
    from . import export_catalog
    return export_catalog()["profile_references"]


def reference_reads(read_results):
    """isam_read requests for the shared definitions present configuration refers to."""
    from .graph import _references
    fields = _profile_fields()
    profiles, other = set(), {}
    for result in read_results:
        data = result.get("data")
        if result.get("status") not in ("ok", "partial") or data in (None, [], {}):
            continue
        resource = result.get("resource")
        if fields.get(resource):
            for kind, name, _field in _references(data, fields[resource]):
                if kind and name:
                    profiles.add((kind, name))
        spec = (FAMILIES.get(resource) or {}).get("sections", {}).get(result.get("section") or "config", {})
        for option, target in (spec.get("references") or {}).items():
            for row in data if isinstance(data, list) else [data]:
                value = row.get(option) if isinstance(row, dict) else None
                if isinstance(value, str) and value and value != "none":
                    other.setdefault(target, set()).add(value[5:] if value.startswith("name:") else value)
    reads = []
    if profiles:
        reads.append({"kind": "configuration", "resource": "qos_profiles", "section": "config",
                      "ids": [{"profile_type": kind, "name": name} for kind, name in sorted(profiles)],
                      "meta": {"refresh": REFRESH_VERSION, "references": True}})
    for target, names in sorted(other.items()):
        resource, _, section = target.partition(".")
        reads.append({"kind": "configuration", "resource": resource, "section": section or "config",
                      "ids": sorted(names), "meta": {"refresh": REFRESH_VERSION, "references": True}})
    return reads


def pending_reference_reads(read_results):
    """reference_reads() minus the definitions already read.

    Definitions refer to further definitions (a scheduler-node profile to its shaper),
    so references resolve in rounds: run these reads, add their results, and call again
    until it returns nothing.
    """
    done = {}
    for result in read_results:
        if (result.get("meta") or {}).get("references"):
            done.setdefault((result.get("resource"), result.get("section") or "config"), []).extend(result.get("ids") or [])
    pending = []
    for read in reference_reads(read_results):
        ids = [value for value in read["ids"] if value not in done.get((read["resource"], read["section"]), [])]
        if ids:
            pending.append(dict(read, ids=ids))
    return pending


def _created_with(spec, objects, value):
    """Whether the device creates the entry ``value`` together with one of ``objects``."""
    for entry in spec.get("created_with", ()):
        prefix = entry.get("prefix")
        if any(kind == entry["object"] for kind, _identity in objects):
            if prefix is None or (isinstance(value, str) and value.startswith(prefix)):
                return True
    return False


def _object_existence(objects, raw, discovery_results):
    """{(kind, identity): "present" | "absent" | "conflict"} for the objects a refresh
    can decide.

    An object discovered as a child exists; its creating section (relations "creates":
    True, e.g. equipment_onts.interfaces for an ONT) says present or absent as read; an
    object whose creating section is a gap stays undecided. Evidence that disagrees
    (discovered, but its creating section confirmed absent: a race, or two sources that
    differ) is a "conflict", never resolved in favour of either side.
    """
    state = {}

    def note(key, value):
        if state.get(key, value) != value:
            state[key] = "conflict"
        else:
            state[key] = value

    for item in discovery_results:
        if item.get("status") == "ok":
            for child in item.get("children") or ():
                note((item["child_kind"], child if isinstance(child, str) else tuple(child)), "present")
    for read, value, status, _reason in raw:
        spec = FAMILIES[read["resource"]]["sections"][read["section"]]
        if not spec.get("creates") or status not in ("present", "absent"):
            continue
        for kind, identity in read["meta"]["objects"][value]:
            if kind == spec.get("object"):
                note((kind, identity if isinstance(identity, str) else tuple(identity)), status)
    return state


def _owner_state(spec, owners, value, existence):
    """"present" / "absent" / "conflict" / None: the state of the object the device
    creates the entry ``value`` with (see _created_with)."""
    for entry in spec.get("created_with", ()):
        prefix = entry.get("prefix")
        if prefix is not None and not (isinstance(value, str) and value.startswith(prefix)):
            continue
        for kind, identity in owners:
            if kind == entry["object"]:
                key = (kind, identity if isinstance(identity, str) else tuple(identity))
                if key in existence:
                    return existence[key]
    return None


def _created_with_card(context, read, value):
    """Whether the card-type rules say the device creates this entry with the card or
    with one of its transceivers."""
    for kind, identity in read["meta"]["objects"][value]:
        key = {"card": "created", "transceiver": "transceiver_created"}.get(kind)
        if key:
            rules, _nt = _rules(context, kind, identity)
            if rules and "%s.%s" % (read["resource"], read["section"]) in rules.get(key, ()):
                return True
    return False


def _classify(result, value):
    if result.get("status") == "error":
        return "gap", "read_%s" % (result.get("error") or "failed")
    if value in (result.get("returned_ids") or []):
        return "present", None
    if value in (result.get("confirmed_absent_ids") or []):
        return "absent", None
    for item in result.get("dependency_gaps") or ():
        if isinstance(item, dict) and item.get("id") == value and item.get("dependency_gap"):
            return "gap", "dependency_gap:%s" % item["dependency_gap"]
    return "gap", "unverified"


def _absent_lineage(owners, existence):
    """Whether one of ``owners``, or one of their physical ancestors, is proven absent.

    The walk up stops at the first object known to exist or in conflict: an absent
    ancestor above an object the device just showed is a conflict, not proof.
    """
    for kind, identity in owners:
        while kind is not None:
            key = (kind, identity if isinstance(identity, str) else tuple(identity))
            if existence.get(key) == "absent":
                return True
            if existence.get(key) in ("present", "conflict"):
                break
            try:
                kind, identity = parent_of(kind, identity) or (None, None)
            except (TypeError, ValueError, IndexError, AttributeError):
                break
    return False


def evaluate(root, discovery_results, read_results, now=None, max_age_seconds=300, collected_since=None,
             context=None, sections=None):
    """The refresh outcome of ``root`` from discovery and isam_read results.

    Every applicable (object, section) of every known object, and every referenced
    definition requested, must be ``present`` or ``absent``; every child relation of
    every known object must have a fresh successful enumeration, and a card's children
    of a counted kind must number what its type has. Anything else is a gap with a
    reason. ``complete`` is True only without gaps. The context comes from the
    context read among ``read_results`` unless given; what the card-type rules
    exclude is listed in ``not_applicable``, never as present or absent. With
    ``sections`` the evaluation covers only those sections (and the objects they need):
    ``complete`` then means complete for the question asked.
    """
    requested = wanted_sections(sections)
    if context is None:
        context = context_from(read_results)
    discovery_results, stale = split_fresh(discovery_results, now, max_age_seconds, collected_since)
    objects = known_objects(root, discovery_results)
    pending, missing_adapters = discovery_requests(root, discovery_results, context, sections)
    stale_relations = {(_parent(i), i["child_kind"]) for i in stale}
    gaps = [dict(item, reason="discovery_unimplemented") for item in missing_adapters]
    gaps += [dict({k: item[k] for k in ("kind", "identity", "child_kind")},
                  reason="discovery_stale" if (_key(item["kind"], item["identity"]), item["child_kind"]) in stale_relations
                  else "discovery_missing")
             for item in pending]
    gaps += [{"kind": _parent(item)[0], "identity": _parent(item)[1], "child_kind": item["child_kind"],
              "reason": "discovery_%s" % item.get("status")}
             for item in discovery_results if item.get("status") != "ok" and _parent(item) in objects]
    gaps += context_gaps(root, context)
    for item in discovery_results:
        parent = _parent(item)
        if item.get("status") != "ok" or parent not in objects or parent[0] != "card":
            continue
        rules, _nt = _rules(context, *parent)
        expected = (rules or {}).get("children", {}).get(item["child_kind"])
        if expected is not None and len(item.get("children") or ()) != expected:
            gaps.append({"kind": "card", "identity": parent[1], "child_kind": item["child_kind"],
                         "expected": expected, "found": len(item.get("children") or ()),
                         "reason": "population_mismatch"})
    wanted, needs = configuration_reads(objects, context, sections)
    results = {}
    for result in read_results:
        results.setdefault((result.get("resource"), result.get("section") or "config"), []).append(result)
    raw = []
    for read in wanted:
        got = results.get((read["resource"], read["section"]))
        for value in read["ids"]:
            if not got:
                status, reason = "gap", "not_read"
            else:
                status, reason = "gap", "unverified"
                for result in got:
                    if value in (result.get("ids") or []) or result.get("status") == "error":
                        status, reason = _classify(result, value)
                        if status != "gap":
                            break
            raw.append((read, value, status, reason))
    existence = _object_existence(objects, raw, discovery_results)
    sections = []
    for read, value, status, reason in raw:
        spec = FAMILIES[read["resource"]]["sections"][read["section"]]
        owners = read["meta"]["objects"][value]
        if reason == "unverified" and _created_with_card(context, read, value):
            # The card-type rules: the device creates this card entry with the card.
            status, reason = "present", None
        if reason == "unverified" and _created_with(spec, owners, value):
            owner = _owner_state(spec, owners, value, existence)
            if owner == "present":
                # The device creates this entry with its object, which exists; a
                # successful read that shows nothing of it means every value is the
                # device default (flat prints only values differing from the default).
                status, reason = "present", None
            elif owner == "absent":
                # Its object is proven absent, so is the entry it would carry
                # (live: 'interface port ont:<missing ONT>' answers the header only).
                status, reason = "absent", None
            elif owner == "conflict":
                status, reason = "gap", "conflicting_existence"
        if reason and reason.startswith("dependency_gap:") and _absent_lineage(owners, existence):
            # The device cannot resolve an object this entry hangs on (a bridge port of
            # a UNI whose ONT does not exist: "lower-interface does not exist"); that
            # object or an ancestor is proven absent, so the entry is absent too.
            status, reason = "absent", None
        if status != "present" and spec.get("observable", True) is False:
            # Accepted by the device but shown in no read: never confirmed absent.
            status, reason = "gap", "not_observable"
        for kind, identity in read["meta"]["objects"][value]:
            entry = {"kind": kind, "identity": identity, "resource": read["resource"],
                     "section": read["section"], "id": value, "status": status}
            if reason:
                entry["reason"] = reason
            sections.append(entry)
            if status == "gap":
                gaps.append(dict(entry))
    references = []
    done = {}
    for r in read_results:
        if (r.get("meta") or {}).get("references"):
            done.setdefault((r.get("resource"), r.get("section") or "config"), []).extend(r.get("ids") or [])
    for read in reference_reads(read_results):
        for value in read["ids"]:
            if value not in done.get((read["resource"], read["section"]), []):
                entry = {"resource": read["resource"], "section": read["section"], "id": value,
                         "status": "gap", "reason": "not_read"}
                references.append(entry)
                gaps.append(dict(entry))
    for result in read_results:
        if not (result.get("meta") or {}).get("references"):
            continue
        for value in result.get("ids") or []:
            status, reason = _classify(result, value)
            entry = {"resource": result.get("resource"), "section": result.get("section"), "id": value, "status": status}
            if reason:
                entry["reason"] = reason
                gaps.append(dict(entry))
            references.append(entry)
    gaps += [{"kind": kind, "identity": list(identity) if isinstance(identity, tuple) else identity,
              "reason": "conflicting_existence"}
             for (kind, identity), state in sorted(existence.items(), key=repr) if state == "conflict"]
    gaps += [dict(item) for item in needs]
    if requested is not None:
        # A requested section that configures nothing under the root is not a question
        # this refresh can answer: name it, so a wrong family name never reads as "done".
        kinds = [root[0]] + descendants(root[0])
        answerable = {"%s.%s" % (r, s) for kind in kinds for r, s, _d in applicable_sections(kind)}
        gaps += [{"section": name, "reason": "section_not_under_root"} for name in sorted(requested - answerable)]
    excluded = [{"kind": kind, "identity": identity, "name": name, "reason": why}
                for kind, identity in objects for name, why in sorted(not_applicable(kind, identity, context).items())]
    return {"refresh": REFRESH_VERSION, "root": list(_key(*root)), "complete": not gaps,
            "sections_requested": sorted(requested) if requested is not None else None,
            "objects": [list(key) for key in objects], "sections": sections,
            "references": references, "not_applicable": excluded, "gaps": deepcopy(gaps)}
