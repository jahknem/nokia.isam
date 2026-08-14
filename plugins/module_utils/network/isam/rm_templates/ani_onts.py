# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Ani_ontsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ani_ontsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "tca_thresh",
            "getval": re.compile(
                r"^configure\s+ani\s+ont\s+(?P<negate>no\s+)?tca-thresh\s+(?P<ont_idx>\S+?)"
                r"(?:\s+(?P<no_lower>no\s+lower-optical-th)|\s+lower-optical-th\s+(?P<lower_optical_th>[-+]?\d+(?:\.\d+)?))?"
                r"(?:\s+(?P<no_upper>no\s+upper-optical-th)|\s+upper-optical-th\s+(?P<upper_optical_th>[-+]?\d+(?:\.\d+)?))?"
                r"(?:\s+(?P<no_rssi>no\s+rssi-profile)|\s+rssi-profile\s+(?P<rssi_profile>\d+))?$"
            ),
            "setval": "configure ani ont {{ 'no ' if tca_thresh == false else '' }}tca-thresh {{ ont_idx }}{% if tca_thresh != false %}{% if lower_optical_th is defined %} lower-optical-th {{ lower_optical_th }}{% endif %}{% if upper_optical_th is defined %} upper-optical-th {{ upper_optical_th }}{% endif %}{% if rssi_profile is defined %} rssi-profile {{ rssi_profile }}{% endif %}{% endif %}",
            "shared": True,
            "result": {
                "{{ ont_idx }}": {
                    "ont_idx": "{{ ont_idx }}",
                    "tca_thresh": "{{ False if negate is defined else True }}",
                    "lower_optical_th": "{{ '' if lower_optical_th is not defined else lower_optical_th|float }}",
                    "upper_optical_th": "{{ '' if upper_optical_th is not defined else upper_optical_th|float }}",
                    "rssi_profile": "{{ '' if rssi_profile is not defined else rssi_profile|int }}",
                }
            },
        },
    ]
