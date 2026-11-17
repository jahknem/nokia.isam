# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_xdsl_inm module.
"""

_SENSOR = {
    "type": "list",
    "elements": "dict",
    "options": {
        "name": {"type": "str", "required": True},
        "inm_mode": {"type": "str"},
        "inm_eq_inp_mode": {"type": "str"},
        "ins_sensitivity": {"type": "str"},
        "inm_cluster_cont": {"type": "str"},
        "inm_iat_offset": {"type": "str"},
        "inm_iat_step": {"type": "str"},
    },
}


class Xdsl_inmArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_xdsl_inm (impulse noise monitoring sensors)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "near_end": dict(_SENSOR),
                "far_end": dict(_SENSOR),
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
