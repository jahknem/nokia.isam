# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import shlex

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    flatten_indented_tree,
    get_targeted_config,
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_boards.xdsl_boards import (
    Xdsl_boardsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_boards import (
    BOARD_ATTRS,
    BOARD_INT_FIELDS,
    BOARD_SUBNODES,
    VP_BOARD_ATTRS,
    VP_LINK_ATTRS,
)


def _tokens(text):
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _grammar(attrs):
    return dict((keyword, (field, kind)) for field, keyword, kind in attrs)


_BOARD = _grammar(BOARD_ATTRS)
_SUBNODES = dict((keyword, (field, _grammar(attrs))) for field, keyword, attrs in BOARD_SUBNODES)
_VP_BOARD = _grammar(VP_BOARD_ATTRS)
_VP_LINK = _grammar(VP_LINK_ATTRS)


def _consume(tokens, index, grammar, target, stop=()):
    """Read keyword tokens from ``index`` into ``target`` until a ``stop`` keyword.

    ``no <keyword>`` is the default the detail output prints (and the removal
    form), so it is not reported; neither is a flag in its negated form.
    Unknown keywords are dropped (with the value that follows them, if any) so
    a keyword this module does not model never fails the read.
    Returns the index of the first unconsumed token.
    """
    while index < len(tokens):
        token = tokens[index]
        if token in stop:
            return index
        if token == "no":
            index += 2
            continue
        known = grammar.get(token)
        nxt = tokens[index + 1] if index + 1 < len(tokens) else None
        takes_value = nxt is not None and nxt != "no" and nxt not in grammar and nxt not in stop
        if known and known[1] == "flag":
            target[known[0]] = True
            index += 1
        elif known:
            if takes_value:
                target[known[0]] = nxt
                index += 2
            else:
                index += 1
        else:
            index += 2 if takes_value else 1
    return index


def config_lines(data):
    """Stripped ``configure xdsl ...`` lines; indented output is flattened first."""
    text = str(unwrap_response(data) or "")
    stripped = [raw.strip() for raw in text.splitlines()]
    if "exit" in stripped:
        indented = "\n".join(raw for raw in text.splitlines() if raw.strip() and not raw.strip().startswith("#"))
        stripped = flatten_indented_tree(indented) or []
    return [line for line in stripped if line.startswith("configure xdsl ")]


class Xdsl_boardsFacts(object):
    """The isam xdsl_boards facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_boardsArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the boards named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "xdsl_boards", self._get_full_config, {
            "boards": "info configure xdsl board %s flat",
            "vp_boards": "info configure xdsl vp-board %s flat",
        })

    @staticmethod
    def _get_full_config(connection):
        return "\n".join(
            [
                unwrap_response(connection.get("info configure xdsl board flat")),
                unwrap_response(connection.get("info configure xdsl vp-board flat")),
            ]
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        objs = self._parse_config(data)
        ansible_facts["ansible_network_resources"].pop("xdsl_boards", None)
        params = utils.remove_empties(
            validate_config_safe(self.argument_spec, {"config": objs})
        )
        facts["xdsl_boards"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def _parse_config(self, config):
        boards = {}
        vp_boards = {}

        for line in config_lines(config):
            parts = _tokens(line[len("configure xdsl "):])
            if len(parts) < 2:
                continue
            if parts[0] == "board":
                board = boards.setdefault(parts[1], {"board_id": parts[1]})
                self._parse_board(board, parts, 2)
            elif parts[0] == "vp-board":
                vp_board = vp_boards.setdefault(parts[1], {"vp_board_id": parts[1]})
                self._parse_vp_board(vp_board, parts, 2)

        for board in boards.values():
            for node, fields in BOARD_INT_FIELDS.items():
                values = board.get(node) or {}
                for field in fields:
                    if field in values:
                        try:
                            values[field] = int(values[field])
                        except (TypeError, ValueError):
                            values.pop(field)
            for node, _grammar_unused in _SUBNODES.values():
                if not board.get(node):
                    board.pop(node, None)
        for vp_board in vp_boards.values():
            if "vp_links" in vp_board:
                vp_board["vp_links"] = [
                    link for link in sorted(vp_board["vp_links"].values(), key=lambda x: _sort_key(x["link_id"]))
                    if len(link) > 1
                ]
                if not vp_board["vp_links"]:
                    vp_board.pop("vp_links")

        return {"boards": list(boards.values()), "vp_boards": list(vp_boards.values())}

    @staticmethod
    def _parse_board(board, parts, index):
        stop = tuple(_SUBNODES)
        grammar = _BOARD
        target = board
        while index < len(parts):
            index = _consume(parts, index, grammar, target, stop)
            if index < len(parts):
                node, grammar = _SUBNODES[parts[index]]
                target = board.setdefault(node, {})
                index += 1

    @staticmethod
    def _parse_vp_board(vp_board, parts, index):
        while index < len(parts):
            index = _consume(parts, index, _VP_BOARD, vp_board, ("vp-link",))
            if index + 1 < len(parts):
                link_id = parts[index + 1]
                links = vp_board.setdefault("vp_links", {})
                link = links.setdefault(link_id, {"link_id": link_id})
                index = _consume(parts, index + 2, _VP_LINK, link, ("vp-link",))
            else:
                break


def _sort_key(value):
    return (0, int(value), "") if str(value).isdigit() else (1, 0, str(value))
