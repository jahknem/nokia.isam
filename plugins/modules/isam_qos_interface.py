#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_qos_interface
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_qos_interface
short_description: 'Manages qos attributes of isam interface.'
description: 'Manages <> attributes of isam <resource>'
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: list
    elements: dict
    suboptions:
      index:
        type: str
        description: The name of the interface
      queue:
        type: dict
      upstream_queue:
        type: dict
      ds_rm_queue:
        type: dict
      scheduler_node:
        description: 
        - profile name to be associated with the interface. Data driven field type.
        type: str
      ingress_profile:
        description: 
        - the name of the ingress profile to be mapped on this user-port Interface. It  only used for EPON ONU interface current. 
        - Data driven field type.
        type: str
      cac_profile:
        description:
        - the name of the cac profile to be mapped on this user-portInterface. 
        - For EPON OLT in downstream, this profile used for CAC on 1G PON bandwidth.
        type: str
      ext_cac:
        description:
        - the name of the cac profile to be mapped on this user-port Interface. 
        - For EPON OLT in downstream, this profile used for CAC on 10G PON bandwidth.
        type: str
      ds_queue_sharing:
        description:
        - enable downstream queue sharing
        type: bool
      us_queue_sharing:
        description:
        - enable upstream queue sharing
        type: bool
      ds_num_queue:
        description:
        - number of downstream queues
        type: bool
      ds_num_rm_queue:
        description:
        - number of remote downstream queues per ont
        type: str
        choices:
        - 'not applicable'
        - '4'
        - '8'
        - '1'
      us_num_queue:
        description:
        - number of upstream queues per uni
        type: str
        choices:
        - 'not applicable'
        - '4'
        - '8'
        - '1'
      queue_stats_on:
        description:
        - enable queue stats collection for ont uni
        type: bool
      autoschedule_on:
        type: bool
      oper_weight:
        type: int
        description:
        - operational weight of the ONT or UNI scheduler
      oper_rate:
        type: int
        description:
        - Operational rate limit when autoShape enabled for ONT or UNI
      us_vlanport_queue: 
        description: Enable Vlan Port Level Queue Configuration
        type: bool
      dsfld_shaper_prof:
        description:
        - the name of the shaper profile attached to the pon. 
        - Data driven field type.
        type: str
      bandwidth_profile:
        description:
        - the name of the bandwidth profile. 
        - Data driven field type.
        type: str
      bandwidth_sharing:
        description:
        - the bandwidth sharing mode. 
        - Data driven field type.
        type: str
        choices:
        - 'no sharing'
        - 'ont-sharing'
      aggr_usq_profile:
        description:
        - the name of the aggr usq profile. 
        - Data driven field type.
        type: str
      aggr_dsq_profile:
        description:
        - the name of the aggr dsq profile. 
        - Data driven field type.
        type: str
      gem_sharing:
        description:
        - the gem sharing mode. 
        type: str
        choices:
        - 'enable'
        - 'disable'
        - 'not-applicable'
      scheduler_mode:
        description:
        - specifies which mode is selected for scheduler
        choices:
        - 'subscriber-hierarchy'
        - 'service-hierarchy'
        - 'service-flat'
      mc_scheduler_node:
        description:
        - the name of the scheduler-node profile to be mapped on multicast port
        - Data driven field type.
        type: str
      bc_scheduler_node:
        description:
        - the name of the scheduler-node profile to be mapped on broadcast port
        - Data driven field type.
        type: str
      ds_schedule_tag:
        description:
        - specifies downstream scheduler reference
        type: str
        choices:
        - 'egressoutertag'
        - 'cvlantag'
        - 'svlabtag'
  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - gathered
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
"""

EXAMPLES = """

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.qos_interface.qos_interface import (
    Qos_interfaceArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.qos_interface.qos_interface import (
    Qos_interface,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Qos_interfaceArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Qos_interface(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
