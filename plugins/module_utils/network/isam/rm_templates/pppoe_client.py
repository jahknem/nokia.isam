# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import parse_cli_fields


class PppoeClientTemplate(object):
    """Parser and renderer for the two PPPoE client resource nodes."""

    PROFILE_FIELDS = ("ipversion", "authproto", "mru")
    INTERFACE_FIELDS = ("client_id", "profile_name", "username", "password", "mac", "pbit")

    def __init__(self, kind):
        self.kind = kind

    def parse(self, config):
        result = []
        prefix = "ppp-profile" if self.kind == "profile" else "interface"
        fields = self.PROFILE_FIELDS if self.kind == "profile" else self.INTERFACE_FIELDS
        for raw in (config or "").splitlines():
            line = raw.strip()
            if line.startswith("configure pppoe-client "):
                line = line[len("configure pppoe-client "):]
            if not line.startswith(prefix + " "):
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            item = {"name": tokens[1]}
            value_fields = {
                field.replace("_", "-"): "int" if field in ("client_id", "mru", "pbit") else "str"
                for field in fields
            }
            item.update(parse_cli_fields(tokens[2:], value_fields=value_fields))
            result.append(item)
        return result

    def render(self, config):
        commands = []
        prefix = "configure pppoe-client ppp-profile" if self.kind == "profile" else "configure pppoe-client interface"
        fields = self.PROFILE_FIELDS if self.kind == "profile" else self.INTERFACE_FIELDS
        cli_fields = {field: field.replace("_", "-") for field in fields}
        for item in config or []:
            command = [prefix, str(item["name"])]
            for field in fields:
                if item.get(field) is not None:
                    command.extend((cli_fields[field], str(item[field])))
            commands.append(" ".join(command))
        return commands


class Pppoel2StatisticsTemplate(object):
    def parse(self, config):
        result = []
        in_pppoel2 = False
        for raw in (config or "").splitlines():
            line = raw.strip()
            if line in ("configure pppoel2", "pppoel2"):
                in_pppoel2 = True
                continue
            if line == "exit":
                in_pppoel2 = False
                continue
            match = re.match(r"(?:configure\s+)?pppoel2\s+(no\s+)?statistics\s+(.+)$", line)
            if not match and in_pppoel2:
                match = re.match(r"(no\s+)?statistics\s+(.+)$", line)
            if match:
                result.append({"name": match.group(2), "enabled": not bool(match.group(1))})
        return result

    def render(self, config):
        return [
            "configure pppoel2 %sstatistics %s"
            % ("" if item.get("enabled", True) else "no ", item["name"])
            for item in (config or [])
        ]
