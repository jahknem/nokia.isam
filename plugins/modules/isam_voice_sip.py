#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_voice_sip
short_description: Manages voice SIP configuration on Nokia ISAM.
description:
  - Manages the C(configure voice sip) resources on the Nokia ISAM system.
  - Supports line identification syntax profiles, voice service providers (VSP),
    SIP register profiles, redundancy settings, system parameters,
    redundancy commands, statistics configuration, and CAS NSM profiles.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description:
      - A dictionary of voice SIP configuration objects.
      - Suboptions mirror the argspec schema consumed by the module.
    type: dict
    suboptions:
      lineid_syn_prof:
        description:
          - List of line identification syntax profiles.
          - Each profile defines the syntax pattern and per-signalling-type syntax.
        type: list
        elements: dict
        suboptions:
          name:
            description: Line identification syntax profile name.
            type: str
            required: true
          syntax_pattern:
            description: Enable syntax pattern.
            type: bool
          pots_syntax:
            description: Enable POTS syntax.
            type: bool
          isdn_syntax:
            description: ISDN syntax string.
            type: str
          cas_r2_syntax:
            description: Enable CAS R2 syntax.
            type: bool
          cas_r1_syntax:
            description: Enable CAS R1 syntax.
            type: bool
      vsp:
        description:
          - List of voice service provider (VSP) entries.
          - Each VSP defines domain name, administrative status, signalling
            options, and SIP timers.
        type: list
        elements: dict
        suboptions:
          name:
            description: VSP profile name.
            type: str
            required: true
          domain_name:
            description: Domain name for the VSP.
            type: str
          admin_status:
            description: Administrative status of the VSP.
            type: bool
          tinfo:
            description: Enable T-info signalling.
            type: bool
          ta4:
            description: Enable TA4 signalling.
            type: bool
          ttir1:
            description: Enable TTIR1 signalling.
            type: bool
          t_acm_delta:
            description: Enable T-ACM delta.
            type: bool
          access_held_time:
            description: Enable access held time.
            type: bool
          awaiting_time:
            description: Enable awaiting time.
            type: bool
          digit_send_mode:
            description: Enable digit send mode.
            type: bool
          overlap_484_act:
            description: Enable overlap 484 activation.
            type: bool
          dmpm_intdg:
            description: Enable DMPM inter-digit guard.
            type: bool
          timer_b:
            description: SIP timer B value (int, milliseconds).
            type: int
          timer_f:
            description: SIP timer F value (int, milliseconds).
            type: int
          timer_t1:
            description: SIP timer T1 value (int, milliseconds).
            type: int
          timer_t2:
            description: SIP timer T2 value (int, milliseconds).
            type: int
      register:
        description:
          - List of SIP register profiles.
          - Each register defines the registration URI, intervals, and delays.
        type: list
        elements: dict
        suboptions:
          name:
            description: Register profile name.
            type: str
            required: true
          register_uri:
            description: Enable register URI.
            type: bool
          register_intv:
            description: Enable register interval.
            type: bool
          reg_retry_intv:
            description: Enable registration retry interval.
            type: bool
          reg_prev_ava_intv:
            description: Enable registration previous available interval.
            type: bool
          reg_head_start:
            description: Enable registration head start.
            type: bool
          reg_start_min:
            description: Enable registration start minimum.
            type: bool
          init_reg_delay:
            description: Enable initial registration delay.
            type: bool
      redundancy:
        description:
          - List of SIP redundancy profiles.
          - Each profile defines DNS timers, failover monitoring, and thresholds.
        type: list
        elements: dict
        suboptions:
          name:
            description: Redundancy profile name.
            type: str
            required: true
          support_redun:
            description: Enable redundancy support.
            type: bool
          dns_purge_timer:
            description: Enable DNS purge timer.
            type: bool
          dns_ini_retr_int:
            description: Enable DNS initial retry interval.
            type: bool
          dns_max_retr_nbr:
            description: Enable DNS maximum retry number.
            type: bool
          fg_monitor_method:
            description: Enable foreground monitor method.
            type: bool
          fg_monitor_int:
            description: Enable foreground monitor interval.
            type: bool
          bg_monitor_method:
            description: Enable background monitor method.
            type: bool
          bg_monitor_int:
            description: Enable background monitor interval.
            type: bool
          stable_obs_period:
            description: Enable stable observation period.
            type: bool
          fo_hystersis:
            description: Enable failover hysteresis.
            type: bool
          del_upd_threshold:
            description: Enable delay update threshold.
            type: bool
      system:
        description:
          - System-level SIP configuration dictionary.
          - Controls session timer, status, minimum SE time, SE time, and admin status.
        type: dict
        suboptions:
          session_timer:
            description: Enable session timer.
            type: bool
          status:
            description: Enable system status.
            type: bool
          min_se_time:
            description: Enable minimum SE time.
            type: bool
          se_time:
            description: Enable SE time.
            type: bool
          admin_status:
            description: Enable administrative status.
            type: bool
      redundancy_cmd:
        description:
          - List of redundancy command profiles.
          - Each profile defines failover type, geo-failover, and time windows.
        type: list
        elements: dict
        suboptions:
          name:
            description: Redundancy command profile name.
            type: str
            required: true
          start_time:
            description: Enable start time.
            type: bool
          end_time:
            description: Enable end time.
            type: bool
          fail_x_type:
            description: Failover cross type (e.g. geo-fail-over).
            type: str
          geo_fail_over:
            description: Geo-failover mode.
            type: str
      statistics:
        description:
          - Statistics configuration dictionary.
          - Controls 5-minute stats, CDR config, and per-line/board/system/call statistics.
        type: dict
        suboptions:
          stats_5min_config:
            description: Enable 5-minute statistics configuration.
            type: bool
          cdr_config:
            description: Enable CDR configuration.
            type: bool
          per_line:
            description: Enable per-line statistics.
            type: bool
          per_board:
            description: Enable per-board statistics.
            type: bool
          per_system:
            description: Enable per-system statistics.
            type: bool
          per_call:
            description: Enable per-call statistics.
            type: bool
          out_any_rsp:
            description: Enable outgoing any response statistics.
            type: bool
          out_180_rsp:
            description: Enable outgoing 180 response statistics.
            type: bool
          out_200_rsp:
            description: Enable outgoing 200 response statistics.
            type: bool
          in_any_rsp:
            description: Enable incoming any response statistics.
            type: bool
          in_180_rsp:
            description: Enable incoming 180 response statistics.
            type: bool
          in_200_rsp:
            description: Enable incoming 200 response statistics.
            type: bool
      cas_nsm_prof:
        description:
          - List of CAS NSM (Network Service Module) profiles.
          - Each profile defines international/country prefixes, calling party
            number length, version, and national prefix.
        type: list
        elements: dict
        suboptions:
          name:
            description: CAS NSM profile name.
            type: str
            required: true
          international_prefix:
            description: International prefix string.
            type: str
          country_code:
            description: Country code string.
            type: str
          outg_cpn_length:
            description: Outgoing calling party number length.
            type: int
          version_nbr:
            description: Enable version number.
            type: bool
          outg_from_no_cgpn:
            description: Enable outgoing from no calling party number.
            type: bool
          national_prefix:
            description: Enable national prefix.
            type: bool
  running_config:
    description:
      - The device-native running configuration as a single string.
      - Required when C(state=parsed).
    type: str
  state:
    description:
      - The desired state of the configuration.
      - C(merged), C(replaced), C(overridden), and C(deleted) push configuration
        to the device.
      - C(gathered) retrieves the running configuration as structured data.
      - C(rendered) produces device-native commands from the provided config
        without connecting to the device.
      - C(parsed) takes a raw running-config string and returns structured data.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather voice SIP configuration from device
  nokia.isam.isam_voice_sip:
    state: gathered
  register: result

