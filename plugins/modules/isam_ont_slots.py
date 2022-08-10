#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ont_slots
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_equipment_ont_slot
short_description: 'Manages equipment attributes of isam ont slots.'
description: 'Manages equipment attributes of isam ont slots'
version_added: 1.0.0
author: Ansible Network Engineer
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: list
    elements: dict
    suboptions:
      ont_slot_idx:
        type: str
        description: The id of the ont ID
      planned_card_type:
        type: str
        description:
        - planned card type
        - 'Possible values:'
        - '- ethernet : 10/100/1000/10000 base-t'
        - '- 10_100base : 10/100 base-t'
        - '- pots : pots'
        - '- vdsl2pots : vdsl2/pots combo'
        - '- vdsl2 : vdsl2'
        - '- ethpots : ethernet/pots combo'
        - '- video : video'
        - '- veip : VEIP card'
        - '- ds1 : ds1'
        - '- e1 : e1'
        - '- hpna : hpna'
        - '- moca : moca'
        required: True
        choices:
        - 10_100base
        - pots
        - vdsl2pots
        - vdsl2
        - ethpots
        - video
        - veip
        - ds1
        - e1
        - hpna
        - moca
      plndnumdataports:
        type: int
        description:
        - planned number of data ports
        required: True
      plndnumvoiceports:
        type: int
        description:
        - planned number of voice ports
        required: True
      port-type:
        type: str
        description:
        - 'optional parameter with default value: "uni"'
        - port type of the line card
        choices:
        - uni
        - nni
      transp-mode-rem:
        type: bool
        description:
        - 'optional parameter with default value: "disable"'
        - transparent mode of the line card
      no_mcast_control:
        type: bool
        description:
        - 'optional parameter with defaultvalue: "disable"'
        - 'related OMCI message should be sent to ONT'
      admin-state:
        type: bool
        description:
        - administrative status of the interface
  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - gathered
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
"""

EXAMPLES = """

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ont_slots.ont_slots import (
    Ont_slotsArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ont_slots.ont_slots import (
    Ont_slots,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ont_slotsArgs.argument_spec,
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

    result = Ont_slots(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
