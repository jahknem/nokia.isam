#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_bridge_learned_mac
short_description: Remove learned unicast MAC addresses from Nokia ISAM bridges.
description:
  - Sends the operational administrative command
    C(admin bridge learned-unicast-mac <vlan-port> unicast-mac-address <mac> delete) (CLI guide 219.2),
    which removes one learned unicast MAC address from a bridge VLAN port.
  - This is an B(action module) it writes to the device, but performs a one-shot operation rather than
    managing persistent configuration. It has no resource states (merged/replaced/deleted/...) and is not
    idempotent; running it is an event. It is not an Ansible action plugin (controller-side helper).
  - I(delete) is the operation and must be C(true). A bare
    C(admin bridge learned-unicast-mac <vlan-port> unicast-mac-address <mac>) without an operation only
    navigates to the entry in the admin hierarchy and performs no action, so it is rejected rather than
    reported as a change.
version_added: 0.3.14
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Learned MAC entries to remove.
    type: list
    elements: dict
    required: true
    suboptions:
      vlan_port:
        description: The bridge VLAN port identifier (a C(vlan-port:rack/shelf/slot/port:...) path).
        type: str
        required: true
      mac_address:
        description: The learned unicast MAC address, six colon-separated hex bytes (C(aa:bb:cc:dd:ee:ff)).
        type: str
        required: true
      delete:
        description:
          - Remove the learned MAC address. This is the operation; it must be C(true).
          - C(false) (the default) names no operation and is rejected.
        type: bool
        default: false
"""

EXAMPLES = """
- name: Remove two learned MAC addresses
  nokia.isam.isam_bridge_learned_mac:
    config:
      - vlan_port: vlan-port:1/1/6/1:3990
        mac_address: aa:bb:cc:dd:ee:ff
        delete: true
      - vlan_port: vlan-port:1/1/6/1:3991
        mac_address: 00:11:22:33:44:55
        delete: true

- name: Check what would run without touching the device
  nokia.isam.isam_bridge_learned_mac:
    config:
      - vlan_port: vlan-port:1/1/6/1:3990
        mac_address: aa:bb:cc:dd:ee:ff
        delete: true
  check_mode: true
"""

RETURN = """
changed:
  description: Whether an action command was (or would be, in check mode) sent.
  returned: always
  type: bool
commands:
  description: The operational commands sent (or that would be sent in check mode).
  returned: always
  type: list
  elements: str
response:
  description: The device responses to the commands (empty in check mode).
  returned: when not check mode
  type: list
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.bridge_learned_mac.bridge_learned_mac import (
    Isam_bridge_learned_macArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.bridge_learned_mac.bridge_learned_mac import (
    Isam_bridge_learned_mac,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_bridge_learned_macArgs.argument_spec,
        supports_check_mode=True,
    )
    module.exit_json(**Isam_bridge_learned_mac(module).execute_module())


if __name__ == "__main__":
    main()
