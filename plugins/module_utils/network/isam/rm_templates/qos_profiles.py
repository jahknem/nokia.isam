# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


def _to_native(value):
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value


class Qos_profilesTemplate(NetworkTemplate):
    """Parser and renderer for ``configure qos profiles``."""

    _TOP_LEVEL = (
        "queue",
        "scheduler-node",
        "cac",
        "policer",
        "session",
        "aggrqueuesconfig",
        "shaper",
        "bandwidth",
        "ingress-qos",
        "rate-limit",
    )
    _INLINE_ORDER = {
        "queue": ("queue-type",),
        "scheduler-node": ("priority", "weight", "shaper-profile"),
        "cac": ("res-voice-bandwidth", "max-mcast-bandwidth", "res-data-bandwidth"),
        "marker-d1p": ("default-dot1p",),
        "policer": ("committed-info-rate", "committed-burst-size"),
        "session": ("logical-flow-type",),
        "shaper": ("committed-info-rate", "committed-burst-size"),
        "bandwidth": ("committed-info-rate", "assured-info-rate", "excessive-info-rate"),
    }
    _CHILD_KEY_MAP = {"type": "shaper-type"}
    _KNOWN_CHILD_KEYS = set((
        "mcast-inc-shape",
        "cac-type",
        "up-policer",
        "down-policer",
        "up-marker",
        "excess-info-rate",
        "type",
        "delay-tolerance",
        "total-rate",
        "total-burst",
        "dot1-p0-tc",
        "dot1-p1-tc",
        "dot1-p2-tc",
        "dot1-p3-tc",
        "dot1-p4-tc",
        "dot1-p5-tc",
        "dot1-p6-tc",
        "dot1-p7-tc",
    ))
    _FIELDS = (
        "profile_type",
        "queue-type",
        "priority",
        "weight",
        "shaper-profile",
        "mcast-inc-shape",
        "res-voice-bandwidth",
        "max-mcast-bandwidth",
        "res-data-bandwidth",
        "cac-type",
        "default-dot1p",
        "committed-info-rate",
        "committed-burst-size",
        "excess-info-rate",
        "shaper-type",
        "assured-info-rate",
        "excessive-info-rate",
        "delay-tolerance",
        "logical-flow-type",
        "up-policer",
        "down-policer",
        "up-marker",
        "total-rate",
        "total-burst",
        "dot1-p0-tc",
        "dot1-p1-tc",
        "dot1-p2-tc",
        "dot1-p3-tc",
        "dot1-p4-tc",
        "dot1-p5-tc",
        "dot1-p6-tc",
        "dot1-p7-tc",
        "attributes",
    )

    def __init__(self, lines=None, module=None):
        super(Qos_profilesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    @classmethod
    def _profile_path(cls, data):
        if data.get("profile_type") == "marker-d1p":
            return "marker d1p {0}".format(data["name"])
        return "{0} {1}".format(data["profile_type"], data["name"])

    @classmethod
    def _render_profile_line(cls, data):
        command = "configure qos profiles {0}".format(cls._profile_path(data))
        for field in cls._INLINE_ORDER.get(data.get("profile_type"), ()):  # pragma: no branch
            if data.get(field) is not None:
                command += " {0} {1}".format(field, data[field]) if field != "queue-type" else " {0}".format(data[field])
        return command

    @classmethod
    def _render_delete_profile(cls, data):
        return "configure qos profiles no {0}".format(cls._profile_path(data))

    @classmethod
    def _render_field(cls, field):
        def render(data):
            if data.get(field) is None:
                return None
            cli_field = "type" if field == "shaper-type" else field
            return "configure qos profiles {0} {1} {2}".format(cls._profile_path(data), cli_field, data[field])
        return render

    @classmethod
    def _render_no_field(cls, field):
        def render(data):
            cli_field = "type" if field == "shaper-type" else field
            return "configure qos profiles {0} no {1}".format(cls._profile_path(data), cli_field)
        return render

    @classmethod
    def _render_attributes(cls, data):
        commands = []
        for attribute in data.get("attributes") or []:
            commands.append("configure qos profiles {0} {1}".format(cls._profile_path(data), attribute))
        return commands

    @classmethod
    def _parse_key_values(cls, rest, dest, inline_order=None):
        tokens = rest.split()
        if inline_order and inline_order[:1] == ("queue-type",) and tokens:
            dest["queue-type"] = tokens.pop(0)
        idx = 0
        while idx + 1 < len(tokens):
            key = cls._CHILD_KEY_MAP.get(tokens[idx], tokens[idx])
            dest[key] = _to_native(tokens[idx + 1])
            idx += 2

    def parse(self):
        result = {}
        current = None
        in_profiles = False
        in_marker = False
        top_re = re.compile(r"^({0})\s+(\S+)(?:\s+(.*))?$".format("|".join(self._TOP_LEVEL)))
        marker_re = re.compile(r"^d1p\s+(\S+)(?:\s+(.*))?$")

        for raw_line in self._lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo "):
                continue
            if stripped == "profiles":
                in_profiles = True
                continue
            if stripped in ("configure qos", "configure qos profiles"):
                in_profiles = True
                continue
            if not in_profiles:
                continue
            if stripped == "marker":
                in_marker = True
                current = None
                continue
            if stripped == "exit":
                if current is not None:
                    current = None
                elif in_marker:
                    in_marker = False
                continue

            match = marker_re.match(stripped) if in_marker else top_re.match(stripped)
            if match:
                if in_marker:
                    profile_type = "marker-d1p"
                    name, rest = match.group(1), match.group(2) or ""
                else:
                    profile_type, name, rest = match.group(1), match.group(2), match.group(3) or ""
                key = "{0}:{1}".format(profile_type, name)
                current = result.setdefault(key, {"profile_type": profile_type, "name": name})
                self._parse_key_values(rest, current, self._INLINE_ORDER.get(profile_type))
                continue

            if current is None:
                continue
            key_value = stripped.split(None, 1)
            if key_value[0] in self._KNOWN_CHILD_KEYS and len(key_value) == 2:
                key = self._CHILD_KEY_MAP.get(key_value[0], key_value[0])
                current[key] = _to_native(key_value[1])
            else:
                current.setdefault("attributes", []).append(stripped)
        return result



Qos_profilesTemplate.PARSERS = [
    {
        "name": "profile_type",
        "getval": re.compile(r"^$"),
        "setval": Qos_profilesTemplate._render_profile_line,
        "remval": Qos_profilesTemplate._render_delete_profile,
        "result": {},
    },
]

for _field in Qos_profilesTemplate._FIELDS:
    if _field == "profile_type":
        continue
    _inline_fields = set()
    for _fields in Qos_profilesTemplate._INLINE_ORDER.values():
        _inline_fields.update(_fields)
    Qos_profilesTemplate.PARSERS.append(
        {
            "name": _field,
            "getval": re.compile(r"^$"),
            "setval": Qos_profilesTemplate._render_attributes
            if _field == "attributes"
            else Qos_profilesTemplate._render_profile_line
            if _field in _inline_fields
            else Qos_profilesTemplate._render_field(_field),
            "remval": None
            if _field == "attributes"
            else Qos_profilesTemplate._render_no_field(_field),
            "result": {},
        }
    )
