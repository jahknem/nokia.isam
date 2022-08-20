#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_bridges
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_bridge
short_description: 'Manages <> attributes of isam <resource>.'
description: 'Manages <> attributes of isam <resource>'
version_added: 1.0.0
author: Ansible Network Engineer
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: dict
    suboptions:
      ageing_time:
        type: int
        description: 
        - "optional parameter with default value: 300"
        - ageing timeout for dynamic macentries
        default: 300
      port:
        type: list
        elements: dict
        description:
        - This command allows the operator to specify various parameters applicable to a specific bridge port. These parameters determine the handling of frames on the bridge port.
        suboptions:
          port:
            type: str
            description:
            - identity of a port (e.g. uplink port, atm pvc, efm port, eth port, la group ...)
          pvid:
            type: int
            description:
            - 'optional parameter with default value: "stacked : 0 : 4097" The parameter is not visible during creation.default vlan id for untagged frames'
          default-priority:
            type: int
            description:
            - 'optional parameter with default value: 0'
            - priority to be set in upstream frames
          mac-learn-off:
            type: bool
            description:
            - 'optional parameter'
            - 'disable mac learning on this port'
          max-unicast-mac:
            type: int
            description:
            - 'optional parameter with default value: 1'
            - 'maximum number of uncommited unicast macs on this port'
          qos-profile:
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'qos profile to be used on this port'
          prio-regen-prof:
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'priority regen profile to be used on this port'
            choices:
            - 'none'
            - 'trusted-port'
            - 'best-effort'
            - 'cl-all-prio-3'
            - 'cl-all-prio-4'
            - 'background'
            - 'be-cl-voice'
            - 'be-cl-1d-voice'
            - 'be-voice'
            - 'l2-vpn-3'
            - 'l2-vpn-4'
            - '11'
            - '12'
            - '13'
            - '14'
            - '15'
            - '16'
            - '17'
            - '18'
            - '19'
            - '20'
            - '21'
            - '22'
            - '23'
            - '24'
            - '25'
            - '26'
            - '27'
            - '28'
            - '29'
            - '30'
            - '31'
            - '32'
          prio-regen-name:
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'priority regen profile name to be used on this port'
          max-commited-mac:
            type: int
            description:
            - 'optional parameter with default value: 65535'
            - 'maximum number of commited unicast macs on this port. 65535 means the committed value is the same as max-unicast-mac'
          mirror-mode:
            type: str
            description:
            - 'optional parameter with default value: "disable"'
            - flow mirroring mode of the bridge port
            choices:
            - 'disable'
            - 'overwrite-outer-vlan'
          mirror-vlan:
            type: int
            description:
            - 'optional parameter with default value: 0. Range: [0...4093]'
            - vlan-id to be inserted into mirrored packets. This configuration value has no effect in case mirroring mode of the bridgeport is disabled (mirror-mode).
          pvid-tagging-flag:
            type: str
            description:
            - 'optional parameter with default value: "onu"'
            - pvid will be tagged in ONU or in OLT.
            choices:
            - 'onu'
            - 'olt'
          ds-pbit-mode:
            type: str
            description:
            - 'optional parameter with default value: "auto"'
            - downstream p-bits mode
            - "auto : transparency for DSL and translated for GPON"
            - "translated : for known p-bits the inverse translation is performed in downstream; unknown p-bits are forwarded unchanged in downstream"
            - "transparency : all p-bits are forwarded unchanged in downstream"
            choices:
            - 'auto'
            - 'translated'
            - 'transparency'
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
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.bridges.bridges import (
    BridgesArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.bridges.bridges import (
    Bridges,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=BridgesArgs.argument_spec,
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

    result = Bridges(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
