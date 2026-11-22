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
  - The write states read C(info configure l2cp session flat) and compare against it; an unset attribute equals its device
    default. A device error fails the module.
  - I(bras_ip_address) is mandatory to create a session; for an existing session it is taken from the device when not given.
    Deletion removes whole sessions (C(no session <index>)).
  - Only I(alive_timer) and I(tcp_retry_time) can be changed on an existing session (C(session <index> alive-timer <value>)).
    All other attributes, I(bras_ip_address) included, are set when the session is created; a different value for an
    existing session fails the module before any change (delete the session first).
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
      gsmp_sub_version:
        description: GSMP sub version.
        type: str
      encap_type:
        description: Encapsulation type.
        type: str
        choices: [tcp]
      topo_discovery:
        description: Topology discovery.
        type: str
        choices: [disabled, enabled]
      layer2_oam:
        description: Layer 2 OAM.
        type: str
        choices: [disabled, enabled]
      alive_timer:
        description: Alive timer.
        type: str
      port_reprt_shaper:
        description: Port report shaper.
        type: str
      aggr_reprt_shaper:
        description: Aggregate report shaper.
        type: str
      tcp_retry_time:
        description: TCP retry time.
        type: str
      gsmp_retry_time:
        description: GSMP retry time.
        type: str
      dslam_name:
        description: DSLAM name.
        type: str
      partition_id:
        description: Partition identifier.
        type: str
      window_size:
        description: Window size.
        type: str
      tcp_port:
        description: TCP port.
        type: str
      router_instance:
        description: Router instance.
        type: str
      sig_partition_id:
        description: Signal the partition identifier.
        type: bool
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
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
