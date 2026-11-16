#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.arp_relay.arp_relay import Isam_arp_relayArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.arp_relay.arp_relay import Isam_arp_relay


MODULE_DESCRIPTION = """
module: isam_arp_relay
short_description: Manage Nokia ISAM ARP relay statistics configuration
description: Manage Nokia ISAM ARP relay statistics configuration.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      statistics:
        type: bool
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""


def main():
    module = AnsibleModule(
        argument_spec=Isam_arp_relayArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_arp_relay(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_arp_relay
short_description: Manage Nokia ISAM ARP relay statistics
description:
  - Manages C(configure arp-relay statistics) on Nokia ISAM.
version_added: 0.3.13
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The ARP relay port configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Port, e.g. C(vlan-port:1/1/5/1/3/1/1:10).
      statistics:
        type: bool
        description: Collect ARP relay statistics on the port.
  running_config:
    description: Device configuration to parse with I(state=parsed).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge the configuration of one port
  nokia.isam.isam_arp_relay:
    config:
      - name: vlan-port:1/1/5/1/3/1/1:10
        statistics: true
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_arp_relay:
    config:
      - name: vlan-port:1/1/5/1/3/1/1:10
    state: gathered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: list
"""
