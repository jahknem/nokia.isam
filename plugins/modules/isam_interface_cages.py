#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_interface_cages
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_interface_cages
version_added: 2.9
short_description: 'Manage interface cage attributes on Nokia ISAM MSAN devices.'
description: 'This module manages interface cage configuration and facts on Nokia ISAM MSAN devices.'
author: Jan Kuehnemund
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: A dictionary of options for interface cages
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description:
        - Configure a specific interface cage identifier.
        required: true
      description:
        type: str
        description:
        - Description of the interface cage.
      apply_qos:
        type: bool
        description:
        - Apply QoS to the interface cage.
  state:
    description:
    - The state the configuration should be left in.
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
- name: Merge interface cage configuration
  nokia.isam.isam_interface_cages:
    config:
      - id: "1"
        description: "Main distribution cage"
        apply_qos: true
    state: merged

- name: Delete interface cage configuration
  nokia.isam.isam_interface_cages:
    config:
      - id: "1"
    state: deleted

- name: Render interface cage commands
  nokia.isam.isam_interface_cages:
    config:
      - id: "2"
        description: "Secondary cage"
        apply_qos: false
    state: rendered

- name: Gather interface cage facts
  nokia.isam.isam_interface_cages:
    state: gathered

- name: Parse interface cage configuration
  nokia.isam.isam_interface_cages:
    running_config: |
      configure interface cage 1 description "Main cage"
      configure interface cage 1 apply-qos
    state: parsed
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - configure interface cage 1
    - configure interface cage 1 description Main cage
    - configure interface cage 1 apply-qos
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - configure interface cage 1
    - configure interface cage 1 description Main cage
    - configure interface cage 1 apply-qos
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_cages.interface_cages import (
    InterfaceCagesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interface_cages.interface_cages import (
    InterfaceCages,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=InterfaceCagesArgs.argument_spec,
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

    result = InterfaceCages(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
