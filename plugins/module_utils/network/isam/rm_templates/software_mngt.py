# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Software_mngtTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Software_mngtTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "database.version",
            "compval": "version",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\sversion\s(?P<version>\S+)$"
            ),
            "setval": "configure software-mngt database version {{ database.version }}",
            "result": {
                "database": {
                    "version": "{{ version }}",
                },
            },
        },
        {
            "name": "database.url",
            "compval": "url",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\surl\s(?P<url>\S+)$"
            ),
            "setval": "configure software-mngt database url {{ database.url }}",
            "result": {
                "database": {
                    "url": "{{ url }}",
                },
            },
        },
        {
            "name": "oswp.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\soswp\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure software-mngt oswp {{ 'no ' if oswp.admin_state == false else '' }}admin-state",
            "result": {
                "oswp": {
                    "admin_state": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "sw_replacement_mode.mode",
            "compval": "mode",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\ssw-replacement-mode\s(?P<mode>\S+)$"
            ),
            "setval": "configure software-mngt sw-replacement-mode {{ sw_replacement_mode.mode }}",
            "result": {
                "sw_replacement_mode": {
                    "mode": "{{ mode }}",
                },
            },
        },
    ]
    # fmt: on
