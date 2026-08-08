#!/usr/bin/python
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
