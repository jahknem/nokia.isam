# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""Attribute tables: one description of a family's CLI grammar drives parsing, rendering,
device defaults and the argument spec.

The ISAM prints every node as one packed line of ``[no] <keyword> [<value>]`` clauses::

    configure voice sip vsp vsp1 domain-name example.com no ta4 timer-b 32000
    configure generic-pon utilization threshold no txmcutilhi numtcint 60

A family describes those lines once, as an :class:`AttributeTable` of :class:`Node` objects,
each with its :class:`Attr` entries taken from the CLI guide. The table then

* parses device text into the resource config (:meth:`AttributeTable.parse`),
* drops values equal to their device default (:meth:`AttributeTable.without_defaults`;
  the device prints a default as ``no <keyword>``, so a default counts as unset),
* renders the commands for one instance or section and state
  (:meth:`AttributeTable.diff_commands`), and
* generates the argument spec (:meth:`AttributeTable.argument_spec`).

:class:`~...resource_module.TableResourceModule` builds the states on top of it. Use a table
for nodes made of uniform clauses; nodes with irregular grammar keep explicit netcommon
``PARSERS`` (see ``docs/development-style.md``).
"""

import shlex

from collections import namedtuple
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties

KINDS = ("flag", "str", "int")
FORMS = ("packed", "solo", "scalar")


class Attr(namedtuple("Attr", "option cli kind default choices removable node form")):
    """One attribute of a node.

    * ``option``    -- the resource option name (snake_case).
    * ``cli``       -- the CLI keyword.
    * ``kind``      -- ``flag`` (``[ [ no ] kw ]``, a bool), ``str`` or ``int``
      (``[ no kw | kw <value> ]``).
    * ``default``   -- the device default (a value equal to it counts as unset); None when
      the guide names no concrete default. Flags default to False.
    * ``choices``   -- the guide's enumerated values, or None.
    * ``removable`` -- False for values without a ``no`` form (mandatory at creation or set
      only); they are never reset, only set when given.
    * ``node``      -- a sub-node the attribute lives on instead of its node's CLI path
      (flat nodes only), e.g. ``statistics stats-config``. Its clauses form their own line.
    * ``form``      -- ``packed`` (joins the node's line), ``solo`` (its own command,
      ``<node> <kw> <value>``) or ``scalar`` (the node's direct argument,
      ``<node> <value>``; one per node).
    """

    __slots__ = ()

    def __new__(cls, option, cli, kind, default=None, choices=None, removable=True, node=None, form="packed"):
        if kind not in KINDS or form not in FORMS:
            raise ValueError("invalid attribute %s: kind %r, form %r" % (option, kind, form))
        if kind == "flag" and default is None:
            default = False
        return super(Attr, cls).__new__(cls, option, cli, kind, default, choices, removable, node, form)


class Node(object):
    """A CLI node: its path in the resource config, its CLI path and its attributes.

    ``key`` is the option holding the node's settings: a name, a nested path tuple
    (``("utilization", "threshold")``) or ``()`` for the resource's top level. A node with an
    ``identity`` (the option naming an instance) is a list of instances; ``mandatory`` are
    the options required to create one.
    """

    def __init__(self, key, cli, attrs, identity=None, mandatory=()):
        self.path = tuple(key) if isinstance(key, (tuple, list)) else ((key,) if key else ())
        self.cli = cli
        self.attrs = tuple(attrs)
        self.identity = identity
        self.mandatory = tuple(mandatory)
        if identity and len(self.path) != 1:
            raise ValueError("a list node needs a single-key path: %r" % (self.path,))
        if identity and any(attr.node for attr in self.attrs):
            raise ValueError("sub-node attributes are only supported on flat nodes: %s" % cli)

    @property
    def is_list(self):
        return self.identity is not None

    @property
    def key(self):
        return self.path[-1] if self.path else None


def quote_value(value):
    """A value as the device prints it: double quotes when it is empty, contains whitespace
    or a quote, or starts with ``#`` (single quotes are an invalid token, lab ISAM)."""
    text = str(value)
    if not text or text.startswith("#") or '"' in text or any(char.isspace() for char in text):
        return '"%s"' % text.replace('"', '\\"')
    return text


