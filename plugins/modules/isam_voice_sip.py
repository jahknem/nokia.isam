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
      - A dictionary of voice SIP configuration objects, generated from the CLI guide grammar.
      - A value equal to the device default counts as unset; facts do not report defaults.
      - C(deleted) naming an instance removes it; naming attributes resets only those (where a removal form exists).
    type: dict
    suboptions:
      lineid_syn_prof:
        description: Line identification syntax profiles (C(configure voice sip lineid-syn-prof)).
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          syntax_pattern:
            description: Value C(configure voice sip lineid-syn-prof syntax-pattern); device default C(terminationuriordn).
            type: str
            choices: [rpregisterdialog, rpregister, physicallineid, terminationuriordn]
          pots_syntax:
            description: Value C(configure voice sip lineid-syn-prof pots-syntax); no concrete default.
            type: str
          isdn_syntax:
            description: Value C(configure voice sip lineid-syn-prof isdn-syntax); no concrete default.
            type: str
          cas_r2_syntax:
            description: Value C(configure voice sip lineid-syn-prof cas-r2-syntax); no concrete default.
            type: str
          cas_r1_syntax:
            description: Value C(configure voice sip lineid-syn-prof cas-r1-syntax); no concrete default.
            type: str
      vsp:
        description: Voice service providers (C(configure voice sip vsp)); I(domain_name) is mandatory at creation.
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          domain_name:
            description: Mandatory value C(configure voice sip vsp domain-name) (no removal form).
            type: str
          admin_status:
            description: Value C(configure voice sip vsp admin-status); device default C(down).
            type: str
            choices: [up, down]
          tinfo:
            description: Value C(configure voice sip vsp tinfo); device default C(1000).
            type: int
          ta4:
            description: Value C(configure voice sip vsp ta4); device default C(4000).
            type: int
          ttir1:
            description: Value C(configure voice sip vsp ttir1); device default C(100).
            type: int
          t_acm_delta:
            description: Value C(configure voice sip vsp t-acm-delta); device default C(18000).
            type: int
          access_held_time:
            description: Value C(configure voice sip vsp access-held-time); device default C(600).
            type: int
          awaiting_time:
            description: Value C(configure voice sip vsp awaiting-time); device default C(60).
            type: int
          digit_send_mode:
            description: Value C(configure voice sip vsp digit-send-mode); device default C(en-bloc).
            type: str
            choices: [en-bloc, overlap-invite, overlap-indialog]
          overlap_484_act:
            description: Value C(configure voice sip vsp overlap-484-act); device default C(release-call).
            type: str
            choices: [release-call, continue]
          dmpm_intdgt_expid:
            description: Value C(configure voice sip vsp dmpm-intdgt-expid); device default C(send-invite).
            type: str
            choices: [send-invite, release-call]
          dial_start_timer:
            description: Value C(configure voice sip vsp dial-start-timer); device default C(10).
            type: int
          dial_long_timer:
            description: Value C(configure voice sip vsp dial-long-timer); device default C(20).
            type: int
          dial_short_timer:
            description: Value C(configure voice sip vsp dial-short-timer); device default C(5).
            type: int
          uri_type:
            description: Value C(configure voice sip vsp uri-type); device default C(sip-uri).
            type: str
            choices: [sip-uri, tel-uri, sips-uri]
          rfc2833_pl_type:
            description: Value C(configure voice sip vsp rfc2833-pl-type); device default C(96).
            type: int
          rfc2833_process:
            description: Value C(configure voice sip vsp rfc2833-process); device default C(audio).
            type: str
            choices: [audio, rfc2833, both, mandatory-audio]
          min_data_jitter:
            description: Value C(configure voice sip vsp min-data-jitter); device default C(50).
            type: int
          init_data_jitter:
            description: Value C(configure voice sip vsp init-data-jitter); device default C(50).
            type: int
          max_data_jitter:
            description: Value C(configure voice sip vsp max-data-jitter); device default C(50).
            type: int
          release_mode:
            description: Value C(configure voice sip vsp release-mode); device default C(normal).
            type: str
            choices: [normal, caller, callee, both]
          dyn_pt_nego_type:
            description: Value C(configure voice sip vsp dyn-pt-nego-type); device default C(far-end).
            type: str
            choices: [far-end, asymmetric]
          vbd_g711a_pl_type:
            description: Value C(configure voice sip vsp vbd-g711a-pl-type); device default C(97).
            type: int
          vbd_g711u_pl_type:
            description: Value C(configure voice sip vsp vbd-g711u-pl-type); device default C(98).
            type: int
          vbd_mode:
            description: Value C(configure voice sip vsp vbd-mode); device default C(autoswitch).
            type: str
            choices: [autoswitch, renegotiation, v152fb-autoswitch, v152fb-reneg]
          warmline_dl_timer:
            description: Value C(configure voice sip vsp warmline-dl-timer); device default C(4).
            type: int
          reg_sub:
            description: Value C(configure voice sip vsp reg-sub); device default C(disable).
            type: str
            choices: [disable, enable]
          dtmf_sip_info:
            description: Value C(configure voice sip vsp dtmf-sip-info); device default C(disable).
            type: str
            choices: [disable, enable]
          sub_period:
            description: Value C(configure voice sip vsp sub-period); device default C(3600).
            type: int
          sub_head_start:
            description: Value C(configure voice sip vsp sub-head-start); device default C(600).
            type: int
          t38_same_udp:
            description: Value C(configure voice sip vsp t38-same-udp); device default C(disable).
            type: str
            choices: [disable, enable]
          dhcp_option82:
            description: Value C(configure voice sip vsp dhcp-option82); device default C(disable).
            type: str
            choices: [enable, disable]
          sspprofile:
            description: Value C(configure voice sip vsp sspprofile); no concrete default.
            type: str
          signaling_ipmode:
            description: Value C(configure voice sip vsp signaling-ipmode); device default C(legacy-ipv4).
            type: str
            choices: [legacy-ipv4, ipv4, ipv6]
          tls_cafile:
            description: Value C(configure voice sip vsp tls-cafile); no concrete default.
            type: str
          media_ipmode:
            description: Value C(configure voice sip vsp media-ipmode); device default C(legacy-ipv4).
            type: str
            choices: [legacy-ipv4, ipv4, ipv6]
          timer_b:
            description: Value C(configure voice sip vsp timer-b) (no removal form).
            type: int
          timer_f:
            description: Value C(configure voice sip vsp timer-f) (no removal form).
            type: int
          timer_t1:
            description: Value C(configure voice sip vsp timer-t1) (no removal form).
            type: int
          timer_t2:
            description: Value C(configure voice sip vsp timer-t2) (no removal form).
            type: int
      register:
        description: SIP register profiles (C(configure voice sip register)).
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          register_uri:
            description: Value C(configure voice sip register register-uri); no concrete default.
            type: str
          register_intv:
            description: Value C(configure voice sip register register-intv); device default C(3600).
            type: int
          reg_retry_intv:
            description: Value C(configure voice sip register reg-retry-intv); device default C(60).
            type: int
          reg_prev_ava_intv:
            description: Value C(configure voice sip register reg-prev-ava-intv); device default C(500).
            type: int
          reg_head_start:
            description: Value C(configure voice sip register reg-head-start); device default C(600).
            type: int
          reg_start_min:
            description: Value C(configure voice sip register reg-start-min); device default C(50).
            type: int
          init_reg_delay:
            description: Value C(configure voice sip register init-reg-delay); device default C(180).
            type: int
      redundancy:
        description: Network redundancy settings (C(configure voice sip redundancy)).
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          support_redun:
            description: Value C(configure voice sip redundancy support-redun); device default C(disable).
            type: str
            choices: [enable, disable]
          dns_purge_timer:
            description: Value C(configure voice sip redundancy dns-purge-timer); device default C(86400).
            type: int
          dns_ini_retr_int:
            description: Value C(configure voice sip redundancy dns-ini-retr-int); device default C(500).
            type: int
          dns_max_retr_nbr:
            description: Value C(configure voice sip redundancy dns-max-retr-nbr); device default C(2).
            type: int
          fg_monitor_method:
            description: Value C(configure voice sip redundancy fg-monitor-method); device default C(register-method).
            type: str
            choices: [register-method, options-method, passive-heartbeat]
          fg_monitor_int:
            description: Value C(configure voice sip redundancy fg-monitor-int); device default C(90).
            type: int
          bg_monitor_method:
            description: Value C(configure voice sip redundancy bg-monitor-method); device default C(options-method).
            type: str
            choices: [options-method]
          bg_monitor_int:
            description: Value C(configure voice sip redundancy bg-monitor-int); device default C(3600).
            type: int
          stable_obs_period:
            description: Value C(configure voice sip redundancy stable-obs-period); device default C(21600).
            type: int
          fo_hystersis:
            description: Value C(configure voice sip redundancy fo-hystersis); device default C(0).
            type: int
          del_upd_threshold:
            description: Value C(configure voice sip redundancy del-upd-threshold); device default C(0).
            type: int
          auto_server_fo:
            description: Value C(configure voice sip redundancy auto-server-fo); device default C(disable).
            type: str
            choices: [enable, disable]
          auto_server_fb:
            description: Value C(configure voice sip redundancy auto-server-fb); device default C(0).
            type: int
          auto_sos_fo:
            description: Value C(configure voice sip redundancy auto-sos-fo); device default C(disable).
            type: str
            choices: [enable, disable]
          auto_sos_fb:
            description: Value C(configure voice sip redundancy auto-sos-fb); device default C(0).
            type: int
          rtry_after_thrsh:
            description: Value C(configure voice sip redundancy rtry-after-thrsh); device default C(0).
            type: int
          options_max_fwd:
            description: Value C(configure voice sip redundancy options-max-fwd); device default C(0).
            type: int
          dns_redun_mode:
            description: Value C(configure voice sip redundancy dns-redun-mode); device default C(dns-redun-primary).
            type: str
            choices: [dns-redun-primary, dns-redun-success]
          fail_obs_timer:
            description: Value C(configure voice sip redundancy fail-obs-timer); device default C(240).
            type: int
          fg_intv_503:
            description: Value C(configure voice sip redundancy fg-intv-503); device default C(2).
            type: int
          time_thrsh_503:
            description: Value C(configure voice sip redundancy time-thrsh-503); device default C(0).
            type: int
          nbr_thrsh_503:
            description: Value C(configure voice sip redundancy nbr-thrsh-503); device default C(1).
            type: int
          auto_srv_fo_timer:
            description: Value C(configure voice sip redundancy auto-srv-fo-timer); device default C(86400).
            type: int
      system:
        description: System session-timer parameters (C(configure voice sip system session-timer)).
        type: dict
        suboptions:
          enable:
            description: On/off flag C(configure voice sip system session-timer enable).
            type: bool
          status:
            description: Value C(configure voice sip system session-timer status); device default C(disable).
            type: str
            choices: [enable, disable, enable-uas]
          min_se_time:
            description: Value C(configure voice sip system session-timer min-se-time); device default C(90).
            type: int
          se_time:
            description: Value C(configure voice sip system session-timer se-time); device default C(1800).
            type: int
          admin_status:
            description: Value C(configure voice sip system session-timer admin-status); device default C(down).
            type: str
            choices: [up, down]
      redundancy_cmd:
        description: Redundancy fail-over commands (C(configure voice sip redundancy-cmd)).
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          start_time:
            description: Value C(configure voice sip redundancy-cmd start-time); device default C(0).
            type: int
          end_time:
            description: Value C(configure voice sip redundancy-cmd end-time); device default C(0).
            type: int
          fail_x_type:
            description: Value C(configure voice sip redundancy-cmd fail-x-type) (no removal form).
            type: str
            choices: [geo-fail-over, geo-fail-back]
      statistics:
        description: Statistics (C(configure voice sip statistics) and C(... stats-config)).
        type: dict
        suboptions:
          stats_5min_config:
            description: Value C(configure voice sip statistics stats-5min-config); device default C(disable).
            type: str
            choices: [disable, enable]
          cdr_config:
            description: Value C(configure voice sip statistics cdr-config); device default C(disable).
            type: str
            choices: [disable, enable]
          per_line:
            description: On/off flag C(configure voice sip statistics stats-config per-line).
            type: bool
          per_board:
            description: On/off flag C(configure voice sip statistics stats-config per-board).
            type: bool
          per_system:
            description: On/off flag C(configure voice sip statistics stats-config per-system).
            type: bool
          per_call:
            description: On/off flag C(configure voice sip statistics stats-config per-call).
            type: bool
          out_any_rsp:
            description: On/off flag C(configure voice sip statistics stats-config out-any-rsp).
            type: bool
          out_180_rsp:
            description: On/off flag C(configure voice sip statistics stats-config out-180-rsp).
            type: bool
          out_200_rsp:
            description: On/off flag C(configure voice sip statistics stats-config out-200-rsp).
            type: bool
          in_any_rsp:
            description: On/off flag C(configure voice sip statistics stats-config in-any-rsp).
            type: bool
          in_180_rsp:
            description: On/off flag C(configure voice sip statistics stats-config in-180-rsp).
            type: bool
          in_200_rsp:
            description: On/off flag C(configure voice sip statistics stats-config in-200-rsp).
            type: bool
      cas_nsm_prof:
        description: CAS number screening/mapping profiles (C(configure voice sip cas-nsm-prof)); I(international_prefix), I(country_code) and I(outg_cpn_length) are mandatory at creation.
        type: list
        elements: dict
        suboptions:
          name:
            description: Instance name.
            type: str
            required: true
          version_nbr:
            description: Value C(configure voice sip cas-nsm-prof version-nbr); device default C(1).
            type: int
          outg_from_no_cgpn:
            description: Value C(configure voice sip cas-nsm-prof outg-from-no-cgpn); device default C(impu-gdn).
            type: str
            choices: [impu-gdn, unavailable]
          international_prefix:
            description: Mandatory value C(configure voice sip cas-nsm-prof international-prefix) (no removal form).
            type: str
          national_prefix:
            description: Value C(configure voice sip cas-nsm-prof national-prefix); no concrete default.
            type: str
          country_code:
            description: Mandatory value C(configure voice sip cas-nsm-prof country-code) (no removal form).
            type: str
          outg_cpn_length:
            description: Mandatory value C(configure voice sip cas-nsm-prof outg-cpn-length) (no removal form).
            type: int
  running_config:
    description:
      - 'Device-native configuration to parse with C(parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The desired state of the resource.
      - C(replaced) reconciles named instances and leaves unnamed instances untouched;
        only C(overridden) removes instances absent from the requested configuration.
      - C(deleted) with configuration touches only named sections and instances.
        Without configuration it removes instances and resets removable settings.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device,
        selected by C(cas_nsm_prof[].name), C(lineid_syn_prof[].name), C(redundancy[].name),
        C(redundancy_cmd[].name), C(register[].name) and C(vsp[].name) (targeted gathering).
        Other fields are ignored and absent instances are not returned; an instance with nothing
        configured answers like an absent one and is not returned either. Without I(config) the whole
        resource is read.
      - C(parsed) and C(rendered) do not write to the device.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_voice_sip:
    config:
      vsp:
        - name: vsp1
      redundancy_cmd:
        - name: vsp1
    state: gathered

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
          admin_status: up
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
          admin_status: up
      register:
        - name: default-reg
          register_uri: sip:reg@example.com
          register_intv: 3600
          init_reg_delay: 180
      system:
        enable: true
        status: enable
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
