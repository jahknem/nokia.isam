# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_boards import (
    BOARD_ATTRS,
    BOARD_SUBNODES,
    VP_BOARD_ATTRS,
    VP_LINK_ATTRS,
    Xdsl_boardsTemplate,
)


class Xdsl_boards(IsamResourceModule):
    """The isam_xdsl_boards config class."""

    # First match wins: the sub-node and vp-link scopes must precede the
    # board/vp-board scope, otherwise e.g. a board-level ``dpbo-profile`` would
    # be appended to a ``vect-fallback`` command and land in the sub-node.
    COMPACT_COMMAND_SCOPES = (
        (r"^(?P<scope>configure xdsl board \S+ vect-fallback) (?P<suffix>.+)$", "vect_fallback"),
        (r"^(?P<scope>configure xdsl board \S+ auto-port-reset) (?P<suffix>.+)$", "auto_port_reset"),
        (r"^(?P<scope>configure xdsl vp-board \S+ vp-link \S+) (?P<suffix>.+)$", "vp_link"),
        (r"^(?P<scope>configure xdsl board \S+) (?P<suffix>.+)$", "board"),
        (r"^(?P<scope>configure xdsl vp-board \S+) (?P<suffix>.+)$", "vp_board"),
    )

    BOARD_FIELDS = [field for field, _keyword, _kind in BOARD_ATTRS]
    VP_BOARD_FIELDS = [field for field, _keyword, _kind in VP_BOARD_ATTRS]

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
        # Without config ResourceModule supplies empty_fact_val, a truthy dict of
        # empty lists: test the contents, otherwise deleted would silently do nothing.
        delete_all = self.state == "deleted" and not any(want.values())

        self._compare_section(
            want.get("boards") or [],
            have.get("boards") or [],
            "board_id",
            "board",
            self._compare_board,
            delete_all or bool(want.get("boards")),
            reset=self._reset_board,
        )
        self._compare_section(
            want.get("vp_boards") or [],
            have.get("vp_boards") or [],
            "vp_board_id",
            "vp_board",
            self._compare_vp_board,
            delete_all or bool(want.get("vp_boards")),
        )

    def _compare_section(self, want_list, have_list, key, parser_prefix, compare, requested=True, reset=None):
        """reset(want, have): remove an entry by resetting its attributes, for entries
        without a removal command (xDSL boards); otherwise the entry's remval is used."""
        wantd = dict((entry[key], entry) for entry in want_list)
        haved = dict((entry[key], entry) for entry in have_list)

        def remove(want, have):
            if reset:
                reset(want, have)
            else:
                self.addcmd(have, parser_prefix, negate=True)

        if self.state == "deleted":
            if not requested:
                return
            for item_key, have in iteritems(haved):
                if not wantd or item_key in wantd:
                    remove(wantd.get(item_key, {}), have)
            return

        if self.state in ["overridden"]:
            for item_key, have in iteritems(haved):
                if item_key not in wantd:
                    remove({}, have)

        for item_key, want in iteritems(wantd):
            compare(want, haved.get(item_key, {}))

    @property
    def _replacing(self):
        return self.state in ("replaced", "overridden") or self._resetting

    _resetting = False

    def _reset_board(self, want, have):
        """A board has no removal command ("configure xdsl no board" is an invalid token,
        lab ISAM): its attributes are reset, only the named ones when want names any."""
        named = [field for field, value in want.items() if field != "board_id" and value not in (None, {}, [])]
        keep = dict((field, value) for field, value in have.items() if named and field not in named)
        self._resetting = True
        try:
            self._compare_board(dict(keep, board_id=have["board_id"]), have)
        finally:
            self._resetting = False

    def _compare_fields(self, want, have, attrs, parser_prefix, render_want, render_have):
        """Set changed attributes; on replaced/overridden remove the unwanted ones.

        Flags compare ``False`` equal to absent: their default (``no <flag>``)
        is not reported by the facts. ``rendered`` has no device state to compare
        with and renders an explicit ``False`` as ``no <flag>``.
        """
        for field, _keyword, kind in attrs:
            inw = want.get(field)
            inh = have.get(field)
            if kind == "flag":
                inw = None if inw is None else bool(inw)
                inh = bool(inh) if self.state != "rendered" else inh
                if inw is not None and inw != inh:
                    self.addcmd(render_want, "%s.%s" % (parser_prefix, field))
                elif inw is None and inh and self._replacing:
                    self.addcmd(render_have, "%s.%s" % (parser_prefix, field), negate=True)
                continue
            if inw is not None and inw != inh:
                self.addcmd(render_want, "%s.%s" % (parser_prefix, field))
            elif inw is None and inh is not None and self._replacing:
                self.addcmd(render_have, "%s.%s" % (parser_prefix, field), negate=True)

    def _compare_board(self, want, have):
        self._compare_fields(want, have, BOARD_ATTRS, "board", want, have)
        for node, _keyword, attrs in BOARD_SUBNODES:
            wnode = want.get(node) or {}
            hnode = have.get(node) or {}
            self._compare_fields(
                wnode, hnode, attrs, "board.%s" % node,
                {"board_id": want["board_id"], node: wnode},
                {"board_id": want["board_id"], node: hnode},
            )

    def _compare_vp_board(self, want, have):
        self._compare_fields(want, have, VP_BOARD_ATTRS, "vp_board", want, have)
        wlinks = dict((link["link_id"], link) for link in want.get("vp_links") or [])
        hlinks = dict((link["link_id"], link) for link in have.get("vp_links") or [])
        for link_id in list(wlinks) + [k for k in hlinks if k not in wlinks]:
            wlink = wlinks.get(link_id, {})
            hlink = hlinks.get(link_id, {})
            if link_id not in wlinks and not self._replacing:
                continue
            render = {"vp_board_id": want["vp_board_id"], "link_id": link_id}
            wdata = dict(render, **wlink)
            hdata = dict(render, **hlink)
            self._compare_fields(wlink, hlink, VP_LINK_ATTRS, "vp_board.vp_links", wdata, hdata)
