#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ipv6_antispoofing_slot
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ipv6_antispoofing_slot
short_description: Manages IPv6 anti-spoofing slot configuration on Nokia ISAM.
description:
  - Manages C(configure ipv6-antispoofing slot) entries on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided IPv6 anti-spoofing slot configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Slot identifier (e.g. 1/1/5).
      bit_len:
        type: int
        description:
          - Prefix bit length used for anti-spoofing.
          - Must be between 64 and 128 (inclusive); other values fail the module before any device access.
  running_config:
    description: The state-parsed running config (output of C(info configure ipv6-antispoofing slot), flat or hierarchical).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - rendered
      - parsed
    default: merged
"""

EXAMPLES = """
- name: Set the anti-spoofing bit length of a slot
  nokia.isam.isam_ipv6_antispoofing_slot:
    config:
      - name: 1/1/5
        bit_len: 72
    state: merged

- name: Gather all slots
  nokia.isam.isam_ipv6_antispoofing_slot:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_ipv6_antispoofing_slot:
    config:
      - name: 1/1/5
    state: gathered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ipv6_antispoofing_slot.ipv6_antispoofing_slot import (
    Isam_ipv6_antispoofing_slotArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ipv6_antispoofing_slot.ipv6_antispoofing_slot import (
    Isam_ipv6_antispoofing_slot,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Isam_ipv6_antispoofing_slotArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_ipv6_antispoofing_slot(module).execute_module())


if __name__ == "__main__":
    main()
