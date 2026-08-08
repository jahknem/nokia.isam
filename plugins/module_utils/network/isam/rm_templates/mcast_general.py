# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Mcast_generalTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Mcast_generalTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure mcast general {{ 'no ' if admin_state == false else '' }}admin-state",
            "result": {
                "admin_state": "{{ False if negate is defined else True }}",
            },
        },
        {
            "name": "forward_method",
            "compval": "forward_method",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\sforward-method\s(?P<forward_method>\S+)$"
            ),
            "setval": "configure mcast general forward-method {{ forward_method }}",
            "result": {
                "forward_method": "{{ forward_method }}",
            },
        },
        {
            "name": "fast_change",
            "compval": "fast_change",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\s(?P<negate>no\s)?(?P<fast_change>fast-change)(?:\s+.*)?$"
            ),
            "setval": "configure mcast general {{ 'no ' if fast_change == false else '' }}fast-change",
            "result": {
                "fast_change": "{{ False if negate is defined else True }}",
            },
        },
        {
            "name": "package_member",
            "compval": "package_member",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\spackage-member\s(?P<package_member>.+)$"
            ),
            "setval": "configure mcast general package-member {{ package_member }}",
            "result": {
                "package_member": "{{ package_member }}",
            },
        },
    ]
    # fmt: on
