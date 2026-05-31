#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_xdsl_bonding
short_description: Manages XDSL bonding configuration on Nokia ISAM.
description:
  - Manages C(configure xdsl-bonding) configuration.
  - Currently supports group-assembly-time settings.
version_added: 1.0.0
author: Jan Kuehnemund
options:
  config:
    description: XDSL bonding configuration.
    type: dict
    suboptions:
      group_assembly_time:
        description: Group assembly time in milliseconds.
        type: int
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: Desired resource state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather XDSL bonding config
  nokia.isam.isam_xdsl_bonding:
    state: gathered

- name: Set group assembly time
  nokia.isam.isam_xdsl_bonding:
    config:
      group_assembly_time: 50
    state: merged

- name: Render XDSL bonding config
  nokia.isam.isam_xdsl_bonding:
    config:
      group_assembly_time: 50
    state: rendered
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
  description: Gathered structured XDSL bonding data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured XDSL bonding data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_bonding.xdsl_bonding import (
    Xdsl_bondingArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_bonding.xdsl_bonding import (
    Xdsl_bonding,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_bondingArgs.argument_spec,
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

    result = Xdsl_bonding(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
