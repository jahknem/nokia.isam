# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Grammar table for the isam_software_mngt resource (global software management).

The device prints ('info configure software-mngt detail flat', lab ISAM)::

    configure software-mngt sw-replacement-mode upgrade-via-standby
    configure software-mngt oswp 1 primary-file-server-id 198.51.100.11 second-file-server-id 0.0.0.0 no activate no auto-verify no on-schedule-time
    configure software-mngt database no activate backup activate:198.51.100.10:path/ backupv6 activate:::/path/ no auto-backup-intvl

SOFTWARE_MNGT_NODES is the single description of that grammar (CLI guide): the facts
parse with it, the config class renders commands and takes the device defaults from it,
and the argspec and documentation are generated from it. An attribute is
``(option, cli, kind, default, choices, form)``:

* kind ``flag``               -- on/off keyword; bool, default False.
* kind ``str``/``int``        -- value with a removal form (``[ no kw | kw <value> ]``).
* kind ``str-nono``/``int-nono`` -- value without a removal form.
* ``default``                 -- device default; a value equal to it counts as unset.
* ``choices``                 -- the guide's enumerated values, or None.
* ``form``                    -- how the attribute is sent:
  ``packed`` joins the node's packed line; ``solo`` is its own command
  (``... <cli> <value>`` or ``... [no] <cli>``); ``scalar`` is the node's direct
  argument (``configure software-mngt sw-replacement-mode <value>``).

