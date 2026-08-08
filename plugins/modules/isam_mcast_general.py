#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_mcast_general
short_description: Manage Nokia ISAM multicast general configuration.
description:
  - Manages C(configure mcast general) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided multicast general configuration.
    type: dict
    suboptions:
      admin_state:
        description: Enable or disable multicast general admin state.
        type: bool
      forward_method:
        description: Multicast forward method.
        type: str
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
- name: Gather multicast general configuration
  nokia.isam.isam_mcast_general:
    state: gathered

- name: Configure multicast general
  nokia.isam.isam_mcast_general:
    config:
      admin_state: true
      forward_method: proxy
    state: merged
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_general.mcast_general import (
    Mcast_generalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.mcast_general.mcast_general import (
    Mcast_general,
)


def main():
    module = AnsibleModule(
        argument_spec=Mcast_generalArgs.argument_spec,
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

    result = Mcast_general(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
