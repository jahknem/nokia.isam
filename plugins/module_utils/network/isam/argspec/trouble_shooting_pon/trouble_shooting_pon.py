# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_trouble_shooting_pon module.
"""


class Trouble_shooting_ponArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_trouble_shooting_pon (configure trouble-shooting pon statistics)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "interfaces": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                    },
                },
                "threshold": {
                    "type": "dict",
                    "options": {
                        "interval": {"type": "int"},
                        "interfaces": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "name": {"type": "str", "required": True},
                                "bw_th_up": {"type": "int"},
                                "bw_th_dn": {"type": "int"},
                            },
                        },
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
