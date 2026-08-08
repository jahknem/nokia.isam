#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_equipment_replan
short_description: Resource module to configure equipment replan
description:
  - Manages C(configure equipment replan) settings on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against Nokia ISAM 6.2.04ng
  - This module works with connection C(network_cli)
options:
  config:
    description: Equipment replan configuration.
    type: dict
    suboptions:
      board_auto_replan:
        description: Enable or disable board auto replan feature.
        type: str
        choices: [enable, disable]
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the device
        by executing the command C(info configure equipment replan).
    type: str
  state:
    description: The state the configuration should be left in.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather equipment replan
  nokia.isam.isam_equipment_replan:
    state: gathered

- name: Enable board auto replan
  nokia.isam.isam_equipment_replan:
    config:
      board_auto_replan: enable
    state: merged
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_replan.equipment_replan import (
    Equipment_replanArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.equipment_replan.equipment_replan import (
    Equipment_replan,
)


def main():
    module = AnsibleModule(
        argument_spec=Equipment_replanArgs.argument_spec,
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

    result = Equipment_replan(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
