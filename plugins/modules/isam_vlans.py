#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_vlans
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_vlans
version_added: 1.0.0
short_description: 'Manage VLAN attributes on Nokia ISAM MSAN devices.'
description: 'This module manages VLAN configuration and facts on Nokia ISAM MSAN devices.'
author: Jan Kühnemund (@jahknem)
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: A dictionary of options for VLANs
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description:
        - Configure a specific VLAN ID (numeric or stacked like 'stacked:<svid>:<cvid>')
      name:
        description:
        - The VLAN name
        type: str
      mode:
        type: str
        description:
        - The mode of the VLAN
        choices:
        - cross-connect
        - residential-bridge
        - qos-aware
        - layer2-terminated
        - mirror
      sntp_proxy:
        aliases: [sntp-proxy]
        type: bool
        description: If the VLAN should be configured as a SNTP proxy
      priority:
        type: int
        description:
        - 'The priority of the VLAN. Range: [0...7]'
      vmac_not_in_opt61:
        aliases: [vmac-not-in-opt61]
        type: bool
        description: Skip vmac translation in dhcp option 61 even when vmac is enabled
      new_broadcast:
        aliases: [new-broadcast]
        type: str
        description: Control downstream broadcast frames.
        choices:
        - inherit
        - enable
        - disable
      protocol_filter:
        aliases: [protocol-filter]
        type: str
        description: Control protocol group filters
        choices:
        - pass-all
        - pass-pppoe
        - pass-ipoe
        - pass-pppoe-ipoe
        - pass-ipv6oe
        - pass-pppoe-ipv6oe
        - pass-ipoe-ipv6oe
        - pass-pppoe-ipoe-ipv6oe
      pppoe_relay_tag:
        aliases: [pppoe-relay-tag]
        type: str
        description:
        - Configure the format of the PPPoE relay tag
        choices:
        - 'true'
        - 'false'
        - configurable
      drly_srv_usr_side:
        aliases: [drly-srv-usr-side]
        description:
        - Enable DHCP(v4/v6) server transparency at the user side when DHCP(v4/v6) relay is enabled. Only applicable for CC forwarder
        type: str
        choices: [enable, disable]
      dhcp_opt82_ext:
        aliases: [dhcp-opt82-ext]
        description:
        - Configure DHCP option 82 handling for subscriber-side DHCP frames.
        type: str
        choices:
        - enable
        - add-or-forward
      dhcp_opt82_nni:
        aliases: [dhcp-opt82-nni]
        type: str
        choices: [enable, disable, transparent, add-or-replace, add-or-forward]
        description:
        - DHCP option 82 handling on the NNI interface (C(dhcp-opt82-nni)); C(disable) is the device default.
        - With C(enable), C(add-or-replace) or C(add-or-forward) at least one of I(circuit_id_dhcp), I(remote_id_dhcp)
          or I(relay_id_dhcp) must be set (the device refuses it otherwise, VLAN MGT error 657); the module sends
          them in one command. Not settable in the command that creates the VLAN; sent as a separate command.
      dhcp_opt82_uplink:
        aliases: [dhcp-opt82-uplink]
        type: str
        choices: [enable, disable, transparent, add-or-replace, add-or-forward]
        description:
        - DHCP option 82 handling on the uplink interface (C(dhcp-opt82-uplink)); C(disable) is the device default.
        - With C(enable), C(add-or-replace) or C(add-or-forward) at least one of I(circuit_id_dhcp), I(remote_id_dhcp)
          or I(relay_id_dhcp) must be set (the device refuses it otherwise, VLAN MGT error 657); the module sends
          them in one command. Not settable in the command that creates the VLAN; sent as a separate command.
      circuit_id_dhcp:
        aliases: [circuit-id-dhcp]
        description:
        - Configure the DHCP option 82 circuit-id format.
        type: str
        choices:
        - physical-id
      remote_id_dhcp:
        aliases: [remote-id-dhcp]
        description:
        - Configure the DHCP option 82 remote-id format.
        type: str
        choices:
        - customer-id
      relay_id_dhcp:
        aliases: [relay-id-dhcp]
        description:
        - Enable DHCP relay-id insertion.
        type: str
        choices: [relay-id, disable]
      dhcp_linerate:
        aliases: [dhcp-linerate]
        description:
        - Enable DHCP line-rate information insertion.
        type: str
        choices: [notadd, addactuallinerate, addalllineparameters]
      pppoe_linerate:
        aliases: [pppoe-linerate]
        description:
        - Enable PPPoE line-rate information insertion.
        type: str
        choices: [notadd, addactuallinerate, addalllineparameters]
      dhcpv6_linerate:
        aliases: [dhcpv6-linerate]
        description:
        - Enable DHCPv6 line-rate information insertion.
        type: str
        choices: [notadd, addactuallinerate, addalllineparameters]
      pppoe_l2_encaps:
        aliases: [pppoe-l2-encaps]
        description:
        - Enable PPPoE Layer 2 encapsulation information insertion.
        type: str
        choices: [notadd, add]
      dhcp_l2_encaps:
        aliases: [dhcp-l2-encaps]
        description:
        - Enable DHCP Layer 2 encapsulation information insertion.
        type: str
        choices: [notadd, add]
      dhcpv6_l2_encaps:
        aliases: [dhcpv6-l2-encaps]
        description:
        - Enable DHCPv6 Layer 2 encapsulation information insertion.
        type: str
        choices: [notadd, add]
      l2_encaps1:
        aliases: [l2-encaps1]
        description:
        - Enable first Layer 2 encapsulation information insertion.
        type: str
        choices: [not-applicable, untagged, single-tagged, dual-tagged]
      pppoer_vlanaware:
        aliases: [pppoer-vlanaware]
        description:
        - Enable VLAN-aware PPPoE relay behavior.
        type: str
      dhcpr_vlanaware:
        aliases: [dhcpr-vlanaware]
        description:
        - Enable VLAN-aware DHCP relay behavior.
        type: str
        choices: [upto-1-uservlan, upto-2-uservlans, upto-untag-uservlan, system-default]
      dhcpv6r_vlanaware:
        aliases: [dhcpv6r-vlanaware]
        description:
        - Enable VLAN-aware DHCPv6 relay behavior.
        type: str
        choices: [upto-1-uservlan, upto-2-uservlans, upto-untag-uservlan, system-default]
      circuit_id_pppoe:
        aliases: [circuit-id-pppoe]
        description:
        - Configure the PPPoE circuit-id format.
        type: str
        choices:
        - physical-id
      remote_id_pppoe:
        aliases: [remote-id-pppoe]
        description:
        - Configure the PPPoE remote-id format.
        type: str
        choices:
        - customer-id
      dhcpv6_itf_id:
        aliases: [dhcpv6-itf-id]
        description:
        - Configure the DHCPv6 interface-id format.
        type: str
        choices:
        - physical-id
      dhcpv6_remote_id:
        aliases: [dhcpv6-remote-id]
        description:
        - Configure the DHCPv6 remote-id format.
        type: str
        choices:
        - customer-id
      dhcpv6_relay_id:
        aliases: [dhcpv6-relay-id]
        description:
        - Enable DHCPv6 relay-id insertion.
        type: str
        choices: [disable, duid-ll]
      dhcpv6_trst_port:
        aliases: [dhcpv6-trst-port]
        description:
        - Enable DHCPv6 trusted-port behavior.
        type: str
        choices: [trusted, untrusted]
      enterprise_number:
        aliases: [enterprise-number]
        description:
        - Configure the enterprise number used in DHCPv6 relay options.
        type: int
      vmac_translation:
        aliases: [vmac-translation]
        description:
        - Enable virtual MAC address translation.
        type: bool
      vmac_dnstr_filter:
        aliases: [vmac-dnstr-filter]
        description:
        - Enable virtual MAC downstream filter behavior.
        type: bool
      icmpv6_sec_fltr:
        aliases: [icmpv6-sec-fltr]
        description:
        - Enable ICMPv6 security filtering.
        type: bool
      new_secure_fwd:
        aliases: [new-secure-fwd]
        description:
        - Enable secure forwarding for the VLAN. On GPON and L2+ LT boards, this can only be controlled at S-VLAN level
        type: str
        choices:
        - inherit
        - enable
        - disable
      aging_time:
        aliases: [aging-time]
        description:
        - Configure MAC aging time in seconds; if default, the system-level value is applicable.
        type: int
      l2cp_transparent:
        aliases: [l2cp-transparent]
        description: Enable l2cp-transparent
        type: bool
      in_qos_prof_name:
        aliases: [in-qos-prof-name]
        description:
        - QoS ingress profile name
        type: str
      ipv4_mcast_ctrl:
        aliases: [ipv4-mcast-ctrl]
        description:
        - 'Enable ipv4 multicast control: forward ipv4 multicast frames in this VLAN'
        type: bool
      ipv6_mcast_ctrl:
        aliases: [ipv6-mcast-ctrl]
        description:
        - 'Enable ipv6 multicast control: forward ipv6 multicast frames in this VLAN'
        type: bool
      mac_mcast_ctrl:
        aliases: [mac-mcast-ctrl]
        description:
        - 'Enable mac multicast control: forward mac multicast frames in this VLAN'
        type: bool
      dis_proto_rip:
        aliases: [dis-proto-rip]
        description:
        - Disable rip-ipv4 protocol
        type: bool
      proto_ntp:
        aliases: [proto-ntp]
        description:
        - Enable ntp protocol
        type: bool
      dis_ip_antispoof:
        aliases: [dis-ip-antispoof]
        description:
        - Disable IP anti-spoofing
        type: bool
      unknown_unicast:
        aliases: [unknown-unicast]
        description:
        - Enable unknown unicast flooding
        type: bool
      pt2ptgem_flooding:
        aliases: [pt2ptgem-flooding]
        description:
        - Enable flooding on unicast GEM port
        type: bool
      mac_movement_ctrl:
        aliases: [mac-movement-ctrl]
        description:
        - Enable MAC movement in this VLAN
        type: bool
      cvlan4095passthru:
        description:
        - Enable C-VLAN 4095 tunneling behavior. Only applicable for S-VLAN CC forwarder
        type: str
        choices:
        - passthru
        - not-applicable
      arp_snooping:
        aliases: [arp-snooping]
        description:
        - Enable ARP snooping
        type: bool
      arp_polling:
        aliases: [arp-polling]
        description:
        - Enable ARP polling
        type: bool
      arp_polling_ip:
        aliases: [arp-polling-ip]
        description:
        - Configure ARP polling IP address in form of
        type: str
      mac_unauth:
        aliases: [mac-unauth]
        description:
        - 'Enable mac unauthorized default: forward the frame to this vlan if authorization failed'
        type: bool
  running_config:
    description:
      - 'Device native VLAN configuration to parse when I(state) is C(parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
