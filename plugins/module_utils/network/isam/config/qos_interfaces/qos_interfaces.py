# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import Qos_interfacesTemplate


class Qos_interfaces(ResourceModule):
    """The isam_qos_interfaces config class."""

    def __init__(self, module):
        super(Qos_interfaces, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="qos_interfaces",
            tmplt=Qos_interfacesTemplate(),
        )
        self.top_parsers = [
            "interface.scheduler_node",
            "interface.ingress_profile",
            "interface.cac_profile",
            "interface.ext_cac",
            "interface.ds_queue_sharing",
            "interface.us_queue_sharing",
            "interface.ds_num_queue",
            "interface.ds_num_rem_queue",
            "interface.us_num_queue",
            "interface.queue_stats_on",
            "interface.autoschedule",
            "interface.oper_weight",
            "interface.oper_rate",
            "interface.us_vlanport_queue",
            "interface.dsfld_shaper_prof",
            "interface.bandwidth_profile",
            "interface.bandwidth_sharing",
            "interface.aggr_usq_profile",
            "interface.aggr_dsq_profile",
            "interface.gem_sharing",
            "interface.scheduler_mode",
            "interface.mc_scheduler_node",
            "interface.bc_scheduler_node",
            "interface.ds_schedule_tag",
        ]
        self.list_parsers = {
            "queue": [
                "interface.queue.priority",
                "interface.queue.weight",
                "interface.queue.oper_weight",
                "interface.queue.queue_profile",
                "interface.queue.shaper_profile",
            ],
            "upstream_queue": [
                "interface.upstream_queue.priority",
                "interface.upstream_queue.weight",
                "interface.upstream_queue.bandwidth_profile",
                "interface.upstream_queue.ext_bw",
                "interface.upstream_queue.bandwidth_sharing",
                "interface.upstream_queue.queue_profile",
                "interface.upstream_queue.shaper_profile",
            ],
            "ds_rem_queue": [
                "interface.ds_rem_queue.priority",
                "interface.ds_rem_queue.weight",
            ],
        }

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
            if not wantd:
                wantd = {}
            else:
                haved = {k: v for k, v in iteritems(haved) if k in wantd}

        if self.state == "overridden" or (self.state == "deleted" and not self.want):
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        if self.state == "deleted" and want:
            requested = {
                key for key in want
                if key not in {"name", "id", "queue", "upstream_queue", "ds_rem_queue"}
            }
            for field in requested:
                value = have.get(field)
                if value is not None:
                    self.addcmd(
                        {"name": have.get("name", want.get("name")), field: value},
                        "interface.%s" % field,
                        True,
                    )
        else:
            self.compare(parsers=self.top_parsers, want=want, have=have)
        for list_name, parsers in iteritems(self.list_parsers):
            self._compare_list(list_name, parsers, want, have)

    def _compare_list(self, list_name, parsers, want, have):
        wantd = {entry["id"]: entry for entry in want.get(list_name, [])}
        haved = {entry["id"]: entry for entry in have.get(list_name, [])}

        targeted_delete = self.state == "deleted" and any(
            key not in {"name", "id"} for key in want
        )
        if self.state == "overridden" or (self.state == "deleted" and not targeted_delete):
            for key, have_entry in iteritems(haved):
                if key not in wantd:
                    self._compare_list_entry(parsers, {}, have_entry, have.get("name"))

        for key, want_entry in iteritems(wantd):
            self._compare_list_entry(parsers, want_entry, haved.get(key, {}), want.get("name"))

    def _compare_list_entry(self, parsers, want, have, name):
        for parser in parsers:
            field = self._tmplt.get_parser(parser).get("compval")
            inw = want.get(field)
            inh = have.get(field)

            if self.state == "merged" and inw is None:
                continue

            data = {"name": name, "id": want.get("id", have.get("id"))}
            if inw is not None and inw != inh:
                data[field] = inw
                self.addcmd(data, parser, False)
            elif inw is None and inh is not None and self.state in ["replaced", "overridden", "deleted"]:
                data[field] = inh
                self.addcmd(data, parser, True)
