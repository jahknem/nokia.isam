#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_pppoel2_statistics
short_description: Manage Nokia ISAM PPPoE-L2 statistics
description: Manage Nokia ISAM PPPoE-L2 statistics.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppoel2.pppoel2 import Pppoel2Args
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppoel2.pppoel2 import Pppoel2


def main():
    module = AnsibleModule(
        argument_spec=Pppoel2Args.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "merged", ["config"]], ["state", "replaced", ["config"]],
                     ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
                     ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Pppoel2(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_pppoel2_statistics
short_description: Manage Nokia ISAM PPPoE-L2 statistics
description: Manage Nokia ISAM PPPoE-L2 statistics.
"""
