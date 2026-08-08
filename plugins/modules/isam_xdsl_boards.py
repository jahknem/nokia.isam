#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_boards
short_description: Resource module to configure xdsl board settings
description:
  - Manages C(configure xdsl board) and C(configure xdsl vp-board) settings
    on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against Nokia ISAM 6.2.04ng
  - This module works with connection C(network_cli)
options:
  config:
    description: XDSL board configuration.
    type: dict
    suboptions:
      boards:
        description: List of XDSL board entries.
        type: list
        elements: dict
        suboptions:
          board_id:
            type: str
            required: true
            description: Board identifier.
          admin_state:
            type: str
            choices: [up, down]
            description: Administrative state.
          card_type:
            type: str
            description: Card type.
      vp_boards:
        description: List of XDSL VP board entries.
        type: list
        elements: dict
        suboptions:
          vp_board_id:
            type: str
            required: true
            description: VP board identifier.
          admin_state:
            type: str
            choices: [up, down]
            description: Administrative state.
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the device
        by executing the command C(info configure xdsl board).
    type: str
  state:
    description: The state the configuration should be left in.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather xdsl boards
  nokia.isam.isam_xdsl_boards:
    state: gathered

- name: Merge an xdsl board
  nokia.isam.isam_xdsl_boards:
    config:
      boards:
        - board_id: 1/1/3
          admin_state: up
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_boards.xdsl_boards import (
    Xdsl_boardsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_boards.xdsl_boards import (
    Xdsl_boards,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_boardsArgs.argument_spec,
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

    result = Xdsl_boards(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
