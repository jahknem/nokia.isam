from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
)


_VERSION_FIELDS = ("sw-ver", "sw-ver-size")
_DOWNLOAD_FIELDS = (
    "ont",
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
    normalized = {_key(field): canonical_key(field) for field in fields}
    headers = None
    rows = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "=")) or set(stripped) <= set("-+=| "):
            continue

        parts = [part.strip() for part in line.split("|")] if "|" in line else stripped.split()
        names = [_key(part) for part in parts]
        if len(parts) > 1 and all(name in normalized for name in names) and len(set(names)) == len(names):
            headers = [normalized[name] for name in names]
            continue
        if not headers:
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
