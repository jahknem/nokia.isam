# -*- coding: utf-8 -*-
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import canonical_key
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import Ngpon2_channel_groupsTemplate, Epon_interfacesTemplate, Channel_pair_pmTemplate


_OPTIONAL_COMMAND_ERROR = re.compile(
    r"invalid token",
    re.IGNORECASE,
)


class _VariantFacts(object):
    """Facts adapter for the small PON variant resources."""
    def __init__(self, resource, module):
        self.resource = resource
        self.module = module

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        if data is None:
            commands = {
                "ngpon2_channel_groups": "info configure channel-group flat",
                "epon_interfaces": "info configure epon interface flat",
                "channel_pair_pm": "info configure channel-pair interface flat",
            }
            try:
                data = get_resource_connection(self.module).get(commands[self.resource])
            except Exception as exc:
                # Optional PON families are absent from some ISAM shelves.
                if not _OPTIONAL_COMMAND_ERROR.search(str(exc)):
                    raise
                data = ""
        return {"ansible_network_resources": {self.resource: self._parse(data)}}, []

    def _parse(self, data):
        records = {}
        for raw_line in (data or "").splitlines():
            line = raw_line.strip()
            if not line.startswith("configure "):
                continue
            tokens = line.split()
            if self.resource == "epon_interfaces" and len(tokens) >= 6:
                name = tokens[3]
                item = records.setdefault(name, {"name": name})
                item[canonical_key(tokens[4])] = tokens[5]
            elif self.resource == "channel_pair_pm" and len(tokens) >= 7:
                name = tokens[3]
                item = records.setdefault(name, {"name": name})
                item[canonical_key(tokens[4])] = tokens[6]
            elif self.resource == "ngpon2_channel_groups" and len(tokens) >= 6:
                group_id = int(tokens[3])
                item = records.setdefault(group_id, {"id": group_id})
                if tokens[4] == "channel-pair" and len(tokens) > 5:
                    item.setdefault("channel_pairs", []).append(tokens[5])
                elif tokens[4] == "subchannel-group" and len(tokens) >= 9:
                    sub_id = int(tokens[6])
                    sub = next(
                        (entry for entry in item.setdefault("subchannel_groups", [])
                         if entry.get("id") == sub_id),
                        None,
                    )
                    if sub is None:
                        sub = {"id": sub_id}
                        item["subchannel_groups"].append(sub)
                    if tokens[7] == "channel-pair":
                        sub.setdefault("channel_pairs", []).append(tokens[8])
                    elif len(tokens) > 8:
                        sub[canonical_key(tokens[7])] = tokens[8]
                else:
                    item[canonical_key(tokens[4])] = tokens[5]
        return list(records.values())

class _Base(ResourceModule):
    fields = ()
    def execute_module(self):
        self.generate_commands()
        if self.state not in ("rendered", "parsed", "gathered"): self.run_commands()
        return self.result
    def generate_commands(self):
        if self._prepare_state_commands():
            return
        for item in self.want or []:
            for field in self.fields:
                if item.get(field) is not None: self.addcmd(item, field)

    def _prepare_state_commands(self):
        desired = self.want or []
        current = {item.get("name", item.get("id")): item for item in self.have or []}
        desired_ids = {item.get("name", item.get("id")) for item in desired}
        if self.state == "deleted":
            targets = desired or list(self.have or [])
            self.commands = [self._delete_command(item) for item in targets]
            return True
        self.commands = []
        if self.state == "overridden":
            self.commands.extend(
                self._delete_command(item)
                for key, item in current.items()
                if key not in desired_ids
            )
        if self.state in ("replaced", "overridden"):
            self.commands.extend(
                self._delete_command(item)
                for item in desired
                if item.get("name", item.get("id")) in current
            )
        return False

    def _delete_command(self, item):
        key = item.get("name", item.get("id"))
        if self.resource == "ngpon2_channel_groups":
            return "configure channel-group no id %s" % key
        if self.resource == "epon_interfaces":
            return "configure epon no interface %s" % key
        return "configure channel-pair no interface %s" % key

class Ngpon2_channel_groups(_Base):
    fields = ("name", "polling_period", "raman_reduct", "ng2sys_id", "admin_state")
    def __init__(self, module): super(Ngpon2_channel_groups, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("ngpon2_channel_groups", module), module=module, resource="ngpon2_channel_groups", tmplt=Ngpon2_channel_groupsTemplate())
    def generate_commands(self):
        if self._prepare_state_commands():
            return
        for group in self.want or []:
            for field in self.fields:
                if group.get(field) is not None: self.addcmd(group, "channel_group." + field)
            for pair in group.get("channel_pairs", []): self.addcmd(dict(id=group["id"], channel_pair=pair), "channel_group.channel_pair")
            for sub in group.get("subchannel_groups", []):
                for field in ("name", "auth_method", "mcast_encrypt", "fec_dn", "closest_ont", "diff_reach", "admin_state", "cpi"):
                    if sub.get(field) is not None: self.addcmd(dict(channel_group_id=group["id"], id=sub["id"], field=field.replace("_", "-"), value=sub[field]), "subchannel_group")
                for pair in sub.get("channel_pairs", []): self.addcmd(dict(channel_group_id=group["id"], id=sub["id"], channel_pair=pair), "subchannel_group.channel_pair")

class Epon_interfaces(_Base):
    fields = ("polling_period", "dba_polling0", "dba_polling1", "dba_polling2", "dba_polling3", "dba_polling4", "admin_state")
    def __init__(self, module): super(Epon_interfaces, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("epon_interfaces", module), module=module, resource="epon_interfaces", tmplt=Epon_interfacesTemplate())
    def generate_commands(self):
        if self._prepare_state_commands():
            return
        for item in self.want or []:
            for field in self.fields:
                if item.get(field) is not None:
                    self.addcmd(dict(name=item["name"], field=field.replace("_", "-"), value=item[field]), "interface")

class Channel_pair_pm(_Base):
    def __init__(self, module): super(Channel_pair_pm, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("channel_pair_pm", module), module=module, resource="channel_pair_pm", tmplt=Channel_pair_pmTemplate())
    def generate_commands(self):
        if self._prepare_state_commands():
            return
        for item in self.want or []:
            for layer in ("fec_tc_layer", "xg_tc_layer"):
                if item.get(layer) is not None: self.addcmd(dict(name=item["name"], layer=layer.replace("_", "-"), pm_collect=item[layer]), "interface")
