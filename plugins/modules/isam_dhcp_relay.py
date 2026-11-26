#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

MODULE_DESCRIPTION = """
module: isam_dhcp_relay
short_description: Manages DHCP relay user port statistics on Nokia ISAM.
description: Manages DHCP relay user port statistics on Nokia ISAM.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      port_stats:
        description: Enable DHCPv4 relay statistics for the VLAN user port.
        type: bool
      v6_port_stats:
        description: Enable DHCPv6 relay statistics for the VLAN user port.
        type: bool
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_relay.dhcp_relay import Isam_dhcp_relayArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dhcp_relay.dhcp_relay import Isam_dhcp_relay


def main():
    module = AnsibleModule(
        argument_spec=Isam_dhcp_relayArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_dhcp_relay(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_dhcp_relay
short_description: Manage Nokia ISAM DHCP relay port statistics
description:
  - Manages C(configure dhcp-relay port-stats / v6-port-stats) on Nokia ISAM.
  - R6.2.04m accepts the setting but shows it in no read (C(info configure ... flat) or C(flat detail)), so the module cannot verify it and C(merged) sends it on every run (lab ISAM).
version_added: 0.3.13
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The DHCP relay port configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Port, e.g. C(vlan:1/1/5/1/3/1/1:10) or C(1/1/3/1). The device refuses the C(vlan-port:) form for this command (lab ISAM).
      port_stats:
        type: bool
        description: DHCPv4 relay port statistics.
      v6_port_stats:
        type: bool
        description: DHCPv6 relay port statistics.
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge the configuration of one port
  nokia.isam.isam_dhcp_relay:
    config:
      - name: vlan:1/1/5/1/3/1/1:10
        port_stats: true
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_dhcp_relay:
    config:
      - name: vlan:1/1/5/1/3/1/1:10
    state: gathered
"""

RETURN = """
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(complete), C(partial), C(failed) or C(unverified)) is reported at
      resource level under C(parse); C(unverified) means the parser did not record its
      coverage of the reply.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
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
