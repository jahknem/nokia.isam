#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_voice_sip
short_description: Manages voice SIP configuration on Nokia ISAM.
description:
  - Manages the C(configure voice sip) resources including registrar, proxy, codec, and sip-profile settings.
version_added: 1.0.0
author: Jan Kuehnemund
options:
  config:
    description: Voice SIP configuration.
    type: dict
    suboptions:
      registrar:
        description: SIP registrar settings.
        type: dict
        suboptions:
          server:
            description: Registrar server address.
            type: str
          port:
            description: Registrar server port.
            type: int
          realm:
            description: Registrar realm.
            type: str
      proxy:
        description: SIP proxy settings.
        type: dict
        suboptions:
          server:
            description: Proxy server address.
            type: str
          port:
            description: Proxy server port.
            type: int
      codec:
        description: SIP codec entries.
        type: list
        elements: dict
        suboptions:
          priority:
            description: Codec priority.
            type: int
            required: true
          type:
            description: Codec type.
            type: str
      sip_profile:
        description: SIP profile entries.
        type: list
        elements: dict
        suboptions:
          name:
            description: SIP profile name.
            type: str
            required: true
          timer_t1:
            description: SIP timer T1 value.
            type: int
          timer_t2:
            description: SIP timer T2 value.
            type: int
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: Desired resource state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather voice SIP config
  nokia.isam.isam_voice_sip:
    state: gathered

- name: Render voice SIP config
  nokia.isam.isam_voice_sip:
    state: rendered
    config:
      registrar:
        server: 10.0.0.1
        port: 5060
        realm: example.com
      proxy:
        server: 10.0.0.2
        port: 5060
      codec:
        - priority: 1
          type: g711a
        - priority: 2
          type: g711u
      sip_profile:
        - name: default
          timer_t1: 500
          timer_t2: 4000
"""

RETURN = """
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured voice SIP data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured voice SIP data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import (
    Isam_voice_sipArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.voice_sip.voice_sip import (
    Isam_voice_sip,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_voice_sipArgs.argument_spec,
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

    result = Isam_voice_sip(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
