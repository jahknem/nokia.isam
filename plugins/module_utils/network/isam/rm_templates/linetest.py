# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
    parse_cli_fields,
)


SESSION_FIELDS = [
    "ownerid", "timeout-period", "line-num", "type-high", "type-low",
    "test-parm-num", "test-mode", "inactive-timer", "type-extend",
    "group-opt", "busy-overwrite", "force-measure",
]
PARAMETER_FIELDS = [
    "value1", "value2", "value3", "value4", "value5", "min-threshold",
    "max-threshold", "min-threshold2", "max-threshold2", "ltstrvalue1",
]
RESET_FIELDS = ("group-opt", "busy-overwrite", "force-measure")


class LinetestTemplate(object):
    """Parse and render declarative LineTest configuration only."""

    def parse(self, config):
        result = {"sessions": [], "parameters": []}
        # Instance block: attribute lines indented below "ltsession <id>" or
        # "ltparm <id> <test>" (hierarchical or scoped "info configure linetest ...").
        block = None
        for raw in (config or "").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("echo"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if block is not None and indent <= block[0]:
                block = None
            if block is not None:
                parts = line.split()
                if parts[0] != "exit":
                    indent_, items, fields, identity = block
                    item = dict(identity)
                    self._fields(item, parts, fields)
                    self._add(items, item, *identity.keys())
                continue
            if line.startswith("configure "):
                line = line[len("configure "):]
            if line.startswith("linetest "):
                line = line[len("linetest "):]
            if line.startswith("single "):
                line = line[len("single "):]
            parts = line.split()
            if not parts:
                continue
            kind = parts.pop(0)
            if kind == "ltsession" and parts:
                item = {"session_id": parts.pop(0)}
                identity = dict(item)
                self._fields(item, parts, SESSION_FIELDS)
                self._add(result["sessions"], item, "session_id")
                block = (indent, result["sessions"], SESSION_FIELDS, identity)
            elif kind == "ltparm" and len(parts) >= 2:
                item = {"session_id": parts.pop(0), "test_name": parts.pop(0)}
                identity = dict(item)
                self._fields(item, parts, PARAMETER_FIELDS)
                self._add(result["parameters"], item, "session_id", "test_name")
                block = (indent, result["parameters"], PARAMETER_FIELDS, identity)
        return self.normalize(result)

    def render(self, config):
        commands = []
        for session in (config or {}).get("sessions") or []:
            commands.extend(self._render("ltsession", session, SESSION_FIELDS, "session_id"))
        for parameter in (config or {}).get("parameters") or []:
            commands.extend(self._render("ltparm", parameter, PARAMETER_FIELDS, "session_id", "test_name"))
        return commands

    def normalize(self, data):
        return {
            "sessions": [dict(item) for item in (data or {}).get("sessions") or []],
            "parameters": [dict(item) for item in (data or {}).get("parameters") or []],
        }

    def _render(self, kind, item, fields, *identifiers):
        prefix = "configure linetest single %s" % kind
        values = [str(item.get(identifier)) for identifier in identifiers]
        commands = []
        for field in fields:
            key = canonical_key(field)
            if key in item and item.get(key) is None and field in RESET_FIELDS:
                commands.append("%s %s %s no" % (prefix, " ".join(values), field))
            elif item.get(key) is not None:
                commands.append("%s %s %s %s" % (prefix, " ".join(values), field, item[key]))
        return commands

    def _fields(self, item, parts, fields):
        # These options reset with a trailing 'no' (CLI guide), not 'no <kw>'.
        # Normalize that grammar before using the shared clause parser so rendered
        # reset commands parse back to unset, never the literal string "no".
        tokens = []
        index = 0
        while index < len(parts):
            if parts[index] == "no" and index + 1 < len(parts) and parts[index + 1] in fields:
                tokens.extend(parts[index:index + 2])
                index += 2
            elif parts[index] in RESET_FIELDS and index + 1 < len(parts) and parts[index + 1] == "no":
                tokens.extend(("no", parts[index]))
                index += 2
            else:
                tokens.append(parts[index])
                index += 1
        item.update(
            parse_cli_fields(
                tokens,
                value_fields={field: "str" for field in fields},
                none_for_negated_values=True,
            )
        )

    def _add(self, items, item, *keys):
        existing = next((entry for entry in items if all(entry.get(key) == item.get(key) for key in keys)), None)
        if existing is None:
            items.append(item)
        else:
            existing.update(item)
