#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_vlan_global
short_description: Manages global VLAN configuration on Nokia ISAM.
description:
  - Manages global C(configure vlan) resources including broadcast-frames, priority-regen, tpid, and vmac-address-format.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: VLAN global configuration.
    type: dict
    suboptions:
      broadcast_frames:
        description: Broadcast frames configuration.
        type: dict
        suboptions:
          drop_unknown_multicast:
            description: Drop unknown multicast frames.
            type: bool
          priority_policy:
            description:
              - Node-level priority policy for broadcast frames,
                C(configure vlan broadcast-frames priority-policy <value>) (for example C(vlan-specific) or
                C(port-default)).
              - C(no priority-policy) on the device is not reported. I(state=replaced), I(state=overridden) and
                I(state=deleted) reset it with C(configure vlan broadcast-frames no priority-policy)
                (reset form from the CLI syntax, not yet verified on a device).
            type: str
      priority_regen:
        description:
          - Priority regeneration profiles, device form
            C(configure vlan priority-regen <id> profile-name <name> pbit0 <v> ... pbit7 <v>).
          - Only the attributes given are rendered; with I(state=replaced) attributes omitted from an entry are not
            reset on the device.
          - Removal (I(state=deleted)/I(state=overridden)) renders C(configure vlan no priority-regen <id>).
        type: list
        elements: dict
        suboptions:
          id:
            description: Priority regeneration profile index.
            type: int
            required: true
          profile_name:
            description: 'Name of the priority regeneration profile (C(profile-name)); mandatory at creation.'
            type: str
          pbit0:
            description: Regenerated priority for incoming p-bit 0.
            type: int
          pbit1:
            description: Regenerated priority for incoming p-bit 1.
            type: int
          pbit2:
            description: Regenerated priority for incoming p-bit 2.
            type: int
          pbit3:
            description: Regenerated priority for incoming p-bit 3.
            type: int
          pbit4:
            description: Regenerated priority for incoming p-bit 4.
            type: int
          pbit5:
            description: Regenerated priority for incoming p-bit 5.
            type: int
          pbit6:
            description: Regenerated priority for incoming p-bit 6.
            type: int
          pbit7:
            description: Regenerated priority for incoming p-bit 7.
            type: int
      tpid:
        description: TPID configuration.
        type: dict
        suboptions:
          value:
            description: TPID value.
            type: str
            choices: ["8100", "9100", "88a8", "9200"]
      vmac_address_format:
        description: VMAC address format configuration.
        type: dict
        suboptions:
          format:
            description: VMAC address format.
            type: str
            choices: ["canonical", "non-canonical", "host-id"]
          host_id:
            description: Host ID used with I(format=host-id).
            type: int
  running_config:
    description:
      - 'Device-native running configuration for parsed state.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), the device exposes no single-instance read for the
        priority-regen profiles, so the whole vlan node is read once and each named profile is
        reported in C(read_outcomes) as C(present) when the parsed catalog lists it and
        C(unknown) when it does not (C(confirmed_absent) only when the device says the node
        itself does not exist); I(gathered) stays the full catalog. Without I(config) the
        whole resource is read, as before.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather VLAN global config
  nokia.isam.isam_vlan_global:
    state: gathered

- name: Read only the named priority-regen profiles (targeted gathering)
  nokia.isam.isam_vlan_global:
    state: gathered
    config:
      priority_regen:
        - id: 11

- name: Render VLAN global config
  nokia.isam.isam_vlan_global:
    state: rendered
    config:
      broadcast_frames:
        drop_unknown_multicast: true
      priority_regen:
        - id: 11
          profile_name: Custom
          pbit0: 0
          pbit1: 0
          pbit2: 2
          pbit3: 2
          pbit4: 4
          pbit5: 4
          pbit6: 6
          pbit7: 6
      tpid:
        value: "8100"
      vmac_address_format:
        format: canonical

- name: Merge VLAN global config
  nokia.isam.isam_vlan_global:
    state: merged
    config:
      broadcast_frames:
        drop_unknown_multicast: true
      tpid:
        value: "88a8"
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
  version_added: 1.0.0
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlan_global.vlan_global import (
    Isam_vlan_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.vlan_global.vlan_global import (
    Isam_vlan_global,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_vlan_globalArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Isam_vlan_global(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
