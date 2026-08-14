from __future__ import absolute_import, division, print_function


class EfmOamArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "admin_up": {"type": "bool"},
                "passive_mode": {"type": "bool"},
                "keep_alive_intvl": {"type": "str"},
                "response_intvl": {"type": "str"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
