#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ont_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_bridge
short_description: 'Manages <> attributes of isam <resource>.'
description: 'Manages <> attributes of isam <resource>'
version_added: 1.0.0
author: Ansible Network Engineer
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: list
    elements: dict
    suboptions:
      ont_idx:
        description: The ont index
        type: int
      battery_bkup:
        description: battery backup
        type: bool
      berint:
        description: accumulation interval (in number of downstream frames) for ONU BER calculation
        type: int
      desc1:
        description: 
        - free-form textual field for user to describe the ONT
        type: str
      desc2:
        description: 
        - free-form textual field for user to describe the ONT
        type: str
      provversion:
        description: 
        - 'optional parameter with default value: "*"'
        - the provisioned version number
        type: str
      sernum:
        description: 
        - 'optional parameter with default value: "ALCL : 00000000"'
        - serial number of the ONT
        type: str
      subslocid:
        description: 
        - 'optional parameter'
        - subscriber location id (SLID)
        type: str
      sw_ver_pland:
        description:
        - mandatory parameter
        - planned ONT software version number. If sw-dnload-version is set to disabled, sw-ver-pland cannot be set to delayactivate.
        required: True
      fec_up:
        description: 
        - 'optional parameter with default value: "disable,ng2 : enable"'
        - enable/disable use of FEC in Upstream direction
        type: bool
      bridge_map_mode:
        description: 
        - 'optional parameter with default value: "1-mp-bridge-map-filter"'
        - ont bridge map mode
        type: str
        choices:
        - '1-mp-bridge-map-filter'
        - 'n-p-bridge-map-filter'
        - 'n-mp-bridge-map-filter'
      pwr_shed_prof_id:
        description: 
        - 'optional parameter with default value: "none"'
        - power shed profile id
        type: int
      ont_enable:
        description: 
        - 'optional parameter with default'
        - 'value: "auto"'
        - 'ONT disabling decision for rogue'
        - 'ONTs'
        type: bool
      p2p_enable:
        description: 
        - 'optional parameter with default value: "disable"'
        - allow port-to-port traffic exchange between ethernet UNIs on the same ONT
        type: bool
      optics_hist:
        description: 
        - 'optional parameter with default value: "disable"'
        - daily optical supervision measurements collection
        type: bool
      sw_dnload_version:
        description: 
        - 'optional parameter with default value: "DISABLED"'
        - standby ONT software version number to be downloaded. If sw-ver-pland is set to delayactivate, sw-dnload-version cannot be set to disabled.
        type: str
      plnd_var:
        description: 
        - 'optional parameter with default value: ""'
        - planned variant of the ONT hardware version.Use DO for Data-only ONTs,SIP for SIP ONTs,H.248 for MEGACO ONTs
        type: str
      rf_filter:
        description: 
        - 'optional parameter with default value: "pass-low-high"'
        - enable/disable use of RF filter in Upstream direction
        type: str
        choices:
        - 'pass-low-high'
        - 'pass-low-middle'
        - 'pass-low'
        - 'pass-none'
      us_police_mode:
        description: 
        - 'optional parameter with default value: "local"'
        - mode of policing in Upstream direction
        type: str
        choices:
        - 'local'
        - 'remote'
        - 'network'
      enable_aes:
        description: 
        - 'optional parameter with default value: "disable"'
        - AES encryption for all bi-directional GEM ports
        type: bool
      voip_allowed:
        description: 
        - 'optional parameter with default value: "disable"'
        - voip support on ONT
        type: str
        choices:
        - 'enable'
        - 'disable'
        - 'iphost'
        - 'veip'
      iphc_allowed:
        description: 
        - 'optional parameter with default value: "disable"'
        - IPHC support on ONT
        type: bool
      slid_visibility:
        description: 
        - 'optional parameter with default value: "disabled"'
        - visibility of subscriber location id (SLID) of the interface
        type: str
        choices:
        - 'disabled'
        - 'enabled-slid-on'
        - 'enabled-all'
      log_auth_id:
        description: 
        - 'optional parameter with default value: ""'
        - the logical id for the ont
        type: int
      log-auth-pwd:
        description: 
        - 'optional parameter with default value: ""'
        - the password for the ont
        - 'Possible values:'
        - '- prompt : prompts the operator for a password'
        - '- plain : the password in plain text'
        type: str
      cvlantrans_mode:
        description: 
        - 'optional parameter with default value: "remote"'
        - cvlan translation settings for all traffic except the configured multicast traffic
        type: str
        choices:
        - 'remote'
        - 'local'
      sn_bundle_ctrl:
        description: 
        - 'optional parameter with default value: "unbundle"'
        - sn bundling behavior associated with slid/loid
        type: str
        choices:
        - 'unbundle'
        - 'bundle'
        - 'auto'
      pland_cfgfile1:
        description: 
        - 'optional parameter with default value: "DISABLED"'
        - indicate the cfgfile1 version to be planned
        - 'possible values: auto'
        type: str
      pland_cfgfile2:
        description: 
        - 'optional parameter with default value: "DISABLED"'
        - indicate the cfgfile2 version to be planned
        - 'possible values: auto'
        type: str
      dnload_fgfile1:
        description: 
        - 'optional parameter with default value: "DISABLED"'
        - indicate the cfgfile1 version to be downloaded
        - 'possible values: auto'
        type: str
      dnload_cfgfile2:
        description: 
        - 'optional parameter with default value: "DISABLED"'
        - indicate the cfgfile2 version to be downloaded
        - 'possible values: auto'
        type: str
      us_tcpolice_mode:
        description: 
        - 'optional parameter with default value: "local"'
        - mode of policing in Upstream direction
        type: str
        choices:
        - 'local'
        - 'remote'
      planned_us_rate:
        description:
        - 'optional parameter with default value: "nominal-line-rate"'
        - planned upstream rate
        choices:
        - 'nominal-line-rate'
        - '2.5G'
        - '10G'
      admin-state:
        description: 
        - 'optional parameter with default value: "up"'
        - administrative state of the ONT
        type: str
        choices:
        - 'up'
        - 'down'
      oltdscppbitalign:
        description: 
        - 'optional parameter with default value: "disable"'
        - if OLT need perform DSCP to Pbit alignment for this ONU, when the DSCP to Pbit alignment is configured on the vlan port
        type: bool
      pref_channel_pair:
        description: 
        - 'optional parameter with default value: "none"'
        - preferred channel pair for the ONT in case of ngpon2
        type: str
      prot-channel-pair:
        description: 
        - 'optional parameter with default value: "none"'
        - protecting channel pair for the ONT in case of ngpon2
        type: str
      alt_pref_ch_pair:
        description: 
        - 'optional parameter with default value: "none"'
        - alternate preferred channel pair for the ONT in case of ngpon2
        type: str
      ratelimit_us_dhcp:
        description: 
        - 'optional parameter with default value: "10"'
        - ratelimit for upstream DHCP traffic, unit is pps which means packets per second
        type: int
      ratelimit-us-arp:
        description: 
        - 'optional parameter with default value: "10"'
        - ratelimit for upstream ARP traffic, unit is pps which means packets per second
        type: int
      flush-mac:
        description: 
        - 'optional parameter with default value: "disable"'
        - flush MAC decision for UNIs of this ONT
        type: bool
    
  state:
    description:
    - The state the configuration should be left in
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
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ont_interfaces.ont_interfaces import (
    Ont_interfacesArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ont_interfaces.ont_interfaces import (
    Ont_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ont_interfacesArgs.argument_spec,
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

    result = Ont_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
