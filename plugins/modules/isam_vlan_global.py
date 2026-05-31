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
author: Jan Kuehnemund
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
      priority_regen:
        description: Priority regeneration table entries.
        type: list
        elements: dict
        suboptions:
          dot1p:
            description: Incoming 802.1p priority value.
            type: int
            required: true
          regen_dot1p:
            description: Regenerated 802.1p priority value.
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
            choices: ["canonical", "non-canonical"]
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: Desired resource state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather VLAN global config
  nokia.isam.isam_vlan_global:
    state: gathered

- name: Render VLAN global config
  nokia.isam.isam_vlan_global:
    state: rendered
    config:
      broadcast_frames:
        drop_unknown_multicast: true
      priority_regen:
        - dot1p: 0
          regen_dot1p: 0
        - dot1p: 1
          regen_dot1p: 1
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
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured VLAN global data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured VLAN global data.
  returned: when state is parsed
  type: dict
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
        mutually_exclusive=[["config", "running_config"]],
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
