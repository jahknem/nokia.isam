# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from copy import deepcopy

from ansible.module_utils._text import to_text
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import covers_entry, deleted_targets
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dist_service.dist_service import Isam_dist_serviceFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dist_service import Isam_dist_serviceTemplate


# Device defaults (CLI guide): "no service-type" is apipe, "no qos-profile" is none.
DEFAULTS = {"service_type": "apipe", "qos_profile": "none"}


class _DistServiceFactsProvider(object):
    def __init__(self, module):
        self._facts = Facts(module)
        self._resource_facts = Isam_dist_serviceFacts(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        ansible_facts = {"ansible_network_resources": {}}
        try:
            self._resource_facts.populate_facts(self._facts._connection, ansible_facts, data=data)
        except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
            self._facts._module.fail_json(msg=to_text(exc))
        return ansible_facts, []


class Isam_dist_service(IsamResourceModule):
    def __init__(self, module):
        super(Isam_dist_service, self).__init__(
            empty_fact_val=[], facts_module=_DistServiceFactsProvider(module), module=module,
            resource="isam_dist_service", tmplt=Isam_dist_serviceTemplate(),
        )
        self.parsers = ["service_type", "qos_profile"]
        self.before = deepcopy(self.have)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = dict((entry["name"], _without_defaults(entry)) for entry in self.want or [])
        haved = dict((entry["name"], _without_defaults(entry)) for entry in self.have or [])
        if self.state == "deleted":
            # an identity (or a full entry) removes the service, named attributes reset only themselves
            for target, have in deleted_targets(wantd, haved, ("name",)):
                if covers_entry(wantd.get(have["name"], {}), have, ("name",)):
                    self.addcmd(have, "service", True)
                else:
                    self.compare(parsers=self.parsers, want=target, have=have)
            return
        if self.state == "overridden":
            for name, have in haved.items():
                if name not in wantd:
                    self.addcmd(have, "service", True)
        for name, want in wantd.items():
            have = haved.get(name, {})
            if self.state == "merged":
                want = dict(have, **want)
            before = len(self.commands)
            self.compare(parsers=self.parsers, want=want, have=have)
            if not have and len(self.commands) == before:
                self.addcmd(want, "service", False)  # a new service with only default settings


def _without_defaults(entry):
    """Device defaults (CLI guide) equal unset values."""
    return dict((key, value) for key, value in entry.items() if value is not None and DEFAULTS.get(key) != value)
