#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ngpon2_channel_groups.ngpon2_channel_groups import Ngpon2_channel_groupsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Ngpon2_channel_groups

MODULE_DESCRIPTION = """
module: isam_ngpon2_channel_groups
short_description: Manages the documented NG-PON2 channel-group subset.
options:
  config: {type: list, elements: dict}
  running_config: {type: str}
  state: {type: str, choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed], default: merged}
"""

def main():
    module = AnsibleModule(argument_spec=Ngpon2_channel_groupsArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Ngpon2_channel_groups(module).execute_module())

if __name__ == "__main__": main()

DOCUMENTATION = """
module: isam_ngpon2_channel_groups
short_description: Manage Nokia ISAM NG-PON2 channel groups
description: Manage Nokia ISAM NG-PON2 channel groups.
"""