- name: Gather VLAN facts from the device
  nokia.isam.isam_vlans:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_vlans:
    state: gathered
    config:
      - id: "100"
      - id: "stacked:200:10"

- name: Create or update a residential bridge VLAN
  nokia.isam.isam_vlans:
    state: merged
    config:
      - id: "100"
        name: "customers-100"
        mode: residential-bridge
        priority: 3
        new-broadcast: enable
        protocol-filter: pass-pppoe-ipoe
        dhcp-opt82-ext: add-or-forward
        circuit-id-dhcp: physical-id
        remote-id-dhcp: customer-id
        vmac-translation: true
        ipv4-mcast-ctrl: true
        arp-snooping: true

- name: Render VLAN commands without applying them
  nokia.isam.isam_vlans:
    state: rendered
    config:
      - id: "stacked:200:10"
        name: "wholesale-200-10"
        mode: cross-connect
        new-secure-fwd: enable
        pppoe-relay-tag: configurable
        unknown-unicast: false
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
    - The parse axis (C(failed) or C(unverified)) is reported at resource level under
      C(parse); C(failed) means the family parser could not process the reply,
      C(unverified) that no parser records its coverage of the reply (a read never claims
      a complete parse).
    - A named instance the device rejected (C(invalid token)) is missing from C(gathered)
      exactly like an absent one; the module also warns, naming the rejected selectors.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: list
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: list
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.vlans.vlans import (
    Vlans,
)


def main():
    """
    Main entry point for module execution

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=VlansArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Vlans(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
