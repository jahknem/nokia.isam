#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_pppoe_client_interface
short_description: Manage Nokia ISAM PPPoE client interfaces
description: Manage Nokia ISAM PPPoE client interfaces.
options:
  config:
    type: list
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppoe_client.pppoe_client import PppoeClientArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppoe_client.pppoe_client import PppoeClient


def main():
    module = AnsibleModule(
        argument_spec=PppoeClientArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "merged", ["config"]], ["state", "replaced", ["config"]],
                     ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
                     ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**PppoeClient(module, "interface").execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_pppoe_client_interface
short_description: Manage Nokia ISAM PPPoE client interfaces
description: Manage Nokia ISAM PPPoE client interfaces.
"""
