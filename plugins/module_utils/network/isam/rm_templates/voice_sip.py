# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_voice_sipTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_voice_sipTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "registrar.server",
            "compval": "server",
            "getval": re.compile(
                r"^configure\svoice\ssip\sregistrar\sserver\s(?P<server>\S+)$"
            ),
            "setval": "configure voice sip registrar server {{ server }}",
            "remval": "configure voice sip registrar no server",
            "result": {
                "registrar": {
                    "server": "{{ server }}",
                },
            },
        },
        {
            "name": "registrar.port",
            "compval": "port",
            "getval": re.compile(
                r"^configure\svoice\ssip\sregistrar\sport\s(?P<port>\d+)$"
            ),
            "setval": "configure voice sip registrar port {{ port }}",
            "remval": "configure voice sip registrar no port",
            "result": {
                "registrar": {
                    "port": "{{ port }}",
                },
            },
        },
        {
            "name": "registrar.realm",
            "compval": "realm",
            "getval": re.compile(
                r"^configure\svoice\ssip\sregistrar\srealm\s(?P<realm>\S+)$"
            ),
            "setval": "configure voice sip registrar realm {{ realm }}",
            "remval": "configure voice sip registrar no realm",
            "result": {
                "registrar": {
                    "realm": "{{ realm }}",
                },
            },
        },
        {
            "name": "proxy.server",
            "compval": "server",
            "getval": re.compile(
                r"^configure\svoice\ssip\sproxy\sserver\s(?P<server>\S+)$"
            ),
            "setval": "configure voice sip proxy server {{ server }}",
            "remval": "configure voice sip proxy no server",
            "result": {
                "proxy": {
                    "server": "{{ server }}",
                },
            },
        },
        {
            "name": "proxy.port",
            "compval": "port",
            "getval": re.compile(
                r"^configure\svoice\ssip\sproxy\sport\s(?P<port>\d+)$"
            ),
            "setval": "configure voice sip proxy port {{ port }}",
            "remval": "configure voice sip proxy no port",
            "result": {
                "proxy": {
                    "port": "{{ port }}",
                },
            },
        },
        {
            "name": "codec.priority",
            "compval": "priority",
            "getval": re.compile(
                r"^configure\svoice\ssip\scodec\spriority\s(?P<priority>\d+)\stype\s(?P<type>\S+)$"
            ),
            "setval": "configure voice sip codec priority {{ priority }} type {{ type }}",
            "remval": "configure voice sip codec priority {{ priority }}",
            "result": {
                "codec": {
                    "{{ priority }}": {
                        "priority": "{{ priority }}",
                        "type": "{{ type }}",
                    },
                },
            },
        },
        {
            "name": "sip_profile.timer_t1",
            "compval": "timer_t1",
            "getval": re.compile(
                r"^configure\svoice\ssip\ssip-profile\s(?P<name>\S+)\stimer-t1\s(?P<timer_t1>\d+)$"
            ),
            "setval": "configure voice sip sip-profile {{ name }} timer-t1 {{ timer_t1 }}",
            "remval": "configure voice sip sip-profile {{ name }} no timer-t1",
            "result": {
                "sip_profile": {
                    "{{ name }}": {
                        "name": "{{ name }}",
                        "timer_t1": "{{ timer_t1 }}",
                    },
                },
            },
        },
        {
            "name": "sip_profile.timer_t2",
            "compval": "timer_t2",
            "getval": re.compile(
                r"^configure\svoice\ssip\ssip-profile\s(?P<name>\S+)\stimer-t2\s(?P<timer_t2>\d+)$"
            ),
            "setval": "configure voice sip sip-profile {{ name }} timer-t2 {{ timer_t2 }}",
            "remval": "configure voice sip sip-profile {{ name }} no timer-t2",
            "result": {
                "sip_profile": {
                    "{{ name }}": {
                        "name": "{{ name }}",
                        "timer_t2": "{{ timer_t2 }}",
                    },
                },
            },
        },
    ]
    # fmt: on
