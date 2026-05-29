#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_equipment_onts
short_description: Manages equipment ONT configuration on Nokia ISAM.
description:
  - Manages C(configure equipment ont) interface, slot, and software control entries.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    type: dict
    description: Equipment ONT configuration.
    suboptions:
      interfaces:
        description: ONT interface entries.
        type: list
        elements: dict
        suboptions:
          ont_idx:
            description: ONT interface index.
            type: str
            required: true
          sw_ver_pland:
            description: Planned software version mode.
            type: str
          sernum:
            description: ONT serial number.
            type: str
          subslocid:
            description: Subscriber location ID.
            type: str
          fec_up:
            description: Upstream FEC setting.
            type: str
          sw_dnload_version:
            description: Software download version mode.
            type: str
          plnd_var:
            description: Planned ONT variant.
            type: str
          enable_aes:
            description: AES enable setting.
            type: str
          log_auth_pwd:
            description: Logical authentication password.
            type: str
          cvlantrans_mode:
            description: C-VLAN translation mode.
            type: str
          planned_us_rate:
            description: Planned upstream rate.
            type: str
          admin_state:
            description: Administrative state.
            type: str
            choices: [up, down]
      slots:
        description: ONT slot entries.
        type: list
        elements: dict
        suboptions:
          ont_slot_idx:
            description: ONT slot index.
            type: str
            required: true
          planned_card_type:
            description: Planned card type.
            type: str
          plndnumdataports:
            description: Planned number of data ports.
            type: int
          plndnumvoiceports:
            description: Planned number of voice ports.
            type: int
          port_type:
            description: Port type.
            type: str
          transp_mode_rem:
            description: Transparent mode remote setting.
            type: str
          no_mcast_control:
            description: Multicast control setting.
            type: str
          admin_state:
            description: Administrative state.
            type: str
            choices: [up, down]
      sw_ctrls:
        description: ONT software control entries.
        type: list
        elements: dict
        suboptions:
          sw_ctrl_id:
            description: Software control ID.
            type: int
            required: true
          hw_version:
            description: Hardware version match.
            type: str
          ont_variant:
            description: ONT variant.
            type: str
          plnd_sw_version:
            description: Planned software version.
            type: str
          plnd_sw_ver_conf:
            description: Planned software version confirmation.
            type: str
          sw_dwload_ver:
            description: Software download version.
            type: str
  running_config:
    description: Device-native running configuration to parse.
    type: str
  state:
    description: Module state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather equipment ONTs
  nokia.isam.isam_equipment_onts:
    state: gathered

- name: Render an ONT interface
  nokia.isam.isam_equipment_onts:
    state: rendered
    config:
      interfaces:
        - ont_idx: 1/1/5/1/1
          sw_ver_pland: auto
          sernum: ALCL:F9772423
          admin_state: up
"""

RETURN = """
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import (
    Equipment_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.equipment_onts.equipment_onts import (
    Equipment_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=Equipment_ontsArgs.argument_spec,
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

    result = Equipment_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
