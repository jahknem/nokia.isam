#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.arp_relay.arp_relay import Isam_arp_relayArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.arp_relay.arp_relay import Isam_arp_relay


MODULE_DESCRIPTION = """
module: isam_arp_relay
short_description: Manage Nokia ISAM ARP relay statistics configuration
description: Manage Nokia ISAM ARP relay statistics configuration.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      statistics:
        type: bool
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""


def main():
    module = AnsibleModule(
        argument_spec=Isam_arp_relayArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_arp_relay(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_arp_relay
short_description: Manage Nokia ISAM ARP relay
description: Manage Nokia ISAM ARP relay.
"""
