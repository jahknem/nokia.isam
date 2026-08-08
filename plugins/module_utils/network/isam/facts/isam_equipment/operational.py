# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re


class EquipmentOperationalParser(object):
    """Parse operational equipment records returned by the ISAM CLI."""

    _RESOURCE_RE = re.compile(
        r"^(?P<resource>shelf|slot|applique|protection-group)\s+(?P<id>\S+)$"
    )
    _FIELD_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*)\s*(?::|\s+)\s*(?P<value>.+?)\s*$")
    _IGNORED_RE = re.compile(
        r"^(?:#|echo\s|configure\s|show\s|[A-Za-z0-9_.:-]+>.*(?:#|$))"
    )

    def parse(self, output):
        """Return operational records grouped by equipment resource."""
        records = {"shelves": [], "slots": [], "appliques": [], "protection_groups": []}
        current = None

        for raw_line in (output or "").splitlines():
            line = raw_line.strip()
            if not line or self._IGNORED_RE.match(line):
                continue

            resource_match = self._RESOURCE_RE.match(line)
            if resource_match:
                resource = resource_match.group("resource")
                current = {"id": self._convert(resource_match.group("id"))}
                records[self._plural(resource)].append(current)
                continue

            if current is None:
                continue

            field_match = self._FIELD_RE.match(line)
            if field_match:
                key = field_match.group("key").replace("-", "_")
                current[key] = self._convert(field_match.group("value"))

        return {key: value for key, value in records.items() if value}

    @staticmethod
    def _plural(resource):
        return {
            "shelf": "shelves",
            "slot": "slots",
            "applique": "appliques",
            "protection-group": "protection_groups",
        }[resource]

    @staticmethod
    def _convert(value):
        value = value.strip()
        lowered = value.lower()
        if lowered in ("true", "yes", "on"):
            return True
        if lowered in ("false", "no", "off"):
            return False
        if re.match(r"^-?\d+$", value):
            return int(value)
        return value
