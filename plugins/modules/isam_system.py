#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_system
short_description: Manages system configuration on Nokia ISAM.
description:
  - Manages the C(configure system) resources including id, sntp, sync-if-timing, syslog, transaction,
    external-leds, auto-laser-shutdown, auto-switch, zero-touch-provision, pon-ont and nt-sftp settings.
  - C(configure system security) belongs to M(nokia.isam.isam_system_security); this module does not read it
    (the I(security) option is deprecated, see there).
  - Settings attributes added from the real C(info configure detail flat) output (marked below) are reported only
    when they differ from the device default (C(no <keyword>)); a flag is reported only when set (C(true)).
    I(state=merged) sets what differs, I(state=replaced) and I(state=overridden) also reset what a given section
    omits with C(configure system <node> no <keyword>) (overridden also omitted sections), I(state=deleted) resets
    the given sections. These set/reset forms are inferred from the detail output and not yet verified on a device.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: System configuration grouped by resource type.
    type: dict
    suboptions:
      id:
        description: System identification parameters.
        type: dict
        suboptions:
          name:
            description: System name.
            type: str
          location:
            description: System location.
            type: str
          contact:
            description: System contact information.
            type: str
          node_id:
            description:
              - System node identifier (the C(<node-id>) of C(configure system id <node-id> ...)).
              - The id attributes below (I(access_oper_id) to I(arp_tca_threshold)) are rendered as
                C(configure system id <node_id> <keyword> ...) with I(node_id) from the task, else from the device.
            type: str
          nt_intercon_vlan:
            description: NT interconnection VLAN identifier.
            type: int
          internal_nw_vlan:
            description: Internal network VLAN identifier.
            type: int
          system_mac:
            description: System MAC address.
            type: str
          access_oper_id:
            description:
              - Access operator identifier (C(configure system id <node-id> access-oper-id)).
            type: str
          system_40gkr4:
            description:
              - 40G KR4 system mode flag (C(configure system id <node-id> system-40gkr4)).
            type: bool
          en_snmp_auth_trap:
            description:
              - Send SNMP authentication failure traps (flag) (C(configure system id <node-id> en-snmp-auth-trap)).
            type: bool
          periph_mgnt_vlan:
            description:
              - Peripheral management VLAN (C(configure system id <node-id> periph-mgnt-vlan)).
            type: int
          periph_mgnt_ctrl:
            description:
              - Peripheral management control (flag) (C(configure system id <node-id> periph-mgnt-ctrl)).
            type: bool
          port_num_in_proto:
            description:
              - Port numbering used in protocols, for example C(type-based) (C(configure system id <node-id> port-num-in-proto)).
            type: str
          ont_trc_dbg_vlan:
            description:
              - ONT trace/debug VLAN (C(configure system id <node-id> ont-trc-dbg-vlan)).
            type: int
          ntr_ssmout_vlan:
            description:
              - NTR SSM-out VLAN (C(configure system id <node-id> ntr-ssmout-vlan)).
            type: int
          ntr_ptp_vlan:
            description:
              - NTR PTP VLAN (C(configure system id <node-id> ntr-ptp-vlan)).
            type: int
          customer_id:
            description:
              - Customer identifier (C(configure system id <node-id> customer-id)).
            type: str
          voiceoswp:
            description:
              - Voice OSWP type, for example C(sip) (C(configure system id <node-id> voiceoswp)).
            type: str
          scalingmode:
            description:
              - System scaling mode (C(configure system id <node-id> scalingmode)).
            type: str
          arp_polling_inter:
            description:
              - ARP polling interval (C(configure system id <node-id> arp-polling-inter)).
            type: int
          bsnap_state:
            description:
              - BSNAP state, for example C(disable) (C(configure system id <node-id> bsnap-state)).
            type: str
          bsnap_server_ip:
            description:
              - BSNAP server IP address (C(configure system id <node-id> bsnap-server-ip)).
            type: str
          bsnap_server_port:
            description:
              - BSNAP server port (C(configure system id <node-id> bsnap-server-port)).
            type: int
          arp_tca_threshold:
            description:
              - ARP TCA threshold (C(configure system id <node-id> arp-tca-threshold)).
            type: int
      security:
        description:
          - Deprecated, use M(nokia.isam.isam_system_security) (for example its C(general.welcome_banner)).
          - C(configure system security) is owned by isam_system_security; this module no longer reads it, so these
            values are never reported, I(state=merged) always sends them and the other states never reset them.
            They are still rendered for compatibility.
        type: dict
        suboptions:
          ssh:
            description: Enable SSH access.
            type: bool
          telnet:
            description: Enable telnet access.
            type: bool
          snmp:
            description: Enable SNMP access.
            type: bool
          welcome_banner:
            description: Quoted welcome banner displayed on management login.
            type: str
      sntp:
        description: SNTP configuration.
        type: dict
        suboptions:
          server:
            description: SNTP server IP address.
            type: str
          server_ip_addr:
            description: SNTP server IP address used by device-native configuration.
            type: str
          port:
            description: SNTP server port.
            type: int
          poll_interval:
            description: Polling interval in seconds.
            type: int
          polling_rate:
            description: SNTP polling rate in seconds.
            type: int
          enabled:
            description: Enable or disable SNTP.
            type: bool
          timezone_offset:
            description: Time zone offset from UTC.
            type: int
          server_port:
            description:
              - SNTP server port of the device-native configuration (C(configure system sntp server-port)).
            type: int
          servers:
            description: SNTP server entries.
            type: list
            elements: dict
            suboptions:
              ip_address:
                description: SNTP server IP address.
                type: str
                required: true
              priority:
                description: SNTP server priority.
                type: int
      syslog:
        description: Syslog configuration.
        type: dict
        suboptions:
          server:
            description: Syslog server address.
            type: str
          facility:
            description: Syslog facility.
            type: str
          severity:
            description: Syslog severity level.
            type: str
          version:
            description:
              - Syslog message format version (C(configure system syslog version)).
            type: str
          time_format:
            description:
              - Syslog time stamp format (C(configure system syslog time-format)).
            type: str
          destinations:
            description: Syslog destination entries.
            type: list
            elements: dict
            suboptions:
              name:
                description: Syslog destination name.
                type: str
                required: true
              type:
                description: Syslog destination type.
                type: str
              disable:
                description:
                  - Destination disabled (flag); only the attributes of existing destinations are set/reset, a destination is never created or removed (C(configure system syslog destination <name> disable)).
                type: bool
              upload_rotate:
                description:
                  - Upload on file rotation (flag) (C(configure system syslog destination <name> upload-rotate)).
                type: bool
              persist_enable:
                description:
                  - Persistent logging enabled (flag) (C(configure system syslog destination <name> persist-enable)).
                type: bool
              persist_timer:
                description:
                  - Persistence timer (C(configure system syslog destination <name> persist-timer)).
                type: int
          routes:
            description: Syslog route entries.
            type: list
            elements: dict
            suboptions:
              destination:
                description: Syslog route destination name.
                type: str
                required: true
              msg_type:
                description: Syslog message type to route.
                type: str
              facility:
                description: Syslog facility to route.
                type: str
              severities:
                description:
                  - Enabled syslog severities of the route (C(emergency), C(alert), ..., C(debug)); C(no <severity>) is not enabled.
                  - Read only (not rendered).
                type: list
                elements: str
              syslog_vlan:
                description:
                  - Syslog VLAN of the route; only the attributes of existing routes are set/reset (C(configure system syslog route <destination> syslog-vlan)).
                type: int
      sync_if_timing:
        description: Synchronous interface timing configuration.
        type: dict
        suboptions:
          mode:
            description: Timing mode.
            type: str
          source:
            description: Timing source.
            type: str
          revert:
            description:
              - Revertive switching back to a recovered higher-priority reference (C(revert) / C(no revert)).
              - Removal resets it with C(no revert).
            type: bool
          wait_time:
            description:
              - Wait-to-restore time before reverting to a recovered reference (C(wait-time)).
              - Removal resets it with C(no wait-time).
            type: int
          output_ql_thresh:
            description:
              - Quality-level threshold below which the timing output is squelched (C(output-ql-thresh)), for example C(clk-ql-dnu).
              - Removal uses C(no output-ql-thresh) (standard ISAM form, not verified on a device).
            type: str
          ssmout_en_bits:
            description:
              - Send SSM on the BITS output (C(ssmout-en-bits)).
              - Removal resets it with C(no ssmout-en-bits).
            type: bool
          ssmout_ceiling:
            description:
              - Highest quality level announced in outgoing SSM (C(ssmout-ceiling)), for example C(clk-ql-prc).
              - Removal uses C(no ssmout-ceiling) (standard ISAM form, not verified on a device).
            type: str
          ais_sensitivity:
            description:
              - Treat AIS on a reference as a failure (C(ais-sensitivity)).
              - Removal resets it with C(no ais-sensitivity).
            type: bool
          bits:
            description:
              - BITS interface mode (C(sync-if-timing bits <mode>)), for example C(autoselect).
              - Removal uses C(no bits) (standard ISAM form, not verified on a device).
            type: str
          bits_bind:
            description: BITS input binding (C(sync-if-timing bits-bind)).
            type: dict
            suboptions:
              bits_a_bind:
                description:
                  - Binding of BITS input A (C(bits-a-bind)). Removal uses C(no bits-a-bind).
                type: str
              bits_b_bind:
                description:
                  - Binding of BITS input B (C(bits-b-bind)). Removal uses C(no bits-b-bind).
                type: str
          force_reference:
            description:
              - Reference the clock is forced to (C(sync-if-timing force-reference)), or C(none).
              - Removal sets it back to C(none).
            type: str
          ref_order:
            description: Timing reference priority order (C(sync-if-timing ref-order prio1|prio2)).
            type: dict
            suboptions:
              prio1:
                description: Reference with priority 1, or C(none). Removal sets it back to C(none).
                type: str
              prio2:
                description: Reference with priority 2, or C(none). Removal sets it back to C(none).
                type: str
          ssm:
            description:
              - Synchronization status message settings per timing reference (C(sync-if-timing ssm <reference>)).
              - References are fixed on the device; an entry is never removed, its attributes are reset with C(no <attr>).
            type: list
            elements: dict
            suboptions:
              reference:
                description: Timing reference, for example C(bits-a), C(bits-b), C(synce-1), C(synce-2), C(ieee1588-a), C(ieee1588-b).
                type: str
                required: true
              ssmenable:
                description: Use received SSM for this reference (C(ssmenable)).
                type: bool
              default_ql:
                description: Quality level assumed without SSM (C(default-ql)), for example C(clk-ql-prc).
                type: str
              target_ql:
                description: Target quality level (C(target-ql)), for example C(clk-ql-dnu).
                type: str
          synce:
            description:
              - SyncE timing references (C(sync-if-timing synce <reference> <port>)).
              - An entry is never removed; removal sets its port back to C(none).
            type: list
            elements: dict
            suboptions:
              reference:
                description: SyncE reference, C(synce-1) or C(synce-2).
                type: str
                required: true
              port:
                description: Port recovering the clock, for example C(nt-a:xfp:1), or C(none).
                type: str
          ssmout_synce:
            description:
              - Outgoing SSM per SyncE capable port (C(sync-if-timing ssmout-synce <port>)).
              - An entry is never removed; removal resets it with C(no ssmout-enable).
            type: list
            elements: dict
            suboptions:
              port:
                description: SyncE port, for example C(nt-a:xfp:1) or C(ntio-1:sfp:6).
                type: str
                required: true
              ssmout_enable:
                description: Send SSM on this port (C(ssmout-enable)).
                type: bool
      loop_id_syntax:
        description: Loop identifier syntax strings by access technology.
        type: dict
        suboptions:
          atm_based_dsl: {description: ATM-based DSL loop syntax., type: str}
          efm_based_dsl: {description: EFM-based DSL loop syntax., type: str}
          efm_based_pon: {description: EFM-based PON loop syntax., type: str}
          efm_based_epon: {description: EFM-based EPON loop syntax., type: str}
          efm_based_ngpon2: {description: EFM-based NG-PON2 loop syntax., type: str}
      relay_id_syntax:
        description: Relay identifier syntax strings by access technology.
        type: dict
        suboptions:
          atm_based_dsl: {description: ATM-based DSL relay syntax., type: str}
          efm_based_dsl: {description: EFM-based DSL relay syntax., type: str}
      max_lt_link_speed:
        description: Maximum link speed used by the line termination.
        type: str
      external_leds:
        description: External LEDs (C(configure system external-leds)).
        type: dict
        suboptions:
          status: {description: External LED status flag (C(status)), type: bool}
      auto_laser_shutdown:
        description: Automatic laser shutdown (C(configure system auto-laser-shutdown)).
        type: dict
        suboptions:
          action: {description: Automatic laser shutdown action (C(action)), type: str}
      auto_switch:
        description: xDSL automatic switching (C(configure system auto-switch)).
        type: dict
        suboptions:
          xdsl_atm_ptm: {description: Automatic ATM/PTM switching flag (C(xdsl-atm-ptm)), type: bool}
          xdsl_stepup_delay: {description: xDSL step-up delay flag (C(xdsl-stepup-delay)), type: bool}
      zero_touch_provision:
        description: Zero touch provisioning (C(configure system zero-touch-provision)).
        type: dict
        suboptions:
          action: {description: Zero touch provisioning action (C(action)), type: str}
      pon_ont:
        description: System wide PON ONT settings (C(configure system pon-ont)).
        type: dict
        suboptions:
          slid_mode: {description: SLID mode (C(slid-mode)), type: str}
          pwrbrst_mode: {description: Power burst mode (C(pwrbrst-mode)), type: str}
          sn_bundle_timer: {description: Serial number bundle timer (C(sn-bundle-timer)), type: int}
          sw_ver_mis_block: {description: Block ONTs on software version mismatch flag (C(sw-ver-mis-block)), type: bool}
          sn_autounlock: {description: Serial number auto unlock flag (C(sn-autounlock)), type: bool}
      nt_sftp:
        description: NT SFTP access (C(configure system nt-sftp)).
        type: dict
        suboptions:
          write_enable: {description: SFTP write access flag (C(write-enable)), type: bool}
      transaction:
        description: Transaction configuration.
        type: dict
        suboptions:
          timeout:
            description:
              - Legacy transaction timeout, form C(configure system transaction timeout <n>).
              - The device prints C(time-out-value); use I(time_out_value).
            type: int
          time_out_value:
            description:
              - Transaction time-out value (C(configure system transaction time-out-value)).
            type: int
          log_full_action:
            description: Action to take when the transaction log is full.
            type: str
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
        C(sntp.servers[].ip_address), C(syslog.destinations[].name), C(syslog.routes[].destination),
        C(sync_if_timing.ssm[].reference), C(sync_if_timing.synce[].reference) and C(sync_if_timing.ssmout_synce[].port)
        (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole
        resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_system:
    config:
      sntp:
        servers:
          - ip_address: 192.0.2.1
      syslog:
        destinations:
          - name: ams
        routes:
          - destination: ams
    state: gathered

- name: Gather system config
  nokia.isam.isam_system:
    state: gathered

- name: Render system config
  nokia.isam.isam_system:
    state: rendered
    config:
      id:
        name: ISAM-01
        location: Datacenter-A
        contact: admin@example.com
        node_id: node-01
        nt_intercon_vlan: 4000
        internal_nw_vlan: 4001
        system_mac: 00:11:22:33:44:55
      security:
        ssh: true
        telnet: false
        snmp: true
      sntp:
        server: 10.0.0.1
        server_ip_addr: 10.0.0.1
        port: 123
        poll_interval: 3600
        polling_rate: 3600
        enabled: true
        timezone_offset: 0
        servers:
          - ip_address: 10.0.0.1
            priority: 1
      syslog:
        server: 10.0.0.2
        facility: local0
        severity: info
        destinations:
          - name: remote-log
            type: ip
        routes:
          - destination: remote-log
            msg_type: event
            facility: local0
            severities:
              - info
      sync_if_timing:
        mode: free-run
        source: internal
      transaction:
        timeout: 300
        log_full_action: overwrite
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
  description: Gathered structured system data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured system data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system.system import (
    Isam_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.system.system import (
    Isam_system,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_systemArgs.argument_spec,
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

    result = Isam_system(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
