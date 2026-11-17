# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


def _lst(options):
    return {"type": "list", "elements": "dict", "options": options}


def _dct(options):
    return {"type": "dict", "options": options}


_SSH_DISABLE_FLAGS = (
    "dis_hmac_sha_1", "dis_hmac_sha_1_96", "dis_hmac_sha2_256", "dis_hmac_sha2_512", "dis_hmac_md5",
    "dis_hmac_md5_96", "dis_aes", "dis_des_3", "dis_blowfish", "dis_des_56", "dis_cast_128_cbc",
    "dis_arcfour", "dis_aes_192_cbc", "dis_aes_256_cbc", "dis_aes_128_ctr", "dis_aes_192_ctr",
    "dis_aes_256_ctr", "dis_dh_grp1_sha1", "dis_dh_grp14_sha1", "dis_ecdh_nistp256",
)


def _ssh_server_profile():
    opts = {
        "server_retries": {"type": "int"},
        "idle_timeout": {"type": "int"},
        "server_host_key": {"type": "str"},
    }
    for flag in _SSH_DISABLE_FLAGS:
        opts[flag] = {"type": "bool"}
    return _dct(opts)


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
                "snmp_notify_views": _lst({
                    "name": {"type": "str", "required": True},
                    "subtree": {"type": "str"},
                    "type": {"type": "str"},
                }),
                "general": _dct({
                    "oper_policy_prio": {"type": "str"},
                    "login_banner": {"type": "str"},
                    "welcome_banner": {"type": "str"},
                    "login_setting": {"type": "str"},
                    "cli_session": {"type": "str"},
                    "unauth_fwd": {"type": "bool"},
                    "src_mac_check": {"type": "bool"},
                }),
                "default_profile": _dct({
                    "description": {"type": "str"},
                    "slot_numbering": {"type": "str"},
                    "prompt": {"type": "str"},
                    "terminal_timeout": {"type": "str"},
                    "permissions": {"type": "dict"},
                }),
                "password": _dct({
                    "min_length": {"type": "int"},
                    "min_num_numeric_char": {"type": "int"},
                    "min_num_special_char": {"type": "int"},
                    "mixed_case": {"type": "bool"},
                }),
                "ssh": _dct({
                    "server_profile": _ssh_server_profile(),
                    "access": _dct({
                        "protocol": {"type": "str"},
                        "cli": {"type": "str"},
                        "tl1": {"type": "str"},
                        "debug": {"type": "bool"},
                        "debugkernel": {"type": "bool"},
                    }),
                    "sftp_users": _lst({
                        "name": {"type": "str", "required": True},
                        "password": {"type": "str", "no_log": True},
                        "auth_type": {"type": "str"},
                        "key_type": {"type": "str"},
                    }),
                }),
                "tacacs": _dct({
                    "auth_super_user": {"type": "str"},
                    "operator_policy": {"type": "str"},
                }),
                "li": _dct({
                    "separate": {"type": "bool"},
                }),
                "slots": _lst({
                    "slot": {"type": "str", "required": True},
                    "debug_usb": {"type": "bool"},
                }),
                "domains": _lst({
                    "name": {"type": "str", "required": True},
                    "authenticator": {"type": "str"},
                    "vlan_id": {"type": "int"},
                    "primary_dns": {"type": "str"},
                    "second_dns": {"type": "str"},
                    "primary_nbns": {"type": "str"},
                    "second_nbns": {"type": "str"},
                    "sess_timeout": {"type": "int"},
                    "qos_policy": {"type": "str"},
                    "admin_down": {"type": "bool"},
                }),
                "filetransfer": _dct({
                    "protocol": {"type": "str"},
                    "tftp_rollovr": {"type": "bool"},
                    "servers": _lst({
                        "server": {"type": "str", "required": True},
                        "user_name": {"type": "str"},
                        "password": {"type": "str", "no_log": True},
                        "auth_type": {"type": "str"},
                        "key_type": {"type": "str"},
                    }),
                }),
                "peripheral_mgnt": _dct({
                    "mac_filters": _lst({
                        "index": {"type": "int", "required": True},
                        "filter": {"type": "str"},
                    }),
                }),
                "pae": _dct({
                    "port_access": {"type": "bool"},
                    "ports": _lst({
                        "port": {"type": "str", "required": True},
                        "initialize": {"type": "bool"},
                        "authenticator": _dct({
                            "controlled_port": {"type": "str"},
                            "quiet_period": {"type": "int"},
                            "tx_period": {"type": "int"},
                            "supp_timeout": {"type": "int"},
                            "server_timeout": {"type": "int"},
                            "max_req": {"type": "int"},
                            "re_auth_enabled": {"type": "bool"},
                            "re_auth_period": {"type": "int"},
                        }),
                        "ext_authenticator": _dct({
                            "authentication": {"type": "bool"},
                            "init_authreq_off": {"type": "bool"},
                            "handshake": {"type": "bool"},
                            "handshake_period": {"type": "int"},
                            "mac_auth": {"type": "bool"},
                            "mab_auth": {"type": "bool"},
                            "dyn_vlan_assign": {"type": "bool"},
                        }),
                    }),
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