def strip_comment(line):
    """line without a trailing ``#`` comment: a ``#`` starting a word outside double
    quotes (a value starting with ``#`` is printed quoted, see :func:`quote_value`)."""
    index = line.find(" #")
    while index != -1:
        if line[:index].count('"') % 2 == 0:
            return line[:index]
        index = line.find(" #", index + 1)
    return line


def tokenize(text):
    """Split a CLI line; double-quoted values stay one token, a comment is dropped."""
    text = strip_comment(text)
    try:
        return shlex.split(text)
    except ValueError:  # unbalanced quotes: fall back to whitespace
        return text.split()


def convert(kind, value):
    """Typed value of a parsed token (a non-numeric int value stays a string)."""
    if kind == "int":
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    return value


def parse_clauses(tokens, attrs):
    """{option: value} of packed ``[no] <kw> [<value>]`` clauses.

    ``no <kw>`` gives None for a value (the device default) and False for a flag; ``<kw>``
    gives True for a flag. A value token that is itself a keyword (or ``no``) is not taken
    as the value, unless it is one of the attribute's choices: in ``system session-timer
    enable status enable`` the value ``enable`` of status is also the flag ``enable``.
    Unknown tokens are skipped, never an error.
    """
    by_cli = dict((attr.cli, attr) for attr in attrs)
    result = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        negate = token == "no" and index + 1 < len(tokens) and tokens[index + 1] in by_cli
        if negate:
            index += 1
            token = tokens[index]
        attr = by_cli.get(token)
        index += 1
        if attr is None:
            continue
        if attr.kind == "flag":
            result[attr.option] = not negate
        elif negate:
            result[attr.option] = None
        elif index < len(tokens) and _is_value(attr, tokens[index], by_cli):
            result[attr.option] = convert(attr.kind, tokens[index])
            index += 1
    return result


def _is_value(attr, token, keywords):
    if token in keywords:
        return token in (attr.choices or ())
    return token != "no"


def change(attr, want, have, state):
    """The clause tokens for one attribute and state, or None when nothing is to send.

    want is the requested value (raw: an explicit default means "reset to default"); have
    holds non-defaults only, so a default equal to an absent have value is already in
    effect. merged sends what differs; replaced/overridden also reset an omitted removable
    attribute; rendered renders every given value (an explicit False as its ``no`` form).
    """
    if state == "rendered":
        return None if want is None else _tokens(attr, want)
    if want is None:
        if state in ("replaced", "overridden") and have is not None and attr.removable:
            return ["no", attr.cli]
        return None
    if want == have or (want == attr.default and have is None):
        return None
    if want == attr.default and attr.removable:
        return ["no", attr.cli]
    return _tokens(attr, want)


def _tokens(attr, value):
    if attr.kind == "flag":
        return [attr.cli] if value else ["no", attr.cli]
    if attr.form == "scalar":
        return [quote_value(value)]
    return [attr.cli, quote_value(value)]


def get_path(config, path):
    """The dict at path in config ({} when absent)."""
    for key in path:
        config = config.get(key) if isinstance(config, dict) else None
    return config if isinstance(config, dict) else {}


def _entries(config, node):
    """The instance/section dicts of node in config (a copy's dicts are modified in place)."""
    if node.is_list:
        return [entry for entry in (config.get(node.key) or []) if isinstance(entry, dict)]
    section = get_path(config, node.path) if node.path else config
    return [section] if section else []


