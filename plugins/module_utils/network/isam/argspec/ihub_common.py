"""Argument specs of the read-only IHUB resource modules.

``config`` of these modules is an instance *selection*, not configuration: it filters
the parsed whole-source read by identity (``id``; services by ``service_type`` and
``id``). It therefore accepts only the identity keys; the parsed projection returned in
``gathered``/``parsed`` carries the full typed configuration (see ihub_config).
"""

from copy import deepcopy


IDENTITY = {"id": {"type": "str", "required": True}}
SELECTIONS = {
    "ihub_ports": {"type": "list", "elements": "dict", "options": IDENTITY},
    "ihub_lags": {"type": "list", "elements": "dict", "options": IDENTITY},
    "ihub_services": {"type": "dict", "options": {
        "customers": {"type": "list", "elements": "dict", "options": IDENTITY},
        "services": {"type": "list", "elements": "dict", "options": dict(
            IDENTITY, service_type={"type": "str", "required": True, "choices": ["vpls", "ies"]})},
    }},
}


def argument_spec(resource):
    return {"config": deepcopy(SELECTIONS[resource]), "running_config": {"type": "str"},
            "state": {"type": "str", "choices": ["gathered", "parsed"], "default": "gathered"},
            "allow_broad_read": {"type": "bool", "default": False}}
