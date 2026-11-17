# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_equipmentArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_equipment module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "shelves": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "planned_type": {"type": "str"},
                    },
                },
                "slots": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "planned_type": {"type": "str"},
                        "unlock": {"type": "bool"},
                        "admin_state": {
                            "type": "str",
                            "choices": ["locked", "unlocked"],
                        },
                    },
                },
                "appliques": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "planned_type": {"type": "str"},
                    },
                },
                "protection_groups": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "int", "required": True},
                        "admin_status": {
                            "type": "str",
                            "choices": ["lock", "unlock"],
                        },
                        "eps_quenchfactor": {"type": "int"},
                    },
                },
                "diagnostics_sfp": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "rssi_prof_id": {"type": "int"},
                        "rssi_state": {"type": "str"},
                    },
                },
                "protection_elements": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "redcy_ctrl_status": {"type": "str"},
                    },
                },
                "racks": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "description": {"type": "str"},
                    },
                },
                "external_link_assigns": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "remote": {"type": "str"},
                    },
                },
                "external_link_hosts": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True},
                        "direction": {"type": "str"},
                    },
                },
                "envbox": {
                    "type": "dict",
                    "options": {
                        "enable_supervise": {"type": "bool"},
                    },
                },
                "isam": {
                    "type": "dict",
                    "options": {
                        "description": {"type": "str"},
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
