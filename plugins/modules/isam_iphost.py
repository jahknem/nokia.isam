#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_iphost
short_description: Manage IP host configuration on Nokia ISAM.
description:
  - Manages C(configure iphost) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided IP host configuration.
    type: dict
    suboptions:
      name:
        description: IP host name.
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
- name: Gather IP host configuration
  nokia.isam.isam_iphost:
    state: gathered

- name: Configure IP host
  nokia.isam.isam_iphost:
    config:
      name: myhost
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.iphost.iphost import (
    IphostArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.iphost.iphost import (
    Iphost,
)


def main():
    module = AnsibleModule(
        argument_spec=IphostArgs.argument_spec,
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

    result = Iphost(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
