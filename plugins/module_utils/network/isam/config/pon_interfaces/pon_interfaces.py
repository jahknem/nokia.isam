# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_interfaces import Pon_interfacesTemplate


class Pon_interfaces(ResourceModule):
    """The isam_pon_interfaces config class."""

    def __init__(self, module):
        super(Pon_interfaces, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="pon_interfaces",
            tmplt=Pon_interfacesTemplate(),
        )
        self.parsers = [
            "interface.label",
            "interface.fec_dn",
            "interface.ponid_interval",
            "interface.ponid_identifier",
            "interface.tconts_per_frame",
            "interface.admin_state",
            "interface.tc_layer.pm_collect",
            "interface.tc_layer.tca_enable",
        ]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = {entry["name"]: entry for entry in self.want}
        haved = {entry["name"]: entry for entry in self.have}

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def addcmd(self, data, tmplt, negate=False):
        parser = self._tmplt.get_parser(tmplt)
        if negate and parser.get("remval"):
            command = self._tmplt._template(value=parser["remval"], variables=data, fail_on_undefined=False)
            if command:
                if isinstance(command, list):
                    self.commands.extend(command)
                else:
                    self.commands.append(command)
            return
        super(Pon_interfaces, self).addcmd(data, tmplt, negate)

    def _compare(self, want, have):
        if want.get("tc_layer", {}).get("pm_collect") is not None or have.get("tc_layer", {}).get("pm_collect") is not None:
            want = dict(want)
            want["tc_layer"] = dict(want.get("tc_layer", {}))
            want["tc_layer"].pop("tca_enable", None)
            if have.get("tc_layer", {}).get("tca_enable") is not None:
                have = dict(have)
                have["tc_layer"] = dict(have["tc_layer"])
                have["tc_layer"].pop("tca_enable", None)
        self.compare(parsers=self.parsers, want=want, have=have)
