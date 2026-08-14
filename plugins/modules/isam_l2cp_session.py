#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_l2cp_session
short_description: Manage Nokia ISAM L2CP sessions
description: Manage Nokia ISAM L2CP sessions.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp_session.l2cp_session import L2cpSessionArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_session.l2cp_session import L2cpSession


def main():
    module = AnsibleModule(argument_spec=L2cpSessionArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cpSession(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_l2cp_session
short_description: Manage Nokia ISAM L2CP sessions
description: Manage Nokia ISAM L2CP sessions.
"""
