#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_profiles
short_description: Manages Nokia ISAM XDSL profile resources.
description:
  - Manages C(configure xdsl) service-profile, spectrum-profile, dpbo-profile,
    vect-profile, and vce-profile configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    type: dict
    description: Grouped XDSL profile configuration.
    suboptions:
      service_profiles:
        type: list
        elements: dict
        description: Service profile configuration entries.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          active:
            type: bool
            description: Whether the profile is active.
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile.
          max_bitrate_down:
            type: int
            description: Maximum downstream bitrate.
          max_bitrate_up:
            type: int
            description: Maximum upstream bitrate.
          max_delay_down:
            type: int
            description: Maximum downstream delay.
          max_delay_up:
            type: int
            description: Maximum upstream delay.
      spectrum_profiles:
        type: list
        elements: dict
        description: Spectrum profile configuration entries.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          active:
            type: bool
            description: Whether the profile is active.
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile.
          dis_ansi_t1413:
            type: bool
            description: Disable ANSI T1.413 mode.
          dis_etsi_dts:
            type: bool
            description: Disable ETSI DTS mode.
          dis_g992_1_a:
            type: bool
            description: Disable G.992.1 Annex A mode.
          dis_g992_1_b:
            type: bool
            description: Disable G.992.1 Annex B mode.
          dis_g992_2_a:
            type: bool
            description: Disable G.992.2 Annex A mode.
          dis_g992_3_a:
            type: bool
            description: Disable G.992.3 Annex A mode.
          dis_g992_3_b:
            type: bool
            description: Disable G.992.3 Annex B mode.
          g992_5_b:
            type: bool
            description: Enable G.992.5 Annex B mode.
          g992_5_aj:
            type: bool
            description: Enable G.992.5 Annex AJ mode.
          dis_etsi_ts:
            type: bool
            description: Disable ETSI TS mode.
          g993_2_17a:
            type: bool
            description: Enable G.993.2 profile 17a mode.
          rf_band_list:
            type: str
            description: RF band list value.
      dpbo_profiles:
        type: list
        elements: dict
        description: DPBO profile configuration entries.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          active:
            type: bool
            description: Whether the profile is active.
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile.
          es_elect_length:
            type: int
            description: E-side electrical length.
          es_cable_model_a:
            type: int
            description: E-side cable model A value.
          es_cable_model_b:
            type: int
            description: E-side cable model B value.
          es_cable_model_c:
            type: int
            description: E-side cable model C value.
          min_usable_signal:
            type: int
            description: Minimum usable signal value.
          min_frequency:
            type: int
            description: Minimum frequency.
          max_frequency:
            type: int
            description: Maximum frequency.
          rs_elect_length:
            type: int
            description: R-side electrical length.
      vect_profiles:
        type: list
        elements: dict
        description: Vectoring profile configuration entries.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          active:
            type: bool
            description: Whether the profile is active.
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile.
          band_control_up:
            type: str
            description: Upstream band control value.
          band_control_dn:
            type: str
            description: Downstream band control value.
      vce_profiles:
        type: list
        elements: dict
        description: VCE profile configuration entries.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          active:
            type: bool
            description: Whether the profile is active.
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile.
          vce_join_timeout:
            type: str
            description: VCE join timeout value.
  running_config:
    type: str
    description: Device-native C(info configure xdsl ...) output for parsed state.
  state:
    type: str
    description: Desired resource state.
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- nokia.isam.isam_xdsl_profiles:
    config:
      service_profiles:
        - id: 11
          name: YPLAY-30-Privat
          version: 1
          max_bitrate_down: 33000
          max_bitrate_up: 5500
          active: true
    state: merged
"""

RETURN = """
commands:
  description: Commands sent to the device.
  returned: when changed
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered XDSL profile facts.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed XDSL profile facts.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_profiles.xdsl_profiles import (
    Xdsl_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_profiles.xdsl_profiles import (
    Xdsl_profilesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_profiles.xdsl_profiles import (
    Xdsl_profiles,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_profilesArgs.argument_spec,
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

    if module.params["state"] == "parsed":
        template = Xdsl_profilesTemplate()
        result = {
            "changed": False,
            "parsed": template.normalize(template.parse(module.params.get("running_config"))),
        }
    elif module.params["state"] == "gathered":
        ansible_facts = {"ansible_network_resources": {}}
        facts = Xdsl_profilesFacts(module).populate_facts(get_resource_connection(module), ansible_facts)
        result = {
            "changed": False,
            "gathered": facts.get("ansible_network_resources", {}).get("xdsl_profiles", {}),
        }
    else:
        result = Xdsl_profiles(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
