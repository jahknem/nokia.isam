#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_dhcp_relay
short_description: Manages DHCP relay user port statistics on Nokia ISAM.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      port_stats:
        type: bool
      v6_port_stats:
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
