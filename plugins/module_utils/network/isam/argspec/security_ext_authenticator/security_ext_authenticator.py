from __future__ import absolute_import, division, print_function


class Isam_security_ext_authenticatorArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "port": {"type": "str", "required": True},
                "clear_statistics": {"type": "bool", "default": False},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["rendered", "parsed"],
            "default": "rendered",
        },
    }
