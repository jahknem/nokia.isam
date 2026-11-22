#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xstp
short_description: Manage Nokia ISAM XSTP configuration.
description:
  - Manages C(configure xstp general) and C(configure xstp port) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided XSTP configuration.
    type: dict
    suboptions:
      general:
        description:
          - Global XSTP settings (C(configure xstp general)).
          - The attributes other than I(enable_stp) and I(region_name) are set with C(general <attr> <value>) and
            reset with C(general no <attr>) (replaced, overridden and deleted reset unmentioned ones). Syntax from the
            CLI reference, not verified on a device.
        type: dict
        suboptions:
          enable_stp:
            description: Enable or disable STP globally.
            type: bool
          region_name:
            description: MSTP region name.
            type: str
          priority:
            description: Bridge priority, a multiple of 4096 (0-61440) (C(priority)); device default C(32768), not reported.
            type: int
          max_instance_num:
            description: Maximum number of spanning trees (1-65) (C(max-instance-num)); device default C(65), not reported.
            type: int
          max_age:
            description: Max age for the root bridge in 10 ms units, a multiple of 100 (600-4000) (C(max-age)); device default C(2000), not reported.
            type: int
          hello_time:
            description: Hello time for the root bridge in 10 ms units, a multiple of 100 (100-1000) (C(hello-time)); device default C(200), not reported.
            type: int
          forward_delay:
            description: Forward delay in 10 ms units, a multiple of 100 (400-3000) (C(forward-delay)); device default C(1500), not reported.
            type: int
          version:
            description: Spanning tree protocol version (C(version)); device default C(mstp), not reported.
            type: str
            choices: [stp-compatible, rstp, mstp]
          tx_hold_count:
            description: Maximum transmission rate limit (1-10) (C(tx-hold-count)); device default C(3), not reported.
            type: int
          path_cost_type:
            description: Version of the default path costs (C(path-cost-type)); device default C(32-bit), not reported.
            type: str
            choices: [16-bit, 32-bit]
          max_hop_count:
            description: Maximum hop count in 10 ms units, a multiple of 100 (600-4000) (C(max-hop-count)); device default C(2000), not reported.
            type: int
          region_version:
            description: MSTP region version (0-65535) (C(region-version)); device default C(0), not reported.
            type: int
          config_id_sel:
            description: Configuration id format selector (0-255) (C(config-id-sel)); device default C(0), not reported.
            type: int
      ports:
        description:
          - XSTP port settings (C(configure xstp port <port>)).
          - I(path_cost) has no reset form and is never removed. The other attributes are set with
            C(port <port> <attr> [<value>]) and reset with C(port <port> no <attr>); overridden resets them on
            ports that are not given, deleted on the named ports (all ports when none is named). Syntax from the
            CLI reference, not verified on a device.
        type: list
        elements: dict
        suboptions:
          port:
            description: Port identifier.
            type: str
          path_cost:
            description: MSTP port path cost.
            type: int
          priority:
            description: Port priority, a multiple of 16 (0-240) (C(priority)); device default C(128), not reported.
            type: int
          enable_stp:
            description: Enable the MSTI port state (C(enable-stp)); C(no enable-stp) is the default and not reported.
            type: bool
          edge_port:
            description: Edge port (C(edge-port)); C(no edge-port) is the default and not reported.
            type: bool
          admin_p2p:
            description: Administrative point-to-point status of the attached LAN segment (C(admin-p2p)); device default C(auto), not reported.
            type: str
            choices: [force-true, force-false, auto]
          hello_time:
            description: Port hello time in 10 ms units, a multiple of 100 (100-1000) (C(hello-time)); device default C(200), not reported.
            type: int
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description:
    - The state of the configuration after module completion.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(ports[].port) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(deleted) and I(config), only the sections and instances named in I(config) are reset; other sections are left alone. Without I(config) everything is deleted. Naming ports does not reset the C(general) settings.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather XSTP configuration
  nokia.isam.isam_xstp:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_xstp:
    state: gathered
    config:
      ports:
        - port: vlan-port:1/1/8/1

- name: Configure XSTP general and port path cost
  nokia.isam.isam_xstp:
    config:
      general:
        enable_stp: true
        region_name: MSTP-REGION
      ports:
        - port: vlan-port:1/1/8/1
          path_cost: 20000
    state: merged
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
  description: The configuration as structured data before module invocation.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xstp.xstp import (
    XstpArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xstp.xstp import (
    Xstp,
)


def main():
    module = AnsibleModule(
        argument_spec=XstpArgs.argument_spec,
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

    result = Xstp(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
