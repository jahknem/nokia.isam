# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class L2uni_ontsArgs(object):  # pylint: disable=R0903
    """Argument spec for isam_l2uni_onts (configure l2uni ont: per-UNI PM settings and TC-layer thresholds)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "performance_monitor": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "uni_idx": {"type": "str", "required": True},
                        "pm_collect": {"type": "str", "choices": ["none", "pm-enable", "tca-enable"]},
                        "pm_collect_64bit": {"type": "str", "choices": ["none", "pm-enable"]},
                        "pm_collect_ext": {
                            "type": "dict",
                            "options": {
                                "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
                                "p_bits": {"type": "int"},
                                "vlan_id": {"type": "int"},
                            },
                        },
                    },
                },
                "tc_layer_threshold": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "uni_idx": {"type": "str", "required": True},
                        "dropped_frames_up": {"type": "int"},
                        "dropped_frames_dn": {"type": "int"},
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
