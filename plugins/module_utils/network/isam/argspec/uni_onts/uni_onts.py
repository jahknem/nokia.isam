# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Uni_ontsArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_uni_onts (configure uni ont tc-layer: TC-layer PM collection per UNI)."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "uni_idx": {"type": "str", "required": True},
                "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
