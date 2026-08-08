#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_interfaces
version_added: 1.0.0
short_description: 'Manages interface attributes of Nokia ISAM MSAN devices.'
description: 'This module manages interface attributes of Nokia ISAM MSAN devices'
author: Jan Kühnemund (@jahknem)
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: A dictionary of options for interface ports
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        aliases: [id]
        description:
        - configure a specific interface port
      admin_up:
        type: bool
        aliases: [admin-up]
        description:
        - If the interface has been activated administratevly
      link_updown_trap:
        type: bool
        aliases: [link-updown-trap]
        description:
        - If up/down state changes of the interface should be trapped
      user:
        type: str
        description:
          - description of the user connected to this interface. (only supported for physical interfaces)
      severity:
        type: str
        description:
        - set minimum severity for alarm to be reported,If ima is the only interface for which this parameter is not supported
        - 'Possible values:'
        - '- indeterminate : not a definite known severity'
        - '- warning : just to inform as a warning'
        - '- minor : not service affecting'
        - '- major : service affecting'
        - '- critical : service breaking'
        - '- no-alarms : do not report alarm'
        - '- default : take default as specified via Interface Alarm Configuration command'
        - '- no-value : no entry in the table'
        choices:
        - indeterminate
        - warning
        - minor
        - major
        - critical
        - no-alarms
        - default
        - no-value
        default: no-value
      port_type:
        aliases: [port-type]
        description:
        - The whole network service model based on this interface
        type: str
        choices:
        - uni
        - nni
        - hc-uni
        - uplink
        default: uni
  running_config:
    description:
    - This option is used only with state C(parsed).
    - The value should be the output of C(info configure interface port flat).
    type: str

  state:
    description:
    - The state the configuration should be left in
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
- name: Gather interface facts
  nokia.isam.isam_interfaces:
    state: gathered

- name: Enable interface and set alarm behavior
  nokia.isam.isam_interfaces:
    state: merged
    config:
      - name: "ethernet-line:1/1/8/1"
        admin_up: true
        link_updown_trap: true
        severity: warning
        port_type: nni

- name: Legacy aliases are still accepted
  nokia.isam.isam_interfaces:
    state: merged
    config:
      - id: "ethernet-line:1/1/8/2"
        admin-up: true
        link-updown-trap: false
        port-type: uni

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
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
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interfaces.interfaces import (
    Interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result from module invocation
    """
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
