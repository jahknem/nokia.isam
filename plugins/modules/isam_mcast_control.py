#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_control.mcast_control import Mcast_controlArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.mcast_control.mcast_control import Mcast_control


DOCUMENTATION = """
---
module: isam_mcast_control
short_description: Manage Nokia ISAM multicast control configuration
description:
  - Owns only the C(configure mcast-control) command family.
options:
  config:
    type: dict
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""


def main():
    module = AnsibleModule(
        argument_spec=Mcast_controlArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Mcast_control(module).execute_module())


if __name__ == "__main__":
    main()
