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
            "interface.ber_calc_period",
            "interface.polling_period",
            "interface.sig_degrade_th",
            "interface.sig_fail_th",
            "interface.raman_reduct",
            "interface.closest_ont",
            "interface.diff_reach",
            "interface.pon_tag",
            "interface.pon_id",
            "interface.mcast_encrypt",
            "interface.auth_method",
            "interface.ponid_interval",
            "interface.ponid_odn",
            "interface.ponid_identifier",
            "interface.max_ranging_onts",
            "interface.tconts_per_frame",
            "interface.pon_speed",
            "interface.burst_overhead",
            "interface.onu_prov_mode",
            "interface.admin_state",
            "interface.tc_layer.pm_collect",
            "interface.tc_layer.tca_enable",
            "interface.tc_layer_threshold.error_frags_up",
            "interface.mcast_tc_layer.pm_collect",
            "interface.phy_layer.pm_collect",
            "interface.fec_tc_layer.pm_collect",
            "interface.xg_tc_layer.pm_collect",
            "interface.otdr.mode",
            "interface.utilization.pon_pmcollect",
            "interface.utilization.ont_pmcollect",
            "interface.utilization.ontbulk_pmcollect",
            "interface.deact_ont_tca.mode",
            "interface.deact_ont_tca.monitor_interval",
        ]
        self.parsers.extend(
            "interface.utilization.threshold.%s" % field
            for field in (
                "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd",
                "txtotutillo", "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi",
                "dbacongperiodmd", "dbacongperiodlo", "txucdropfrmhi", "txucdropfrmmd",
                "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
                "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi",
                "rxtotdropfrmmd", "rxtotdropfrmlo", "numtcint", "numtcintdba", "dbacongthresh",
            )
        )
        for section in ("threshold_percent", "threshold_number"):
            self.parsers.extend(
                "interface.deact_ont_tca.%s.%s" % (section, field)
                for field in ("high", "high_clr", "low", "low_clr")
            )

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
            # PON interfaces are hardware resources, not removable objects.
            # Do not turn an identity-only request into a full reset.
            requested = self._module.params.get("config") or []
            if requested and all(
                not any(value is not None for key, value in entry.items() if key != "name")
                for entry in requested
            ):
                return
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
        restricted = ("fec_dn", "closest_ont", "diff_reach", "auth_method")
        restricted_change = any(
            want.get(field) is not None and want.get(field) != have.get(field)
            for field in restricted
        ) or (
            self.state in ["replaced", "overridden", "deleted"]
            and any(have.get(field) is not None and want.get(field) is None for field in restricted)
        )

        if restricted_change and have.get("admin_state") == "up":
            original_want_admin = want.get("admin_state")
            want = dict(want)
            have = dict(have)
            have["admin_state"] = "down"
            if original_want_admin != "down":
                want["admin_state"] = "up"
            self.addcmd({"name": have["name"], "admin_state": "down"}, "interface.admin_state")
            self.compare(
                parsers=[parser for parser in self.parsers if parser != "interface.admin_state"],
                want=want,
                have=have,
            )
            if original_want_admin != "down":
                self.addcmd({"name": have["name"], "admin_state": "up"}, "interface.admin_state")
            return

        if want.get("tc_layer", {}).get("pm_collect") is not None or have.get("tc_layer", {}).get("pm_collect") is not None:
            want = dict(want)
            want["tc_layer"] = dict(want.get("tc_layer", {}))
            want["tc_layer"].pop("tca_enable", None)
            if have.get("tc_layer", {}).get("tca_enable") is not None:
                have = dict(have)
                have["tc_layer"] = dict(have["tc_layer"])
                have["tc_layer"].pop("tca_enable", None)
        self.compare(parsers=self.parsers, want=want, have=have)
