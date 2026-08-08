#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xstp
short_description: Manage Nokia ISAM XSTP configuration.
description:
  - Manages C(configure xstp general) and C(configure xstp port) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided XSTP configuration.
    type: dict
    suboptions:
      general:
        description: Global XSTP settings.
        type: dict
        suboptions:
          enable_stp:
            description: Enable or disable STP globally.
            type: bool
          region_name:
            description: MSTP region name.
            type: str
      ports:
        description: XSTP port settings.
        type: list
        elements: dict
        suboptions:
          port:
            description: Port identifier.
            type: str
          path_cost:
            description: MSTP port path cost.
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
- name: Gather XSTP configuration
  nokia.isam.isam_xstp:
    state: gathered

- name: Configure XSTP general and port path cost
  nokia.isam.isam_xstp:
    config:
      general:
        enable_stp: true
        region_name: MSTP-REGION
      ports:
        - port: vlan-port:1/1/8/1
          path_cost: 20000
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xstp.xstp import (
    XstpArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xstp.xstp import (
    Xstp,
)


def main():
    module = AnsibleModule(
        argument_spec=XstpArgs.argument_spec,
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

    result = Xstp(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
