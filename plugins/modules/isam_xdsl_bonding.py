#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_xdsl_bonding
short_description: Manages XDSL bonding configuration on Nokia ISAM.
description:
  - Manages C(configure xdsl-bonding) configuration.
  - Currently supports group-assembly-time settings.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: XDSL bonding configuration.
    type: dict
    suboptions:
      group_assembly_time:
        description:
          - Maximum time for a bonding group to become operational (C(group-assembly-time)), in seconds per the CLI
            reference (0-65535, 0 waits until all lines are up).
        type: int
      ptm_init_mode:
        description:
          - PTM bonding group initialization mode (C(group-assembly-time <sec> ptm-init-mode <mode>)).
          - The CLI sets it as a parameter of the C(group-assembly-time) command, so the module repeats the assembly
            time (from I(group_assembly_time), else the device value, else C(0)); reset with
            C(group-assembly-time <sec> no ptm-init-mode). Syntax from the CLI reference, not verified on a device.
          - The device default C(mode1) is not reported and equals an absent value. Bonding groups configured
            before a change need an NT reset to use the new mode.
        type: str
        choices: [mode1, mode2]
      groups:
        description:
          - Bonding groups (C(configure xdsl-bonding group <bonding-group-idx>)).
          - Detail output lists every group with defaults; only groups with a non-default attribute are reported.
          - Each attribute is set with C(group <idx> <attr> <value>) / C(group <idx> up) and reset with
            C(group <idx> no <attr>). Syntax from the CLI reference, not verified on a device.
          - Links of a group (C(group <idx> link <link-id>)) are not modelled and are left unchanged.
        type: list
        elements: dict
        suboptions:
          group_id:
            description: Bonding group index, for example C(1/1/3/1).
            type: str
            required: true
          group_profile:
            description: Bonding group profile, an index or C(name:<name>); device default C(none) (not reported).
            type: str
          group_rtx_profile:
            description: Bonding group RTX profile, an index or C(name:<name>); device default C(none) (not reported).
            type: str
          up:
            description: Administrative state up (C(up)); C(no up) is the default and not reported.
            type: bool
      boards:
        description:
          - Per-board bonding settings (C(configure xdsl-bonding board <board-index>)).
          - Only boards with a non-default vectoring fallback attribute are reported.
        type: list
        elements: dict
        suboptions:
          board_id:
            description: Board index, for example C(1/1/3).
            type: str
            required: true
          vect_fallback:
            description:
              - Profiles used when a bonding group enters vectoring fallback mode
                (C(board <board-index> vect-fallback [no] group-profile|group-rtx-profile)).
              - Syntax from the CLI reference, not verified on a device.
            type: dict
            suboptions:
              group_profile:
                description: Fallback group profile, C(group-level), an index or C(name:<name>); device default C(group-level) (not reported).
                type: str
              group_rtx_profile:
                description: Fallback group RTX profile, C(none), C(group-level), an index or C(name:<name>); device default C(group-level) (not reported).
                type: str
  running_config:
    description:
      - 'Device-native running configuration for parsed state.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device,
        selected by C(boards[].board_id) and C(groups[].group_id) (targeted gathering). Other fields
        are ignored and absent instances are not returned; an instance with nothing configured answers
        like an absent one and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather XDSL bonding config
  nokia.isam.isam_xdsl_bonding:
    state: gathered

- name: Set group assembly time
  nokia.isam.isam_xdsl_bonding:
    config:
      group_assembly_time: 50
    state: merged

- name: Render XDSL bonding config
  nokia.isam.isam_xdsl_bonding:
    config:
      group_assembly_time: 50
    state: rendered

- name: Assign a bonding group profile and bring the group up
  nokia.isam.isam_xdsl_bonding:
    config:
      groups:
        - group_id: 1/1/3/1
          group_profile: "1"
          up: true
      boards:
        - board_id: 1/1/3
          vect_fallback:
            group_profile: "2"
    state: merged
# - configure xdsl-bonding group 1/1/3/1 group-profile 1
# - configure xdsl-bonding group 1/1/3/1 up
# - configure xdsl-bonding board 1/1/3 vect-fallback group-profile 2

- name: Read only the named groups and boards (targeted gathering, once enabled for xdsl_bonding)
  nokia.isam.isam_xdsl_bonding:
    config:
      groups:
        - group_id: 1/1/3/1
    state: gathered
"""

RETURN = """
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(failed) or C(unverified)) is reported at resource level under
      C(parse); C(failed) means the family parser could not process the reply,
      C(unverified) that no parser records its coverage of the reply (a read never claims
      a complete parse).
    - A named instance the device rejected (C(invalid token)) is missing from C(gathered)
      exactly like an absent one; the module also warns, naming the rejected selectors.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_bonding.xdsl_bonding import (
    Xdsl_bondingArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_bonding.xdsl_bonding import (
    Xdsl_bonding,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_bondingArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Xdsl_bonding(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