- name: Print gathered voice SIP data
  ansible.builtin.debug:
    var: result.gathered

- name: Render voice SIP configuration (VSP, CAS NSM, redundancy, statistics)
  nokia.isam.isam_voice_sip:
    state: rendered
    config:
      vsp:
        - name: vsp1
          domain_name: DomainName.com
          admin_status: true
          timer_b: 30000
          timer_f: 32000
          timer_t1: 500
          timer_t2: 4000
      cas_nsm_prof:
        - name: common-cas-profile
          international_prefix: "#"
          country_code: "#"
          outg_cpn_length: 0
      redundancy_cmd:
        - name: vsp1
          fail_x_type: geo-fail-over
      statistics:
        per_line: true
        per_board: true
        per_system: true
        per_call: true
        out_any_rsp: true
        in_any_rsp: true

- name: Merge voice SIP configuration onto device
  nokia.isam.isam_voice_sip:
    state: merged
    config:
      vsp:
        - name: vsp1
          domain_name: DomainName.com
          admin_status: true
      register:
        - name: default-reg
          register_uri: true
          register_intv: true
          init_reg_delay: true
      system:
        session_timer: true
        status: true
"""

RETURN = """
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
  description: Gathered structured voice SIP data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured voice SIP data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import (
    Isam_voice_sipArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.voice_sip.voice_sip import (
    Isam_voice_sip,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_voice_sipArgs.argument_spec,
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

    result = Isam_voice_sip(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
