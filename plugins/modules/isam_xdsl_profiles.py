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
