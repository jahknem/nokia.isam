#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_traps
short_description: Manages Nokia ISAM trap definition and manager configuration.
description:
  - Manages C(configure trap) resources for trap definitions, SNMP managers, and IPv6 managers.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Trap configuration grouped by resource type.
    type: dict
    suboptions:
      definitions:
        description: Trap definition entries keyed by name.
        type: list
        elements: dict
        suboptions:
          name:
            description: Trap definition name.
            type: str
            required: true
          priority:
            description: Trap priority.
            type: str
            choices: [urgent, high, medium, low]
      managers:
        description: SNMP trap manager entries keyed by address.
        type: list
        elements: dict
        suboptions:
          address:
            description: Manager IPv4 address with optional port.
            type: str
            required: true
          priority:
            description: Trap manager priority.
            type: str
            choices: [urgent, high, medium, low]
          cold_start_trap: &trap_bool
            description: Enable or disable this trap type for the manager.
            type: bool
          link_down_trap: *trap_bool
          link_up_trap: *trap_bool
          auth_fail_trap: *trap_bool
          change_trap: *trap_bool
          line_test_trap: *trap_bool
          init_started_trap: *trap_bool
          lic_key_chg_occr: *trap_bool
          topology_chg: *trap_bool
          selt_state_chg: *trap_bool
          dhcp_sess_pre: *trap_bool
          alarm_chg_trap: *trap_bool
          phys_line_trap: *trap_bool
          eqpt_change_trap: *trap_bool
          success_set_trap: *trap_bool
          other_alarm_trap: *trap_bool
          warning_trap: *trap_bool
          minor_trap: *trap_bool
          major_trap: *trap_bool
          critical_trap: *trap_bool
          redundancy_trap: *trap_bool
          eqpt_prot_trap: *trap_bool
          craft_login_trap: *trap_bool
          restart_trap: *trap_bool
          ntr_trap: *trap_bool
          rad_srvr_fail: *trap_bool
          login_occr_trap: *trap_bool
          logout_occr_trap: *trap_bool
          trapmngr_chg_trap: *trap_bool
          mst_genral: *trap_bool
          mst_error: *trap_bool
          mst_protocol_mig: *trap_bool
          mst_inv_bpdu_rx: *trap_bool
          mst_reg_conf_chg: *trap_bool
          dying_gasp: *trap_bool
          alrm_chg_occur: *trap_bool
          mac_auth_fail: *trap_bool
          new_ont_alrm: *trap_bool
          ont_prov_status: *trap_bool
          outofsync: *trap_bool
          actual_cp_changed: *trap_bool
          register_node: *trap_bool
          avail_bw_changed: *trap_bool
          login_occr6_trap: *trap_bool
          logout_occr6_trap: *trap_bool
          trapmgr_chg6_trap: *trap_bool
          ont_prov_template: *trap_bool
          auto_replan_board: *trap_bool
          max_per_window:
            description: Maximum traps sent per shaping window.
            type: int
          window_size:
            description: Trap shaping window size.
            type: int
          max_queue_size:
            description: Maximum queued traps for shaping.
            type: int
          min_interval:
            description: Minimum interval between sent traps.
            type: int
          min_severity:
            description: Minimum severity to send to the manager.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
      v6managers:
        description: SNMP IPv6 trap manager entries keyed by IPv6 address.
        type: list
        elements: dict
        suboptions:
          ipv6address:
            description: Manager IPv6 address with optional port.
            type: str
            required: true
          priority:
            description: Trap manager priority.
            type: str
            choices: [urgent, high, medium, low]
          cold_start_trap: *trap_bool
          link_down_trap: *trap_bool
          link_up_trap: *trap_bool
          auth_fail_trap: *trap_bool
          change_trap: *trap_bool
          line_test_trap: *trap_bool
          init_started_trap: *trap_bool
          lic_key_chg_occr: *trap_bool
          topology_chg: *trap_bool
          selt_state_chg: *trap_bool
          dhcp_sess_pre: *trap_bool
          alarm_chg_trap: *trap_bool
          phys_line_trap: *trap_bool
          eqpt_change_trap: *trap_bool
          success_set_trap: *trap_bool
          other_alarm_trap: *trap_bool
          warning_trap: *trap_bool
          minor_trap: *trap_bool
          major_trap: *trap_bool
          critical_trap: *trap_bool
          redundancy_trap: *trap_bool
          eqpt_prot_trap: *trap_bool
          craft_login_trap: *trap_bool
          restart_trap: *trap_bool
          ntr_trap: *trap_bool
          rad_srvr_fail: *trap_bool
          login_occr_trap: *trap_bool
          logout_occr_trap: *trap_bool
          trapmngr_chg_trap: *trap_bool
          mst_genral: *trap_bool
          mst_error: *trap_bool
          mst_protocol_mig: *trap_bool
          mst_inv_bpdu_rx: *trap_bool
          mst_reg_conf_chg: *trap_bool
          dying_gasp: *trap_bool
          alrm_chg_occur: *trap_bool
          mac_auth_fail: *trap_bool
          new_ont_alrm: *trap_bool
          ont_prov_status: *trap_bool
          outofsync: *trap_bool
          actual_cp_changed: *trap_bool
          register_node: *trap_bool
          avail_bw_changed: *trap_bool
          login_occr6_trap: *trap_bool
          logout_occr6_trap: *trap_bool
          trapmgr_chg6_trap: *trap_bool
          ont_prov_template: *trap_bool
          auto_replan_board: *trap_bool
          max_per_window:
            description: Maximum traps sent per shaping window.
            type: int
          window_size:
            description: Trap shaping window size.
            type: int
          max_queue_size:
            description: Maximum queued traps for shaping.
            type: int
          min_interval:
            description: Minimum interval between sent traps.
            type: int
          min_severity:
            description: Minimum severity to send to the manager.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
        C(definitions[].name) and C(managers[].address) and C(v6managers[].ipv6address) (targeted gathering). Other
        fields are ignored and absent instances are not returned. Without I(config) the whole resource is read.
      - With C(deleted) and I(config), only the sections and instances named in I(config) are deleted or reset; other sections are left alone. Without I(config) everything is deleted.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_traps:
    config:
      definitions:
        - name: cold-start
      managers:
        - address: 10.0.0.1:162
    state: gathered

- name: Gather trap configuration
  nokia.isam.isam_traps:
    state: gathered

- name: Render trap configuration
  nokia.isam.isam_traps:
    state: rendered
    config:
      definitions:
        - name: cold-start
          priority: high
        - name: link-down
      managers:
        - address: 10.0.0.1:162
          priority: high
          cold_start_trap: true
          link_down_trap: true
          max_per_window: 10
      v6managers:
        - ipv6address: 2001:db8::1/162
          priority: medium
          link_up_trap: true
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
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured trap data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured trap data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.traps.traps import (
    Isam_trapsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.traps.traps import (
    Isam_traps,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_trapsArgs.argument_spec,
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

    result = Isam_traps(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
