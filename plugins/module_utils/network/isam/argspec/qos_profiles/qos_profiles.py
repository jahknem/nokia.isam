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
        "priority": {"type": "int"},
        "weight": {"type": "int"},
        "shaper-profile": {"type": "str"},
        "mcast-inc-shape": {"type": "str"},
        "res-voice-bandwidth": {"type": "int"},
        "max-mcast-bandwidth": {"type": "int"},
        "res-data-bandwidth": {"type": "int"},
        "cac-type": {"type": "str"},
        "default-dot1p": {"type": "int"},
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
            }
        )

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
