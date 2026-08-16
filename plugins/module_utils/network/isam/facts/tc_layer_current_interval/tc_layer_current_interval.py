from __future__ import absolute_import, division, print_function

import re


class TcLayerCurrentIntervalParser(object):
    """Parse ``show pon interface tc-layer current-interval`` output."""

    _FIELDS = frozenset(
        (
            "tx_gem_frames",
            "rx_gem_frames",
            "tx_payload_bytes",
            "rx_payload_bytes",
            "encrypkey_errors",
            "err_frags_up",
        )
    )
    _IDENTIFIERS = frozenset(("resource_identifier", "pon_idx"))
    _FIELD_RE = re.compile(
        r"^(?P<key>[A-Za-z][A-Za-z0-9 _-]*?)\s*(?::|=|\s{2,})\s*(?P<value>.+?)\s*$"
    )

    def parse(self, output):
        records = []
        current = None
        headers = None

        for raw_line in (output or "").splitlines():
            line = raw_line.strip()
            if not line or self._is_noise(line):
                continue

            if "|" in line:
                parts = [self._key(part) for part in line.split("|")]
                if self._is_table_header(parts):
                    headers = parts
                    continue
                if headers:
                    values = [part.strip() for part in line.split("|")]
                    if len(values) == len(headers):
                        records.append(
                            {
                                key: self._value(value)
                                for key, value in zip(headers, values)
                                if key
                            }
                        )
                        continue

            match = self._FIELD_RE.match(line)
            if match:
                key = self._key(match.group("key"))
                value = self._value(match.group("value"))
                if key in self._IDENTIFIERS:
                    if current:
                        records.append(current)
                    current = {key: value}
                elif key in self._FIELDS:
                    if current is None:
                        current = {}
                    current[key] = value
                continue

            if headers:
                values = line.split()
                if len(values) == len(headers):
                    records.append(
                        {
                            key: self._value(value)
                            for key, value in zip(headers, values)
                            if key
                        }
                    )

        if current:
            records.append(current)
        return records

    @classmethod
    def _is_table_header(cls, parts):
        return bool(parts) and any(part in cls._IDENTIFIERS for part in parts) and any(
            part in cls._FIELDS for part in parts
        )

    @staticmethod
    def _key(value):
        return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")

    @staticmethod
    def _value(value):
        value = value.strip()
        return int(value) if re.match(r"^\d+$", value) else value

    @staticmethod
    def _is_noise(line):
        return (
            line.startswith(("#", "echo ", "->", "show "))
            or set(line) <= set("-+=_| ")
        )


def parse_tc_layer_current_interval(output):
    """Return current TC-layer counters as a list of resource records."""
    return TcLayerCurrentIntervalParser().parse(output)
