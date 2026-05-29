# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_xdsl_lines module.
"""


class Xdsl_linesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xdsl_lines module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True, "aliases": ["if_index"]},
                "service_profile": {"type": "str", "aliases": ["service-profile"]},
                "spectrum_profile": {"type": "str", "aliases": ["spectrum-profile"]},
                "dpbo_profile": {"type": "str", "aliases": ["dpbo-profile"]},
                "vect_profile": {"type": "str", "aliases": ["vect-profile"]},
                "admin_up": {"type": "bool", "aliases": ["admin-up"]},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }
