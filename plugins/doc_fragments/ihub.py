"""Shared contract for explicitly requested, read-only IHUB resources."""


class ModuleDocFragment:
    DOCUMENTATION = r"""
options:
  state:
    description:
      - Read live configuration with C(gathered), or parse supplied hierarchical configuration offline with C(parsed).
      - This module does not implement mutating or rendered states.
    type: str
    choices: [gathered, parsed]
    default: gathered
  running_config:
    description:
      - Native hierarchical output, required for C(state=parsed).
      - Flat access-side configuration is not an IHUB source and is rejected.
    type: str
  allow_broad_read:
    description:
      - Permit a device-wide hierarchical root source when no narrower read has been verified.
      - Also required when I(config) selects instances, because selection filters a whole-source read rather than issuing scoped CLI reads.
      - Actual source breadth is always returned in C(source.read_scope).
    type: bool
    default: false
notes:
  - These resources are explicit opt-in modules, not implicitly added to C(isam_facts) all-resource or shared-flat gathering.
  - I(config) is an instance selection, not configuration; it accepts only the identity keys.
  - Unknown commands are reported in C(coverage.unparsed), without their potentially sensitive values.
  - C(coverage.complete) means all syntax in the selected source family was modeled, not that the whole device configuration is covered.
  - Unsupported, blank, malformed or incomplete sources fail rather than confirming an empty family.
  - The modules never change the device, so check mode reads and parses exactly like a normal run.
"""
