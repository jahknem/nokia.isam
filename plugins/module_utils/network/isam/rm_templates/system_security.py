# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure system security``.

The lab device's system-security tree is not in rm_models, so the structure is derived
from real ``info configure detail flat`` output. Every CLI node is described once in
``NODES``; attributes are parsed generically using the argspec field types, profile
permission flags become a permissions dict.

Sections are addressed by their (dotted) path in the config, e.g. ``operators``,
``ssh.sftp_users`` or ``pae.ports``:

* instance lists (``LISTS``) are keyed by their identity fields. ``create`` lists are
  removed with ``no <node> <id>``; ``fixed`` lists (slots, MAC filters, 802.1X ports)
  always exist on the device and are reset attribute by attribute (``no <attr>``).
* settings blocks (``SETTINGS``) are single dicts, reset with ``no <attr>``.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import (
    Isam_system_securityArgs,
)

_TOKEN = re.compile(r'"[^"]*"|\S+')
PREFIX = "configure system security"

# (CLI node after PREFIX, section path, identity fields or None for a settings block,
#  sub-dict of the instance the node fills or None). Longest CLI paths first.
NODES = [
    ("snmp community", "snmp_communities", ("name", "host_address"), None),
    ("snmp view", "snmp_views", ("name", "subtree"), None),
    ("snmp notify-view", "snmp_notify_views", ("name", "subtree"), None),
    ("snmp manager", "snmp_managers", ("name",), None),
    ("snmp notify-profile", "snmp_notify_profiles", ("name",), None),
    ("radius auth-server", "radius_auth_servers", ("name",), None),
    ("radius policy", "radius_policies", ("name",), None),
    ("radius dyn-auth-client", "radius_dyn_auth_clients", ("name",), None),
    ("radius auth-super-user", "radius_auth_super_user", None, None),
    ("operator", "operators", ("name",), None),
    ("profile", "profiles", ("name",), None),
    ("default-profile", "default_profile", None, None),
    ("password", "password", None, None),
    ("ssh server-profile", "ssh.server_profile", None, None),
    ("ssh access", "ssh.access", None, None),
    ("ssh sftp-user", "ssh.sftp_users", ("name",), None),
    ("tacacs", "tacacs", None, None),
    ("li", "li", None, None),
    ("slot", "slots", ("slot",), None),
    ("domain", "domains", ("name",), None),
    ("filetransfer server", "filetransfer.servers", ("server",), None),
    ("filetransfer", "filetransfer", None, None),
    ("peripheral-mgnt mac-filter", "peripheral_mgnt.mac_filters", ("index",), None),
    ("pae port", "pae.ports", ("port",), None),
    ("pae authenticator", "pae.ports", ("port",), "authenticator"),
    ("pae ext-authenticator", "pae.ports", ("port",), "ext_authenticator"),
    ("pae", "pae", None, None),
    ("", "general", None, None),
]

# instance lists: section -> (identity fields, "create" | "fixed")
LISTS = {}
# settings blocks, in render order
SETTINGS = []
for _cli, _section, _ident, _sub in NODES:
    if _ident is not None:
        LISTS.setdefault(_section, (_ident, "fixed" if _section in (
            "slots", "peripheral_mgnt.mac_filters", "pae.ports") else "create"))
    elif _section not in SETTINGS:
        SETTINGS.append(_section)

# section -> secret fields (masked values are replaced by the device value before comparing)
SECRET_FIELDS = {
    "operators": ("password",),
    "radius_auth_servers": ("secret",),
    "radius_dyn_auth_clients": ("secret",),
    "ssh.sftp_users": ("password",),
    "filetransfer.servers": ("password",),
}

_PROFILE_SCALARS = ("description", "slot_numbering", "prompt", "password_timeout", "terminal_timeout")


def _snake(key):
    return key.replace("-", "_")


def _kebab(key):
    return key.replace("_", "-")


def _options(section, sub=None):
    opts = Isam_system_securityArgs.argument_spec["config"]
    for part in section.split("."):
        opts = opts["options"][part]
    if sub:
        opts = opts["options"][sub]
    return opts.get("options") or {}


def scalar_fields(section, sub=None):
    """Scalar (non-list, non-dict) option names -> type of one CLI node."""
    return dict((k, v.get("type")) for k, v in _options(section, sub).items()
                if v.get("type") not in ("list", "dict"))


