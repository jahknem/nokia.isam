# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_pppox_relay_global module.
"""


class Pppox_relay_globalArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_pppox_relay_global (configure pppox-relay cross-connect global-session)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "pado_timeout": {"type": "int"},
                "pads_timeout": {"type": "int"},
                "max_pad_attempts": {"type": "int"},
                "trans_max_age": {"type": "int"},
                "cc_max_age": {"type": "int"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
