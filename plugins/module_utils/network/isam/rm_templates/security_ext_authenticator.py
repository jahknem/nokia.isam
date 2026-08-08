from __future__ import absolute_import, division, print_function

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_security_ext_authenticatorTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        self.PARSERS = [
            {
                "name": "port",
                "getval": re.compile(
                    r"^admin\s+security\s+ext-authenticator\s+(?P<port>\S+)"
                    r"(?:\s+(?P<clear_statistics>clear-statistics))?$"
                ),
                "setval": (
                    "admin security ext-authenticator {{ port }}"
                    "{{ ' clear-statistics' if clear_statistics else '' }}"
                ),
                "result": {
                    "config": [
                        {
                            "port": "{{ port }}",
                            "clear_statistics": "{{ clear_statistics is defined }}",
                        }
                    ]
                },
            }
        ]
        super(Isam_security_ext_authenticatorTemplate, self).__init__(
            lines=lines, tmplt=self, module=module
        )