class AttributeTable(object):
    """The grammar of one family: ``prefix`` (e.g. ``configure voice sip``) and its nodes."""

    def __init__(self, prefix, nodes):
        self.prefix = prefix
        self.nodes = tuple(nodes)
        # one parse group per CLI path: (path words, node, attrs on that path), longest
        # path first so 'statistics stats-config' is tried before 'statistics' and the
        # top-level node (empty path) last
        groups = {}
        for node in self.nodes:
            for attr in node.attrs:
                path = attr.node or node.cli
                groups.setdefault((path, id(node)), (path.split(), node, []))[2].append(attr)
        self._groups = sorted(groups.values(), key=lambda group: -len(group[0]))
        paths = [tuple(words) for words, _node, _attrs in self._groups]
        # An explicit leaf path identifies its node even when a new firmware
        # keyword precedes the attributes we know. Prefix-only/root and parent
        # groups still need a known first clause to avoid consuming sibling nodes.
        self._leaf_paths = {path for path in paths if path and not any(
            len(other) > len(path) and other[:len(path)] == path for other in paths)}

    def node(self, key):
        """The node whose path ends in key (a name or a path tuple)."""
        path = tuple(key) if isinstance(key, (tuple, list)) else ((key,) if key else ())
        return next(node for node in self.nodes if node.path == path)

    # -- reading ---------------------------------------------------------------------

    def parse(self, text):
        """The resource config of the ``<prefix> ...`` lines in text (raw: defaults kept,
        ``no <kw>`` as None/False). Later lines win; lists keep the device's order."""
        result, lists = {}, {}
        for raw in str(text or "").splitlines():
            line = raw.strip()
            if not line.startswith(self.prefix + " "):
                continue
            tokens = tokenize(line[len(self.prefix) + 1:])
            for words, node, attrs in self._groups:
                if tokens[:len(words)] != words:
                    continue
                rest = tokens[len(words):]
                name = None
                if node.identity:
                    if not rest:
                        break
                    name, rest = rest[0], rest[1:]
                if tuple(words) not in self._leaf_paths and not self._belongs(rest, attrs):
                    continue
                values = self._parse_values(rest, attrs)
                if node.is_list:
                    entries = lists.setdefault(node.key, {})
                    entries.setdefault(name, {node.identity: name}).update(values)
                else:
                    section = result
                    for key in node.path:
                        section = section.setdefault(key, {})
                    section.update(values)
                break
        for key, entries in lists.items():
            result[key] = list(entries.values())
        return result

    @staticmethod
    def _belongs(rest, attrs):
        """Guard ambiguous root/parent groups with a known first clause or bare line.

        Explicit leaf paths bypass this guard. A later known keyword alone cannot
        prove an ambiguous line belongs to its parent ('configure pon interface ...'
        is not a 'configure pon' settings line).
        """
        if not rest:
            return True
        first = rest[1] if rest[0] == "no" and len(rest) > 1 else rest[0]
        return any(first == attr.cli for attr in attrs if attr.form != "scalar") or \
            any(attr.form == "scalar" for attr in attrs)

    @staticmethod
    def _parse_values(rest, attrs):
        scalar = [attr for attr in attrs if attr.form == "scalar"]
        if scalar:
            return {scalar[0].option: convert(scalar[0].kind, rest[0])} if rest else {}
        return parse_clauses(rest, attrs)

    def without_defaults(self, config):
        """A copy of config without values equal to their device default and without
        empty sections (defaults count as unset; flags are kept)."""
        config = deepcopy(config or {})
        for node in self.nodes:
            for entry in _entries(config, node):
                for attr in node.attrs:
                    if attr.kind != "flag" and attr.default is not None and entry.get(attr.option) == attr.default:
                        del entry[attr.option]
        return remove_empties(config)

    # -- writing ---------------------------------------------------------------------

    def diff_commands(self, node, name, want, have, state):
        """The commands bringing one instance (name) or section (name None) from have to
        want for state (see :func:`change`). Packed clauses share one line per CLI path
        (in the order of the table); solo and scalar attributes follow, one command each."""
        lines, solo = {}, []
        for attr in node.attrs:
            tokens = change(attr, want.get(attr.option), have.get(attr.option), state)
            if not tokens:
                continue
            if attr.form == "packed":
                lines.setdefault(attr.node or node.cli, []).extend(tokens)
            else:
                solo.append(self.command(node.cli, name, tokens))
        return [self.command(path, name, tokens) for path, tokens in lines.items()] + solo

    def command(self, path, name=None, tokens=()):
        """``<prefix> <path> [<name>] <tokens...>``."""
        parts = [self.prefix, path] + ([quote_value(name)] if name is not None else []) + list(tokens)
        return " ".join(part for part in parts if part)

    def removal_command(self, node, name):
        return self.command("no " + node.cli, name)

    def creation_command(self, node, name):
        return self.command(node.cli, name)

    def retained_on_delete(self, want, have):
        """(node, instance name or None, attr) for every attribute a deleted request names
        that has no removal form (``removable=False``) and is set in have: it cannot be
        reset and stays until its instance is removed. Instances removed as a whole (named
        by their identity alone or as a full entry) retain nothing."""
        retained = []
        for node in self.nodes:
            fixed = [attr for attr in node.attrs if not attr.removable]
            if not fixed:
                continue
            if node.is_list:
                haved = dict((str(entry.get(node.identity)), entry) for entry in _entries(have or {}, node))
                pairs = []
                for entry in _entries(want or {}, node):
                    name = str(entry.get(node.identity))
                    have_entry = haved.get(name)
                    if have_entry is None:
                        continue
                    named = set(k for k, v in entry.items() if k != node.identity and v is not None)
                    present = set(k for k, v in have_entry.items() if k != node.identity and v is not None)
                    if named and not present <= named:  # not removed as a whole
                        pairs.append((name, entry, have_entry))
            else:
                pairs = [(None, get_path(want or {}, node.path), get_path(have or {}, node.path))]
            for name, want_entry, have_entry in pairs:
                retained.extend((node, name, attr) for attr in fixed
                                if want_entry.get(attr.option) is not None and have_entry.get(attr.option) is not None)
        return retained

    # -- argument spec ---------------------------------------------------------------

    def argument_spec(self):
        """The ``config`` suboptions of the table (nested by node path)."""
        options = {}
        for node in self.nodes:
            container = options
            for key in node.path[:-1]:
                container = container.setdefault(key, {"type": "dict", "options": {}})["options"]
            if not node.path:
                target = container
            elif node.is_list:
                target = container.setdefault(node.key, {"type": "list", "elements": "dict", "options": {}})["options"]
                target[node.identity] = {"type": "str", "required": True}
            else:
                target = container.setdefault(node.key, {"type": "dict", "options": {}})["options"]
            for attr in node.attrs:
                spec = {"type": {"flag": "bool", "int": "int", "str": "str"}[attr.kind]}
                if attr.choices:
                    spec["choices"] = list(attr.choices)
                target[attr.option] = spec
        return options


class RetainedOnDeleteWarnings(object):
    """Mixin for :class:`~...resource_module.TableResourceModule` families: deleted warns
    for each named attribute without removal form instead of silently keeping it (as
    ``IsamResourceModule.addcmd`` does for ``no_remval`` parsers)."""

    def generate_commands(self):
        super(RetainedOnDeleteWarnings, self).generate_commands()
        if self.state != "deleted":
            return
        for node, name, attr in self.TABLE.retained_on_delete(self.want, self.TABLE.without_defaults(self.have)):
            where = node.cli + (" " + name if name is not None else "")
            self._module.warn("%s %s has no removal form in ISAM CLI; it is retained%s"
                              % (where, attr.cli, " until the instance is removed" if name is not None else ""))


class TableTemplate(NetworkTemplate):
    """The NetworkTemplate of a table family: ``parse`` reads the lines with ``TABLE``
    (raw: defaults kept). Subclasses only set ``TABLE``."""

    TABLE = None
    PARSERS = []

    def __init__(self, lines=None, module=None):
        super(TableTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        return self.TABLE.parse("\n".join(self._lines or []))
