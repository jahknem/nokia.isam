# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Qos_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_qos_interfaces module."""

    _queue_options = {
        "id": {"type": "int", "required": True},
        "priority": {"type": "int"},
        "weight": {"type": "int"},
        "oper_weight": {"type": "int"},
        "queue_profile": {"type": "str"},
        "shaper_profile": {"type": "str"},
    }

    _upstream_queue_options = {
        "id": {"type": "int", "required": True},
        "priority": {"type": "int"},
        "weight": {"type": "int"},
        "bandwidth_profile": {"type": "str"},
        "ext_bw": {"type": "str"},
        "bandwidth_sharing": {"type": "str"},
        "queue_profile": {"type": "str"},
        "shaper_profile": {"type": "str"},
    }

    _ds_rem_queue_options = {
        "id": {"type": "int", "required": True},
        "priority": {"type": "int"},
        "weight": {"type": "int"},
    }

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "scheduler_node": {"type": "str"},
                "ingress_profile": {"type": "str"},
                "cac_profile": {"type": "str"},
                "ext_cac": {"type": "str"},
                "ds_queue_sharing": {"type": "bool"},
                "us_queue_sharing": {"type": "bool"},
                "ds_num_queue": {"type": "str"},
                "ds_num_rem_queue": {"type": "str"},
                "us_num_queue": {"type": "str"},
                "queue_stats_on": {"type": "bool"},
                "autoschedule": {"type": "bool"},
                "oper_weight": {"type": "int"},
                "oper_rate": {"type": "int"},
                "us_vlanport_queue": {"type": "bool"},
                "dsfld_shaper_prof": {"type": "str"},
                "bandwidth_profile": {"type": "str"},
                "bandwidth_sharing": {"type": "str"},
                "aggr_usq_profile": {"type": "str"},
                "aggr_dsq_profile": {"type": "str"},
                "gem_sharing": {"type": "str"},
                "scheduler_mode": {"type": "str"},
                "mc_scheduler_node": {"type": "str"},
                "bc_scheduler_node": {"type": "str"},
                "ds_schedule_tag": {"type": "str"},
                "queue": {
                    "type": "list",
                    "elements": "dict",
                    "options": _queue_options,
                },
                "upstream_queue": {
                    "type": "list",
                    "elements": "dict",
                    "options": _upstream_queue_options,
                },
                "ds_rem_queue": {
                    "type": "list",
                    "elements": "dict",
                    "options": _ds_rem_queue_options,
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
