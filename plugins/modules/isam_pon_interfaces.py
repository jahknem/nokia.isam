#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

DOCUMENTATION = """
module: isam_pon_interfaces
short_description: Manages Nokia ISAM PON interface attributes.
description:
  - Resource module for C(configure pon interface).
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: PON interface configuration entries.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: PON interface index.
      label:
        type: str
        description: Label of the PON port.
      fec_dn:
        type: str
        choices: [enable, disable]
        description: Downstream FEC setting.
       ber_calc_period: {type: int, description: BER calculation period (1-864000 deciseconds).}
       polling_period: {type: int, description: PON polling period (1-864000 deciseconds).}
       sig_degrade_th: {type: int, description: Signal degradation threshold (4-10).}
       sig_fail_th: {type: int, description: Signal failure threshold (3-8).}
      raman_reduct:
        type: str
        choices: [enable, disable]
        description: Raman reduction setting.
       closest_ont: {type: int, description: Closest ONT distance in km (0-40; XGS 0-20).}
       diff_reach: {type: int, choices: [20, 34, 40], description: Differential reach in km.}
       pon_tag: {type: str, description: Up to 16 hexadecimal characters.}
       pon_id: {type: str, description: Up to 8 hexadecimal characters.}
      mcast_encrypt:
        type: str
        choices: [enable, disable]
        description: Multicast encryption setting.
      auth_method: {type: str, description: PON authentication method.}
      ponid_interval:
        type: int
        description: Interval to send GPON-ID PLOAM message in seconds.
      ponid_odn:
        type: str
        choices: [a, b, bplus, c, cplus, auto]
        description: ODN profile used for PON-ID handling.
       ponid_identifier:
         type: str
         description: Exactly 14 hexadecimal characters.
       tconts_per_frame:
         type: int
         description: Maximum number of TCONT containers per upstream frame (0-64).
       max_ranging_onts: {type: int, description: Maximum number of ranging ONTs (0-128).}
      pon_speed: {type: str, description: PON speed mode.}
      burst_overhead: {type: str, description: Burst overhead mode.}
      onu_prov_mode: {type: str, description: ONU provisioning mode.}
      admin_state:
        type: str
        choices: [up, down]
        description: Administrative state of the interface.
      tc_layer:
        description: TC-layer performance monitoring settings.
        type: dict
        suboptions:
          pm_collect:
            type: str
            choices: [none, pm-enable, tca-enable]
            description: OLT-side aggregate TC layer PM mode.
           tca_enable:
             type: bool
             description: Convenience flag mapping to tc-layer pm-collect tca-enable when true.
       tc_layer_threshold:
         type: dict
         suboptions:
           error_frags_up: {type: str, description: Errored-fragments threshold or disabled.}
       mcast_tc_layer:
         type: dict
         suboptions:
           pm_collect: {type: str, choices: [enable, disable]}
       phy_layer:
         type: dict
         suboptions:
           pm_collect: {type: str, choices: [enable, disable]}
       fec_tc_layer:
         type: dict
         suboptions:
           pm_collect: {type: str, choices: [enable, disable]}
       xg_tc_layer:
         type: dict
         suboptions:
           pm_collect: {type: str, choices: [enable, disable]}
       otdr:
         type: dict
         suboptions:
           mode: {type: str, choices: [enable, disable, test]}
       utilization:
         type: dict
         description: PON and ONT utilization performance monitoring.
       deact_ont_tca:
         type: dict
         description: Deactivated-ONT detection thresholds.
  running_config:
    type: str
    description: Native running configuration for parsed state.
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
    description: Module state.
"""

EXAMPLES = """
- name: Render PON interface commands
  nokia.isam.isam_pon_interfaces:
    config:
      - name: 1/1/1/1
        label: access-pon-1
        fec_dn: enable
        ponid_interval: 10
        ponid_identifier: '00000000000001'
        tconts_per_frame: 44
        admin_state: down
        tc_layer:
          pm_collect: tca-enable
    state: rendered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted)
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Gathered resource facts.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Parsed structured data from I(running_config).
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_interfaces.pon_interfaces import Pon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_interfaces.pon_interfaces import Pon_interfaces


def _validate_pon_config(module):
    """Validate constraints that depend on more than one PON field."""
    for item in module.params.get("config") or []:
        name = item["name"]
        if not re.match(
            r"^(?:\d+/\d+/\d+/\d+|(?:x-pon|25g-pon):\d+/\d+/\d+/\d+)$", name
        ):
            module.fail_json(msg="Invalid PON interface name: %s" % name)
        if item.get("label") is not None and len(item["label"]) > 80:
            module.fail_json(msg="PON label must not exceed 80 characters")
        for field, limit in (("pon_tag", 16), ("pon_id", 8)):
            value = item.get(field)
            if value is not None and (
                len(value) > limit or not re.match(r"^[0-9A-Fa-f]*$", value)
            ):
                module.fail_json(msg="%s must contain at most %d hexadecimal characters" % (field, limit))
        identifier = item.get("ponid_identifier")
        if identifier is not None and not re.match(r"^[0-9A-Fa-f]{14}$", identifier):
            module.fail_json(msg="ponid_identifier must contain exactly 14 hexadecimal characters")
        if (
            item.get("sig_degrade_th") is not None
            and item.get("sig_fail_th") is not None
            and item["sig_degrade_th"] <= item["sig_fail_th"]
        ):
            module.fail_json(msg="sig_degrade_th must be greater than sig_fail_th")
        if name.startswith("x-pon:") and item.get("closest_ont") is not None and item["closest_ont"] > 20:
            module.fail_json(msg="closest_ont must be between 0 and 20 for XGS PON")
        if name.startswith("x-pon:") and item.get("diff_reach") is not None and item["diff_reach"] not in (20, 40):
            module.fail_json(msg="diff_reach must be 20 or 40 for XGS PON")


def main():
    module = AnsibleModule(
        argument_spec=Pon_interfacesArgs.argument_spec,
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

    _validate_pon_config(module)

    result = Pon_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
