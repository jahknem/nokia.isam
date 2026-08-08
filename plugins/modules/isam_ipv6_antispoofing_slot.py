#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ipv6_antispoofing_slot.ipv6_antispoofing_slot import Isam_ipv6_antispoofing_slotArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ipv6_antispoofing_slot.ipv6_antispoofing_slot import Isam_ipv6_antispoofing_slot


DOCUMENTATION = """
module: isam_ipv6_antispoofing_slot
short_description: Manage Nokia ISAM IPv6 anti-spoofing slot configuration
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      bit_len:
        type: int
        default: 64
        choices: [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""


def main():
    module = AnsibleModule(
        argument_spec=Isam_ipv6_antispoofing_slotArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_ipv6_antispoofing_slot(module).execute_module())


if __name__ == "__main__":
    main()
