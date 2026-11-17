class CfmArgs(object):
    """Argument specification for the documented CFM command tree."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "domains": {"type": "list", "elements": "dict"},
                "slm": {
                    "type": "dict",
                    "options": {
                        "inactivity_time": {"type": "int"},
                    },
                },
                "y1731pm": {"type": "list", "elements": "dict"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
