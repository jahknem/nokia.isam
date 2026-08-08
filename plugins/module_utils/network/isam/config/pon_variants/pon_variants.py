# -*- coding: utf-8 -*-
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import Ngpon2_channel_groupsTemplate, Epon_interfacesTemplate, Channel_pair_pmTemplate

class _VariantFacts(object):
    """Keep these new resources independent of the shared facts registry."""
    def __init__(self, resource): self.resource = resource
    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        return {"ansible_network_resources": {self.resource: []}}, []

class _Base(ResourceModule):
    fields = ()
    def execute_module(self):
        self.generate_commands()
        if self.state not in ("rendered", "parsed", "gathered"): self.run_commands()
        return self.result
    def generate_commands(self):
        for item in self.want or []:
            for field in self.fields:
                if item.get(field) is not None: self.addcmd(item, field)

class Ngpon2_channel_groups(_Base):
    fields = ("name", "polling_period", "raman_reduct", "ng2sys_id", "admin_state")
    def __init__(self, module): super(Ngpon2_channel_groups, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("ngpon2_channel_groups"), module=module, resource="ngpon2_channel_groups", tmplt=Ngpon2_channel_groupsTemplate())
    def generate_commands(self):
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
    def __init__(self, module): super(Epon_interfaces, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("epon_interfaces"), module=module, resource="epon_interfaces", tmplt=Epon_interfacesTemplate())
    def generate_commands(self):
        for item in self.want or []:
            for field in self.fields:
                if item.get(field) is not None:
                    self.addcmd(dict(name=item["name"], field=field.replace("_", "-"), value=item[field]), "interface")

class Channel_pair_pm(_Base):
    def __init__(self, module): super(Channel_pair_pm, self).__init__(empty_fact_val=[], facts_module=_VariantFacts("channel_pair_pm"), module=module, resource="channel_pair_pm", tmplt=Channel_pair_pmTemplate())
    def generate_commands(self):
        for item in self.want or []:
            for layer in ("fec_tc_layer", "xg_tc_layer"):
                if item.get(layer) is not None: self.addcmd(dict(name=item["name"], layer=layer.replace("_", "-"), pm_collect=item[layer]), "interface")
