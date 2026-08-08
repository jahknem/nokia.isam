# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_boards import (
    Xdsl_boardsTemplate,
)


class Xdsl_boards(ResourceModule):
    """The isam_xdsl_boards config class."""

    BOARD_FIELDS = [
        "admin_state",
        "card_type",
        "dpbo_profile",
        "vce_profile",
    ]
    VP_BOARD_FIELDS = [
        "admin_state",
    ]

    def __init__(self, module):
        super(Xdsl_boards, self).__init__(
            empty_fact_val={"boards": [], "vp_boards": []},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_boards",
            tmplt=Xdsl_boardsTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self.want or {"boards": [], "vp_boards": []}
        have = self.have or {"boards": [], "vp_boards": []}

        self._compare_section(
            want.get("boards") or [],
            have.get("boards") or [],
            "board_id",
            "board",
            self.BOARD_FIELDS,
        )
        self._compare_section(
            want.get("vp_boards") or [],
            have.get("vp_boards") or [],
            "vp_board_id",
            "vp_board",
            self.VP_BOARD_FIELDS,
        )

    def _compare_section(self, want_list, have_list, key, parser_prefix, fields):
        wantd = {entry[key]: entry for entry in want_list}
        haved = {entry[key]: entry for entry in have_list}

        if self.state == "deleted":
            for item_key, have in iteritems(haved):
                if not wantd or item_key in wantd:
                    self.addcmd(have, parser_prefix, negate=True)
            return

        if self.state in ["replaced", "overridden"]:
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
