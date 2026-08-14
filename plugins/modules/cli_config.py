#!/usr/bin/python
"""Apply text configuration to a Nokia ISAM device."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: cli_config
short_description: Apply text configuration to Nokia ISAM
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
    support: full
"""

EXAMPLES = r"""
- name: Apply configuration text
  nokia.isam.cli_config:
    config: |
      configure system id name access-node
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
            "provider": {"type": "dict", "required": False},
        },
        supports_check_mode=True,
    )
    commands = [line for line in module.params["config"].splitlines() if line.strip()]
    if module.params["commit"] and commands and not module.check_mode:
        get_resource_connection(module).edit_config(candidate=commands)
    module.exit_json(changed=bool(commands and module.params["commit"]), commands=commands)


if __name__ == "__main__":
    main()