def sub_dicts(section):
    """Sub-dicts of a section that are filled by their own CLI node (pae ports)."""
    return [sub for _cli, sec, _ident, sub in NODES if sec == section and sub]


def node_cli(section, sub=None):
    for cli, sec, _ident, nsub in NODES:
        if sec == section and nsub == sub:
            return cli
    raise KeyError(section)


def _field_map(section, sub=None):
    return dict((_kebab(k), (k, t)) for k, t in scalar_fields(section, sub).items())


def _unquote(value):
    return value[1:-1] if len(value) >= 2 and value.startswith('"') and value.endswith('"') else value


def _quote(value):
    value = str(value)
    if value == "" or re.search(r'[\s\\"]', value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _cast(value, ftype):
    if ftype == "int" and str(value).lstrip("-").isdigit():
        return int(value)
    return value


def _match_node(body):
    for cli, section, ident, sub in NODES:
        if not cli:
            continue
        if body == cli or body.startswith(cli + " "):
            return cli, section, ident, sub
    # the bare 'configure system security <attrs>' line
    tokens = body.split()
    fmap = _field_map("general")
    if tokens and (tokens[0] in fmap or (tokens[0] == "no" and len(tokens) > 1 and tokens[1] in fmap)):
        return NODES[-1]
    return None


class Isam_system_securityTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_system_securityTemplate, self).__init__(lines=lines, tmplt=self, module=module)
        self.unparsed = []

    def parse(self):
        store = {}
        self.unparsed = []
        for raw in self._lines:
            line = raw.strip()
            if line != PREFIX and not line.startswith(PREFIX + " "):
                continue
            body = line[len(PREFIX):].strip()
            node = _match_node(body)
            if node is None:
                self.unparsed.append(line)
                continue
            cli, section, ident, sub = node
            tokens = _TOKEN.findall(body[len(cli):].strip())
            if ident is None:
                self._parse_attrs(section, None, tokens, store.setdefault(section, {}))
                continue
            if not tokens:
                self.unparsed.append(line)
                continue
            first_type = scalar_fields(section).get(ident[0])
            entry = {ident[0]: _cast(_unquote(tokens[0]), first_type)}
            target = entry.setdefault(sub, {}) if sub else entry
            self._parse_attrs(section, sub, tokens[1:], target)
            key = tuple(entry.get(f) for f in ident)
            entries = store.setdefault(section, {})
            existing = entries.get(key)
            if existing is None:
                entries[key] = entry
            elif sub:
                existing.setdefault(sub, {}).update(entry[sub])
            else:
                existing.update(entry)
        return self._nest(store)

    @staticmethod
    def _nest(store):
        out = {}
        for section, value in store.items():
            parts = section.split(".")
            parent = out
            for part in parts[:-1]:
                parent = parent.setdefault(part, {})
            if section in LISTS:
                parent[parts[-1]] = list(value.values())
            else:
                parent.setdefault(parts[-1], {}).update(value)
        return out

    def _parse_attrs(self, section, sub, tokens, entry):
        if section == "profiles":
            self._parse_profile(tokens, entry)
            return
        if section == "default_profile":
            self._parse_profile(tokens, entry, negate_is_default=True)
            return
        fmap = _field_map(section, sub)
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = token == "no" and i + 1 < len(tokens)
            key = tokens[i + 1] if negate else token
            if key not in fmap:
                i += 2 if negate else 1
                continue
            snake, ftype = fmap[key]
            if ftype == "bool":
                entry[snake] = not negate
                i += 2 if negate else 1
            elif negate:
                entry.pop(snake, None)
                i += 2
            elif i + 1 < len(tokens) and tokens[i + 1] != "no" and tokens[i + 1] not in fmap:
                entry[snake] = _cast(_unquote(tokens[i + 1]), ftype)
                i += 2
            else:
                entry[snake] = True
                i += 1

    @staticmethod
    def _parse_profile(tokens, entry, negate_is_default=False):
        """Profile attributes: scalars plus '<area> read|write|none' / 'no <area>' flags.

        For profiles 'no <area>' means no access ("none"); the default-profile prints
        'no <area>' for an unset (default) flag and '<area> none' for an explicit one.
        """
        scalar = dict((_kebab(k), k) for k in _PROFILE_SCALARS)
        permissions = entry.setdefault("permissions", {})
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = token == "no" and i + 1 < len(tokens)
            key = tokens[i + 1] if negate else token
            if key in scalar:
                snake = scalar[key]
                if negate:
                    entry.pop(snake, None)
                    i += 2
                elif i + 1 < len(tokens) and tokens[i + 1] != "no" and tokens[i + 1] not in scalar:
                    entry[snake] = _unquote(tokens[i + 1])
                    i += 2
                else:
                    entry[snake] = True
                    i += 1
                continue
            if negate:
                if negate_is_default:
                    permissions.pop(key, None)
                else:
                    permissions[key] = "none"
                i += 2
            elif i + 1 < len(tokens) and tokens[i + 1] in ("read", "write", "none"):
                permissions[key] = tokens[i + 1]
                i += 2
            else:
                permissions[key] = "write"
                i += 1
        if not permissions:
            entry.pop("permissions", None)

    PARSERS = [{"name": "system_security", "getval": re.compile(r"^$"), "setval": "", "result": {}}]

    # ---------------------------------------------------------------- rendering

    @staticmethod
    def _base(section, entry=None, sub=None):
        cli = node_cli(section, sub)
        parts = [PREFIX] + ([cli] if cli else [])
        if section in LISTS:
            ident = LISTS[section][0]
            parts.append(_quote(entry[ident[0]]))
            for field in ident[1:]:
                if entry.get(field) is not None:
                    parts.append("{0} {1}".format(_kebab(field), _quote(entry[field])))
        return " ".join(parts)

    @staticmethod
    def _attr_parts(section, sub, entry, skip=()):
        types = scalar_fields(section, sub)
        parts = []
        for key, value in entry.items():
            if key in skip or value is None or key not in types and key != "permissions":
                continue
            if key == "permissions":
                for area, mode in (value or {}).items():
                    if mode is None:
                        continue
                    if section == "profiles" and mode == "none":
                        parts.append("no " + area)
                    else:
                        parts.append("{0} {1}".format(area, mode))
                continue
            cli = _kebab(key)
            if types[key] == "bool":
                parts.append(cli if value else "no " + cli)
            elif value is True:
                parts.append(cli)
            else:
                parts.append("{0} {1}".format(cli, _quote(value)))
        return parts

    @classmethod
    def render_entry(cls, section, entry, always=None):
        """Commands setting the given attributes of one instance or settings block.

        Create lists always render the instance (creating it); fixed lists and
        settings blocks render nothing when no attribute is given.
        """
        if always is None:
            always = LISTS.get(section, (None, "fixed"))[1] == "create"
        ident = LISTS[section][0] if section in LISTS else ()
        commands = []
        parts = cls._attr_parts(section, None, entry, skip=ident)
        if parts or always:
            base = cls._base(section, entry)
            commands.append(base + ((" " + " ".join(parts)) if parts else ""))
        for sub in sub_dicts(section):
            sub_parts = cls._attr_parts(section, sub, entry.get(sub) or {})
            if sub_parts:
                commands.append(cls._base(section, entry, sub) + " " + " ".join(sub_parts))
        return commands

    @classmethod
    def render_reset(cls, section, entry):
        """Reset every attribute given in entry with 'no <attr>' (fixed lists, settings)."""
        ident = LISTS[section][0] if section in LISTS else ()
        commands = []
        parts = cls._reset_parts(section, None, entry, ident)
        if parts:
            commands.append(cls._base(section, entry) + " " + " ".join(parts))
        for sub in sub_dicts(section):
            sub_parts = cls._reset_parts(section, sub, entry.get(sub) or {}, ())
            if sub_parts:
                commands.append(cls._base(section, entry, sub) + " " + " ".join(sub_parts))
        return commands

    @staticmethod
    def _reset_parts(section, sub, entry, skip):
        types = scalar_fields(section, sub)
        parts = []
        for key, value in entry.items():
            if key in skip or value is None:
                continue
            if key == "permissions" and isinstance(value, dict):
                parts.extend("no " + area for area in value)
            elif key in types:
                parts.append("no " + _kebab(key))
        return parts

    @classmethod
    def render_remove(cls, section, entry):
        """Remove one instance of a create list: 'configure system security [<parent>] no <node> <id>'."""
        if not isinstance(entry, dict):
            entry = {LISTS[section][0][0]: entry}
        words = node_cli(section).split()
        base = cls._base(section, entry)
        tail = base[len(" ".join([PREFIX] + words)):]
        return " ".join([PREFIX] + words[:-1] + ["no", words[-1]]) + tail
