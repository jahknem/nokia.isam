# -*- coding: utf-8 -*-
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import Ngpon2_channel_groupsTemplate, Epon_interfacesTemplate, Channel_pair_pmTemplate

def _parsed(data, template):
    return utils.remove_empties(template(lines=[line.strip() for line in unwrap_response(data).splitlines() if line.strip()]).parse())

class Ngpon2_channel_groupsFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = None
    def populate_facts(self, connection, ansible_facts, data=None):
        ansible_facts["ansible_network_resources"]["ngpon2_channel_groups"] = _parsed(data or connection.get("info configure channel-group flat"), Ngpon2_channel_groupsTemplate)
        return ansible_facts

class Epon_interfacesFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = None
    def populate_facts(self, connection, ansible_facts, data=None):
        ansible_facts["ansible_network_resources"]["epon_interfaces"] = _parsed(data or connection.get("info configure epon flat"), Epon_interfacesTemplate)
        return ansible_facts

class Channel_pair_pmFacts(object):
    def __init__(self, module, subspec="config", options="options"): self.argument_spec = None
    def populate_facts(self, connection, ansible_facts, data=None):
        ansible_facts["ansible_network_resources"]["channel_pair_pm"] = _parsed(data or connection.get("info configure channel-pair flat"), Channel_pair_pmTemplate)
        return ansible_facts
