# -*- coding: utf-8 -*-
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.channel_pair_pm.channel_pair_pm import Channel_pair_pmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.epon_interfaces.epon_interfaces import Epon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ngpon2_channel_groups.ngpon2_channel_groups import Ngpon2_channel_groupsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import canonical_key


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


# Whole-resource read and single-instance read (targeted gathering) per resource.
VARIANT_COMMANDS = {
    "ngpon2_channel_groups": ("info configure channel-group flat", "info configure channel-group id %s flat"),
    "epon_interfaces": ("info configure epon interface flat", "info configure epon interface %s flat"),
    "channel_pair_pm": ("info configure channel-pair interface flat", "info configure channel-pair interface %s flat"),
}


class _OptionalConnection(object):
    """A platform without the feature ("invalid token") has no instances, also for single reads."""

    def __init__(self, connection):
        self._connection = connection

    def get(self, command, *args, **kwargs):
        return _get_optional_config(self._connection, command)


def get_variant_config(module, connection, resource):
    """The whole resource, or only the instances named in config with state gathered."""
    full, single = VARIANT_COMMANDS[resource]
    module = module if getattr(module, "params", None) is not None else None
    return get_targeted_config(module, _OptionalConnection(connection), resource, full, {"config": single})


_ARGSPECS = {
    "ngpon2_channel_groups": Ngpon2_channel_groupsArgs.argument_spec,
    "epon_interfaces": Epon_interfacesArgs.argument_spec,
    "channel_pair_pm": Channel_pair_pmArgs.argument_spec,
}


def _typed(options, key, value):
    """value converted to the argspec type of key (int fields); left as is when it is not a number."""
    if (options.get(key) or {}).get("type") == "int":
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    return value


def _parse_lines(data, resource):
    """The one parser of the PON variant resources (isam_facts and the resource modules), typed per argspec."""
    options = _ARGSPECS[resource]["config"]["options"]
    sub_options = (options.get("subchannel_groups") or {}).get("options") or {}
    records = {}
    for raw_line in unwrap_response(data).splitlines():
        line = raw_line.strip()
        if not line.startswith("configure "):
            continue
        tokens = line.split()
        if resource == "epon_interfaces" and len(tokens) >= 6:
            name = tokens[3]
            item = records.setdefault(name, {"name": name})
            field = canonical_key(tokens[4])
            item[field] = _typed(options, field, tokens[5])
        elif resource == "channel_pair_pm" and len(tokens) >= 7:
            name = tokens[3]
            item = records.setdefault(name, {"name": name})
            item[canonical_key(tokens[4])] = tokens[6]
        elif resource == "ngpon2_channel_groups" and len(tokens) >= 6:
            group_id = _typed(options, "id", tokens[3])
            item = records.setdefault(group_id, {"id": group_id})
            if tokens[4] == "channel-pair" and len(tokens) > 5:
                item.setdefault("channel_pairs", []).append(tokens[5])
            elif tokens[4] == "subchannel-group" and len(tokens) >= 9:
                sub_id = _typed(sub_options, "id", tokens[6])
                sub = next((entry for entry in item.setdefault("subchannel_groups", []) if entry.get("id") == sub_id), None)
                if sub is None:
                    sub = {"id": sub_id}
                    item["subchannel_groups"].append(sub)
                if tokens[7] == "channel-pair":
                    sub.setdefault("channel_pairs", []).append(tokens[8])
                elif len(tokens) > 8:
                    key = canonical_key(tokens[7])
                    sub[key] = _typed(sub_options, key, tokens[8])
            else:
                key = canonical_key(tokens[4])
                item[key] = _typed(options, key, tokens[5])
    return list(records.values())

class Ngpon2_channel_groupsFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ngpon2_channel_groupsArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = get_variant_config(self._module, connection, "ngpon2_channel_groups")
        ansible_facts["ansible_network_resources"]["ngpon2_channel_groups"] = _parse_lines(data, "ngpon2_channel_groups")
        return ansible_facts

class Epon_interfacesFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Epon_interfacesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = get_variant_config(self._module, connection, "epon_interfaces")
        ansible_facts["ansible_network_resources"]["epon_interfaces"] = _parse_lines(data, "epon_interfaces")
        return ansible_facts

class Channel_pair_pmFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Channel_pair_pmArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = get_variant_config(self._module, connection, "channel_pair_pm")
        ansible_facts["ansible_network_resources"]["channel_pair_pm"] = _parse_lines(data, "channel_pair_pm")
        return ansible_facts
