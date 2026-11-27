"""Configuration scope classification for resource sections.

Not all configuration belongs to a physical descendant subtree. This catalog
classifies every TARGETED_GATHER section into one of three scopes so consumers
know where it belongs and never attach it to a guessed physical parent:

* ``object_owned``: instance configuration owned by a physical object (its section
  names an "object" in relations/<family>.py). Recursive refresh reads it per descendant.
* ``device_global``: device-wide settings with no physical owner (system,
  security, software, alarms, traps, global QoS maps, ...). A full-MSAN refresh
  reads it once; a scoped subtree refresh does not claim it.
* ``shared_profile``: named definitions referenced by object configuration
  (xDSL/QoS/voice profiles). Read once and deduplicated; following a reference
  must not pull in the profile's other consumers.

This is a classification, not a parent/child edge. It is declared per section in
relations/<family>.py ("scope"); a section naming an "object" is ``object_owned``
unless it is explicitly a shared definition. The tables below are views of those
declarations. A section with neither is an unclassified gap, never silently
device-global.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.relations import FAMILIES




def _sections_with_scope(scope):
    found = {}
    for resource, family in FAMILIES.items():
        sections = tuple(name for name, section in family["sections"].items() if section.get("scope") == scope)
        if sections:
            found[resource] = sections
    return found


# resource -> sections. object_owned is derived from the object bindings.
DEVICE_GLOBAL = _sections_with_scope("device_global")
SHARED_PROFILE = _sections_with_scope("shared_profile")

# Sections owned by a physical object but not yet bound to a decoder. Classified
# object_owned so they are not mistaken for device-global; the missing binding
# remains an explicit gap until a decoder is added. Empty: every such section is
# bound today. The mechanism stays for evidence-gated additions.
OBJECT_OWNED_PENDING = {}

# Families that are one device-wide settings block without instance lists.
# Explicit ownership, not a default for unrecognized families.
GLOBAL_RESOURCES = tuple(sorted(resource for resource, family in FAMILIES.items() if not family["sections"]))

# Device-wide scalar settings in otherwise instance-oriented families. Unlisted
# settings remain gaps; global ownership is never inferred from a scalar type.
GLOBAL_SETTINGS = {resource: tuple(family["settings"]) for resource, family in FAMILIES.items() if family.get("settings")}


def section_scopes(bindings):
    """{(resource, section): scope} for every classified section.

    bindings is the catalog's binding list (resource/section/identity/decoder).
    Explicit shared definitions retain that scope even when they have a decoder.
    Physical bindings imply object_owned. A physical binding also listed as
    device-global is an error, not a silent override.
    """
    scopes = {}
    profiles = {(resource, section) for resource, sections in SHARED_PROFILE.items() for section in sections}
    for binding in bindings:
        key = (binding["resource"], binding["section"])
        # A definition can have a decoder without becoming physical hardware.
        scopes[key] = "shared_profile" if key in profiles else "object_owned"
    for resource, sections in DEVICE_GLOBAL.items():
        for section in sections:
            key = (resource, section)
            if key in scopes:
                raise ValueError("Section %s.%s is both object-owned and device-global" % key)
            scopes[key] = "device_global"
    for resource, sections in SHARED_PROFILE.items():
        for section in sections:
            key = (resource, section)
            if key in scopes and scopes[key] != "shared_profile":
                raise ValueError("Section %s.%s is both object-owned and shared-profile" % key)
            scopes[key] = "shared_profile"
    for resource, sections in OBJECT_OWNED_PENDING.items():
        for section in sections:
            key = (resource, section)
            if key in scopes:
                raise ValueError("Section %s.%s is both bound and pending object-owned" % key)
            scopes[key] = "object_owned"
    return scopes
