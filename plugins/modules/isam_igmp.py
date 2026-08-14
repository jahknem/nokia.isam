#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.igmp.igmp import IgmpArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.igmp.igmp import Igmp


DOCUMENTATION = """
---
module: isam_igmp
short_description: Manage Nokia ISAM IGMP configuration
description: |
  - Owns only the C(configure igmp) command family.
options:
  config:
    description: IGMP configuration.
    type: dict
  running_config:
    description: Device-native configuration to parse.
    type: str
  state:
    description: Desired state of the configuration.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""


def main():
    module = AnsibleModule(
        argument_spec=IgmpArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Igmp(module).execute_module())


if __name__ == "__main__":
    main()

MODULE_DESCRIPTION = """
module: isam_igmp
short_description: Manage Nokia ISAM IGMP
description: Manage Nokia ISAM IGMP using the configure igmp command family.
"""
