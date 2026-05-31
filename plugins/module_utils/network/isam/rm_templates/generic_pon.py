# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Generic_ponTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Generic_ponTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "dpinteg_threshold",
            "getval": re.compile(
                r"""
                ^configure\sgeneric-pon\sdpinteg-threshold\s(?P<dpinteg_threshold>\S+)
                $""", re.VERBOSE),
            "setval": "configure generic-pon dpinteg-threshold {{ dpinteg_threshold }}",
            "result": {
                "dpinteg_threshold": "{{ dpinteg_threshold }}",
            },
        },
    ]
    # fmt: on
