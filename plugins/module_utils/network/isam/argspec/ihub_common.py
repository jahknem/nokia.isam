"""Pure-data schemas for read-only IHUB resource projections."""

from copy import deepcopy


SAP_OPTIONS = {"id": {"type": "str", "required": True}, "shutdown": {"type": "bool"}, "description": {"type": "str"}}
INTERFACE_OPTIONS = {"name": {"type": "str", "required": True}, "address": {"type": "str"},
                     "shutdown": {"type": "bool"}, "description": {"type": "str"},
                     "saps": {"type": "list", "elements": "dict", "options": SAP_OPTIONS}}
COMMON = {"id": {"type": "str", "required": True}, "shutdown": {"type": "bool"}, "description": {"type": "str"}}
PORT = dict(COMMON, ethernet={"type": "dict", "options": {
    "speed": {"type": "int"}, "lldp": {"type": "list", "elements": "dict", "options": {
        "destination": {"type": "str", "required": True}, "admin_status": {"type": "str"},
        "tx_tlvs": {"type": "list", "elements": "str"},
    }},
}})
LAG = dict(COMMON, ports={"type": "list", "elements": "str"}, lacp={"type": "dict", "options": {
    "mode": {"type": "str", "choices": ["active", "passive"]}, "administrative_key": {"type": "int"},
}})
SERVICE = dict(COMMON, service_type={"type": "str", "required": True, "choices": ["vpls", "ies"]},
               customer_id={"type": "str"}, vpls_type={"type": "str", "choices": ["v-vpls"]}, vlan_id={"type": "int"},
               stp={"type": "dict", "options": {"shutdown": {"type": "bool"}}},
               saps={"type": "list", "elements": "dict", "options": SAP_OPTIONS},
               interfaces={"type": "list", "elements": "dict", "options": INTERFACE_OPTIONS})
SCHEMAS = {
    "ihub_ports": {"type": "list", "elements": "dict", "options": PORT},
    "ihub_lags": {"type": "list", "elements": "dict", "options": LAG},
    "ihub_services": {"type": "dict", "options": {
        "customers": {"type": "list", "elements": "dict", "options": {"id": COMMON["id"], "description": COMMON["description"]}},
        "services": {"type": "list", "elements": "dict", "options": SERVICE},
    }},
}


def argument_spec(resource):
    return {"config": deepcopy(SCHEMAS[resource]), "running_config": {"type": "str"},
            "state": {"type": "str", "choices": ["gathered", "parsed"], "default": "gathered"},
            "allow_broad_read": {"type": "bool", "default": False}}
