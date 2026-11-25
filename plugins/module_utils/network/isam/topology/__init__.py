"""Versioned Nokia object relationships. No CLI execution or Ansible dependency.

The catalog is derived: relations/<family>.py says what each family addresses,
creates, references and requires; objects.py says which device objects exist
and what they contain. Unmapped syntax/identities never acquire a guessed owner.
"""

from copy import deepcopy

from ..relations import FAMILIES
from ..targeted import TARGETED_GATHER
from . import ihub, scopes
from .objects import OBJECTS

SCHEMA_VERSION = 1


def export_catalog():
    """JSON-compatible direct neighbors and resource bindings for consumers."""
    bindings = []
    for resource, family in sorted(FAMILIES.items()):
        for section, spec in family["sections"].items():
            if "object" not in spec:
                continue
            if family.get("source") == "ihub":
                bindings.append({"resource": resource, "section": section, "identity": deepcopy(spec["identity"]),
                                 "decoder": spec["object"], "read_scope": "all"})
            else:
                bindings.append({"resource": resource, "section": section,
                                 "identity": TARGETED_GATHER[resource][section], "decoder": spec["object"]})
    objects = deepcopy(OBJECTS)
    for obj in objects.values():
        obj["parents"] = []
    for kind, obj in objects.items():
        for child in obj["children"]:
            objects[child]["parents"].append(kind)
    # Per-child discovery availability, derived from the actual adapters so the
    # catalog and coverage certificate cannot drift. A child relation is
    # "implemented" only when an enumeration adapter exists for it.
    from .discovery import ENUMERATION, SOURCES, evidence_for
    for kind, obj in objects.items():
        discovery = {
            child: ("implemented" if (kind, child) in ENUMERATION or kind in SOURCES.get(child, {}).get("parents", ())
                    else "unimplemented")
            for child in obj["children"]
        }
        obj["discovery"] = discovery
        # Validation provenance is separate from availability: an implemented
        # adapter may be live-verified or only documented. Consumers must not
        # equate "implemented" with "verified on a device".
        obj["discovery_evidence"] = {child: evidence_for(kind, child) for child in obj["children"]
                                     if discovery[child] == "implemented"}
        availability = set(discovery.values())
        obj["status"] = ("leaf" if not availability else "implemented" if availability == {"implemented"}
                         else "partial" if "implemented" in availability else "unimplemented")
    # Rack-less controller IDs (nt-a/nt-b) do not encode a shelf. They attach to
    # the device, not an invented shelf 1/1. The instance decoder expresses this.
    section_scope = scopes.section_scopes(bindings)
    unclassified = ["%s.%s" % (resource, section)
                    for resource, sections in sorted(TARGETED_GATHER.items())
                    for section in sections
                    if (resource, section) not in section_scope]
    bound = {(binding["resource"], binding["section"]): binding for binding in bindings}
    models = {}
    for (resource, section), scope in sorted(section_scope.items()):
        binding = bound.get((resource, section))
        if binding:
            model = {"scope": scope, "model": "decoded_object", "decoder": binding["decoder"]}
            if binding.get("read_scope"):
                model["read_scope"] = binding["read_scope"]
        elif scope == "device_global":
            model = {"scope": scope, "model": "device_settings", "owner": "msan", "read_scope": "all"}
        elif scope == "shared_profile":
            model = {"scope": scope, "model": "shared_definition", "owner": "msan",
                     "identity": TARGETED_GATHER[resource][section]}
        else:
            model = {"scope": scope, "model": "unimplemented", "reason": "object_binding_missing"}
        models["%s.%s" % (resource, section)] = model
    # Option name -> profile type, for the families whose options name profiles.
    profile_references = {resource: dict(FAMILIES[family["profile_references"]]["reference_fields"])
                          for resource, family in sorted(FAMILIES.items()) if family.get("profile_references")}
    typed_references, creates, created_with, requires = [], {}, [], []
    for resource, family in sorted(FAMILIES.items()):
        for section, spec in family["sections"].items():
            for field, target in spec.get("references", {}).items():
                target_resource, target_section = target.split(".", 1)
                typed_references.append({"resource": resource, "section": section, "field": field,
                                         "target_resource": target_resource, "target_section": target_section})
            # The command of this section creates the object; every other family
            # addressing the kind configures an existing one.
            if spec.get("creates"):
                if spec["object"] in creates:
                    raise ValueError("Two sections create object kind %s" % spec["object"])
                creates[spec["object"]] = {"resource": resource, "section": section}
            # Entries the device creates itself with an object, at these defaults.
            for entry in spec.get("created_with", ()):
                created_with.append({"resource": resource, "section": section, "identity": spec["identity"],
                                     "prefix": entry["prefix"], "object": entry["object"],
                                     "default": deepcopy(entry["default"])})
            # Sections that must be written before this one (and removed after it).
            for need in spec.get("requires", ()):
                target_resource, target_section = need["section"].split(".", 1)
                if target_section not in FAMILIES[target_resource]["sections"]:
                    raise ValueError("%s.%s requires the unknown section %s" % (resource, section, need["section"]))
                requires.append({"resource": resource, "section": section,
                                 "target_resource": target_resource, "target_section": target_section,
                                 "target_kind": need.get("kind"), "evidence": need["evidence"]})
    return {"schema_version": SCHEMA_VERSION, "bindings": deepcopy(bindings), "objects": objects,
            "relationships_exhaustive": False,
            # TARGETED_GATHER covers access-side resource families, not every
            # configuration namespace supported by the device's separate CLI
            # parsers. Fully binding its sections does not close these domains.
            "unmodeled_configuration_domains": ["ihub_router", "ihub_qos", "ihub_system_security", "ihub_other_domains"],
            "partial_configuration_domains": ["ihub_ports", "ihub_lags", "ihub_services"],
            "configuration_read_capabilities": deepcopy(ihub.READ_CAPABILITIES),
            "profile_references": profile_references,
            "typed_references": typed_references,
            "creates": creates,
            "created_with": created_with,
            "requires": requires,
            "global_resources": list(scopes.GLOBAL_RESOURCES),
            "global_settings": deepcopy(scopes.GLOBAL_SETTINGS),
            "section_scopes": {"%s.%s" % key: value for key, value in sorted(section_scope.items())},
            "section_models": models,
            "unbound_object_sections": sorted(key for key, model in models.items() if model["model"] == "unimplemented"),
            "relations": {
                "contains": {"meaning": "direct_physical_or_interface_parent", "recursive": True},
                "owns": {"meaning": "device_owns_settings_or_definition", "recursive": "full_msan_only"},
                "configures": {"meaning": "read_unit_supplies_object_configuration", "traversal": "reverse"},
                "candidate_owner": {"meaning": "configuration_may_belong_to_object_ownership_unresolved",
                                    "traversal": "reverse_include_config_only"},
                "references": {"meaning": "configuration_references_shared_definition", "traversal": "forward_only"},
                "member_of": {"meaning": "port_membership_in_logical_aggregation", "recursive": False},
            },
            "unclassified_sections": unclassified,
            "unmapped_sections": ["%s.%s" % (resource, section)
                                  for resource, sections in sorted(TARGETED_GATHER.items())
                                  for section in sections
                                  if not any(b["resource"] == resource and b["section"] == section for b in bindings)]}
