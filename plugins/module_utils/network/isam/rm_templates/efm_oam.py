from __future__ import absolute_import, division, print_function

import re


class EfmOamTemplate(object):
    fields = ("admin_up", "passive_mode", "keep_alive_intvl", "response_intvl")

    def parse(self, config):
        resources = []
        pattern = re.compile(r"^(?:configure\s+)?efm-oam\s+interface\s+(\S+)(.*)$")
        for raw in (config or "").splitlines():
            line = raw.strip()
            match = pattern.match(line)
            if not match:
                continue
            item = {"name": match.group(1)}
            tokens = match.group(2).split()
            index = 0
            while index < len(tokens):
                token = tokens[index]
                if token in ("admin-up", "passive-mode"):
                    item[token.replace("-", "_")] = True
                    index += 1
                elif token == "no" and index + 1 < len(tokens) and tokens[index + 1] in ("admin-up", "passive-mode"):
                    item[tokens[index + 1].replace("-", "_")] = False
                    index += 2
                elif token in ("keep-alive-intvl", "response-intvl") and index + 1 < len(tokens):
                    item[token.replace("-", "_")] = tokens[index + 1]
                    index += 2
                elif token == "no" and index + 1 < len(tokens) and tokens[index + 1] in ("keep-alive-intvl", "response-intvl"):
                    item[tokens[index + 1].replace("-", "_")] = None
                    index += 2
                else:
                    index += 1
            resources.append(item)
        return resources

    def render(self, config):
        commands = []
        for item in config or []:
            command = ["configure", "efm-oam", "interface", str(item["name"])]
            for field, cli_name in (("admin_up", "admin-up"), ("passive_mode", "passive-mode")):
                if field in item and item[field] is not None:
                    command.extend(([cli_name] if item[field] else ["no", cli_name]))
            for field, cli_name in (("keep_alive_intvl", "keep-alive-intvl"), ("response_intvl", "response-intvl")):
                if field in item and item[field] is not None:
                    command.extend((cli_name, str(item[field])))
                elif field in item:
                    command.extend(("no", cli_name))
            commands.append(" ".join(command))
        return commands
