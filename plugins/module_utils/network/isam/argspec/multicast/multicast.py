# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy

# configure igmp package (index) / configure mcast-control package (index)
PACKAGE_OPTIONS = {  # type: dict
    "index": {"type": "int", "required": True},
    "name": {"type": "str"},
    "template_name": {"type": "str"},
    "template_version": {"type": "int"},
}

# configure igmp system cdr-type / configure mcast-control system cdr-type
CDR_TYPE_OPTIONS = {  # type: dict
    "periodic": {"type": "bool"},
    "period": {"type": "int"},
    "attempt_max_pview": {"type": "bool"},
    "attempt_blackout": {"type": "bool"},
    "attempt_no_perm": {"type": "bool"},
}


def _system_options(mld):
    """configure igmp system (mld=False) / configure mcast-control system (mld=True)."""
    options = {"src_ip_address": {"type": "str"}}  # type: dict
    if mld:
        options["v6_src_ip_address"] = {"type": "str"}
    options.update({
        "verify_checksum": {"type": "bool"},
        "query_interval": {"type": "int"},
        "max_rsp_time": {"type": "int"},
        "robustness": {"type": "int"},
        "mem_query_int": {"type": "int"},
        "last_memb_cnt": {"type": "int"},
        "last_max_resp_tim": {"type": "int"},
        "host_report_intv": {"type": "int"},
        "start": {"type": "bool"},
        "preview_valid": {"type": "int"},
        "cdr_validation": {"type": "str"},
        "cdr_generation": {"type": "bool"},
        "except_cdr_rate": {"type": "int"},
        "cdr_export": {"type": "str", "choices": ["local-file-storage", "remote-logging"]},
        "cdr_file_aging": {"type": "int"},
        "cdr_polling": {"type": "int"},
        "user_igmp_version": {"type": "str", "choices": ["2", "3"]},
        "netw_igmp_version": {"type": "str", "choices": ["2", "3"]},
    })
    if mld:
        options["user_mld_version"] = {"type": "str", "choices": ["1", "2"]}
        options["netw_mld_version"] = {"type": "str", "choices": ["1", "2"]}
    options.update({
        "v3_max_num_rec": {"type": "int"},
        "forking": {"type": "bool"},
        "lt_ont_signaling": {"type": "bool"},
        "vlan_selection": {"type": "bool"},
        "disc_lwr_version": {"type": "bool"},
        "uncfg_mcast_supp": {"type": "str", "choices": ["legacy", "asmandssm"]},
        "cdr_type": {"type": "dict", "options": copy.deepcopy(CDR_TYPE_OPTIONS)},
    })
    return options


IGMP_OPTIONS = {  # type: dict
    "mcast_svc_context": {"type": "str"},
    "mld_snooping": {"type": "bool"},
    "mld_querier": {"type": "bool"},
    "igmp_snooping": {"type": "bool"},
    "igmp_querier": {"type": "bool"},
    "query_interval": {"type": "int"},
    "query_response_interval": {"type": "int"},
    "robustness_count": {"type": "int"},
    "system": {"type": "dict", "options": _system_options(False)},
    "packages": {"type": "list", "elements": "dict", "options": copy.deepcopy(PACKAGE_OPTIONS)},
}

MCAST_CONTROL_OPTIONS = {  # type: dict
    "mcast_svc_context": {"type": "str"},
    "admin_state": {"type": "bool"},
    "max_groups": {"type": "int"},
    "max_sources": {"type": "int"},
    "system": {"type": "dict", "options": _system_options(True)},
    "packages": {"type": "list", "elements": "dict", "options": copy.deepcopy(PACKAGE_OPTIONS)},
}


class MulticastArgs(object):
    """The arg spec for the isam_multicast module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "igmp": {
                    "type": "dict",
                    "options": copy.deepcopy(IGMP_OPTIONS),
                },
                "mcast_control": {
                    "type": "dict",
                    "options": copy.deepcopy(MCAST_CONTROL_OPTIONS),
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
