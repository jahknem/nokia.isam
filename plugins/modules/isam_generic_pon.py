#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_generic_pon
short_description: Manage the global generic PON settings.
description:
  - Manages C(configure generic-pon) dpinteg-threshold, utilization (incl. thresholds), ont and alarmflag settings.
  - A value equal to the device default counts as unset; facts do not report defaults.
  - C(deleted) resets the named sections, and within a section only the named settings; without I(config) every setting.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided generic PON configuration.
    type: dict
    suboptions:
      dpinteg_threshold:
        description: Data path integrity threshold (C(configure generic-pon dpinteg-threshold)); mandatory value without removal form, only set when given.
        type: int
      utilization:
        description: PON utilization PM collection (C(configure generic-pon utilization)).
        type: dict
        suboptions:
          pon_pmcollect:
            description: C(configure generic-pon utilization pon-pmcollect); device default C(none).
            type: str
            choices: [none, pm-enable, tca-enable]
          ont_pmcollect:
            description: C(configure generic-pon utilization ont-pmcollect); device default C(disable).
            type: str
            choices: [enable, disable]
          threshold:
            description: PON utilization TCA thresholds (C(configure generic-pon utilization threshold)), C(disabled) or a value.
            type: dict
            suboptions:
              txmcutilhi:
                description: C(configure generic-pon utilization threshold txmcutilhi); device default C(disabled).
                type: str
              txmcutilmd:
                description: C(configure generic-pon utilization threshold txmcutilmd); device default C(disabled).
                type: str
              txmcutillo:
                description: C(configure generic-pon utilization threshold txmcutillo); device default C(disabled).
                type: str
              txtotutilhi:
                description: C(configure generic-pon utilization threshold txtotutilhi); device default C(disabled).
                type: str
              txtotutilmd:
                description: C(configure generic-pon utilization threshold txtotutilmd); device default C(disabled).
                type: str
              txtotutillo:
                description: C(configure generic-pon utilization threshold txtotutillo); device default C(disabled).
                type: str
              rxtotutilhi:
                description: C(configure generic-pon utilization threshold rxtotutilhi); device default C(disabled).
                type: str
              rxtotutilmd:
                description: C(configure generic-pon utilization threshold rxtotutilmd); device default C(disabled).
                type: str
              rxtotutillo:
                description: C(configure generic-pon utilization threshold rxtotutillo); device default C(disabled).
                type: str
              dbacongperiodhi:
                description: C(configure generic-pon utilization threshold dbacongperiodhi); device default C(disabled).
                type: str
              dbacongperiodmd:
                description: C(configure generic-pon utilization threshold dbacongperiodmd); device default C(disabled).
                type: str
              dbacongperiodlo:
                description: C(configure generic-pon utilization threshold dbacongperiodlo); device default C(disabled).
                type: str
              txucdropfrmhi:
                description: C(configure generic-pon utilization threshold txucdropfrmhi); device default C(disabled).
                type: str
              txucdropfrmmd:
                description: C(configure generic-pon utilization threshold txucdropfrmmd); device default C(disabled).
                type: str
              txucdropfrmlo:
                description: C(configure generic-pon utilization threshold txucdropfrmlo); device default C(disabled).
                type: str
              txmcdropfrmhi:
                description: C(configure generic-pon utilization threshold txmcdropfrmhi); device default C(disabled).
                type: str
              txmcdropfrmmd:
                description: C(configure generic-pon utilization threshold txmcdropfrmmd); device default C(disabled).
                type: str
              txmcdropfrmlo:
                description: C(configure generic-pon utilization threshold txmcdropfrmlo); device default C(disabled).
                type: str
              txbcdropfrmhi:
                description: C(configure generic-pon utilization threshold txbcdropfrmhi); device default C(disabled).
                type: str
              txbcdropfrmmd:
                description: C(configure generic-pon utilization threshold txbcdropfrmmd); device default C(disabled).
                type: str
              txbcdropfrmlo:
                description: C(configure generic-pon utilization threshold txbcdropfrmlo); device default C(disabled).
                type: str
              rxtotdropfrmhi:
                description: C(configure generic-pon utilization threshold rxtotdropfrmhi); device default C(disabled).
                type: str
              rxtotdropfrmmd:
                description: C(configure generic-pon utilization threshold rxtotdropfrmmd); device default C(disabled).
                type: str
              rxtotdropfrmlo:
                description: C(configure generic-pon utilization threshold rxtotdropfrmlo); device default C(disabled).
                type: str
              numtcint:
                description: C(configure generic-pon utilization threshold numtcint); device default C(disabled).
                type: str
              numtcintdba:
                description: C(configure generic-pon utilization threshold numtcintdba); device default C(disabled).
                type: str
              dbacongthresh:
                description: C(configure generic-pon utilization threshold dbacongthresh); device default C(disabled).
                type: str
      ont:
        description: ONT settings (C(configure generic-pon ont)).
        type: dict
        suboptions:
          slid_mode:
            description: C(configure generic-pon ont slid-mode); device default C(ascii).
            type: str
            choices: [ascii, hexa-dec]
          sn_bundle_timer:
            description: C(configure generic-pon ont sn-bundle-timer); device default C(24).
            type: int
          sw_ver_mis_block:
            description: C(configure generic-pon ont sw-ver-mis-block); device default C(enable).
            type: str
            choices: [enable, disable]
          sn_autounlock:
            description: C(configure generic-pon ont sn-autounlock); device default C(disable).
            type: str
            choices: [enable, disable]
      alarmflag:
        description: Alarm flags (C(configure generic-pon alarmflag)).
        type: dict
        suboptions:
          ponlos_alarm_ctrl:
            description: C(configure generic-pon alarmflag ponlos-alarm-ctrl); device default C(disable).
            type: str
            choices: [enable, disable]
  running_config:
    description:
      - 'Device native configuration to parse.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather generic PON configuration
  nokia.isam.isam_generic_pon:
    state: gathered

- name: Configure dpinteg-threshold
  nokia.isam.isam_generic_pon:
    config:
      dpinteg_threshold: "50"
    state: merged
"""

RETURN = """
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With C(deleted) and I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With C(deleted) and I(running_config) (offline preview of the removal) they are rendered only, never
    sent.
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
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import (
    Generic_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.generic_pon.generic_pon import (
    Generic_pon,
)


def main():
    module = AnsibleModule(
        argument_spec=Generic_ponArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Generic_pon(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
