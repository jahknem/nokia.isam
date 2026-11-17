# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

_PBIT = ["svlanpbitbased", "cvlanpbitbased"]
_RATE_BURST = {
    "sustained_rate": {"type": "int"},
    "burst_size": {"type": "int"},
}


class Qos_globalArgs(object):
    """Argument spec for isam_qos_global (global configure qos settings)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "general": {
                    "type": "dict",
                    "options": {
                        "atm_overhead_fact": {"type": "int"},
                        "eth_efm_fact": {"type": "int"},
                        "enable_alignment": {"type": "bool"},
                        "cac_mode": {"type": "str", "choices": ["nocac", "msr", "alr"]},
                        "use_dei": {"type": "bool"},
                        "set_dei": {"type": "bool"},
                    },
                },
                "line_cards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "buffer_occ_thresh": {"type": "int"},
                        "queue_stats": {"type": "bool"},
                        "dsload_tca": {"type": "bool"},
                        "dsload_thresh": {"type": "int"},
                        "buffer_tca": {"type": "bool"},
                        "up_buf_thresh": {"type": "int"},
                        "up_obc_thresh": {"type": "int"},
                        "dn_obc_thresh": {"type": "int"},
                        "dn_buf_thresh": {"type": "int"},
                        "part_buf_thresh": {"type": "int"},
                    },
                },
                "dsl_ctrl_pkt_policer": {
                    "type": "dict",
                    "options": dict(_RATE_BURST, protocol_ctrl={"type": "str", "choices": ["police-arprip", "nopolice-arprip"]}),
                },
                "nni_ctrl_pkt_policer": {
                    "type": "dict",
                    "options": dict(_RATE_BURST),
                },
                "ctrl_pkt_policer": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(_RATE_BURST, protocol={"type": "str", "required": True}),
                },
                "pbit_scheduling": {
                    "type": "dict",
                    "options": {
                        "sc_xcon_us": {"type": "str", "choices": list(_PBIT)},
                        "sc_xcon_dn": {"type": "str", "choices": list(_PBIT)},
                        "sc_rb_us": {"type": "str", "choices": list(_PBIT)},
                        "sc_rb_dn": {"type": "str", "choices": list(_PBIT)},
                    },
                },
                "upstr_prot_dsl": {
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
