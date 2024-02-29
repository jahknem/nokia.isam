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
module: isam_interfaces
version_added: 2.9
short_description: 'Manages interface attributes of Nokia ISAM MSAN devices.'
description: 'This module manages interface attributes of Nokia ISAM MSAN devices'
author: Jan Kuehnemund
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: A dictionary of options for vlans
    type: list
    elements: dict
    suboptions:
      id:
        type: int
        description: 
        - configure a specific VLAN
      name:
        description: 
        - The name of the VLAN
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
        description: skip vmac translation in dhcp option 61 even when vmac is enabled
      new-broadcast::
        type: str
        description: switch downstream broadcast frames (On GPON and L2+ LT boards, broadcast control for S+C L2 Forwarders can only be controlled at S-VLAN level, not individually at S+C-VLAN-port level)
        choices:
        - inherit
        - enable
        - disable
        default: inherit
      protocol-filter:
        type: str
        description: control protocol group filters
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
        - configure the format of the PPPoE relay tag
        - true                  ! pppoe tag with the current fixed format
        - false                 ! no pppoe tag
        - configurable          ! circuit-id-pppoe and remote-id-pppoe controlling format
        choices:
        - true
        - false
        - configurable
      drly-srv-usr-side:
        description:
        - enable DHCP(v4/v6) server transparency at the user side when DHCP(v4/v6) relay is enabled.Only applicable for CC forwarder
        - default = disable
        - enable                ! enable DHCP(v4/v6) server transparency at the user side when DHCP(v4/v6) relay is enabled.
        - disable               ! disable DHCP(v4/v6) server transparency at the user side when DHCP(v4/v6) relay is enabled.
        type: bool
        default: disable
      new-secure-fwd:
        description: 
        - enable secure forwarding for the VLAN (On GPON and L2+ LT boards, secure forwarding can only be controlled at S-VLAN level, not individually at S+C-VLAN-port level)
        - default = inherit
        - inherit               ! inherit new-secure-forwarding
        - disable               ! disable new-secure-forwarding
        - enable                ! enable new-secure-forwarding
        type: str
        choices:
        - inherit
        - enable
        - disable
      aging-time:
        description: 
        - configure MAC aging time in seconds; in case of default,the system-level value is applicable.
        - default = -1
        type: int
      l2cp-transparent:
        description: enable l2cp-transparent
        type: bool
      in-qos-prof-name:
        description:
        - QoS ingress profile name
        - default = default
        type: str
      ipv4-mcast-ctrl:
        description:
        - 'enable ipv4 multicast control: forward ipv4 multicast frames in this VLAN'
        type: bool
      ipv6-mcast-ctrl:
        description:
        - 'enable ipv6 multicast control: forward ipv6 multicast frames in this VLAN'
        type: bool
      mac-mcast-ctrl:
        description:
        - 'enable mac multicast control: forward mac multicast frames in this VLAN'
        type: bool
      dis-proto-rip:
        description:
        - disable rip-ipv4 protocol
        type: bool
      proto-ntp:
        description:
        - enable ntp protocol
        type: bool
      dis-ip-antispoof:
        description:
        - disable IP anti-spoofing
        type: bool
      unknown-unicast:
        description:
        - enable unknown unicast flooding
        type: bool
      pt2ptgem-flooding:
        description:
        - enable flooding on unicast GEM port
        type: bool
      mac-movement-ctrl:
        description:
        - enable mac movement in this vlan
        type: bool
      cvlan4095passthru:
        description:
        - enable C-VLAN 4095 tunneling behavior. Only applicable for S-VLAN CC forwarder
        type: str
        choices:
        - passthru
        - not-applicable
      arp-snooping:
        description:
        - enable arp snooping
        type: bool
      arp-polling:
        description:
        - enable arp polling
        type: bool
      arp-polling-ip:
        description:
        - configure ARP polling IP address in form of 
        - default = 0.0.0.0
        type: str
      mac-unauth:
        description:
        - 'enable mac unauthorized default : forward the frame to this vlan if authorization failed'
        type: bool
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.vlans.vlans import (
    Vlans,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
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
