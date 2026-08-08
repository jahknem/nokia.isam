# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_systemArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_system module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "id": {
                    "type": "dict",
                    "options": {
                        "name": {"type": "str"},
                        "location": {"type": "str"},
                        "contact": {"type": "str"},
                        "node_id": {"type": "str"},
                        "nt_intercon_vlan": {"type": "int"},
                        "internal_nw_vlan": {"type": "int"},
                        "system_mac": {"type": "str"},
                    },
                },
                "security": {
                    "type": "dict",
                    "options": {
                        "ssh": {"type": "bool"},
                        "telnet": {"type": "bool"},
                        "snmp": {"type": "bool"},
                    },
                },
                "sntp": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "server_ip_addr": {"type": "str"},
                        "port": {"type": "int"},
                        "poll_interval": {"type": "int"},
                        "polling_rate": {"type": "int"},
                        "enabled": {"type": "bool"},
                        "timezone_offset": {"type": "int"},
                        "servers": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "ip_address": {"type": "str", "required": True},
                                "priority": {"type": "int"},
                            },
                        },
                    },
                },
                "syslog": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "facility": {"type": "str"},
                        "severity": {"type": "str"},
                        "destinations": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "name": {"type": "str", "required": True},
                                "type": {"type": "str"},
                            },
                        },
                        "routes": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "destination": {"type": "str", "required": True},
                                "msg_type": {"type": "str"},
                                "facility": {"type": "str"},
                                "severities": {"type": "list", "elements": "str"},
                            },
                        },
                    },
                },
                "sync_if_timing": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str"},
                        "source": {"type": "str"},
                    },
                },
                "transaction": {
                    "type": "dict",
                    "options": {
                        "timeout": {"type": "int"},
                        "log_full_action": {"type": "str"},
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }
