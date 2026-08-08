#!/usr/bin/python
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
