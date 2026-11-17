# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Qos_tcaArgs(object):
    """Argument spec for isam_qos_tca (per-port/queue threshold crossing alarms)."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "queue": {"type": "int", "required": True},
                "tca_enable": {"type": "bool"},
                "load_thresh": {"type": "int"},
                "dis_frame_th": {"type": "int"},
                "qpeak_usage_th": {"type": "int"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
