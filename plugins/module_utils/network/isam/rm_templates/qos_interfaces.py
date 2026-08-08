# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate


def _top_parser(field, cli_name, value_re=r"\S+", value_type="string"):
    result_filter = "|int" if value_type == "int" else "|string"
    return {
        "name": "interface.%s" % field,
        "compval": field,
        "getval": re.compile(
            r"""
            configure\sqos\sinterface\s(?P<name>\S+)\s((?P<negate>no\s%s)|%s\s(?P<%s>%s))
            $""" % (re.escape(cli_name), re.escape(cli_name), field, value_re),
            re.VERBOSE,
        ),
        "setval": "configure qos interface {{ name }} %s {{ %s }}" % (cli_name, field),
        "remval": "configure qos interface {{ name }} no %s" % cli_name,
        "result": {
            "{{ name }}": {
                "name": "{{ name }}",
                field: "{{ none if negate is defined else %s%s }}" % (field, result_filter),
            }
        },
    }


def _top_bool_parser(field, cli_name):
    return {
        "name": "interface.%s" % field,
        "compval": field,
        "getval": re.compile(
            r"""
            configure\sqos\sinterface\s(?P<name>\S+)\s((?P<negate>no\s%s)|(?P<%s>%s))
            $""" % (re.escape(cli_name), field, re.escape(cli_name)),
            re.VERBOSE,
        ),
        "setval": "configure qos interface {{ name }} {{ 'no ' if %s is sameas false else '' }}%s" % (field, cli_name),
        "remval": "configure qos interface {{ name }} no %s" % cli_name,
        "result": {
            "{{ name }}": {
                "name": "{{ name }}",
                field: "{{ false if negate is defined else true }}",
            }
        },
    }


def _queue_parser(list_name, field, cli_name, value_re=r"\S+", value_type="string", negatable=False):
    result_filter = "|int" if value_type == "int" else "|string"
    no_part = r"(?P<negate>no\s%s)|" % re.escape(cli_name) if negatable else ""
    return {
        "name": "interface.%s.%s" % (list_name, field),
        "compval": field,
        "getval": re.compile(
            r"""
            configure\sqos\sinterface\s(?P<name>\S+)\s%s\s(?P<id>\d+)\s(%s%s\s(?P<%s>%s))
            $""" % (re.escape(list_name.replace("_", "-")), no_part, re.escape(cli_name), field, value_re),
            re.VERBOSE,
        ),
        "setval": "configure qos interface {{ name }} %s {{ id }} %s {{ %s }}" % (list_name.replace("_", "-"), cli_name, field),
        "remval": "configure qos interface {{ name }} %s {{ id }} no %s" % (list_name.replace("_", "-"), cli_name),
        "result": {
            "{{ name }}": {
                "name": "{{ name }}",
                list_name: {
                    "{{ id }}": {
                        "id": "{{ id|int }}",
                        field: "{{ none if negate is defined else %s%s }}" % (field, result_filter),
                    }
                },
            }
        },
    }


class Qos_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Qos_interfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # This initial module intentionally covers the live-observed subset of the
    # large QoS interface grammar. Profile references are kept as raw CLI values
    # such as "none" or "name:PROFILE" so device-driven names round-trip safely.
    PARSERS = [
        _top_parser("scheduler_node", "scheduler-node"),
        _top_parser("ingress_profile", "ingress-profile"),
        _top_parser("cac_profile", "cac-profile"),
        _top_parser("ext_cac", "ext-cac"),
        _top_bool_parser("ds_queue_sharing", "ds-queue-sharing"),
        _top_bool_parser("us_queue_sharing", "us-queue-sharing"),
        _top_parser("ds_num_queue", "ds-num-queue"),
        _top_parser("ds_num_rem_queue", "ds-num-rem-queue"),
        _top_parser("us_num_queue", "us-num-queue"),
        _top_bool_parser("queue_stats_on", "queue-stats-on"),
        _top_bool_parser("autoschedule", "autoschedule"),
        _top_parser("oper_weight", "oper-weight", value_re=r"\d+", value_type="int"),
        _top_parser("oper_rate", "oper-rate", value_re=r"\d+", value_type="int"),
        _top_bool_parser("us_vlanport_queue", "us-vlanport-queue"),
        _top_parser("dsfld_shaper_prof", "dsfld-shaper-prof"),
        _top_parser("bandwidth_profile", "bandwidth-profile"),
        _top_parser("bandwidth_sharing", "bandwidth-sharing"),
        _top_parser("aggr_usq_profile", "aggr-usq-profile"),
        _top_parser("aggr_dsq_profile", "aggr-dsq-profile"),
        _top_parser("gem_sharing", "gem-sharing"),
        _top_parser("scheduler_mode", "scheduler-mode"),
        _top_parser("mc_scheduler_node", "mc-scheduler-node"),
        _top_parser("bc_scheduler_node", "bc-scheduler-node"),
        _top_parser("ds_schedule_tag", "ds-schedule-tag"),
        _queue_parser("queue", "priority", "priority", value_re=r"\d+", value_type="int"),
        _queue_parser("queue", "weight", "weight", value_re=r"\d+", value_type="int"),
        _queue_parser("queue", "oper_weight", "oper-weight", value_re=r"\d+", value_type="int"),
        _queue_parser("queue", "queue_profile", "queue-profile"),
        _queue_parser("queue", "shaper_profile", "shaper-profile"),
        _queue_parser("upstream_queue", "priority", "priority", value_re=r"\d+", value_type="int", negatable=True),
        _queue_parser("upstream_queue", "weight", "weight", value_re=r"\d+", value_type="int", negatable=True),
        _queue_parser("upstream_queue", "bandwidth_profile", "bandwidth-profile", negatable=True),
        _queue_parser("upstream_queue", "ext_bw", "ext-bw", negatable=True),
        _queue_parser("upstream_queue", "bandwidth_sharing", "bandwidth-sharing", negatable=True),
        _queue_parser("upstream_queue", "queue_profile", "queue-profile", negatable=True),
        _queue_parser("upstream_queue", "shaper_profile", "shaper-profile", negatable=True),
        _queue_parser("ds_rem_queue", "priority", "priority", value_re=r"\d+", value_type="int", negatable=True),
        _queue_parser("ds_rem_queue", "weight", "weight", value_re=r"\d+", value_type="int", negatable=True),
    ]
