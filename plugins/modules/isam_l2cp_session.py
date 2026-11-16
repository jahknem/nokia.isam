#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_l2cp_session
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_l2cp_session
short_description: Manages Nokia ISAM L2CP sessions.
description:
  - Manages C(configure l2cp session) on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: L2CP sessions.
    type: list
    elements: dict
    suboptions:
      name:
        description: Session identifier.
        type: str
        required: true
      bras_ip_address:
        description: BRAS IP address (a session without it is deleted).
        type: str
      gsmp_version:
        description: GSMP version.
        type: str
        default: "3"
      gsmp_sub_version:
        description: GSMP sub version.
        type: str
        default: "1"
      encap_type:
        description: Encapsulation type.
        type: str
        default: "tcp"
        choices: [tcp]
      topo_discovery:
        description: Topology discovery.
        type: str
        default: "enabled"
        choices: [disabled, enabled]
      layer2_oam:
        description: Layer 2 OAM.
        type: str
        default: "enabled"
        choices: [disabled, enabled]
      alive_timer:
        description: Alive timer.
        type: str
        default: "250"
      port_reprt_shaper:
        description: Port report shaper.
        type: str
        default: "10"
      aggr_reprt_shaper:
        description: Aggregate report shaper.
        type: str
        default: "10"
      tcp_retry_time:
        description: TCP retry time.
        type: str
        default: "10"
      gsmp_retry_time:
        description: GSMP retry time.
        type: str
        default: "10"
      dslam_name:
        description: DSLAM name.
        type: str
        default: "00 : 00 : 00"
      partition_id:
        description: Partition identifier.
        type: str
        default: "0"
      window_size:
        description: Window size.
        type: str
        default: "10"
      tcp_port:
        description: TCP port.
        type: str
        default: "6068"
      router_instance:
        description: Router instance.
        type: str
        default: "base"
      sig_partition_id:
        description: Signal the partition identifier.
        type: bool
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned. Without I(config) the whole resource is read.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - rendered
      - parsed
    default: merged
"""

EXAMPLES = """
- name: Gather the whole resource
  nokia.isam.isam_l2cp_session:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_l2cp_session:
    config:
      - name: \"1\"
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp_session.l2cp_session import L2cpSessionArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_session.l2cp_session import L2cpSession


def main():
    module = AnsibleModule(argument_spec=L2cpSessionArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cpSession(module).execute_module())


if __name__ == "__main__":
    main()
