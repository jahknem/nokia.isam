#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.channel_pair_pm.channel_pair_pm import Channel_pair_pmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Channel_pair_pm

MODULE_DESCRIPTION = """
module: isam_channel_pair_pm
short_description: Manages the documented channel-pair FEC and TC PM subset.
description: Manages the documented channel-pair FEC and TC PM subset.
options:
  config: {type: list, elements: dict}
  running_config: {type: str}
  state: {type: str, choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed], default: merged}
"""

def main():
    module = AnsibleModule(argument_spec=Channel_pair_pmArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Channel_pair_pm(module).execute_module())

if __name__ == "__main__": main()

DOCUMENTATION = """
module: isam_channel_pair_pm
short_description: Manage Nokia ISAM channel-pair performance management
description: Manage Nokia ISAM channel-pair performance management.
"""
