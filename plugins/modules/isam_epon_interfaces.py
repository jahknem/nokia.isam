#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.epon_interfaces.epon_interfaces import Epon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Epon_interfaces

DOCUMENTATION = """
module: isam_epon_interfaces
short_description: Manages the documented EPON interface provisioning subset.
options:
  config: {type: list, elements: dict}
  running_config: {type: str}
  state: {type: str, choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed], default: merged}
"""

def main():
    module = AnsibleModule(argument_spec=Epon_interfacesArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Epon_interfaces(module).execute_module())

if __name__ == "__main__": main()
