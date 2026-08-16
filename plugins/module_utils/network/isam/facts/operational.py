# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.isam_equipment.operational import (
    EquipmentOperationalParser,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ont_operational.ont_operational import (
    parse_operational_facts,
    parse_status_table,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm_status import (
    AlarmStatusParser,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ont_ranging_status import (
    OntRangingStatusParser,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ont_software.ont_software import (
    parse_ont_sw_download,
    parse_ont_sw_version,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.tc_layer_current_interval.tc_layer_current_interval import (
    parse_tc_layer_current_interval,
)

class _OperationalFacts(object):
    command = None
    key = None

    def __init__(self, module, subspec="config", options="options"):
        self._module = module

    def populate_facts(self, connection, data=None):
        output = connection.get(self.command) if data is None else data
        return {self.key: self.parse(output)}

    def parse(self, output):
        return parse_operational_facts(output)


class Equipment_statusFacts(_OperationalFacts):
    command = "show equipment slot"
    key = "equipment_status"

    def parse(self, output):
        table = parse_status_table(output)
        return {"slots": table} if table else EquipmentOperationalParser().parse(output)


class Ont_statusFacts(_OperationalFacts):
    command = "show equipment ont status pon"
    key = "ont_status"

    def parse(self, output):
        return parse_status_table(output)


class Pon_statusFacts(_OperationalFacts):
    command = "show pon interface"
    key = "pon_status"

    def parse(self, output):
        return parse_status_table(output)


class Interface_statusFacts(_OperationalFacts):
    command = "show interface port"
    key = "interface_status"

    def parse(self, output):
        return parse_status_table(output)


class Active_alarmsFacts(_OperationalFacts):
    command = "show alarm current table"
    key = "active_alarms"

    def parse(self, output):
        return AlarmStatusParser().parse(output)


class Software_statusFacts(_OperationalFacts):
    command = "show software-mngt oswp"
    key = "software_status"

    def parse(self, output):
        return parse_status_table(output)


class Ont_ranging_statusFacts(_OperationalFacts):
    command = "show equipment ont ranging-status channel-pair"
    key = "ont_ranging_status"

    def parse(self, output):
        return OntRangingStatusParser().parse(output)


class Ont_software_statusFacts(_OperationalFacts):
    key = "ont_software_status"

    def populate_facts(self, connection, data=None):
        return {self.key: {
            "sw_version": parse_ont_sw_version(connection.get("show equipment ont sw-version")),
            "sw_download": parse_ont_sw_download(connection.get("show equipment ont sw-download")),
        }}


class Pon_pm_statusFacts(_OperationalFacts):
    command = "show pon interface tc-layer current-interval"
    key = "pon_pm_status"

    def parse(self, output):
        return parse_tc_layer_current_interval(output)


class Dhcp_relayFacts(object):
    """Gather DHCP relay sessions and configured per-port counters."""

    def __init__(self, module):
        self._module = module

    @staticmethod
    def _configured_ports(output):
        ports = {"port_stats": set(), "v6_port_stats": set()}
        in_relay = False
        for raw_line in (output or "").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo"):
                continue
            if stripped in ("configure dhcp-relay", "dhcp-relay"):
                in_relay = True
                continue
            if stripped == "exit":
                in_relay = False
                continue

            match = re.match(r"^(?:configure dhcp-relay\s+)?(v6-)?port-stats\s+(\S+)$", stripped)
            if in_relay or match:
                if match:
                    key = "v6_port_stats" if match.group(1) else "port_stats"
                    ports[key].add(match.group(2))
        return ports

    def _parse_port_output(self, output, port):
        records = []
        current = None
        section = re.compile(
            r"^dhcp-relay\s+(?P<version>v6-)?port-stats\s+\S+\s+vlan\s+(?P<vlan>\S+)\s+(?:v6)?summary"
        )
        for raw_line in (output or "").splitlines():
            line = raw_line.strip()
            match = section.match(line)
            if match:
                if current:
                    records.append(current)
                current = {
                    "port": port,
                    "vlan": match.group("vlan"),
                }
                if match.group("version"):
                    current["version"] = "v6"
                continue
            if current and ":" in line:
                key, value = (part.strip() for part in line.split(":", 1))
                value = int(value) if value.isdigit() else value
                current[re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")] = value
        if current:
            records.append(current)
        if not records:
            records = parse_status_table(output) or parse_operational_facts(output)
            if not records and output and output.strip():
                records = [{"value": output.strip()}]
        for record in records:
            record["port"] = self._port_interface(record.get("port", port))
        return records

    @staticmethod
    def _port_interface(value):
        """Convert a VLAN-port resource identifier to a show-command interface."""
        value = str(value)
        for prefix in ("vlan-port:", "vlanport:"):
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        if ":" in value:
            value = value.rsplit(":", 1)[0]
        return value

    def populate_facts(self, connection, data=None):
        config = data if data is not None else connection.get("info configure dhcp-relay flat")
        configured = self._configured_ports(config)
        session_output = connection.get("show dhcp-relay session")
        sessions = parse_status_table(session_output) or parse_operational_facts(session_output)
        result = {
            "sessions": sessions,
            "port_stats": [],
            "v6_port_stats": [],
        }

        session_ports = {
            self._port_interface(session["client"])
            for session in sessions
            if session.get("client")
        }
        v4_ports = {
            self._port_interface(port) for port in configured["port_stats"]
        } or session_ports
        v6_ports = {
            self._port_interface(port) for port in configured["v6_port_stats"]
        }
        for port in sorted(v4_ports):
            output = connection.get("show dhcp-relay port-stats %s" % port)
            result["port_stats"].extend(self._parse_port_output(output, port))
        for port in sorted(v6_ports):
            output = connection.get("show dhcp-relay v6-port-stats %s" % port)
            result["v6_port_stats"].extend(self._parse_port_output(output, port))
        return {"dhcp_relay": result}
