# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


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


def parse_status_table(output):
    """Parse Nokia fixed-width tables with a pipe-delimited header."""
    rows = []
    lines = (output or "").splitlines()
    headers = None
    widths = None

    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        if "|" in line and not line.lstrip().startswith(("#", "=")):
            candidate = [part.strip() for part in line.split("|")]
            if len(candidate) > 1 and all(candidate):
                headers = [_key(part) for part in candidate]
                if index + 1 < len(lines) and "+" in lines[index + 1]:
                    widths = [len(part) for part in lines[index + 1].split("+")]
                continue
        if not headers or not line.strip() or line.startswith(("-", "=", "#")):
            continue
        if line.lower().startswith(("port count", "slot count")):
            continue
        fields = [field.strip() for field in line.split()]
        if len(fields) < len(headers):
            continue
        rows.append(dict(zip(headers, fields[:len(headers)])))

    return rows
