# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re


class OntRangingStatusParser(object):
    """Parse the table returned by the ONT channel-pair ranging command."""

    def parse(self, data):
        lines = data.splitlines() if isinstance(data, str) else (data or [])
        headers = None
        rows = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line or self._is_framing(line):
                continue
            if line.lower().startswith(("channel-pair count", "ont count")):
                continue

            fields = self._split(line)
            normalized = [self._normalize_header(field) for field in fields]
            if self._is_header(line, normalized):
                headers = ["ont", "usage_by_ont"] if len(fields) == 1 else normalized
                continue
            if headers is None:
                continue

            if len(fields) < len(headers):
                fields = line.split(None, len(headers) - 1)
            if len(fields) > len(headers):
                fields = fields[:len(headers) - 1] + [" ".join(fields[len(headers) - 1:])]
            if len(fields) == len(headers):
                rows.append(dict(zip(headers, fields)))

        return {"ranging_status": rows}

    @staticmethod
    def _split(line):
        if "|" in line:
            return [field.strip() for field in line.strip("|").split("|") if field.strip()]
        return [field.strip() for field in re.split(r"\s{2,}", line) if field.strip()]

    @staticmethod
    def _is_framing(line):
        return line.startswith(("#", "=", "-")) or not re.search(r"[A-Za-z0-9]", line)

    @staticmethod
    def _is_header(line, normalized):
        if "ont" in normalized and "usage_by_ont" in normalized:
            return True
        if "chpair" in normalized and "ont" in normalized and "usage_by_ont" in normalized:
            return True
        compact = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
        return bool(re.match(r"^ont\s+usage\s+by\s+ont$", compact))

    @staticmethod
    def _normalize_header(value):
        normalized = re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")
        return {"usage_by_ont": "usage_by_ont", "chpair": "chpair"}.get(normalized, normalized)
