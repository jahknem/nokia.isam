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
