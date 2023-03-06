#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ethernet_line
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_equipment
short_description: 'Manages equipment attributes of nokia isam.'
description: |
  configure
    ethernet
      line
        (if-index)
        port-type
        [no] admin-up
        tca-line-threshold
          [no] enable
          [no] los
          [no] fcs
          [no] rx-octets
          [no] tx-octets
          [no] los-day
          [no] fcs-day
          [no] rx-octets-day
          [no] tx-octets-day
        mau
          (index)
          type
          power
          [no] speed-auto-sense
          [no] autonegotiate
          [no] cap100base-tfd
          [no] cap1000base-xfd
          [no] cap1000base-tfd
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - 'Tested against isam-release: R6.2.04m'
options:
  config:
    description: |
      This command allows the operator to configure the ethernet line.
      > configure ethernet line (if-index) [ port-type <ETHITF::PortType> ] [ [ no ] admin-up ]
    type: list
    elements: dict
    suboptions:
      if_index:
        type: str
        description: interface index of the port
        required: true
      port_type:
        type: str
        description: 
        - optional parameter with default value "uni" 
        - the whole network service model based on this interface.
        choices:
        - "uni"
        - "nni"
        - "hc-uni"
        - "uplink"
      admin_up:
        type: bool
        description: 
        - optional parameter 
        - admin status is up (read-only for voicefxs interface).        
      tca_line_threshold:
        type: dict
        description: |
          This command allows the operator to configure the Threshold Crossing Alert (TCA) thresholds. The configuration is specific per ethernet line.
          > configure ethernet line (if-index) tca-line-threshold [ [ no ] enable ] [ no los | los <ETHITF::TcaThresholdLOS> ] [ no fcs | fcs <ETHITF::TcaThresholdFCS> ] [ no rx-octets | rx-octets <ETHITF::TcaThresholdMB> ] [ no tx-octets | tx-octets <ETHITF::TcaThresholdMB> ] [ no los-day | los-day <ETHITF::TcaThresholdLOS> ] [ no fcs-day | fcs-day <ETHITF::TcaThresholdFCS> ] [ no rx-octets-day | rx-octets-day <ETHITF::TcaThresholdMB> ] [ no tx-octets-day | tx-octets-day <ETHITF::TcaThresholdMB> ]
        suboptions:
          enable:
            type: bool
            description: |
              optional parameter
              enable the reporting of TCA's for this ethernet line
          los:
            type: int
            description: |
              optional parameter with default value: 0
              loss of signal error in 15 minute
            default: 0
          fcs:
            type: int
            description: |
              optional parameter with default value: 0
              frame check sequence error in 15 minute
              Format
              - the tca threshold value (frames), 0 - disable
            default: 0
          rx_octets:
            type: int
            description: |
              optional parameter with default value: 0
              receive octets in 15 minute (specify in MB)
              Format:
              - the tca threshold value (specify octets in MB), 0 - disable
            default: 0
          tx_octets:
            type: int
            description: |
              optional parameter with default value: 0
              transmit octets in 15 minute (specify in MB)
              Format:
              - the tca threshold value (specify octets in MB), 0 - disable
            default: 0
          los_day:
            type: int
            description: |
              optional parameter with default value: 0
              loss of signal error in 24 hour
              Format:
              - the tca threshold value (times), 0 - disable
            default: 0
          fcs_day:
            type: int
            description: |
              optional parameter with default value: 0
              frame check sequence error in 24 hour
              Format:
              - the tca threshold value (frames), 0 - disable
            default: 0
          rx_octets_day:
            type: int
            description: |
              optional parameter with default value: 0
              receive octets in 24 hour (specify in MB)
              Format:
              - the tca threshold value (specify octets in MB), 0 - disable
            default: 0
          tx_octets_day:
            type: int
            description: |
              optional parameter with default value: 0
              transmit octets in 24 hour (specify in MB)
              Format:
              - the tca threshold value (specify octets in MB), 0 - disable
            default: 0
      mau:
        type: list
        elements: dict
        description: |
          This command allows the operator to configure the MAU (Media Access Unit) parameters. The configuration is specific per ethernet line.
          > configure ethernet line (if-index) mau (index) [ type <Ether::MAUType> ] [ power <ETHITF::Power> ] [ [ no ] speed-auto-sense ] [ [ no ] autonegotiate ] [ [ no ] cap100base-tfd ] [ [ no ] cap1000base-xfd ] [ [ no ] cap1000base-tfd ]
        suboptions:
          index:
            type: int
            description: index of the MAU
          mau_type:
            description: |
              optional parameter
              the mau type
              - 10baset : UTP 10M
              - 100basetxhd : UTP 100M half duplex
              - 100basetxfd : UTP 100M full duplex
              - 100basefxhd : X fiber over PMT half
              - 100basefxhd : X fiber over PMT half duplex
              - 100basefxfd : X fiber over PMT full duplex
              - 1000basexhd : PCS/PMA,unknown PMD, half duplex
              - 1000basexfd : PCS/PMA,unknown PMD, full duplex
              - 1000baselxhd : fiber over long-wavelength laser half
              duplex
              - 1000baselxfd : fiber over long-wavelength laser full duplex
              - 1000basesxhd : fiber over short-wavelength laser half
              duplex
              - 1000basesxfd : fiber over short-wavelength laser full
              duplex
              - 1000basethd : UTP 1G half duplex
              - 1000basetfd : UTP 1G full duplex
              - 10gbasex : fiber 10G ethernet, PCS 8B/10B
              - 10gbaser : fiber 10G ethernet, PCS 64B/66B
              - 10gbaseer : fiber 10G ethernet extended reach, 30km
              - 10gbaselr : fiber 10G ethernet long reach, 10km
              - 10gbasesr : fiber 10G ethernet short reach, 300m
              - 100basebx10d : one single-mode fiber OLT long
              wavelength, 10km, 100 base
              - 100basebx10u : one single-mode fiber ONU, long
              wavelength, 10km, 100 base
              - 100baselx10 : two single-mode fibers over long
              wavelength, 10km, 100 base
              - 1000basebx10d : one single-mode fiber OLT over long
              wavelength, 10km, 1000 base
              - 1000basebx10u : one single-mode fiber ONU over long
              wavelength, 10km, 1000 base
              - 1000baselx10 : two single-mode fibers over long
              wavelength, 10km, 1000 base
              - 2500basex : single-mode fibers, 2.5G base
              - 10gbasetfd : UTP 10G full duplex
            type: str
            choices:
              - 10baset
              - 100basetxhd
              - 100basetxfd
              - 100basefxhd
              - 100basefxhd
              - 100basefxfd
              - 1000basexhd
              - 1000basexfd
              - 1000baselxhd
              - 1000baselxfd
              - 1000basesxhd
              - 1000basesxfd
              - 1000basethd
              - 1000basetfd
              - 10gbasex
              - 10gbaser
              - 10gbaseer
              - 10gbaselr
              - 10gbasesr
              - 100basebx10d
              - 100basebx10u
              - 100baselx10
              - 1000basebx10d
              - 1000basebx10u
              - 1000baselx10
              - 2500basex
              - 10gbasetfd
          power:
            description: |
              optional parameter
              the power mode of the MAU
              - up : power on
              - down : power off
            type: str
            choices:
              - up
              - down
          speed_auto_sense:
            type: bool
            description: |
              optional parameter
              enable autosensing  fiber speed on this port
          autonegotiate:
            type: bool
            description: |
              optional parameter
              enable auto-negotiation on this port
          cap100base_tfd:
            type: bool
            description: |
              optional parameter
              advertise 100M electrical
          cap1000base_xfd:
            type: bool
            description: |
              optional parameter
              advertise 1G optical
          cap1000base_tfd:
            type: bool
            description: |
              optional parameter
              advertise 1G electrical
  running_config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source. There are times when it is not
        desirable to have the task get the current running-config for
        every task in a playbook. The I(running_config) argument allows the
        implementer to pass in the configuration to use as the base
        config for comparison.
    type: str
  state:
    description:
    - The state of the configuration after module completion.
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
import debugpy

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ethernet_line.ethernet_line import (
    Ethernet_lineArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ethernet_line.ethernet_line import (
    Ethernet_line,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    debugpy.listen(("localhost",3000))
    debugpy.wait_for_client()
    debugpy.breakpoint()
    module = AnsibleModule(
        argument_spec=Ethernet_lineArgs.argument_spec,
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

    result = Ethernet_line(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
