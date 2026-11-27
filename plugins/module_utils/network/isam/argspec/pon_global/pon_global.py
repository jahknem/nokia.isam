# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_pon_global module.
"""


class Pon_globalArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_pon_global (configure pon)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "pwrbrst_mode": {"type": "str", "choices": ["disable", "enable"]},
                "range_mode": {"type": "str", "choices": ["normal", "alientolerant"]},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
