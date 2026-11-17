# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_xdsl_onts module.
"""


class Xdsl_ontsArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_xdsl_onts (xDSL settings of xDSL ONTs)."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ont_idx": {"type": "str", "required": True},
                "dpbo_profile": {"type": "str"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
