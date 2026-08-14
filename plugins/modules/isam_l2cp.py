#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_l2cp
short_description: Manage Nokia ISAM L2CP configuration
description: Manage Nokia ISAM L2CP configuration.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp.l2cp import L2cpArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp.l2cp import L2cp


def main():
    module = AnsibleModule(argument_spec=L2cpArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cp(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_l2cp
short_description: Manage Nokia ISAM L2CP
description: Manage Nokia ISAM L2CP.
"""
