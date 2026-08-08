# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate


class Isam_dist_serviceTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_dist_serviceTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "service_type",
            "compval": "service_type",
            "getval": re.compile(r"^configure\s+dist-service\s+(?P<name>\S+)\s+(?P<negate>no\s+)?service-type(?:\s+(?P<service_type>\S+))?$"),
            "setval": "configure dist-service {{ name }} service-type {{ service_type }}",
            "remval": "configure dist-service {{ name }} no service-type",
            "result": {"{{ name }}": {"name": "{{ name }}", "service_type": "{{ 'apipe' if negate is defined else service_type }}"}},
        },
        {
            "name": "qos_profile",
            "compval": "qos_profile",
            "getval": re.compile(r"^configure\s+dist-service\s+(?P<name>\S+)\s+(?P<negate>no\s+)?qos-profile(?:\s+(?P<qos_profile>\S+))?$"),
            "setval": "configure dist-service {{ name }} qos-profile {{ qos_profile }}",
            "remval": "configure dist-service {{ name }} no qos-profile",
            "result": {"{{ name }}": {"name": "{{ name }}", "qos_profile": "{{ 'none' if negate is defined else qos_profile }}"}},
        },
    ]
