#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_li_vlan
short_description: Manage LI VLAN configuration on Nokia ISAM.
description:
  - Manages C(configure li_vlan vlan-id) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided LI VLAN configuration.
    type: dict
    suboptions:
      vlan_id:
        description: LI VLAN ID (0-4093).
        type: int
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather LI VLAN configuration
  nokia.isam.isam_li_vlan:
    state: gathered

- name: Configure LI VLAN
  nokia.isam.isam_li_vlan:
    config:
      vlan_id: 100
    state: merged
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.li_vlan.li_vlan import (
    Li_vlanArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.li_vlan.li_vlan import (
    Li_vlan,
)


def main():
    module = AnsibleModule(
        argument_spec=Li_vlanArgs.argument_spec,
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

    result = Li_vlan(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
