from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
)


_VERSION_FIELDS = ("sw-ver-id", "sw-ver", "sw-ver-size")
_DOWNLOAD_FIELDS = (
    "ont",
    "ont-idx",
    "planned",
    "inactive",
    "planned-notok",
    "download-notok",
    "download-inprogress",
    "ntlt-inprogress",
    "omci-inprogress",
    "ontflash-inprogress",
    "ontswact-inprogress",
    "ntlt-failure",
    "omci-failure",
    "ontflash-failure",
    "ontswact-failure",
    "download-file-notfound",
    "no-matching-software",
    "sw-version-mismatch",
    "sw-download-failure",
    "sw-delayactivate",
    "sw-download-pending",
)


def _key(value):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def _table_rows(output, fields):
    """Read pipe-delimited or whitespace-delimited Nokia display tables."""
    lines = [line.rstrip() for line in (output or "").splitlines()]
    aliases = {"ont-idx": "ont"}
    normalized = {_key(field): aliases.get(field, canonical_key(field)) for field in fields}
    headers = None
    pending_header = None
    rows = []
    count_line = re.compile(r"^[\w\-]+\s+count\s*:\s*\d+\s*$")

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "=")) or set(stripped) <= set("-+=| "):
            continue
        if count_line.match(stripped):
            continue

        parts = [part.strip() for part in line.split("|")] if "|" in line else stripped.split()
        names = [_key(part) for part in parts]
        if headers is None:
            if all(parts) and len(parts) > 1 and all(name in normalized for name in names) and len(set(names)) == len(names):
                headers = [normalized[name] for name in names]
                pending_header = None
                continue
            if not all(parts) and len(parts) > 1 and any(parts):
                pending_header = parts
                continue
            if pending_header and len(pending_header) == len(parts) and all(parts):
                names = [
                    _key("_".join(part for part in (top, bottom) if part))
                    for top, bottom in zip(pending_header, parts)
                ]
                pending_header = None
                if all(name in normalized for name in names) and len(set(names)) == len(names):
                    headers = [normalized[name] for name in names]
                    continue
            continue

        values = [part.strip() for part in line.split("|")] if "|" in line else stripped.split()
        if len(values) < len(headers):
            continue
        rows.append(dict(zip(headers, values[: len(headers)])))

    return rows


def _labeled_record(output, fields):
    """Read the detail form, where each display parameter is labeled."""
    allowed = {_key(field): canonical_key(field) for field in fields}
    records = []
    current = {}
    key_value = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9 _-]*?)\s*(?::|=)\s*(?P<value>.+?)\s*$")

    for raw_line in (output or "").splitlines():
        line = raw_line.strip()
        match = key_value.match(line)
        if not match:
            continue
        key = _key(match.group("key"))
        if key not in allowed:
            continue
        if key in current:
            records.append(current)
            current = {}
        value = match.group("value").strip().strip('"')
        current[allowed[key]] = value

    if current:
        records.append(current)
    return records


def _parse(output, fields):
    return _table_rows(output, fields) or _labeled_record(output, fields)


def parse_ont_sw_version(output):
    """Parse ``show equipment ont sw-version`` output."""
    return _parse(output, _VERSION_FIELDS)


def parse_ont_sw_download(output):
    """Parse ``show equipment ont sw-download`` output."""
    return _parse(output, _DOWNLOAD_FIELDS)
