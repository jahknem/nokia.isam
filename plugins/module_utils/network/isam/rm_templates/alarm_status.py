# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


class AlarmStatusParser(object):
    """Parse the tabular output returned by the active-alarm CLI command."""

    _HEADER_NAMES = {
        "alarm": "alarm_id",
        "alarm-id": "alarm_id",
        "alarm_id": "alarm_id",
        "id": "alarm_id",
        "index": "index",
        "type": "type",
        "last-updated-on": "last_updated_on",
        "severity": "severity",
        "state": "state",
        "status": "state",
        "source": "source",
        "location": "source",
        "description": "description",
        "text": "description",
    }

    def parse(self, data):
        lines = data.splitlines() if isinstance(data, str) else data
        headers = None
        alarms = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith(("#", "---", "===", "Alarm:")):
                continue

            fields = self._split(line)
            normalized = [self._normalize_header(field) for field in fields]
            if any(normalized) and all(field is not None for field in normalized) and len(normalized) >= 2:
                headers = normalized
                continue
            if headers is None or not fields:
                continue

            values = fields[:len(headers)]
            if len(fields) > len(headers):
                values = fields[:len(headers) - 1] + [" ".join(fields[len(headers) - 1:])]
            if len(values) < len(headers):
                continue
            alarms.append(dict((key, value) for key, value in zip(headers, values) if key))

        return {"alarms": alarms}

    @staticmethod
    def _split(line):
        if "|" in line:
            return [field.strip() for field in line.split("|") if field.strip()]
        return [field.strip() for field in re.split(r"\s{2,}", line.strip()) if field.strip()]

    @classmethod
    def _normalize_header(cls, field):
        return cls._HEADER_NAMES.get(re.sub(r"\s+", "-", field.lower()))
