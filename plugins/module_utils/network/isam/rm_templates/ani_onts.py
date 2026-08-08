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
                r"^configure\s+ani\s+ont\s+tca-thresh\s+(?P<ont_idx>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure ani ont tca-thresh {{ ont_idx }}",
            "shared": True,
            "result": {
                "{{ ont_idx }}": {
                    "ont_idx": "{{ ont_idx }}",
                    "tca_thresh": True,
                }
            },
        },
        {
            "name": "tca_profile",
            "getval": re.compile(
                r"^configure\s+ani\s+ont\s+(?P<ont_idx>\S+)\s+tca-profile\s+(?P<tca_profile>\S+)\s*$"
            ),
            "setval": "configure ani ont {{ ont_idx }} tca-profile {{ tca_profile }}",
            "result": {
                "{{ ont_idx }}": {
                    "ont_idx": "{{ ont_idx }}",
                    "tca_profile": "{{ tca_profile }}",
                }
            },
        },
        {
            "name": "admin_state",
            "getval": re.compile(
                r"^configure\s+ani\s+ont\s+(?P<ont_idx>\S+)\s+admin-state\s+(?P<admin_state>\S+)\s*$"
            ),
            "setval": "configure ani ont {{ ont_idx }} admin-state {{ admin_state }}",
            "result": {
                "{{ ont_idx }}": {
                    "ont_idx": "{{ ont_idx }}",
                    "admin_state": "{{ admin_state }}",
                }
            },
        },
    ]
