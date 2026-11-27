# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_xdsl_system module.
"""


class Xdsl_systemArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_xdsl_system (system-wide xDSL settings)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "auto_port_reset": {
                    "type": "dict",
                    "options": {
                        "enable": {"type": "bool"},
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
