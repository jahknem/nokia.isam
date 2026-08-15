# -*- coding: utf-8 -*-
import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import canonical_key

class Ngpon2_channel_groupsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ngpon2_channel_groupsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        for raw_line in self._lines or []:
            tokens = raw_line.strip().split()
            if len(tokens) < 6 or tokens[:3] != ["configure", "channel-group", "id"]:
                continue
            group_id = int(tokens[3])
            item = result.setdefault(group_id, {"id": group_id})
            if tokens[4] == "channel-pair":
                item.setdefault("channel_pairs", []).append(tokens[5])
            elif tokens[4] == "subchannel-group" and len(tokens) >= 9:
                sub_id = int(tokens[6])
                sub = next((entry for entry in item.setdefault("subchannel_groups", []) if entry["id"] == sub_id), None)
                if sub is None:
                    sub = {"id": sub_id}
                    item["subchannel_groups"].append(sub)
                if tokens[7] == "channel-pair":
                    sub.setdefault("channel_pairs", []).append(tokens[8])
                else:
                    sub[canonical_key(tokens[7])] = tokens[8]
            elif len(tokens) >= 6:
                item[canonical_key(tokens[4])] = tokens[5]
        return result
    PARSERS = [
        {"name": "channel_group.name", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) name (?P<name>\S+)$"), "setval": "configure channel-group id {{ id }} name {{ name }}", "result": {"{{ id }}": {"id": "{{ id }}", "name": "{{ name }}"}}},
        {"name": "channel_group.polling_period", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) polling-period (?P<polling_period>\S+)$"), "setval": "configure channel-group id {{ id }} polling-period {{ polling_period }}"},
        {"name": "channel_group.raman_reduct", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) raman-reduct (?P<raman_reduct>\S+)$"), "setval": "configure channel-group id {{ id }} raman-reduct {{ raman_reduct }}"},
        {"name": "channel_group.ng2sys_id", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) ng2sys-id (?P<ng2sys_id>\S+)$"), "setval": "configure channel-group id {{ id }} ng2sys-id {{ ng2sys_id }}"},
        {"name": "channel_group.admin_state", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) admin-state (?P<admin_state>\S+)$"), "setval": "configure channel-group id {{ id }} admin-state {{ admin_state }}"},
        {"name": "channel_group.channel_pair", "getval": re.compile(r"^configure channel-group id (?P<id>\S+) channel-pair (?P<channel_pair>\S+)$"), "setval": "configure channel-group id {{ id }} channel-pair {{ channel_pair }}"},
        {"name": "subchannel_group", "getval": re.compile(r"^configure channel-group id (?P<channel_group_id>\S+) subchannel-group id (?P<id>\S+) (?P<field>name|auth-method|mcast-encrypt|fec-dn|closest-ont|diff-reach|admin-state|cpi) (?P<value>\S+)$"), "setval": "configure channel-group id {{ channel_group_id }} subchannel-group id {{ id }} {{ field }} {{ value }}"},
        {"name": "subchannel_group.channel_pair", "getval": re.compile(r"^configure channel-group id (?P<channel_group_id>\S+) subchannel-group id (?P<id>\S+) channel-pair (?P<channel_pair>\S+)$"), "setval": "configure channel-group id {{ channel_group_id }} subchannel-group id {{ id }} channel-pair {{ channel_pair }}"},
    ]

class Epon_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Epon_interfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        for raw_line in self._lines or []:
            tokens = raw_line.strip().split()
            if len(tokens) < 6 or tokens[:3] != ["configure", "epon", "interface"]:
                continue
            name = tokens[3]
            item = result.setdefault(name, {"name": name})
            field = canonical_key(tokens[4])
            value = tokens[5]
            item[field] = int(value) if field.startswith(("polling_period", "dba_polling")) else value
        return result
    PARSERS = [
        {"name": "interface", "getval": re.compile(r"^configure epon interface (?P<name>\S+) (?P<field>polling-period|dba-polling[0-4]|admin-state) (?P<value>\S+)$"), "setval": "configure epon interface {{ name }} {{ field }} {{ value }}", "result": {"{{ name }}": {"name": "{{ name }}"}}},
        {"name": "interface.polling_period", "getval": re.compile(r"^configure epon interface (?P<name>\S+) polling-period (?P<polling_period>\S+)$"), "setval": "configure epon interface {{ name }} polling-period {{ polling_period }}", "result": {"{{ name }}": {"name": "{{ name }}", "polling_period": "{{ polling_period }}"}}},
        {"name": "interface.dba_polling", "getval": re.compile(r"^configure epon interface (?P<name>\S+) (?P<dba_polling>dba-polling[0-4]) (?P<value>\S+)$"), "setval": "configure epon interface {{ name }} {{ dba_polling }} {{ value }}", "result": {"{{ name }}": {"name": "{{ name }}", "{{ dba_polling }}": "{{ value }}"}}},
        {"name": "interface.admin_state", "getval": re.compile(r"^configure epon interface (?P<name>\S+) admin-state (?P<admin_state>\S+)$"), "setval": "configure epon interface {{ name }} admin-state {{ admin_state }}", "result": {"{{ name }}": {"name": "{{ name }}", "admin_state": "{{ admin_state }}"}}},
    ]

class Channel_pair_pmTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Channel_pair_pmTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        for raw_line in self._lines or []:
            tokens = raw_line.strip().split()
            if len(tokens) < 7 or tokens[:4] != ["configure", "channel-pair", "interface", tokens[3]]:
                continue
            item = result.setdefault(tokens[3], {"name": tokens[3]})
            item[canonical_key(tokens[4])] = tokens[6]
        return result
    PARSERS = [
        {"name": "interface", "compval": "name", "getval": re.compile(r"^configure channel-pair interface (?P<name>\S+) (?P<layer>fec-tc-layer|xg-tc-layer) pm-collect (?P<pm_collect>\S+)$"), "setval": "configure channel-pair interface {{ name }} {{ layer }} pm-collect {{ pm_collect }}", "result": {"{{ name }}": {"name": "{{ name }}"}}},
        {"name": "interface.fec_tc_layer", "compval": "name", "getval": re.compile(r"^configure channel-pair interface (?P<name>\S+) fec-tc-layer pm-collect (?P<pm_collect>\S+)$"), "setval": "configure channel-pair interface {{ name }} fec-tc-layer pm-collect {{ pm_collect }}", "result": {"{{ name }}": {"name": "{{ name }}", "fec_tc_layer": "{{ pm_collect }}"}}},
        {"name": "interface.xg_tc_layer", "compval": "name", "getval": re.compile(r"^configure channel-pair interface (?P<name>\S+) xg-tc-layer pm-collect (?P<pm_collect>\S+)$"), "setval": "configure channel-pair interface {{ name }} xg-tc-layer pm-collect {{ pm_collect }}", "result": {"{{ name }}": {"name": "{{ name }}", "xg_tc_layer": "{{ pm_collect }}"}}},
    ]
