from __future__ import absolute_import, division, print_function


class L2cpArgs(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "name": {"type": "str", "required": True},
            "partition_type": {"type": "str", "choices": ["no-partition", "fixed-assigned"], "default": "no-partition"},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
