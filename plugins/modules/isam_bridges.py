#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_bridges
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_bridges
short_description: 'Manages bridge configuration on Nokia ISAM devices.'
description: 'Manages bridge configuration including ageing time, bridge ports, VLAN membership, and port parameters on Nokia ISAM devices.'
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
  - >-
    Attaching a VLAN to a bridge port on an ONT UNI needs a bandwidth profile on the
    UNI's upstream queue (C(isam_qos_interfaces) C(upstream_queue.bandwidth_profile)).
    Without it the device refuses the attachment with "VLAN MGT error 277 : Attach
    ingress QoS profile to VLAN port refused due to missing bandwidth profile".
options:
  config:
    description: The provided configuration
    type: dict
    suboptions:
      ageing_time:
        type: int
        description:
        - "optional parameter with default value: 300"
        - ageing timeout for dynamic macentries
        default: 300
      port:
        type: list
        elements: dict
        description:
        - This command allows the operator to specify various parameters applicable to a specific bridge port. These parameters determine the handling of frames on the bridge port.
        suboptions:
          port:
            type: str
            description:
            - identity of a port (e.g. uplink port, atm pvc, efm port, eth port, la group ...)
          pvid:
            type: int
            description:
            - 'optional parameter with default value: "stacked : 0 : 4097" The parameter is not visible during creation.default vlan id for untagged frames'
          default-priority:
            aliases: [default_priority]
            type: int
            description:
            - 'optional parameter with default value: 0'
            - priority to be set in upstream frames
          mac-learn-off:
            aliases: [mac_learn_off]
            type: bool
            description:
            - 'optional parameter'
            - 'disable mac learning on this port'
          max-unicast-mac:
            aliases: [max_unicast_mac]
            type: int
            description:
            - 'optional parameter with default value: 1'
            - 'maximum number of uncommited unicast macs on this port'
          qos-profile:
            aliases: [qos_profile]
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'qos profile to be used on this port'
          prio-regen-prof:
            aliases: [prio_regen_prof]
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'priority regen profile to be used on this port'
            choices:
            - 'none'
            - 'trusted-port'
            - 'best-effort'
            - 'cl-all-prio-3'
            - 'cl-all-prio-4'
            - 'background'
            - 'be-cl-voice'
            - 'be-cl-1d-voice'
            - 'be-voice'
            - 'l2-vpn-3'
            - 'l2-vpn-4'
            - '11'
            - '12'
            - '13'
            - '14'
            - '15'
            - '16'
            - '17'
            - '18'
            - '19'
            - '20'
            - '21'
            - '22'
            - '23'
            - '24'
            - '25'
            - '26'
            - '27'
            - '28'
            - '29'
            - '30'
            - '31'
            - '32'
          prio-regen-name:
            aliases: [prio_regen_name]
            type: str
            description:
            - 'optional parameter with default value: "none"'
            - 'priority regen profile name to be used on this port'
          max-committed-mac:
            aliases: [max-commited-mac, max_commited_mac, max_comitted_mac, max_committed_mac]
            type: int
            description:
            - 'optional parameter with default value: 65535'
            - 'maximum number of commited unicast macs on this port. 65535 means the committed value is the same as max-unicast-mac'
          mirror-mode:
            aliases: [mirror_mode]
            type: str
            description:
            - 'optional parameter with default value: "disable"'
            - flow mirroring mode of the bridge port
            choices:
            - 'disable'
            - 'overwrite-outer-vlan'
            - 'insert-mirror-vlan'
          mirror-vlan:
            aliases: [mirror_vlan]
            type: int
            description:
            - 'optional parameter with default value: 0. Range: [0...4093]'
            - vlan-id to be inserted into mirrored packets. This configuration value has no effect in case mirroring mode of the bridgeport is disabled (mirror-mode).
          pvid-tagging-flag:
            aliases: [pvid_tagging_flag]
            type: str
            description:
            - 'optional parameter with default value: "onu"'
            - pvid will be tagged in ONU or in OLT.
            choices:
            - 'onu'
            - 'olt'
          ds-pbit-mode:
            aliases: [ds_pbit_mode]
            type: str
            description:
            - 'optional parameter with default value: "auto"'
            - downstream p-bits mode
            - "auto : transparency for DSL and translated for GPON"
            - "translated : for known p-bits the inverse translation is performed in downstream; unknown p-bits are forwarded unchanged in downstream"
            - "transparency : all p-bits are forwarded unchanged in downstream"
            choices:
            - 'auto'
            - 'translated'
            - 'transparency'
            - 'filtervlanandpbit'
          outervlancapture:
            type: int
            description:
            - 'optional parameter with default value: 0. Range: [0...4093]'
            - Outer VLAN to be matched for mirroring the packets received on the bridge port.
            - Rendered as C(outervlancapture <vlan>); removal renders C(no outervlancapture).
          direction:
            type: str
            description:
            - 'optional parameter with default value: "bidirection"'
            - Direction in which packets are captured and mirrored.
            - Rendered as C(direction <value>); removal renders C(no direction).
            choices:
            - 'ingress'
            - 'egress'
            - 'bidirection'
          default_tpid:
            type: str
            description:
            - 'optional parameter with default value: "8100"'
            - Default outer TPID as a hex string (600-ffff), for example C(88a8).
            - Rendered as C(default-tpid <hex>); removal renders C(no default-tpid).
          vlan_tpid0:
            type: dict
            description:
            - The port's C(vlan-tpid0 0) sub-node (outer TPID entry 0).
            - Only reported when its TPID is not at the default (C(no tpid)).
            - Rendered as C(vlan-tpid0 0 tpid <hex>); removal renders C(vlan-tpid0 0 no tpid). The write forms repeat the device's read form and are not verified
              on a device.
            suboptions:
              tpid:
                type: str
                description:
                - TPID as a hex string.
          vlan_tpid1:
            type: dict
            description:
            - The port's C(vlan-tpid1 1) sub-node (outer TPID entry 1).
            - Only reported when its TPID is not at the default (C(no tpid)).
            - Rendered as C(vlan-tpid1 1 tpid <hex>); removal renders C(vlan-tpid1 1 no tpid). The write forms repeat the device's read form and are not verified
              on a device.
            suboptions:
              tpid:
                type: str
                description:
                - TPID as a hex string.
          vlan_id:
            type: list
            elements: dict
            description:
            - VLAN membership entries for the bridge port.
            suboptions:
              id:
                type: str
                description:
                - identity of a vlan
              tag:
                type: str
                description:
                - 'optional parameter with default value: "untagged"'
                - 'tag control for egress port'
                choices:
                - 'untagged'
                - 'single-tagged'
                - 'priority-tagged'
              l2fwder_vlan:
                type: str
                description:
                - 'optional parameter with default value: "stacked 0 : 4097"'
                - 'layer2 forwarder vlan id'
                - 'this is the canonical VLAN mapping attribute; it is always
                   rendered as the C(l2fwder-vlan) command and is also the key
                   reported when the device is configured with the obsolete
                   C(network-vlan) spelling'
              network_vlan:
                type: int
                description:
                - 'obsolete CLI alias of l2fwder_vlan, kept for backwards
                   compatibility'
                - 'the value is normalized to l2fwder_vlan and rendered as the
                   C(l2fwder-vlan) command; supplying both names with
                   different values fails'
                - 'prefer l2fwder_vlan in new configuration'
              vlan_scope:
                type: str
                description:
                - 'optional parameter with default value: "l2fwder"'
                - 'the vlan scope'
                - 'the C(network) value is an obsolete alternative replaced by
                   C(l2fwder) and is normalized to C(l2fwder); C(local) is passed
                   through unchanged'
                choices:
                - 'local'
                - 'l2fwder'
                - 'network'
              qos:
                type: str
                description:
                - 'optional parameter with default value: "none"'
                - 'the qos policy'
                default: none
              qos_profile:
                type: str
                description:
                - 'optional parameter with default value: "none"'
                - 'the qos profile'
                default: none
              prior_best_effort:
                type: boolean
                description:
                - 'optional parameter with default value: false'
                - 'enable best effort priority (value: 0)'
                default: False
              prior_background:
                type: boolean
                description:
                - 'optional parameter with default value: false'
                - 'enable background priority (value: 1)'
                default: False
              prior_spare:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable spare priority (value: 2)'
              prior_exc_effort:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable excellen effort priority (value: 3)'
              prior_ctrl_load:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable controlled load priority (value: 4)'
              prior_less_100ms:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable less than 100ms latency and jitter priority (value: 5)'
              prior_less_10ms:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable less than 10ms latency and jitter priority (value: 6)'
              prior_nw_ctrl:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable network controlled priority (value: 7)'
              in_qos_prof_name:
                type: str
                description:
                - 'optional parameter with default value: "name: Default_TC0"'
                - 'the input qos profile name'
              max_up_qos_policy:
                type: int
                description:
                - 'optional parameter with default value: "0"'
                - 'the maximum number of qos policy numbers on a VLAn port basis'
              max_ip_antispoof:
                type: int
                description:
                - 'optional parameter with default value: "65335"'
                - 'the maximum number of ip address number in IP antispoofing and/or ARP relay'
              max_unicast_mac:
                aliases: [max_unicaast_mac]
                type: int
                description:
                - 'optional parameter with default value: "65535"'
                - 'the maximum number of uncommited unicast macs adresses'
              max_ipv6_antispf:
                type: int
                description:
                - 'optional parameter with default value: "65335"'
                - 'the maximum number of ipv6 address number in IP antispoofing and/or ARP relay'
              mac_learn_ctrl:
                type: int
                description:
                - 'optional parameter with default value: "3"'
                - 'MAC address learned control up(1), down(2), inherit from bridgedPort(3)'
              min_cvlan_id:
                type: int
                description:
                - 'optional parameter with default value: "1"'
                - 'This object configures the lower boundary of CVLAN range for protocol awareness for S-VLAN cross-connect(Tunnel)'
              max_cvlan_id:
                type: int
                description:
                - 'optional parameter with default value: "4095"'
                - This object configures the upper boundary of CVLAN range for protocol awareness for S-VLAN cross-connect(Tunnel)
              ds-dedicated-q:
                aliases: [ds_dedicated_q]
                type: bool
                description:
                - 'optional parameter with default value: "disable"'
              tpid:
                type: str
                description:
                - 'optional parameter with default value: "8100"'
                - 'This object configures vlan port tpid in hex values'
                - Always reported as a string (for example C("8100")).
              inner_pbit_remark:
                type: str
                description:
                - VLAN port C(inner-pbit-remark) value, passed through verbatim.
                - Rendered as C(vlan-id <id> inner-pbit-remark <value>); removal renders C(vlan-id <id> no inner-pbit-remark).
                - No CLI help is available for this attribute; the write forms are not verified on a device.
              groupid:
                type: str
                description:
                - VLAN port C(groupid) value, passed through verbatim (reported as a string).
                - Rendered as C(vlan-id <id> groupid <value>); removal renders C(vlan-id <id> no groupid).
                - No CLI help is available for this attribute; the write forms are not verified on a device.
              usacceptframetype:
                type: str
                description:
                - VLAN port upstream acceptable frame type (C(usacceptframetype)), passed through verbatim.
                - Rendered as C(vlan-id <id> usacceptframetype <value>); removal renders C(vlan-id <id> no usacceptframetype).
                - No CLI help is available for this attribute; the write forms are not verified on a device.
              oltregenprofile:
                type: str
                description:
                - VLAN port OLT priority regeneration profile (C(oltregenprofile)), passed through verbatim.
                - Rendered as C(vlan-id <id> oltregenprofile <value>); removal renders C(vlan-id <id> no oltregenprofile).
                - No CLI help is available for this attribute; the write forms are not verified on a device.
              static_user:
                type: list
                elements: dict
                description:
                - Static subscriber IP addresses associated with this VLAN membership.
                suboptions:
                  ip_address:
                    type: str
                    description:
                    - Static subscriber IP address in CIDR notation.

  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(port[].port) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
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
# Gathered example
# Retrieve existing bridge configuration from the device
- name: Gather bridge facts
  nokia.isam.isam_bridges:
    state: gathered

