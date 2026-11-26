#!/usr/bin/python
"""Apply text configuration to a Nokia ISAM device."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: cli_config
short_description: Apply text configuration to Nokia ISAM
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
description:
  - Sends configuration text through the active Nokia network_cli connection.
  - Nokia ISAM does not expose replace-file or rollback operations through the
    collection's cliconf plugin, so this module supports only config input.
options:
  config:
    description: Configuration text to send to the device.
    required: true
    type: str
  commit:
    description: Whether to send the configuration to the device.
    type: bool
    default: true
attributes:
  check_mode:
    description: Lists the commands that would be sent without sending them.
    support: full
"""

EXAMPLES = r"""
- name: Apply configuration text
  nokia.isam.cli_config:
    config: |
      configure system id name access-node
"""

RETURN = r"""
commands:
  description:
    - The non-empty lines of I(config), in order; sent to the device unless I(commit) is
      false or the task runs in check mode.
  returned: always
  type: list
  elements: str
  sample: ['configure system id name access-node']
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)


def main():
    module = AnsibleModule(
        argument_spec={
            "config": {"type": "str", "required": True},
            "commit": {"type": "bool", "default": True},
        },
        supports_check_mode=True,
    )
    commands = [line for line in module.params["config"].splitlines() if line.strip()]
    if module.params["commit"] and commands and not module.check_mode:
        connection = get_resource_connection(module)
        connection.edit_config(candidate=commands)
    module.exit_json(changed=bool(commands and module.params["commit"]), commands=commands)


if __name__ == "__main__":
    main()
