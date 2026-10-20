# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

# Preserve the public import location without forcing lightweight filters to
# import the ISAM ResourceModule compatibility hooks and resource framework.
from ansible_collections.nokia.isam.plugins.module_utils.tables import parse_status_table


_SECTION_RE = re.compile(r"^(?P<kind>ont|pon)(?:\s+interface)?\s+(?P<id>\S+?)(?:\s*:)?$", re.I)
_KEY_VALUE_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9 _./-]*?)\s*(?::|=)\s*(?P<value>.+?)\s*$")


def _key(value):
    """Convert device labels to the snake-case used by facts resources."""
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def _value(value):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def parse_operational_facts(output):
    """Parse labeled ONT/PON operational output into a list of records.

    ISAM emits these commands as human-readable sections rather than as
    configuration lines.  Unknown labels are deliberately retained, while
    command prompts, comments, and table separator lines are ignored.
    """
    records = []
    current = None

    for raw_line in (output or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "echo ", "->")):
            continue
        if set(line) <= set("-+= "):
            continue

        section = _SECTION_RE.match(line)
        if section:
            if current:
                records.append(current)
            current = {"type": section.group("kind").lower(), "id": section.group("id")}
            continue

        match = _KEY_VALUE_RE.match(line)
        if not match:
            continue
        if current is None:
            current = {}
        current[_key(match.group("key"))] = _value(match.group("value"))

    if current:
        records.append(current)
    return records


def parse_ont_operational(output):
    """Parse operational data returned for ONT interfaces."""
    return [record for record in parse_operational_facts(output) if record.get("type") in (None, "ont")]


def parse_pon_operational(output):
    """Parse operational data returned for PON interfaces."""
    return [record for record in parse_operational_facts(output) if record.get("type") in (None, "pon")]
