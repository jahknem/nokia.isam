#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_system
short_description: Manages system configuration on Nokia ISAM.
description:
  - Manages the C(configure system) resources including id, security, sntp,
    sync-if-timing, syslog, and transaction settings.
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
            description: System node identifier.
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
      security:
        description: System security settings.
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
                description: Syslog severities to route.
                type: list
                elements: str
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
      transaction:
        description: Transaction configuration.
        type: dict
        suboptions:
          timeout:
            description: Transaction timeout in seconds.
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
