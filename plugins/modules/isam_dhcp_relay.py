#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

MODULE_DESCRIPTION = """
module: isam_dhcp_relay
short_description: Manages DHCP relay user port statistics on Nokia ISAM.
description: Manages DHCP relay user port statistics on Nokia ISAM.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      port_stats:
        description: Enable DHCPv4 relay statistics for the VLAN user port.
        type: bool
      v6_port_stats:
        description: Enable DHCPv6 relay statistics for the VLAN user port.
        type: bool
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_relay.dhcp_relay import Isam_dhcp_relayArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dhcp_relay.dhcp_relay import Isam_dhcp_relay


def main():
    module = AnsibleModule(
        argument_spec=Isam_dhcp_relayArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_dhcp_relay(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_dhcp_relay
short_description: Manage Nokia ISAM DHCP relay port statistics
description:
  - Manages C(configure dhcp-relay port-stats / v6-port-stats) on Nokia ISAM.
version_added: 0.3.13
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The DHCP relay port configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Port, e.g. C(vlan-port:1/1/5/1/3/1/1:10).
      port_stats:
        type: bool
        description: DHCPv4 relay port statistics.
      v6_port_stats:
        type: bool
        description: DHCPv6 relay port statistics.
  running_config:
    description: Device configuration to parse with I(state=parsed).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge the configuration of one port
  nokia.isam.isam_dhcp_relay:
    config:
      - name: vlan-port:1/1/5/1/3/1/1:10
        port_stats: true
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_dhcp_relay:
    config:
      - name: vlan-port:1/1/5/1/3/1/1:10
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
