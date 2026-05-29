# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.equipment_onts import (
    Equipment_ontsTemplate,
)


class Equipment_onts(ResourceModule):
    """The isam_equipment_onts config class."""

    INTERFACE_FIELDS = [
        "sw_ver_pland",
        "sernum",
        "subslocid",
        "fec_up",
        "sw_dnload_version",
        "plnd_var",
        "enable_aes",
        "log_auth_pwd",
        "cvlantrans_mode",
        "planned_us_rate",
        "admin_state",
    ]
    SLOT_FIELDS = [
        "planned_card_type",
        "plndnumdataports",
        "plndnumvoiceports",
        "port_type",
        "transp_mode_rem",
        "no_mcast_control",
        "admin_state",
    ]
    SW_CTRL_FIELDS = [
        "hw_version",
        "ont_variant",
        "plnd_sw_version",
        "plnd_sw_ver_conf",
        "sw_dwload_ver",
    ]

    def __init__(self, module):
        super(Equipment_onts, self).__init__(
            empty_fact_val={"interfaces": [], "slots": [], "sw_ctrls": []},
            facts_module=Facts(module),
            module=module,
            resource="equipment_onts",
            tmplt=Equipment_ontsTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self.want or {"interfaces": [], "slots": [], "sw_ctrls": []}
        have = self.have or {"interfaces": [], "slots": [], "sw_ctrls": []}

        self._compare_section(
            want.get("interfaces") or [],
            have.get("interfaces") or [],
            "ont_idx",
            "interface",
            self.INTERFACE_FIELDS,
        )
        self._compare_section(
            want.get("slots") or [],
            have.get("slots") or [],
            "ont_slot_idx",
            "slot",
            self.SLOT_FIELDS,
        )
        self._compare_section(
            want.get("sw_ctrls") or [],
            have.get("sw_ctrls") or [],
            "sw_ctrl_id",
            "sw_ctrl",
            self.SW_CTRL_FIELDS,
        )

    def _compare_section(self, want_list, have_list, key, parser_prefix, fields):
        wantd = {entry[key]: entry for entry in want_list}
        haved = {entry[key]: entry for entry in have_list}

        if self.state == "deleted":
            for item_key, have in iteritems(haved):
                if not wantd or item_key in wantd:
                    self.addcmd(have, parser_prefix, negate=True)
            return

        if self.state == "overridden":
            for item_key, have in iteritems(haved):
                if item_key not in wantd:
                    self.addcmd(have, parser_prefix, negate=True)

        for item_key, want in iteritems(wantd):
            have = haved.get(item_key, {})
            desired = deepcopy(want)
            if self.state == "merged" and have:
                desired = deepcopy(have)
                desired.update(want)
            self._compare_entry(desired, have, parser_prefix, fields)

    def _compare_entry(self, want, have, parser_prefix, fields):
        for field in fields:
            inw = want.get(field)
            inh = have.get(field)
            if inw is not None and inw != inh:
                self.addcmd(want, "%s.%s" % (parser_prefix, field))
            elif self.state in ("replaced", "overridden") and inw is None and inh is not None:
                self.addcmd(have, "%s.%s" % (parser_prefix, field), negate=True)
