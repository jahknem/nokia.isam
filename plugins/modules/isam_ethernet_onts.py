#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ethernet_onts
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ethernet_onts
short_description: Manages Nokia ISAM ONT Ethernet port provisioning.
description:
  - Manages C(configure ethernet ont) attributes on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Initial implementation covers live-observed ONT Ethernet UNI fields.
options:
  config:
    description: The provided ONT Ethernet port configuration.
    type: list
    elements: dict
    suboptions:
      uni_idx:
        type: str
        required: true
        aliases: [name]
        description: Identification of the ONT Ethernet UNI interface index.
      cust_info:
        type: str
        description: Customer or port information string.
      auto_detect:
        type: str
        description: Auto detection configuration.
        choices:
          - 10_100baset-auto
          - 10baset-fd
          - 100baset-fd
          - 1000baset-fd
          - auto-basetfd
          - 10gig-fd
          - 2.5gig-fd
          - 5gig-fd
          - 10baset-auto
          - 10baset-hd
          - 100baset-hd
          - 1000baset-hd
          - autobaset-hd
          - 10_100_1000baset-auto
          - 100baset-auto
          - auto
          - 1000baset-auto
      admin_state:
        type: str
        description: Administrative state of the interface.
        choices:
          - up
          - down
  running_config:
    description: The state-parsed running config.
    type: str
  state:
    description: The state the configuration should be left in.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - rendered
      - parsed
    default: merged
"""

EXAMPLES = """
- name: Render ONT Ethernet port configuration
  nokia.isam.isam_ethernet_onts:
    config:
      - uni_idx: 1/1/1/1/1/1/1
        cust_info: "Customer port 1"
        auto_detect: auto
        admin_state: up
    state: rendered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ethernet_onts.ethernet_onts import (
    Ethernet_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ethernet_onts.ethernet_onts import (
    Ethernet_onts,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Ethernet_ontsArgs.argument_spec,
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

    result = Ethernet_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
