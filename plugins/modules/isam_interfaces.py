#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_interfaces
"""

from __future__ import absolute_import, division, print_function

import debugpy

__metaclass__ = type

DOCUMENTATION = """
module: isam_interfaces
short_description: Interface resource module
description:
- This modules creates and manages VLAN configurations for the Interface.
version_added: 0.0.0
notes:
- Tested against ISAM R6.2.04m
- This module works with connection C(network_cli)
author: Jan Hendrik Kühnemund (@jahknem)
options:
  config:
    description: A dict of vlan id configuration
    type: list
    elements: dict
    suboptions:
      name:
        description:
         - Full name of the interface.
        type: str
        required: true
      admin-up:
        type: bool
        description: 
          - If the interface has been activated administratevly
      link-state-trap:
        type: str
        description:
          - If link-up/link-down traps should be activated or disabled
        choices:
          - enable
          - disable
          - no-value
        default: no-value
      link-up-down-trap:
        type: bool
        description: If the interface has been activated administratevly       
      severity:
        type: str
        description:
          - How the 
        choices:
          - indetermiante
          - warning
          - minor
          - major
          - critical
          - no-alarms
          - default
          - no-value
        default: no-value
      port-type:
        description:
          - The Type of the port this port should be configured as
        type: str
        choices:
          - uni
          - nni
          - hc-uni
          - uplink
        default: uni
  state:
    description:
    - The state the configuration should be left in.
    - The states C(replaced) and C(overridden) have identical behaviour for this module.
    - Please refer to examples for more details.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - parsed
    - gathered
    - rendered
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
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.interfaces.interfaces import (
    Interfaces,
)
from ansible_collections.


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    debugFile = open("/tmp/isam_facts.log", "w")
    debugFile.write("Started\n")
    debugFile.flush()
    debugFile.close()
    debugpy.listen(3000)
    debugpy.wait_for_client()       
    debugpy.breakpoint()
    module = AnsibleModule(
        argument_spec=InterfacesArgs.argument_spec,
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

    result = Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
