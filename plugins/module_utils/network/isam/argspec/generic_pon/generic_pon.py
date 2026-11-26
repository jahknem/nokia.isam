# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import TABLE


class Generic_ponArgs(object):
    """The arg spec for the isam_generic_pon module (generated from its attribute table)."""

    argument_spec = {
        "config": {"type": "dict", "options": TABLE.argument_spec()},
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
