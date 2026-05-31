# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class MulticastTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(MulticastTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "igmp.mld_snooping",
            "compval": "mld_snooping",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<mld_snooping>mld-snooping)$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.mld_snooping == false else '' }}mld-snooping",
            "result": {
                "igmp": {
                    "mld_snooping": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.mld_querier",
            "compval": "mld_querier",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<mld_querier>mld-querier)$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.mld_querier == false else '' }}mld-querier",
            "result": {
                "igmp": {
                    "mld_querier": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.igmp_snooping",
            "compval": "igmp_snooping",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<igmp_snooping>igmp-snooping)$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.igmp_snooping == false else '' }}igmp-snooping",
            "result": {
                "igmp": {
                    "igmp_snooping": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.igmp_querier",
            "compval": "igmp_querier",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<igmp_querier>igmp-querier)$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.igmp_querier == false else '' }}igmp-querier",
            "result": {
                "igmp": {
                    "igmp_querier": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.query_interval",
            "compval": "query_interval",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\squery-interval\s(?P<query_interval>\d+)$"
            ),
            "setval": "configure igmp mcast-svc-context query-interval {{ igmp.query_interval }}",
            "result": {
                "igmp": {
                    "query_interval": "{{ query_interval|int }}",
                },
            },
        },
        {
            "name": "igmp.query_response_interval",
            "compval": "query_response_interval",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\squery-response-interval\s(?P<query_response_interval>\d+)$"
            ),
            "setval": "configure igmp mcast-svc-context query-response-interval {{ igmp.query_response_interval }}",
            "result": {
                "igmp": {
                    "query_response_interval": "{{ query_response_interval|int }}",
                },
            },
        },
        {
            "name": "igmp.robustness_count",
            "compval": "robustness_count",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\srobustness-count\s(?P<robustness_count>\d+)$"
            ),
            "setval": "configure igmp mcast-svc-context robustness-count {{ igmp.robustness_count }}",
            "result": {
                "igmp": {
                    "robustness_count": "{{ robustness_count|int }}",
                },
            },
        },
        {
            "name": "mcast_control.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\smcast-control\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure mcast-control {{ 'no ' if mcast_control.admin_state == false else '' }}admin-state",
            "result": {
                "mcast_control": {
                    "admin_state": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "mcast_control.max_groups",
            "compval": "max_groups",
            "getval": re.compile(
                r"^configure\smcast-control\smax-groups\s(?P<max_groups>\d+)$"
            ),
            "setval": "configure mcast-control max-groups {{ mcast_control.max_groups }}",
            "result": {
                "mcast_control": {
                    "max_groups": "{{ max_groups|int }}",
                },
            },
        },
        {
            "name": "mcast_control.max_sources",
            "compval": "max_sources",
            "getval": re.compile(
                r"^configure\smcast-control\smax-sources\s(?P<max_sources>\d+)$"
            ),
            "setval": "configure mcast-control max-sources {{ mcast_control.max_sources }}",
            "result": {
                "mcast_control": {
                    "max_sources": "{{ max_sources|int }}",
                },
            },
        },
    ]
    # fmt: on
