# -*- coding: utf-8 -*-
import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate

class Ngpon2_channel_groupsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ngpon2_channel_groupsTemplate, self).__init__(lines=lines, tmplt=self, module=module)
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
    PARSERS = [{"name": "interface", "getval": re.compile(r"^configure epon interface (?P<name>\S+) (?P<field>polling-period|dba-polling[0-4]|admin-state) (?P<value>\S+)$"), "setval": "configure epon interface {{ name }} {{ field }} {{ value }}", "result": {"{{ name }}": {"name": "{{ name }}"}}}]

class Channel_pair_pmTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Channel_pair_pmTemplate, self).__init__(lines=lines, tmplt=self, module=module)
    PARSERS = [{"name": "interface", "compval": "name", "getval": re.compile(r"^configure channel-pair interface (?P<name>\S+) (?P<layer>fec-tc-layer|xg-tc-layer) pm-collect (?P<pm_collect>\S+)$"), "setval": "configure channel-pair interface {{ name }} {{ layer }} pm-collect {{ pm_collect }}", "result": {"{{ name }}": {"name": "{{ name }}", "{{ layer }}": "{{ pm_collect }}"}}}]
