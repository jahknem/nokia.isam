#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_dhcp_server
short_description: Manages DHCP server configuration on Nokia ISAM.
description:
  - Manages the DHCP server configuration including the dynamic IPv4 pool, subnet mask, lease time, and restart flag.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: DHCP server configuration.
    type: dict
    suboptions:
      start_addr:
        description: Starting IP address for DHCP pool.
        type: str
      end_addr:
        description: Compatibility alias for stop_addr.
        type: str
      stop_addr:
        description: Stopping IP address for DHCP pool.
        type: str
      subnet_mask:
        description: Subnet mask for DHCP pool.
        type: str
      lease_time:
        description: Lease time in seconds.
        type: int
      lease_time_enabled:
        description: Whether the device DHCP lease-time setting is enabled. Set false to render no lease-time.
        type: bool
      restart:
        description: Restart the DHCP server.
        type: bool
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
- name: Gather DHCP server config
  nokia.isam.isam_dhcp_server:
    state: gathered

- name: Render DHCP server config
  nokia.isam.isam_dhcp_server:
    state: rendered
    config:
      start_addr: 192.168.1.100
      stop_addr: 192.168.1.200
      subnet_mask: 255.255.255.0
      lease_time: 86400

- name: Configure DHCP server
  nokia.isam.isam_dhcp_server:
    state: merged
    config:
      start_addr: 192.168.1.100
      end_addr: 192.168.1.200
      subnet_mask: 255.255.255.0
      lease_time: 86400
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
  description: Gathered structured DHCP server data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured DHCP server data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_server.dhcp_server import (
    Isam_dhcp_serverArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dhcp_server.dhcp_server import (
    Isam_dhcp_server,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_dhcp_serverArgs.argument_spec,
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

    result = Isam_dhcp_server(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
