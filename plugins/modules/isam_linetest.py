#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.linetest.linetest import LinetestArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.linetest.linetest import Linetest


DOCUMENTATION = r'''
---
module: isam_linetest
short_description: Parse and render safe Nokia ISAM LineTest configuration
description:
  - Supports declarative single LineTest session and parameter configuration.
  - Does not execute LineTest actions or send configuration to a device.
options:
  config:
    type: dict
    description: Declarative LineTest configuration to render.
  running_config:
    type: str
    description: Output from C(info configure linetest) for parsed state.
  state:
    type: str
    choices: [rendered, parsed, gathered]
    default: rendered
'''


def main():
    module = AnsibleModule(
        argument_spec=LinetestArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Linetest(module).execute_module())


if __name__ == "__main__":
    main()
