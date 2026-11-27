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
        cmd = "configure qos tc-map-dot1p {0} tc {1}".format(data["dot1p"], data["tc"])
        if data.get("dpcolor"):
            cmd += " dpcolor {0}".format(data["dpcolor"])
        if data.get("policer_color"):
            cmd += " policer-color {0}".format(data["policer_color"])
        return cmd

    @classmethod
    def _render_no_tc_map_dot1p(cls, data):
        return "configure qos no tc-map-dot1p {0}".format(data["dot1p"])

    @classmethod
    def _render_dscp_map_dot1p(cls, data):
        return "configure qos dscp-map-dot1p {0} dot1p-value {1}".format(data["dscp"], data["dot1p"])

    @classmethod
    def _render_no_dscp_map_dot1p(cls, data):
        return "configure qos no dscp-map-dot1p {0}".format(data["dscp"])

    @classmethod
    def _render_ctrl_pkt(cls, node, data, reset=()):
        """Set the given parameters; ``reset`` names parameters to return to their
        default with the inline ``no <param>`` form (CLI help, configure qos
        up-ctrl-pkt/dn-ctrl-pkt: ``[ no dscp | dscp <v> ] [ no pbit | pbit <v> ]
        [ no tc | tc <v> ]``)."""
        cmd = "configure qos {0} {1}".format(node, data["protocol"])
        for attr in ("dscp", "pbit", "tc"):
            if data.get(attr) is not None:
                cmd += " {0} {1}".format(attr, data[attr])
            elif attr in reset:
                cmd += " no {0}".format(attr)
        return cmd

    @classmethod
    def _render_up_ctrl_pkt(cls, data):
        return cls._render_ctrl_pkt("up-ctrl-pkt", data)

    @classmethod
    def _render_no_up_ctrl_pkt(cls, data):
        return "configure qos no up-ctrl-pkt {0}".format(data["protocol"])

    @classmethod
    def _render_dn_ctrl_pkt(cls, data):
        return cls._render_ctrl_pkt("dn-ctrl-pkt", data)

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

        tc_re = re.compile(r"^tc-map-dot1p\s+(?P<dot1p>\d+)\s+tc\s+(?P<tc>\d+)(?:\s+dpcolor\s+(?P<dpcolor>\S+))?(?:\s+policer-color\s+(?P<policer_color>\S+))?\s*$")
        dscp_re = re.compile(r"^dscp-map-dot1p\s+(?P<dscp>\S+)\s+(?:dot1p|dot1p-value)\s+(?P<dot1p>\d+)\s*$")
        up_ctrl_re = re.compile(r"^up-ctrl-pkt\s+(?P<protocol>\S+)(?:\s+dscp\s+(?P<dscp>\d+))?(?:\s+pbit\s+(?P<pbit>\d+))?(?:\s+tc\s+(?P<tc>\d+))?\s*$")
        dn_ctrl_re = re.compile(r"^dn-ctrl-pkt\s+(?P<protocol>\S+)(?:\s+dscp\s+(?P<dscp>\d+))?(?:\s+pbit\s+(?P<pbit>\d+))?(?:\s+tc\s+(?P<tc>\d+))?\s*$")

        for raw_line in self._lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo "):
                continue
            if stripped.startswith("configure qos "):
                stripped = stripped[len("configure qos "):]
            elif stripped in ("configure", "qos", "exit"):
                continue

            match = tc_re.match(stripped)
            if match:
                result["tc_map_dot1p"].append({
                    "dot1p": int(match.group("dot1p")),
                    "tc": int(match.group("tc")),
                })
                if match.group("dpcolor"):
                    result["tc_map_dot1p"][-1]["dpcolor"] = match.group("dpcolor")
                if match.group("policer_color"):
                    result["tc_map_dot1p"][-1]["policer_color"] = match.group("policer_color")
                continue

            match = dscp_re.match(stripped)
            if match:
                entry = {"dscp": match.group("dscp"), "dot1p": int(match.group("dot1p"))}
                result["dscp_map_dot1p"].append(entry)
                continue

            match = up_ctrl_re.match(stripped)
            if match:
                entry = {"protocol": match.group("protocol")}
                for attr in ("dscp", "pbit", "tc"):
                    if match.group(attr):
                        entry[attr] = int(match.group(attr))
                result["up_ctrl_pkt"].append(entry)
                continue

            match = dn_ctrl_re.match(stripped)
            if match:
                entry = {"protocol": match.group("protocol")}
                for attr in ("dscp", "pbit", "tc"):
                    if match.group(attr):
                        entry[attr] = int(match.group(attr))
                result["dn_ctrl_pkt"].append(entry)
                continue

        return result


Qos_mapsTemplate.PARSERS = [
    {
        "name": "tc_map_dot1p",
        "getval": re.compile(
            r"""^tc-map-dot1p\s+(?P<dot1p>\d+)\s+tc\s+(?P<tc>\d+)(?:\s+dpcolor\s+(?P<dpcolor>\S+))?(?:\s+policer-color\s+(?P<policer_color>\S+))?\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_tc_map_dot1p,
        "remval": Qos_mapsTemplate._render_no_tc_map_dot1p,
        "result": {
            "tc_map_dot1p": [
                {
                    "dot1p": "{{ dot1p|int }}",
                    "tc": "{{ tc|int }}",
                    "dpcolor": "{{ dpcolor }}",
                    "policer_color": "{{ policer_color }}",
                }
            ],
        },
        "shared": True,
    },
    {
        "name": "dscp_map_dot1p",
        "getval": re.compile(
            r"""^dscp-map-dot1p\s+(?P<dscp>\S+)\s+(?:dot1p|dot1p-value)\s+(?P<dot1p>\d+)\s*$""",
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
            r"""^up-ctrl-pkt\s+(?P<protocol>\S+)(?:\s+dscp\s+(?P<dscp>\d+))?(?:\s+pbit\s+(?P<pbit>\d+))?(?:\s+tc\s+(?P<tc>\d+))?\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_up_ctrl_pkt,
        "remval": Qos_mapsTemplate._render_no_up_ctrl_pkt,
        "result": {
            "up_ctrl_pkt": [
                {
                    "protocol": "{{ protocol }}",
                    "dscp": "{{ dscp }}",
                    "pbit": "{{ pbit }}",
                    "tc": "{{ tc }}",
                }
            ],
        },
        "shared": True,
    },
    {
        "name": "dn_ctrl_pkt",
        "getval": re.compile(
            r"""^dn-ctrl-pkt\s+(?P<protocol>\S+)(?:\s+dscp\s+(?P<dscp>\d+))?(?:\s+pbit\s+(?P<pbit>\d+))?(?:\s+tc\s+(?P<tc>\d+))?\s*$""",
            re.VERBOSE,
        ),
        "setval": Qos_mapsTemplate._render_dn_ctrl_pkt,
        "remval": Qos_mapsTemplate._render_no_dn_ctrl_pkt,
        "result": {
            "dn_ctrl_pkt": [
                {
                    "protocol": "{{ protocol }}",
                    "dscp": "{{ dscp }}",
                    "pbit": "{{ pbit }}",
                    "tc": "{{ tc }}",
                }
            ],
        },
        "shared": True,
    },
]
