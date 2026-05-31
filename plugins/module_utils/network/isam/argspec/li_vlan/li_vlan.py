# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Li_vlanArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_li_vlan module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "vlan_id": {"type": "int", "aliases": ["vlan-id"]},
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
