#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.linetest.linetest import LinetestArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.linetest.linetest import Linetest


DOCUMENTATION = r'''
---
module: isam_linetest
short_description: Manage Nokia ISAM LineTest configuration
description:
  - Supports declarative single LineTest session and parameter configuration.
  - Sends only configuration commands; it does not execute LineTest actions.
options:
  config:
    type: dict
    description: Declarative LineTest configuration to render.
  running_config:
    type: str
    description: Output from C(info configure linetest) for parsed state.
  state:
    description: Desired resource state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
'''


def main():
    module = AnsibleModule(
        argument_spec=LinetestArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", state, ["config"]]
            for state in ("merged", "replaced", "overridden", "rendered")
        ] + [["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Linetest(module).execute_module())


if __name__ == "__main__":
    main()
