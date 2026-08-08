# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

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

OPERATIONAL_FACT_RESOURCES = frozenset(
    (
        "active_alarms",
        "equipment_status",
        "interface_status",
        "ont_status",
        "pon_status",
        "software_status",
        "ont_ranging_status",
        "ont_software_status",
        "pon_pm_status",
    )
)


class _OperationalFacts(object):
    command = None
    key = None

    def __init__(self, module, subspec="config", options="options"):
        self._module = module

    def populate_facts(self, connection, ansible_facts, data=None):
        output = connection.get(self.command) if data is None else data
        value = self.parse(output)
        ansible_facts["ansible_network_resources"][self.key] = value
        return ansible_facts

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


class Ont_ranging_statusFacts(_OperationalFacts):
    command = "show equipment ont ranging-status channel-pair"
    key = "ont_ranging_status"

    def parse(self, output):
        return OntRangingStatusParser().parse(output)


class Ont_software_statusFacts(_OperationalFacts):
    key = "ont_software_status"

    def populate_facts(self, connection, ansible_facts, data=None):
        ansible_facts["ansible_network_resources"][self.key] = {
            "sw_version": parse_ont_sw_version(connection.get("show equipment ont sw-version")),
            "sw_download": parse_ont_sw_download(connection.get("show equipment ont sw-download")),
        }
        return ansible_facts


class Pon_pm_statusFacts(_OperationalFacts):
    command = "show pon interface tc-layer current-interval"
    key = "pon_pm_status"

    def parse(self, output):
        return parse_tc_layer_current_interval(output)
