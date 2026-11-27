from __future__ import absolute_import, division, print_function


class Isam_security_ext_authenticatorArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "required": True,
            "elements": "dict",
            "options": {
                "port": {"type": "str", "required": True},
                "clear_statistics": {"type": "bool", "default": False},
            },
        },
    }
