"""Prove missing-owner reads absent through the shared object/section model.

A missing dependency is not itself an absence proof. Read an authoritative section
of its containment lineage, by exact identity, and require a confirmed absence.
Present or contradictory evidence stops the walk. All evidence belongs to one read
batch; nothing cached from a previous run is used.
"""

import time

from ..relations import FAMILIES
from ..targeted import TARGETED_GATHER, absence_policy
from .identity import UnknownIdentity, decode, parent_of
from .objects import OBJECTS
from .refresh import NotEncodable, encode


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _key(kind, identity):
    return kind, tuple(identity) if isinstance(identity, (list, tuple)) else identity


def _spec(resource, section):
    return FAMILIES.get(resource, {}).get("sections", {}).get(section, {})


def _defines(spec, kind, value):
    if spec.get("creates") and spec.get("object") == kind:
        return True
    return any(entry["object"] == kind and
               (entry.get("prefix") is None or isinstance(value, str) and value.startswith(entry["prefix"]))
               for entry in spec.get("created_with", ()))


def _objects(result):
    """Direct present/absent object evidence, never an arbitrary section's absence."""
    if result.get("kind") != "configuration" or result.get("status") != "ok":
        return
    resource, section = result["resource"], result.get("section") or "config"
    spec = _spec(resource, section)
    decoder = spec.get("object")
    if not decoder:
        return
    for field, state in (("returned_ids", "present"), ("confirmed_absent_ids", "absent")):
        for value in result.get(field) or ():
            try:
                kind, identity = decode(decoder, value)
            except (UnknownIdentity, TypeError, ValueError):
                continue
            if state == "absent" and not _defines(spec, kind, value):
                continue
            yield _key(kind, identity), state, {
                "kind": kind, "identity": identity, "resource": resource, "section": section, "id": value,
            }


def _lineage(kind, identity):
    """Only declared containment edges; not a string-prefix ancestry guess."""
    seen = set()
    while _key(kind, identity) not in seen:
        seen.add(_key(kind, identity))
        yield kind, identity
        parent = parent_of(kind, identity)
        if parent is None:
            return
        children = OBJECTS.get(parent[0], {}).get("children", ())
        if not isinstance(children, (list, tuple)) or kind not in children:
            return
        kind, identity = parent


def _source(kind, identity):
    """One exact authoritative existence read, selected from relation data.

    The section that creates the object is preferred; a section whose entries the
    device creates with the object is the fallback."""
    candidates = []
    for resource, family in sorted(FAMILIES.items()):
        if family.get("source") == "ihub":
            continue
        targeted = TARGETED_GATHER.get(resource, {})
        if not isinstance(targeted, dict):
            continue
        for section, spec in sorted(family["sections"].items()):
            if section not in targeted:
                continue
            if "kinds" in spec and kind not in spec["kinds"]:
                continue
            try:
                value = encode(spec.get("object"), kind, identity)
            except (NotEncodable, TypeError, ValueError):
                continue
            if _defines(spec, kind, value) and absence_policy(resource, section) != "unobservable":
                creates = bool(spec.get("creates")) and spec.get("object") == kind
                candidates.append((0 if creates else 1, resource, section, value))
    if not candidates:
        return None
    _rank, resource, section, value = min(candidates)
    return {"kind": "configuration", "resource": resource, "section": section, "ids": [value]}


def resolve_owner_absence(results, read):
    """Refine dependency gaps in-place; ``read(request)`` executes an isolated proof read.

    Auxiliary reads are bounded to one per distinct owner/source and reused in this
    batch. Public results keep their original order and requested scope. Neither a
    missing row, a rejected read nor a failed proof read can erase cached data.
    """
    evidence, attempted, lineages = {}, set(), {}

    def contradicted(ancestor):
        """Whether present (or conflicting) evidence exists for the ancestor or anything
        it contains: a shown child, sibling or descendant means the ancestor exists."""
        for obj, (state, proof) in evidence.items():
            if state == "absent":
                continue
            if obj not in lineages:
                try:
                    lineages[obj] = set(_key(k, i) for k, i in _lineage(*obj))
                except (UnknownIdentity, TypeError, ValueError, IndexError):
                    lineages[obj] = set([obj])
            if ancestor in lineages[obj]:
                return True
        return False

    def note(result):
        for obj, state, proof in _objects(result):
            previous = evidence.get(obj)
            if previous and previous[0] != state:
                evidence[obj] = ("conflict", None)
            elif previous is None:
                evidence[obj] = state, proof

    for result in results:
        note(result)
        if result.get("kind") == "configuration":
            for value in result.get("ids") or ():
                if isinstance(value, str):
                    attempted.add((result["resource"], result.get("section") or "config", value))

    for result in results:
        if result.get("status") != "ok":
            continue
        spec = _spec(result["resource"], result.get("section") or "config")
        if spec.get("observable", True) is False or absence_policy(result["resource"], result.get("section") or "config") == "unobservable":
            continue
        remaining = []
        for gap in result.get("dependency_gaps") or ():
            value, proof = gap.get("id"), None
            if value not in result.get("unverified_ids", ()) or value in result.get("confirmed_absent_ids", ()):
                remaining.append(gap)
                continue
            try:
                owner = decode(spec.get("object"), value)
                lineage = list(_lineage(*owner))
            except (UnknownIdentity, TypeError, ValueError, IndexError):
                remaining.append(gap)
                continue
            for kind, identity in lineage:
                obj = _key(kind, identity)
                state = evidence.get(obj)
                # The failed section itself cannot serve as its own proof.
                request = _source(kind, identity)
                if state is None and request is not None:
                    source = (request["resource"], request["section"], request["ids"][0])
                    if source not in attempted:
                        attempted.add(source)
                        answer = read(request)
                        note(answer)
                        if answer.get("status") != "ok":
                            break
                        state = evidence.get(obj)
                if state:
                    if state[0] == "absent" and not contradicted(obj):
                        proof = state[1]
                    break  # present/conflict (here or below) block an absent ancestor
            if proof is None:
                remaining.append(gap)
            else:
                result["unverified_ids"] = [item for item in result["unverified_ids"] if item != value]
                result["confirmed_absent_ids"].append(value)
                result.setdefault("absence_evidence", []).append({"id": value, "owner": proof, "checked_at": _now()})
        if "dependency_gaps" in result:
            result["dependency_gaps"] = remaining
