# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm import (
    AlarmTemplate,
)


class Alarm(ResourceModule):
    def __init__(self, module):
        super(Alarm, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="alarm",
            tmplt=AlarmTemplate(),
        )
        self.parsers = []

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = self.want or {}
        haved = self.have or {}

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            if wantd:
                haved = {k: v for k, v in iteritems(haved) if k in wantd} if wantd else {}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        if want.get("log") != have.get("log"):
            log = want.get("log") or have.get("log") or {}
            if log:
                self._compare_log(want_log=want.get("log", {}), have_log=have.get("log", {}))

        self.compare(parsers=["entry"], want=want, have=have)

    def _compare_log(self, want_log, have_log):
        if want_log:
            cmd = "configure alarm log-sev-level {0} log-full-action {1} non-itf-rep-sev-level {2}".format(
                want_log.get("log_sev_level", have_log.get("log_sev_level", "warning")),
                want_log.get("log_full_action", have_log.get("log_full_action", "wrap")),
                want_log.get("non_itf_rep_sev_level", have_log.get("non_itf_rep_sev_level", "warning")),
            )
            self.commands.append(cmd)
