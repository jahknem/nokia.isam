#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_qos_maps
version_added: 1.0.0
short_description: Manage QoS maps on Nokia ISAM devices
description:
- Manage QoS mapping tables on Nokia ISAM devices.
- Supports C(tc-map-dot1p), C(dscp-map-dot1p), C(up-ctrl-pkt), and C(dn-ctrl-pkt) sub-families.
author: Jan Kuehnemund
notes:
- Tested against read-only output from Nokia ISAM 6.2.04ng.
options:
  config:
    type: dict
    description: QoS maps configuration.
    suboptions:
      tc_map_dot1p:
        type: list
        elements: dict
        description: List of 802.1p to traffic-class mappings.
        suboptions:
          dot1p:
            type: int
            description: 802.1p priority value (0-7).
            required: true
          tc:
            type: int
            description: Traffic class index.
      dscp_map_dot1p:
        type: list
        elements: dict
        description: List of DSCP to 802.1p mappings.
        suboptions:
          dscp:
            type: str
            description: DSCP value (numeric or name like C(CS0), C(EF), etc.).
            required: true
          dot1p:
            type: int
            description: 802.1p priority value.
      up_ctrl_pkt:
        type: list
        elements: dict
        description: List of upstream control-packet classifications.
        suboptions:
          protocol:
            type: str
            description: Protocol name (e.g. C(arp), C(dhcp), C(pppoe)).
            required: true
          queue:
            type: int
            description: Queue index.
          profile:
            type: str
            description: Profile name.
      dn_ctrl_pkt:
        type: list
        elements: dict
        description: List of downstream control-packet classifications.
        suboptions:
          protocol:
            type: str
            description: Protocol name.
            required: true
          queue:
            type: int
            description: Queue index.
          profile:
            type: str
            description: Profile name.
  running_config:
    type: str
    description: Output from C(info configure qos), used with state C(parsed).
  state:
    description: Desired resource state.
    type: str
    default: merged
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
"""

EXAMPLES = """
- name: Gather QoS maps
  nokia.isam.isam_qos_maps:
    state: gathered

- name: Render tc-map-dot1p entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      tc_map_dot1p:
        - dot1p: 0
          tc: 0
        - dot1p: 7
          tc: 7

- name: Render dscp-map-dot1p entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      dscp_map_dot1p:
        - dscp: CS0
          dot1p: 0
        - dscp: EF
          dot1p: 5

- name: Render control-packet entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      up_ctrl_pkt:
        - protocol: dhcp
          queue: 0
          profile: default
      dn_ctrl_pkt:
        - protocol: dhcp
          queue: 0
          profile: default
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
  description: Gathered structured QoS maps data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured QoS maps data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_maps.qos_maps import (
    Qos_mapsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_maps.qos_maps import (
    Qos_maps,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_mapsArgs.argument_spec,
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
    result = Qos_maps(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
