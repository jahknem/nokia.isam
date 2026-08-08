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
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Equipment configuration grouped by resource type.
    type: dict
    suboptions:
      shelves:
        description: Equipment shelf entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Shelf identifier.
            type: str
            required: true
          planned_type:
            description: Planned shelf type.
            type: str
      slots:
        description: Equipment slot entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Slot identifier.
            type: str
            required: true
          planned_type:
            description: Planned slot type.
            type: str
          unlock:
            description: Convenience flag for unlocking the slot.
            type: bool
          admin_state:
            description: Administrative slot state.
            type: str
            choices: [locked, unlocked]
      appliques:
        description: Equipment applique entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Applique identifier.
            type: str
            required: true
          planned_type:
            description: Planned applique type.
            type: str
      protection_groups:
        description: Equipment protection group entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Protection group identifier.
            type: int
            required: true
          admin_status:
            description: Protection group administrative status.
            type: str
            choices: [lock, unlock]
          eps_quenchfactor:
            description: EPS quench factor.
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
  description: Gathered structured equipment data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured equipment data.
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
