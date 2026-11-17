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
        {
            "name": "diagnostics_sfp.rssi_prof_id",
            "compval": "rssi_prof_id",
            "getval": re.compile(r"^configure\sequipment\sdiagnostics\ssfp\s(?P<id>\S+)\srssi-prof-id\s(?P<rssi_prof_id>\d+)$"),
            "setval": "configure equipment diagnostics sfp {{ id }} rssi-prof-id {{ rssi_prof_id }}",
            "remval": "configure equipment diagnostics sfp {{ id }} no rssi-prof-id",
            "result": {
                "diagnostics_sfp": {
                    "{{ id }}": {"id": "{{ id }}", "rssi_prof_id": "{{ rssi_prof_id }}"},
                },
            },
        },
        {
            "name": "diagnostics_sfp.rssi_state",
            "compval": "rssi_state",
            "getval": re.compile(r"^configure\sequipment\sdiagnostics\ssfp\s(?P<id>\S+)\srssi-state\s(?P<rssi_state>\S+)$"),
            "setval": "configure equipment diagnostics sfp {{ id }} rssi-state {{ rssi_state }}",
            "remval": "configure equipment diagnostics sfp {{ id }} no rssi-state",
            "result": {
                "diagnostics_sfp": {
                    "{{ id }}": {"id": "{{ id }}", "rssi_state": "{{ rssi_state }}"},
                },
            },
        },
        {
            "name": "protection_element.redcy_ctrl_status",
            "compval": "redcy_ctrl_status",
            "getval": re.compile(r"^configure\sequipment\sprotection-element\s(?P<id>\S+)\sredcy-ctrl-status\s(?P<redcy_ctrl_status>\S+)$"),
            "setval": "configure equipment protection-element {{ id }} redcy-ctrl-status {{ redcy_ctrl_status }}",
            "remval": "configure equipment protection-element {{ id }} no redcy-ctrl-status",
            "result": {
                "protection_elements": {
                    "{{ id }}": {"id": "{{ id }}", "redcy_ctrl_status": "{{ redcy_ctrl_status }}"},
                },
            },
        },
        {
            "name": "rack.description",
            "compval": "description",
            "getval": re.compile(r"^configure\sequipment\srack\s(?P<id>\S+)\sdescription\s(?P<description>.+)$"),
            "setval": "configure equipment rack {{ id }} description {{ description }}",
            "remval": "configure equipment rack {{ id }} no description",
            "result": {
                "racks": {
                    "{{ id }}": {"id": "{{ id }}", "description": "{{ description }}"},
                },
            },
        },
        {
            "name": "external_link_assign.remote",
            "compval": "remote",
            "getval": re.compile(r"^configure\sequipment\sexternal-link-assign\s(?P<id>\S+)\sremote\s(?P<remote>\S+)$"),
            "setval": "configure equipment external-link-assign {{ id }} remote {{ remote }}",
            "remval": "configure equipment external-link-assign {{ id }} no remote",
            "result": {
                "external_link_assigns": {
                    "{{ id }}": {"id": "{{ id }}", "remote": "{{ remote }}"},
                },
            },
        },
        {
            "name": "external_link_host.direction",
            "compval": "direction",
            "getval": re.compile(r"^configure\sequipment\sexternal-link-host\s(?P<id>\S+)\sdirection\s(?P<direction>\S+)$"),
            "setval": "configure equipment external-link-host {{ id }} direction {{ direction }}",
            "remval": "configure equipment external-link-host {{ id }} no direction",
            "result": {
                "external_link_hosts": {
                    "{{ id }}": {"id": "{{ id }}", "direction": "{{ direction }}"},
                },
            },
        },
        {
            "name": "envbox.enable_supervise",
            "compval": "enable_supervise",
            "getval": re.compile(r"^configure\sequipment\senvbox\s((?P<negate>no\senable-supervise)|enable-supervise)$"),
            "setval": "configure equipment envbox enable-supervise",
            "remval": "configure equipment envbox no enable-supervise",
            "result": {
                "envbox": {"enable_supervise": "{{ False if negate is defined else True }}"},
            },
        },
        {
            "name": "isam.description",
            "compval": "description",
            "getval": re.compile(r"^configure\sequipment\sisam\sdescription\s(?P<description>.+)$"),
            "setval": "configure equipment isam description {{ description }}",
            "remval": "configure equipment isam no description",
            "result": {
                "isam": {"description": "{{ description }}"},
            },
        },
    ]
    # fmt: on
