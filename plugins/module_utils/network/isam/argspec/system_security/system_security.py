# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


def _lst(options):
    return {"type": "list", "elements": "dict", "options": options}


class Isam_system_securityArgs(object):
    """Argument spec for isam_system_security (configure system security)."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "operators": _lst({
                    "name": {"type": "str", "required": True},
                    "password": {"type": "str", "no_log": True},
                    "profile": {"type": "str"},
                    "prompt": {"type": "str"},
                    "description": {"type": "str"},
                    "more": {"type": "bool"},
                    "confirm_prompt": {"type": "bool"},
                    "bgn_time": {"type": "str"},
                    "end_time": {"type": "str"},
                }),
                "profiles": _lst({
                    "name": {"type": "str", "required": True},
                    "description": {"type": "str"},
                    "slot_numbering": {"type": "str"},
                    "prompt": {"type": "str"},
                    "password_timeout": {"type": "str"},
                    "terminal_timeout": {"type": "str"},
                    "permissions": {"type": "dict"},
                }),
                "snmp_communities": _lst({
                    "name": {"type": "str", "required": True, "no_log": True},
                    "host_address": {"type": "str"},
                    "context": {"type": "str"},
                    "privilege": {"type": "str"},
                    "read_view": {"type": "str"},
                    "write_view": {"type": "str"},
                    "notify_view": {"type": "str"},
                }),
                "snmp_views": _lst({
                    "name": {"type": "str", "required": True},
                    "subtree": {"type": "str"},
                    "type": {"type": "str"},
                }),
                "snmp_managers": _lst({
                    "name": {"type": "str", "required": True},
                    "destination": {"type": "str"},
                    "notify_profile": {"type": "str"},
                    "nt": {"type": "bool"},
                    "shub": {"type": "bool"},
                    "ihub": {"type": "bool"},
                    "epon": {"type": "bool"},
                    "vvpsa": {"type": "bool"},
                    "xvps1": {"type": "bool"},
                    "xvps2": {"type": "bool"},
                    "xvps3": {"type": "bool"},
                    "xvps4": {"type": "bool"},
                    "xvps5": {"type": "bool"},
                    "xvps6": {"type": "bool"},
                    "xvps7": {"type": "bool"},
                    "xvps8": {"type": "bool"},
                }),
                "snmp_notify_profiles": _lst({
                    "name": {"type": "str", "required": True},
                    "snmp_version": {"type": "str"},
                }),
                "radius_auth_servers": _lst({
                    "name": {"type": "str", "required": True},
                    "router_instance": {"type": "str"},
                    "ip_address": {"type": "str"},
                    "secret": {"type": "str", "no_log": True},
                    "port": {"type": "int"},
                    "timeout_limit": {"type": "int"},
                    "dead_interval": {"type": "int"},
                    "retry_limit": {"type": "int"},
                    "admin_down": {"type": "bool"},
                }),
                "radius_policies": _lst({
                    "name": {"type": "str", "required": True},
                    "nas_id": {"type": "str"},
                    "nas_ip_address": {"type": "str"},
                    "keep_domain_name": {"type": "bool"},
                    "disable_accnt_msg": {"type": "bool"},
                    "disable_eap": {"type": "bool"},
                    "acc_interval": {"type": "int"},
                    "auth_server": {"type": "str"},
                    "auth_router_inst": {"type": "str"},
                    "acc_server": {"type": "str"},
                    "acc_router_inst": {"type": "str"},
                    "priority": {"type": "int"},
                }),
                "radius_auth_super_user": {
                    "type": "dict",
                    "options": {
                        "operator_policy": {"type": "str"},
                        "aut_s_unreach_act": {"type": "str"},
                    },
                },
                "radius_dyn_auth_clients": _lst({
                    "name": {"type": "str", "required": True},
                    "ip_address": {"type": "str"},
                    "secret": {"type": "str", "no_log": True},
                    "router_instance": {"type": "str"},
                }),
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
