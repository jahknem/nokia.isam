# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    Generic_ponTemplate,
)


class Generic_pon(ResourceModule):
    """The isam_generic_pon config class."""

    def __init__(self, module):
        super(Generic_pon, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="generic_pon",
            tmplt=Generic_ponTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self._normalize(self.want)
        have = self._normalize(self.have)

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        self._compare_dpinteg_threshold(want, have)
        self._compare_utilization(want, have)
        self._compare_ont(want, have)
        self._compare_alarmflag(want, have)

    def _compare_dpinteg_threshold(self, want, have):
        wk = want.get("dpinteg_threshold")
        hk = have.get("dpinteg_threshold")
        if wk is not None and wk != hk:
            self.addcmd({"dpinteg_threshold": wk}, "dpinteg_threshold")
        # NOTE: dpinteg_threshold has no no-form in the template (no `negate`
        # in getval, no `'no ' if ...` in setval), so it cannot be negated for
        # replaced/overridden states when absent from want.

    def _compare_utilization(self, want, have):
        wsec = want.get("utilization", {})
        hsec = have.get("utilization", {})
        self._compare_section("utilization", wsec, hsec,
                              ["pon_pmcollect", "ont_pmcollect"])

    def _compare_ont(self, want, have):
        wsec = want.get("ont", {})
        hsec = have.get("ont", {})
        self._compare_section("ont", wsec, hsec,
                              ["slid_mode", "sn_bundle_timer", "sw_ver_mis_block", "sn_autounlock"])

    def _compare_alarmflag(self, want, have):
        wsec = want.get("alarmflag", {})
        hsec = have.get("alarmflag", {})
        self._compare_section("alarmflag", wsec, hsec,
                              ["ponlos_alarm_ctrl"])

    def _compare_section(self, section, want, have, fields):
        for field in fields:
            wv = want.get(field)
            hv = have.get(field)
            if wv is not None and wv != hv:
                self.addcmd({section: {field: wv}}, section + "." + field)
            elif (
                self.state in ["replaced", "overridden"]
                and hv is not None
                and wv is None
            ):
                # Negate: field present in have but absent from want
                self.addcmd({section: {field: False}}, section + "." + field)

    def _normalize(self, data):
        if not data:
            return {}
        return deepcopy(data)