A node is ``(key, cli, identity, is_list, attrs)``; ``identity`` is the option holding
the instance name (None for a flat section). ``on-schedule-time`` (a datetime) and
``backup``/``backupv6`` (``activate:host:path/`` strings) are kept as raw string values.
"""

import shlex

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import canonical_key, parse_cli_fields

_PREFIX = "configure software-mngt "

_DATABASE = (
    ("version", "version", "str-nono", None, None, "solo"),
    ("url", "url", "str-nono", None, None, "solo"),
    ("activate", "activate", "str", "manually", ["after-download", "manually"], "packed"),
    ("backup", "backup", "str", "manually", None, "packed"),
    ("backupv6", "backupv6", "str", "manually", None, "packed"),
    ("auto_backup_interval", "auto-backup-intvl", "int", 24, None, "packed"),
)

_OSWP = (
    ("primary_file_server_id", "primary-file-server-id", "str-nono", None, None, "packed"),
    ("second_file_server_id", "second-file-server-id", "str-nono", None, None, "packed"),
    ("download_set", "download-set", "str-nono", None, ["min-set", "actual-set", "complete-set"], "packed"),
    ("autofetch", "autofetch", "str-nono", None, ["disabled", "enabled"], "packed"),
    ("activate", "activate", "str", "manually", ["manually", "after-download", "on-schedule"], "packed"),
    ("auto_verify", "auto-verify", "str", "disabled", ["disabled", "enabled"], "packed"),
    ("on_schedule_time", "on-schedule-time", "str", None, None, "packed"),
    ("admin_state", "admin-state", "flag", False, None, "solo"),
)

_SW_REPLACEMENT_MODE = (
    ("mode", "sw-replacement-mode", "str-nono", None,
     ["upgrade-via-active", "upgrade-via-standby", "lt-by-lt"], "scalar"),
)


def _node(key, cli, identity, is_list, attrs):
    return {"key": key, "cli": cli, "identity": identity, "is_list": is_list, "attrs": attrs}


SOFTWARE_MNGT_NODES = (
    _node("database", "database", None, False, _DATABASE),
    _node("oswp", "oswp", "id", True, _OSWP),
    _node("sw_replacement_mode", "sw-replacement-mode", None, False, _SW_REPLACEMENT_MODE),
)

NODES_BY_KEY = dict((n["key"], n) for n in SOFTWARE_MNGT_NODES)
_NODES_BY_CLI = sorted(SOFTWARE_MNGT_NODES, key=lambda n: -len(n["cli"]))

_INT_KINDS = ("int", "int-nono")
_VALUE_KINDS = ("str", "int", "str-nono", "int-nono")
_REMOVABLE_KINDS = ("str", "int", "flag")


def is_int(kind):
    return kind in _INT_KINDS


def is_value(kind):
    return kind in _VALUE_KINDS


def is_removable(kind):
    return kind in _REMOVABLE_KINDS


def value_fields(node):
    return dict((a[1], "int" if is_int(a[2]) else "str") for a in node["attrs"] if is_value(a[2]))


def flag_fields(node):
    return tuple(a[1] for a in node["attrs"] if a[2] == "flag")


def quote_value(value):
    text = str(value)
    if not text or any(c.isspace() for c in text) or '"' in text:
        return '"%s"' % text.replace('"', '\\"')
    return text


def without_defaults(config):
    """A copy of config without values equal to their device default (defaults count as unset)."""
    config = deepcopy(config or {})
    for node in SOFTWARE_MNGT_NODES:
        entries = config.get(node["key"])
        entries = (entries or []) if node["is_list"] else ([entries] if isinstance(entries, dict) else [])
        for entry in entries:
            for option, _cli, kind, default, _choices, _form in node["attrs"]:
                if default is not None and kind != "flag" and entry.get(option) == default:
                    del entry[option]
    return remove_empties(config)


def parse_lines(data):
    """Parse 'configure software-mngt ...' lines into the resource config dict."""
    result = {}
    for raw in str(data or "").splitlines():
        line = raw.strip()
        if not line.startswith(_PREFIX):
            continue
        tokens = shlex.split(line[len(_PREFIX):])
        if not tokens:
            continue
        for node in _NODES_BY_CLI:
            cli_words = node["cli"].split()
            if tokens[:len(cli_words)] != cli_words:
                continue
            rest = tokens[len(cli_words):]
            # scalar node: the value is the node's direct argument
            if any(a[5] == "scalar" for a in node["attrs"]):
                option = node["attrs"][0][0]
                if rest:
                    result.setdefault(node["key"], {})[option] = rest[0]
                break
            name = None
            if node["identity"]:
                if not rest:
                    break
                name, rest = rest[0], rest[1:]
            fields = parse_cli_fields(rest, bool_fields=flag_fields(node),
                                      value_fields=value_fields(node), none_for_negated_values=True)
            # parse_cli_fields keys by the CLI spelling; map to the option names
            # (e.g. 'auto-backup-intvl' -> auto_backup_interval, not auto_backup_intvl)
            option_of = dict((canonical_key(a[1]), a[0]) for a in node["attrs"])
            fields = dict((option_of.get(k, k), v) for k, v in fields.items())
            if node["is_list"]:
                bucket = result.setdefault(node["key"], {})
                bucket.setdefault(name, {node["identity"]: name}).update(dict(fields, **{node["identity"]: name}))
            else:
                result.setdefault(node["key"], {}).update(fields)
            break
    for node in SOFTWARE_MNGT_NODES:
        if node["is_list"] and node["key"] in result:
            result[node["key"]] = list(result[node["key"]].values())
    return result


def _attr_tokens(kind, cli, value):
    if kind == "flag":
        return [cli] if value else ["no", cli]
    if is_int(kind):
        return [cli, str(value)]
    return [cli, quote_value(value)]


def _target_tokens(kind, cli, value, default):
    """Setting to the device default is a reset (no kw) where a removal form exists."""
    if value == default and is_removable(kind):
        return ["no", cli]
    return _attr_tokens(kind, cli, value)


def diff_commands(node, name, want, have, state):
    """Commands for one instance/section: packed attributes share one line, solo and
    scalar attributes each get their own. merged sends only changes; replaced/overridden
    also reset omitted removable attributes; rendered sends every given attribute.
    want is raw (an explicit default means 'reset to default'); have holds non-defaults
    only, so a default equal to an absent have value is already in effect (no command)."""
    packed, solo = [], []
    prefix = _PREFIX.rstrip() + " " + node["cli"] + ((" " + quote_value(name)) if name is not None else "")
    for option, cli, kind, default, _choices, form in node["attrs"]:
        w, h = want.get(option), have.get(option)
        tokens = None
        if state == "rendered":
            if w is not None:
                tokens = _attr_tokens(kind, cli, w)
        elif state == "merged":
            if w is not None and w != h and not (w == default and h is None):
                tokens = _target_tokens(kind, cli, w, default)
        elif state in ("replaced", "overridden"):
            if w is None:
                if h is not None and is_removable(kind):
                    tokens = ["no", cli]
            elif w != h and not (w == default and h is None):
                tokens = _target_tokens(kind, cli, w, default)
        if not tokens:
            continue
        if form == "packed":
            packed.extend(tokens)
        elif form == "scalar":
            solo.append(_PREFIX.rstrip() + " " + cli + " " + quote_value(w))
        else:  # solo
            solo.append(prefix + " " + " ".join(tokens))
    commands = []
    if packed:
        commands.append(prefix + " " + " ".join(packed))
    commands.extend(solo)
    return commands


def removal_command(node, name):
    return "%sno %s %s" % (_PREFIX, node["cli"], quote_value(name))


def creation_command(node, name):
    return "%s%s %s" % (_PREFIX, node["cli"], quote_value(name))


class Software_mngtTemplate(NetworkTemplate):
    """Holds the grammar table; parsing and rendering are table-driven (see above)."""

    def __init__(self, lines=None, module=None):
        super(Software_mngtTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        return parse_lines("\n".join(self._lines or []))

    PARSERS = []