# Merged example
# Configure bridge ageing time and port parameters
- name: Merge bridge configuration
  nokia.isam.isam_bridges:
    config:
      ageing_time: 300
      port:
        - port: "1/1/x1"
          pvid: 100
          default-priority: 0
          vlan_id:
            - id: "100"
              tag: "untagged"
    state: merged

# Rendered example
# Render bridge configuration as device-native commands (offline)
- name: Render bridge configuration
  nokia.isam.isam_bridges:
    config:
      ageing_time: 300
      port:
        - port: "1/1/x1"
          pvid: 100
          vlan_id:
            - id: "100"
              tag: "untagged"
    state: rendered

# Replaced example
- name: Replace bridge configuration
  nokia.isam.isam_bridges:
    config:
      ageing_time: 600
      port:
        - port: "1/1/x1"
          pvid: 200
          mac-learn-off: false
          vlan_id:
            - id: "200"
              tag: "single-tagged"
    state: replaced

# Deleted example
- name: Delete bridge port configuration
  nokia.isam.isam_bridges:
    config:
      port:
        - port: "1/1/x1"
    state: deleted

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_bridges:
    config:
      port:
        - port: 1/1/5/1/3/1/1
    state: gathered
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.bridges.bridges import (
    BridgesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.bridges.bridges import (
    Bridges,
)


def main():
    """
    Main entry point for module execution

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=BridgesArgs.argument_spec,
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

    result = Bridges(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
