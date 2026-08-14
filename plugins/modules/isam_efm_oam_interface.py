#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_efm_oam_interface
short_description: Manage Nokia ISAM EFM OAM interfaces
description: Manage Nokia ISAM EFM OAM interfaces.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.efm_oam.efm_oam import EfmOamArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.efm_oam.efm_oam import EfmOam


def main():
    module = AnsibleModule(
        argument_spec=EfmOamArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**EfmOam(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_efm_oam_interface
short_description: Manage Nokia ISAM EFM OAM interfaces
description: Manage Nokia ISAM EFM OAM interfaces.
"""
