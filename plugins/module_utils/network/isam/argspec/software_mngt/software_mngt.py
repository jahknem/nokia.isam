# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Software_mngtArgs(object):
    """The arg spec for the isam_software_mngt module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "database": {
                    "type": "dict",
                    "options": {
                        "version": {"type": "str"},
                        "url": {"type": "str"},
                        "backup": {"type": "str"},
                        "backupv6": {"type": "str"},
                        "auto_backup_interval": {"type": "int"},
                    },
                },
                "oswp": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "primary_file_server_id": {"type": "str"},
                        "second_file_server_id": {"type": "str"},
                        "activate": {"type": "bool"},
                        "auto_verify": {"type": "bool"},
                        "admin_state": {"type": "bool"},
                    },
                },
                "sw_replacement_mode": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str"},
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
