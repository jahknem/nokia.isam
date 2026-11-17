# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure system security`` (operators, profiles, SNMP, RADIUS).

The lab device's system-security tree is not in rm_models, so the structure is derived
from real ``info configure detail flat`` output. Attributes are parsed generically using
the argspec field types; profile permission flags become a permissions dict.
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
_PREFIX = "configure system security "

# section -> (CLI prefix after _PREFIX, identity field or None for a settings dict)
_NODES = [
    ("snmp_communities", "snmp community ", "name"),
    ("snmp_views", "snmp view ", "name"),
    ("snmp_managers", "snmp manager ", "name"),
    ("snmp_notify_profiles", "snmp notify-profile ", "name"),
    ("radius_auth_servers", "radius auth-server ", "name"),
    ("radius_policies", "radius policy ", "name"),
    ("radius_dyn_auth_clients", "radius dyn-auth-client ", "name"),
    ("radius_auth_super_user", "radius auth-super-user", None),
    ("operators", "operator ", "name"),
    ("profiles", "profile ", "name"),
]


def _snake(key):
    return key.replace("-", "_")


def _kebab(key):
    return key.replace("_", "-")


def _field_map(section):
    opts = Isam_system_securityArgs.argument_spec["config"]["options"][section]
    opts = opts.get("options") or {}
    return {_kebab(k): (k, v.get("type")) for k, v in opts.items()}


def _unquote(value):
    return value[1:-1] if len(value) >= 2 and value.startswith('"') and value.endswith('"') else value


class Isam_system_securityTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_system_securityTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        for raw in self._lines:
            line = raw.strip()
            if not line.startswith(_PREFIX):
                continue
            body = line[len(_PREFIX):]
            for section, prefix, ident in _NODES:
                if not body.startswith(prefix):
                    continue
                rest = body[len(prefix):].strip()
                tokens = _TOKEN.findall(rest)
                if ident is None:
                    entry = result.setdefault(section, {})
                    self._parse_attrs(section, tokens, entry)
                else:
                    if not tokens:
                        break
                    name = _unquote(tokens[0])
                    key = (section, name)
                    entry = result.setdefault(key, {"name": name})
                    self._parse_attrs(section, tokens[1:], entry)
                break
        # flatten the (section, name) keys into per-section lists
        out = {}
        for key, value in result.items():
            if isinstance(key, tuple):
                out.setdefault(key[0], []).append(value)
            else:
                out[key] = value
        return out

    def _parse_attrs(self, section, tokens, entry):
        if section == "profiles":
            self._parse_profile(tokens, entry)
            return
        fmap = _field_map(section)
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = token == "no"
            key = tokens[i + 1] if negate else token
            if key not in fmap:
                i += 2 if negate else 1
                continue
            snake, ftype = fmap[key]
            if ftype == "bool":
                entry[snake] = not negate
                i += 2 if negate else 1
            else:
                if negate:
                    entry.pop(snake, None)
                    i += 2
                elif i + 1 < len(tokens) and tokens[i + 1] != "no" and tokens[i + 1] not in fmap:
                    value = _unquote(tokens[i + 1])
                    entry[snake] = int(value) if ftype == "int" and value.lstrip("-").isdigit() else value
                    i += 2
                else:
                    entry[snake] = True
                    i += 1

    @staticmethod
    def _parse_profile(tokens, entry):
        scalar = {"description": "description", "slot-numbering": "slot_numbering", "prompt": "prompt",
                  "password-timeout": "password_timeout", "terminal-timeout": "terminal_timeout"}
        permissions = entry.setdefault("permissions", {})
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = token == "no"
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
            # permission flag: <area> read|write|none, or 'no <area>'
            if negate:
                permissions[key] = "none"
                i += 2
            elif i + 1 < len(tokens) and tokens[i + 1] in ("read", "write", "none"):
                permissions[key] = tokens[i + 1]
                i += 2
            else:
                permissions[key] = "write"
                i += 1

    PARSERS = [{"name": "system_security", "getval": re.compile(r"^$"), "setval": "", "result": {}}]

    # section -> CLI node path (reverse of _NODES) for rendering
    _NODE_PATH = {
        "operators": "operator",
        "profiles": "profile",
        "snmp_communities": "snmp community",
        "snmp_views": "snmp view",
        "snmp_managers": "snmp manager",
        "snmp_notify_profiles": "snmp notify-profile",
        "radius_auth_servers": "radius auth-server",
        "radius_policies": "radius policy",
        "radius_dyn_auth_clients": "radius dyn-auth-client",
        "radius_auth_super_user": "radius auth-super-user",
    }
    _BOOL_FIELDS = {
        "operators": {"more", "confirm_prompt"},
        "snmp_managers": {"nt", "shub", "ihub", "epon", "vvpsa", "xvps1", "xvps2", "xvps3", "xvps4", "xvps5", "xvps6", "xvps7", "xvps8"},
        "radius_auth_servers": {"admin_down"},
        "radius_policies": {"keep_domain_name", "disable_accnt_msg", "disable_eap"},
    }

    @classmethod
    def render_entry(cls, section, entry):
        """Render one object as a single command with its configured attributes."""
        node = cls._NODE_PATH[section]
        ident = entry.get("name")
        base = "configure system security " + node + ((" " + str(ident)) if ident is not None else "")
        if section == "profiles":
            return [cls._render_profile(base, entry)]
        bools = cls._BOOL_FIELDS.get(section, set())
        parts = []
        for key, value in entry.items():
            if key == "name" or value is None:
                continue
            cli = _kebab(key)
            if key in bools:
                parts.append(cli if value else "no " + cli)
            elif value is True:
                parts.append(cli)
            else:
                parts.append("{0} {1}".format(cli, value))
        return [base + ((" " + " ".join(parts)) if parts else "")]

    @staticmethod
    def _render_profile(base, entry):
        parts = []
        for key in ("description", "slot_numbering", "prompt", "password_timeout", "terminal_timeout"):
            value = entry.get(key)
            if value is None:
                continue
            parts.append("{0} {1}".format(_kebab(key), value) if value is not True else _kebab(key))
        for area, mode in (entry.get("permissions") or {}).items():
            parts.append("no " + area if mode == "none" else "{0} {1}".format(area, mode))
        return base + ((" " + " ".join(parts)) if parts else "")

    @classmethod
    def render_remove(cls, section, name):
        node = cls._NODE_PATH[section]
        return "configure system security no " + node + ((" " + str(name)) if name is not None else "")
