#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp_user_port.l2cp_user_port import L2cpUserPortArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_user_port.l2cp_user_port import L2cpUserPort


def main():
    module = AnsibleModule(argument_spec=L2cpUserPortArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cpUserPort(module).execute_module())


if __name__ == "__main__":
    main()
