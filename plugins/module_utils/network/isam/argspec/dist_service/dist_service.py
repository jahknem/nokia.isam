# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_dist_serviceArgs(object):
    """The arg spec for the isam_dist_service module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "service_type": {
                    "type": "str",
                    "choices": ["unknown", "epipe", "p3pipe", "tls", "vprn", "ies", "mirror", "apipe", "fpipe", "ipipe", "cpipe"],
                    "default": "apipe",
                },
                "qos_profile": {"type": "str", "default": "none"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
