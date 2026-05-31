# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Qos_mapsTemplate(NetworkTemplate):
    """Parser and renderer for ``configure qos`` map sub-families."""

    _FIELDS = (
        "tc_map_dot1p",
        "dscp_map_dot1p",
        "up_ctrl_pkt",
        "dn_ctrl_pkt",
    )

    def __init__(self, lines=None, module=None):
        super(Qos_mapsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    @classmethod
    def _render_tc_map_dot1p(cls, data):
        return "configure qos tc-map-dot1p {0} tc {1}".format(data["dot1p"], data["tc"])

    @classmethod
    def _render_no_tc_map_dot1p(cls, data):
        return "configure qos no tc-map-dot1p {0}".format(data["dot1p"])

    @classmethod
    def _render_dscp_map_dot1p(cls, data):
        return "configure qos dscp-map-dot1p {0} dot1p {1}".format(data["dscp"], data["dot1p"])

    @classmethod
    def _render_no_dscp_map_dot1p(cls, data):
        return "configure qos no dscp-map-dot1p {0}".format(data["dscp"])

    @classmethod
    def _render_up_ctrl_pkt(cls, data):
        cmd = "configure qos up-ctrl-pkt {0} queue {1}".format(data["protocol"], data["queue"])
        if data.get("profile"):
            cmd += " profile {0}".format(data["profile"])
        return cmd

    @classmethod
    def _render_no_up_ctrl_pkt(cls, data):
        return "configure qos no up-ctrl-pkt {0}".format(data["protocol"])

    @classmethod
    def _render_dn_ctrl_pkt(cls, data):
        cmd = "configure qos dn-ctrl-pkt {0} queue {1}".format(data["protocol"], data["queue"])
        if data.get("profile"):
            cmd += " profile {0}".format(data["profile"])
        return cmd

    @classmethod
    def _render_no_dn_ctrl_pkt(cls, data):
        return "configure qos no dn-ctrl-pkt {0}".format(data["protocol"])

    def parse(self):
        result = {
            "tc_map_dot1p": [],
            "dscp_map_dot1p": [],
            "up_ctrl_pkt": [],
            "dn_ctrl_pkt": [],
        }

        tc_re = re.compile(r"^tc-map-dot1p\s+(?P<dot1p>\d+)\s+tc\s+(?P<tc>\d+)\s*$")
        dscp_re = re.compile(r"^dscp-map-dot1p\s+(?P<dscp>\S+)\s+dot1p\s+(?P<dot1p>\d+)\s*$")
        up_ctrl_re = re.compile(r"^up-ctrl-pkt\s+(?P<protocol>\S+)\s+queue\s+(?P<queue>\d+)(?:\s+profile\s+(?P<profile>\S+))?\s*$")
        dn_ctrl_re = re.compile(r"^dn-ctrl-pkt\s+(?P<protocol>\S+)\s+queue\s+(?P<queue>\d+)(?:\s+profile\s+(?P<profile>\S+))?\s*$")

        in_qos = False

        for raw_line in self._lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo "):
                continue
            if stripped == "configure qos":
                in_qos = True
                continue
            if stripped == "exit" and in_qos:
                in_qos = False
                continue
            if not in_qos:
                continue

            match = tc_re.match(stripped)
            if match:
                result["tc_map_dot1p"].append({
                    "dot1p": int(match.group("dot1p")),
                    "tc": int(match.group("tc")),
                })
                continue

            match = dscp_re.match(stripped)
            if match:
                entry = {"dscp": match.group("dscp"), "dot1p": int(match.group("dot1p"))}
                result["dscp_map_dot1p"].append(entry)
                continue

            match = up_ctrl_re.match(stripped)
            if match:
                entry = {
                    "protocol": match.group("protocol"),
                    "queue": int(match.group("queue")),
                }
                if match.group("profile"):
                    entry["profile"] = match.group("profile")
                result["up_ctrl_pkt"].append(entry)
                continue

            match = dn_ctrl_re.match(stripped)
            if match:
                entry = {
                    "protocol": match.group("protocol"),
                    "queue": int(match.group("queue")),
                }
                if match.group("profile"):
                    entry["profile"] = match.group("profile")
                result["dn_ctrl_pkt"].append(entry)
                continue

        return result


Qos_mapsTemplate.PARSERS = [
    {
        "name": "tc_map_dot1p",
        "getval": re.compile(
            r"""^tc-map-dot1p\s+(?P<dot1p>\d+)\s+tc\s+(?P<tc>\d+)\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_tc_map_dot1p,
        "remval": Qos_mapsTemplate._render_no_tc_map_dot1p,
        "result": {
            "tc_map_dot1p": [
                {
                    "dot1p": "{{ dot1p|int }}",
                    "tc": "{{ tc|int }}",
                }
            ],
        },
        "shared": True,
    },
    {
        "name": "dscp_map_dot1p",
        "getval": re.compile(
            r"""^dscp-map-dot1p\s+(?P<dscp>\S+)\s+dot1p\s+(?P<dot1p>\d+)\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_dscp_map_dot1p,
        "remval": Qos_mapsTemplate._render_no_dscp_map_dot1p,
        "result": {
            "dscp_map_dot1p": [
                {
                    "dscp": "{{ dscp }}",
                    "dot1p": "{{ dot1p|int }}",
                }
            ],
        },
        "shared": True,
    },
    {
        "name": "up_ctrl_pkt",
        "getval": re.compile(
            r"""^up-ctrl-pkt\s+(?P<protocol>\S+)\s+queue\s+(?P<queue>\d+)(?:\s+profile\s+(?P<profile>\S+))?\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_up_ctrl_pkt,
        "remval": Qos_mapsTemplate._render_no_up_ctrl_pkt,
        "result": {
            "up_ctrl_pkt": [
                {
                    "protocol": "{{ protocol }}",
                    "queue": "{{ queue|int }}",
                    "profile": "{{ profile }}",
                }
            ],
        },
        "shared": True,
    },
    {
        "name": "dn_ctrl_pkt",
        "getval": re.compile(
            r"""^dn-ctrl-pkt\s+(?P<protocol>\S+)\s+queue\s+(?P<queue>\d+)(?:\s+profile\s+(?P<profile>\S+))?\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_dn_ctrl_pkt,
        "remval": Qos_mapsTemplate._render_no_dn_ctrl_pkt,
        "result": {
            "dn_ctrl_pkt": [
                {
                    "protocol": "{{ protocol }}",
                    "queue": "{{ queue|int }}",
                    "profile": "{{ profile }}",
                }
            ],
        },
        "shared": True,
    },
]
