# -*- coding: utf-8 -*-
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.channel_pair_pm.channel_pair_pm import Channel_pair_pmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.epon_interfaces.epon_interfaces import Epon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ngpon2_channel_groups.ngpon2_channel_groups import Ngpon2_channel_groupsArgs


_OPTIONAL_COMMAND_ERROR = re.compile(
    r"invalid token",
    re.IGNORECASE,
)


def _get_optional_config(connection, command):
    try:
        return connection.get(command)
    except Exception as exc:
        if not _OPTIONAL_COMMAND_ERROR.search(str(exc)):
            raise
        return ""


def _parse_lines(data, resource):
    records = {}
    for raw_line in unwrap_response(data).splitlines():
        line = raw_line.strip()
        if not line.startswith("configure "):
            continue
        tokens = line.split()
        if resource == "epon_interfaces" and len(tokens) >= 6:
            name = tokens[3]
            item = records.setdefault(name, {"name": name})
            field = tokens[4].replace("-", "_")
            value = tokens[5]
            item[field] = int(value) if field.startswith(("polling_period", "dba_polling")) else value
        elif resource == "channel_pair_pm" and len(tokens) >= 7:
            name = tokens[3]
            item = records.setdefault(name, {"name": name})
            item[tokens[4].replace("-", "_")] = tokens[6]
        elif resource == "ngpon2_channel_groups" and len(tokens) >= 6:
            group_id = int(tokens[3])
            item = records.setdefault(group_id, {"id": group_id})
            if tokens[4] == "channel-pair" and len(tokens) > 5:
                item.setdefault("channel_pairs", []).append(tokens[5])
            elif tokens[4] == "subchannel-group" and len(tokens) >= 9:
                sub_id = int(tokens[6])
                sub = next((entry for entry in item.setdefault("subchannel_groups", []) if entry.get("id") == sub_id), None)
                if sub is None:
                    sub = {"id": sub_id}
                    item["subchannel_groups"].append(sub)
                if tokens[7] == "channel-pair":
                    sub.setdefault("channel_pairs", []).append(tokens[8])
                elif len(tokens) > 8:
                    key = tokens[7].replace("-", "_")
                    value = tokens[8]
                    sub[key] = int(value) if key in ("closest_ont", "diff_reach") else value
            else:
                key = tokens[4].replace("-", "_")
                value = tokens[5]
                item[key] = int(value) if key == "polling_period" else value
    return utils.remove_empties(list(records.values()))

class Ngpon2_channel_groupsFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = Ngpon2_channel_groupsArgs.argument_spec
    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None: data = _get_optional_config(connection, "info configure channel-group flat")
        ansible_facts["ansible_network_resources"]["ngpon2_channel_groups"] = _parse_lines(data, "ngpon2_channel_groups")
        return ansible_facts

class Epon_interfacesFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = Epon_interfacesArgs.argument_spec
    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None: data = _get_optional_config(connection, "info configure epon interface flat")
        ansible_facts["ansible_network_resources"]["epon_interfaces"] = _parse_lines(data, "epon_interfaces")
        return ansible_facts

class Channel_pair_pmFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = Channel_pair_pmArgs.argument_spec
    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None: data = _get_optional_config(connection, "info configure channel-pair interface flat")
        ansible_facts["ansible_network_resources"]["channel_pair_pm"] = _parse_lines(data, "channel_pair_pm")
        return ansible_facts
