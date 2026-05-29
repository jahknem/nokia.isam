#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_equipment
short_description: Manages equipment shelf, slot, applique, and protection-group configuration on Nokia ISAM.
description:
  - Manages the initial core C(configure equipment) resources for shelves, slots, appliques, and protection groups.
  - C(equipment ont) is intentionally excluded and belongs in a separate resource module.
version_added: 1.0.0
author: Jan Kuehnemund
options:
  config:
    type: dict
    suboptions:
      shelves:
        type: list
        elements: dict
        suboptions:
          id:
            type: str
            required: true
          planned_type:
            type: str
      slots:
        type: list
        elements: dict
        suboptions:
          id:
            type: str
            required: true
          planned_type:
            type: str
          unlock:
            type: bool
          admin_state:
            type: str
            choices: [locked, unlocked]
      appliques:
        type: list
        elements: dict
        suboptions:
          id:
            type: str
            required: true
          planned_type:
            type: str
      protection_groups:
        type: list
        elements: dict
        suboptions:
          id:
            type: int
            required: true
          admin_status:
            type: str
            choices: [lock, unlock]
          eps_quenchfactor:
            type: int
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather equipment config
  nokia.isam.isam_equipment:
    state: gathered

- name: Render equipment config
  nokia.isam.isam_equipment:
    state: rendered
    config:
      shelves:
        - id: 1/1
          planned_type: nfxs-b
      slots:
        - id: lt:1/1/1
          planned_type: ndps-c
          admin_state: unlocked
      appliques:
        - id: ntio-1
          planned_type: ncnc-d
      protection_groups:
        - id: 33
          admin_status: lock
          eps_quenchfactor: 0
"""

RETURN = """
before:
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  returned: when changed
  type: dict
commands:
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  returned: when state is rendered
  type: list
gathered:
  returned: when state is gathered
  type: dict
parsed:
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.isam_equipment.isam_equipment import (
    Isam_equipmentArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.isam_equipment.isam_equipment import (
    Isam_equipment,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_equipmentArgs.argument_spec,
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

    result = Isam_equipment(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
