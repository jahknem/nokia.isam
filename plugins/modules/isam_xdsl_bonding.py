#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_xdsl_bonding
short_description: Manages XDSL bonding configuration on Nokia ISAM.
description:
  - Manages C(configure xdsl-bonding) configuration.
  - Writes the group-assembly-time setting.
  - Reads bonding groups and boards (C(gathered), C(parsed)); with C(state=gathered)
    and I(config) naming groups or boards only those are read, each with its own read
    outcome. Writing groups or boards is not supported yet and fails before any command.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: XDSL bonding configuration.
    type: dict
    suboptions:
      group_assembly_time:
        description: Group assembly time in milliseconds.
        type: int
      groups:
        description:
          - Bonding groups (C(configure xdsl-bonding group <line>)). Read only.
        type: list
        elements: dict
        suboptions:
          group_id:
            description: Group identity (the primary line, for example C(1/1/3/1)).
            type: str
            required: true
          group_profile:
            description: Bonding group profile; unset is the device default.
            type: str
          group_rtx_profile:
            description: Bonding group retransmission profile; unset is the device default.
            type: str
          up:
            description: Group administratively up.
            type: bool
      boards:
        description:
          - Bonding settings per board (C(configure xdsl-bonding board <board>)). Read only.
        type: list
        elements: dict
        suboptions:
          board_id:
            description: Board identity, for example C(1/1/3).
            type: str
            required: true
          vect_fallback:
            description: Vectoring fallback.
            type: bool
          group_profile:
            description: Default bonding group profile of the board.
            type: str
          group_rtx_profile:
            description: Default bonding group retransmission profile of the board.
            type: str
  running_config:
    description:
      - 'Native C(info configure xdsl-bonding flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the groups and boards named in I(config) are read from the device, selected by C(group_id) and C(board_id) (targeted gathering, with C(read_outcomes)). Without I(config) the whole resource is read.
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
    - Only C(confirmed_absent) is evidence the instance is gone -- the device's explicit
      "instance does not exist" about that instance, or a header-only reply to its
      C(flat detail) read (which prints every existing instance, also one with defaults
      only). C(unknown) (an invalid-token rejection, a missing dependency, another
      instance's line, a setting whose reads never show it, or a failed read) is never
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
  - With C(deleted) and I(running_config) (offline preview) it is the supplied configuration.
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
  - With C(deleted) and I(running_config) (offline preview of the removal) they are rendered only, never
    sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
  sample:
  - configure xdsl-bonding group-assembly-time 50
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
