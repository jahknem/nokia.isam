"""Dependency-light Nokia fixed-width table parsing, shared by facts and filters."""
import re


def _key(value):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def parse_status_table(output):
    """Parse Nokia fixed-width tables with a pipe-delimited header."""
    rows = []
    lines = (output or "").splitlines()
    headers = None
    widths = None
    pending_header = None
    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        if headers and "|" in line and not line.lstrip().startswith(("#", "=")):
            candidate = [part.strip() for part in line.split("|")]
            if len(candidate) == len(headers) and all(candidate):
                rows.append(dict(zip(headers, candidate)))
                continue
        if "|" in line and not line.lstrip().startswith(("#", "=")):
            candidate = [part.strip() for part in line.split("|")]
            if len(candidate) > 1 and any(candidate):
                if not all(candidate):
                    pending_header = candidate
                    continue
                if pending_header and len(pending_header) == len(candidate):
                    candidate = ["_".join(part for part in (top, bottom) if part)
                                 for top, bottom in zip(pending_header, candidate)]
                    pending_header = None
                headers = [_key(part) for part in candidate]
                if index + 1 < len(lines) and "+" in lines[index + 1]:
                    widths = [len(part) for part in lines[index + 1].split("+")]
                continue
        if not headers or not line.strip() or line.strip().startswith(("-", "=", "#")):
            continue
        if line.lower().startswith(("port count", "slot count", "pon count")) or " count :" in line.lower():
            continue
        if widths:
            fields = []
            offset = 0
            for width in widths:
                fields.append(line[offset:offset + width].strip())
                offset += width + 1
        else:
            fields = [field.strip() for field in line.split()]
        if len(fields) >= len(headers):
            rows.append(dict(zip(headers, fields[:len(headers)])))
    return rows
