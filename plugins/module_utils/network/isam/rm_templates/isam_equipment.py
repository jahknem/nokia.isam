# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_equipmentTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_equipmentTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "shelf.planned_type",
            "compval": "planned_type",
            "getval": re.compile(r"^configure\sequipment\sshelf\s(?P<id>\S+)\splanned-type\s(?P<planned_type>\S+)$"),
            "setval": "configure equipment shelf {{ id }} planned-type {{ planned_type }}",
            "remval": "configure equipment shelf {{ id }} no planned-type",
            "result": {
                "shelves": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "planned_type": "{{ planned_type }}",
                    },
                },
            },
        },
        {
            "name": "slot.planned_type",
            "compval": "planned_type",
            "getval": re.compile(r"^configure\sequipment\sslot\s(?P<id>\S+)\splanned-type\s(?P<planned_type>\S+)$"),
            "setval": "configure equipment slot {{ id }} planned-type {{ planned_type }}",
            "remval": "configure equipment slot {{ id }} no planned-type",
            "result": {
                "slots": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "planned_type": "{{ planned_type }}",
                    },
                },
            },
        },
        {
            "name": "slot.unlock",
            "compval": "unlock",
            "getval": re.compile(r"^configure\sequipment\sslot\s(?P<id>\S+)\s((?P<negate>no\sunlock)|unlock)$"),
            "setval": "configure equipment slot {{ id }} unlock",
            "remval": "configure equipment slot {{ id }} no unlock",
            "result": {
                "slots": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "unlock": "{{ False if negate is defined else True }}",
                    },
                },
            },
        },
        {
            "name": "applique.planned_type",
            "compval": "planned_type",
            "getval": re.compile(r"^configure\sequipment\sapplique\s(?P<id>\S+)\splanned-type\s(?P<planned_type>\S+)$"),
            "setval": "configure equipment applique {{ id }} planned-type {{ planned_type }}",
            "remval": "configure equipment applique {{ id }} no planned-type",
            "result": {
                "appliques": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "planned_type": "{{ planned_type }}",
                    },
                },
            },
        },
        {
            "name": "protection_group.admin_status",
            "compval": "admin_status",
            "getval": re.compile(r"^configure\sequipment\sprotection-group\s(?P<id>\d+)\sadmin-status\s(?P<admin_status>\S+)$"),
            "setval": "configure equipment protection-group {{ id }} admin-status {{ admin_status }}",
            "remval": "configure equipment protection-group {{ id }} no admin-status",
            "result": {
                "protection_groups": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "admin_status": "{{ admin_status }}",
                    },
                },
            },
        },
        {
            "name": "protection_group.eps_quenchfactor",
            "compval": "eps_quenchfactor",
            "getval": re.compile(r"^configure\sequipment\sprotection-group\s(?P<id>\d+)\seps-quenchfactor\s(?P<eps_quenchfactor>\d+)$"),
            "setval": "configure equipment protection-group {{ id }} eps-quenchfactor {{ eps_quenchfactor }}",
            "remval": "configure equipment protection-group {{ id }} no eps-quenchfactor",
            "result": {
                "protection_groups": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "eps_quenchfactor": "{{ eps_quenchfactor }}",
                    },
                },
            },
        },
    ]
    # fmt: on
