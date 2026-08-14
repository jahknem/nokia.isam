#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_cfm
short_description: Manage Nokia ISAM CFM configuration
description: Manage Nokia ISAM CFM configuration.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.cfm.cfm import CfmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.cfm.cfm import Cfm


def main():
    module = AnsibleModule(argument_spec=CfmArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Cfm(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_cfm
short_description: Manage Nokia ISAM CFM
description: Manage Nokia ISAM CFM.
"""
