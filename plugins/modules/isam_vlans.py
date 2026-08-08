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
      sntp-proxy:
        type: bool
        description: If the VLAN should be configured as a SNTP proxy
      priority:
        type: int
        description:
        - 'The priority of the VLAN. Range: [0...7]'
      vmac-not-in-opt61:
        type: bool
        description: Skip vmac translation in dhcp option 61 even when vmac is enabled
      new-broadcast:
        type: str
        description: Control downstream broadcast frames.
        choices:
        - inherit
        - enable
        - disable
        default: inherit
      protocol-filter:
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
        default: pass-all
      pppoe-relay-tag:
        type: str
        description:
        - Configure the format of the PPPoE relay tag
        choices:
        - true
        - false
        - configurable
      drly-srv-usr-side:
        description:
        - Enable DHCP(v4/v6) server transparency at the user side when DHCP(v4/v6) relay is enabled. Only applicable for CC forwarder
        type: bool
        default: false
      dhcp-opt82-ext:
        description:
        - Configure DHCP option 82 handling for subscriber-side DHCP frames.
        type: str
        choices:
        - enable
        - add-or-forward
      dhcp-opt82-nni:
        description:
        - Enable DHCP option 82 processing on the network-to-network interface.
        type: bool
      dhcp-opt82-uplink:
        description:
        - Enable DHCP option 82 processing on uplink DHCP traffic.
        type: bool
      circuit-id-dhcp:
        description:
        - Configure the DHCP option 82 circuit-id format.
        type: str
        choices:
        - physical-id
      remote-id-dhcp:
        description:
        - Configure the DHCP option 82 remote-id format.
        type: str
        choices:
        - customer-id
      relay-id-dhcp:
        description:
        - Enable DHCP relay-id insertion.
        type: bool
      dhcp-linerate:
        description:
        - Enable DHCP line-rate information insertion.
        type: bool
      pppoe-linerate:
        description:
        - Enable PPPoE line-rate information insertion.
        type: bool
      dhcpv6-linerate:
        description:
        - Enable DHCPv6 line-rate information insertion.
        type: bool
      pppoe-l2-encaps:
        description:
        - Enable PPPoE Layer 2 encapsulation information insertion.
        type: bool
      dhcp-l2-encaps:
        description:
        - Enable DHCP Layer 2 encapsulation information insertion.
        type: bool
      dhcpv6-l2-encaps:
        description:
        - Enable DHCPv6 Layer 2 encapsulation information insertion.
        type: bool
      l2-encaps1:
        description:
        - Enable first Layer 2 encapsulation information insertion.
        type: bool
      pppoer-vlanaware:
        description:
        - Enable VLAN-aware PPPoE relay behavior.
        type: bool
      dhcpr-vlanaware:
        description:
        - Enable VLAN-aware DHCP relay behavior.
        type: bool
      dhcpv6r-vlanaware:
        description:
        - Enable VLAN-aware DHCPv6 relay behavior.
        type: bool
      circuit-id-pppoe:
        description:
        - Configure the PPPoE circuit-id format.
        type: str
        choices:
        - physical-id
      remote-id-pppoe:
        description:
        - Configure the PPPoE remote-id format.
        type: str
        choices:
        - customer-id
      dhcpv6-itf-id:
        description:
        - Configure the DHCPv6 interface-id format.
        type: str
        choices:
        - physical-id
      dhcpv6-remote-id:
        description:
        - Configure the DHCPv6 remote-id format.
        type: str
        choices:
        - customer-id
      dhcpv6-relay-id:
        description:
        - Enable DHCPv6 relay-id insertion.
        type: bool
      dhcpv6-trst-port:
        description:
        - Enable DHCPv6 trusted-port behavior.
        type: bool
      enterprise-number:
        description:
        - Configure the enterprise number used in DHCPv6 relay options.
        type: int
      vmac-translation:
        description:
        - Enable virtual MAC address translation.
        type: bool
      vmac-dnstr-filter:
        description:
        - Enable virtual MAC downstream filter behavior.
        type: bool
      icmpv6-sec-fltr:
        description:
        - Enable ICMPv6 security filtering.
        type: bool
      new-secure-fwd:
        description:
        - Enable secure forwarding for the VLAN. On GPON and L2+ LT boards, this can only be controlled at S-VLAN level
        type: str
        choices:
        - inherit
        - enable
        - disable
      aging-time:
        description:
        - Configure MAC aging time in seconds; if default, the system-level value is applicable.
        type: int
      l2cp-transparent:
        description: Enable l2cp-transparent
        type: bool
      in-qos-prof-name:
        description:
        - QoS ingress profile name
        type: str
      ipv4-mcast-ctrl:
        description:
        - 'Enable ipv4 multicast control: forward ipv4 multicast frames in this VLAN'
        type: bool
      ipv6-mcast-ctrl:
        description:
        - 'Enable ipv6 multicast control: forward ipv6 multicast frames in this VLAN'
        type: bool
      mac-mcast-ctrl:
        description:
        - 'Enable mac multicast control: forward mac multicast frames in this VLAN'
        type: bool
      dis-proto-rip:
        description:
        - Disable rip-ipv4 protocol
        type: bool
      proto-ntp:
        description:
        - Enable ntp protocol
        type: bool
      dis-ip-antispoof:
        description:
        - Disable IP anti-spoofing
        type: bool
      unknown-unicast:
        description:
        - Enable unknown unicast flooding
        type: bool
      pt2ptgem-flooding:
        description:
        - Enable flooding on unicast GEM port
        type: bool
      mac-movement-ctrl:
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
      arp-snooping:
        description:
        - Enable ARP snooping
        type: bool
      arp-polling:
        description:
        - Enable ARP polling
        type: bool
      arp-polling-ip:
        description:
        - Configure ARP polling IP address in form of
        type: str
      mac-unauth:
        description:
        - 'Enable mac unauthorized default: forward the frame to this vlan if authorization failed'
        type: bool
  running_config:
    description:
    - Device native VLAN configuration to parse when I(state) is C(parsed).
    type: str
  state:
    description:
    - The state the configuration should be left in.
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
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
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
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
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

    result = Vlans(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
