# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Qos_profilesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_qos_profiles module."""

    _profile_options = {
        "profile_type": {
            "type": "str",
            "required": True,
            "choices": [
                "queue",
                "scheduler-node",
                "cac",
                "marker-d1p",
                "policer",
                "session",
                "aggrqueuesconfig",
                "shaper",
                "bandwidth",
                "ingress-qos",
                "rate-limit",
            ],
        },
        "name": {"type": "str", "required": True},
        "queue-type": {"type": "str"},
        "unit": {"type": "str", "choices": ["packet", "byte"]},
        "priority": {"type": "int"},
        "weight": {"type": "int"},
        "shaper-profile": {"type": "str"},
        "ext-shaper": {"type": "str"},
        "autoshape": {"type": "str"},
        "mcast-inc-shape": {"type": "str"},
        "res-voice-bandwidth": {"type": "int"},
        "max-mcast-bandwidth": {"type": "int"},
        "res-data-bandwidth": {"type": "int"},
        "cac-type": {"type": "str"},
        "default-dot1p": {"type": "int"},
        "use-dei": {"type": "bool"},
        "policer-type": {"type": "str"},
        "excess-burst-size": {"type": "int"},
        "coupling-flag": {"type": "str"},
        "color-mode": {"type": "str"},
        "green-action": {"type": "str"},
        "yellow-action": {"type": "str"},
        "red-action": {"type": "str"},
        "policed-size-ctrl": {"type": "str"},
        "peak-info-rate": {"type": "int"},
        "peak-burst-size": {"type": "int"},
        "cos-threshold": {"type": "str"},
        "ing-outer-marker": {"type": "str"},
        "ds-schedule-tag": {"type": "str"},
        "up-policer-per-tc": {"type": "str"},
        "up-dscptotc-prof": {"type": "str"},
        "dn-dscptotc-prof": {"type": "str"},
        "up-pbittotc-prof": {"type": "str"},
        "dn-pbittotc-prof": {"type": "str"},
        "up-default-tc": {"type": "int"},
        "dn-default-tc": {"type": "int"},
        "assu-burst-size": {"type": "int"},
        "exce-burst-size": {"type": "int"},
        "dbru": {"type": "str"},
        "committed-info-rate": {"type": "int"},
        "committed-burst-size": {"type": "int"},
        "excess-info-rate": {"type": "int"},
        "shaper-type": {"type": "str"},
        "assured-info-rate": {"type": "int"},
        "excessive-info-rate": {"type": "int"},
        "delay-tolerance": {"type": "int"},
        "logical-flow-type": {"type": "str"},
        "up-policer": {"type": "str"},
        "down-policer": {"type": "str"},
        "up-marker": {"type": "str"},
        "total-rate": {"type": "int"},
        "total-burst": {"type": "int"},
        "dot1-p0-tc": {"type": "int"},
        "dot1-p1-tc": {"type": "int"},
        "dot1-p2-tc": {"type": "int"},
        "dot1-p3-tc": {"type": "int"},
        "dot1-p4-tc": {"type": "int"},
        "dot1-p5-tc": {"type": "int"},
        "dot1-p6-tc": {"type": "int"},
        "dot1-p7-tc": {"type": "int"},
        "attributes": {"type": "list", "elements": "str"},
    }

    for _queue_index in range(8):
        _profile_options.update(
            {
                "q{0}-priority".format(_queue_index): {"type": "int"},
                "q{0}-weight".format(_queue_index): {"type": "int"},
                "q{0}-queue-prof".format(_queue_index): {"type": "str"},
                "q{0}-shaper-prof".format(_queue_index): {"type": "str"},
                "q{0}-bandwidth-prof".format(_queue_index): {"type": "str"},
                "q{0}-bw-sharing".format(_queue_index): {"type": "str"},
            }
        )

    for _rate_name in (
        "arp", "dhcp", "igmp", "pppoe", "nd", "icmpv6", "mld", "dhcpv6", "cfm"
    ):
        _profile_options.update({
            "{0}-rate".format(_rate_name): {"type": "int"},
            "{0}-burst".format(_rate_name): {"type": "int"},
        })

    for _pbit_index in range(8):
        _profile_options.update({
            "dot1-p{0}-color".format(_pbit_index): {"type": "str"},
            "dot1-p{0}-pol-tc".format(_pbit_index): {"type": "int"},
        })

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": _profile_options,
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
