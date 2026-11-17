# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure qos tca <port> queue <n>`` (per-queue TCA)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

_LINE = re.compile(r"^qos\s+tca\s+(?P<name>\S+)\s+queue\s+(?P<queue>\d+)(?P<rest>.*)$")
_ATTR = re.compile(r"(no\s+)?(tca-enable|load-thresh|dis-frame-th|qpeak-usage-th)(?:\s+(\d+))?")
_INT_ATTRS = {"load-thresh": "load_thresh", "dis-frame-th": "dis_frame_th", "qpeak-usage-th": "qpeak_usage_th"}


class Qos_tcaTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Qos_tcaTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        for raw in self._lines:
            line = raw.strip()
            if line.startswith("configure "):
                line = line[len("configure "):]
            match = _LINE.match(line)
            if not match:
                continue
            key = (match.group("name"), int(match.group("queue")))
            entry = result.setdefault(key, {"name": match.group("name"), "queue": int(match.group("queue"))})
            for negate, attr, value in _ATTR.findall(match.group("rest")):
                if attr == "tca-enable":
                    entry["tca_enable"] = not negate
                elif attr in _INT_ATTRS:
                    if not negate and value is not None and value != "":
                        entry[_INT_ATTRS[attr]] = int(value)
                    else:
                        entry.pop(_INT_ATTRS[attr], None)
        return result

    @staticmethod
    def command(name, queue, suffix=""):
        cmd = "configure qos tca {0} queue {1}".format(name, queue)
        return cmd + (" " + suffix if suffix else "")

    @staticmethod
    def render_attr(entry, attr):
        """One attribute set/reset command for an entry (attr is the canonical name)."""
        name, queue = entry["name"], entry["queue"]
        if attr == "tca_enable":
            value = entry.get("tca_enable")
            if value is None:
                return None
            return Qos_tcaTemplate.command(name, queue, "tca-enable" if value else "no tca-enable")
        cli = {"load_thresh": "load-thresh", "dis_frame_th": "dis-frame-th", "qpeak_usage_th": "qpeak-usage-th"}[attr]
        value = entry.get(attr)
        if value is None:
            return Qos_tcaTemplate.command(name, queue, "no " + cli)
        return Qos_tcaTemplate.command(name, queue, "{0} {1}".format(cli, value))

    PARSERS = [
        {"name": "qos_tca", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]
