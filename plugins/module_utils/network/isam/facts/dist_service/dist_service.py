# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dist_service.dist_service import Isam_dist_serviceArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dist_service import Isam_dist_serviceTemplate


class Isam_dist_serviceFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_dist_serviceArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the services named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "isam_dist_service", "info configure dist-service flat", {
            "config": "info configure dist-service %s flat",
        }, bare_sections=("config",))  # a service with only defaults answers its single read with a header (lab ISAM)

    def populate_facts(self, connection, ansible_facts, data=None):
        data = unwrap_response(data if data else self.get_config(connection))
        parser = Isam_dist_serviceTemplate(lines=self._flatten_config(data), module=self._module)
        objects = list(parser.parse().values())
        ansible_facts["ansible_network_resources"].pop("isam_dist_service", None)
        params = utils.remove_empties(parser.validate_config(self.argument_spec, {"config": objects}, redact=True)) or {}
        ansible_facts["ansible_network_resources"]["isam_dist_service"] = params.get("config") or []
        return ansible_facts

    @staticmethod
    def _flatten_config(config):
        lines = []
        in_service = False
        service_name = None
        for raw_line in (config or "").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo"):
                continue
            if line.startswith("configure dist-service ") and len(stripped.split()) > 3:
                lines.extend(Isam_dist_serviceFacts._split_flat_line(stripped))
            elif stripped.startswith("configure dist-service "):
                lines.append(stripped)
                in_service = True
                service_name = stripped.split()[2]
            elif stripped == "exit":
                in_service = False
                service_name = None
            elif in_service and stripped.startswith(("service-type", "no service-type", "qos-profile", "no qos-profile")):
                lines.append("configure dist-service %s %s" % (service_name, stripped))
        return lines

    @staticmethod
    def _split_flat_line(line):
        """One line per attribute: flat output can carry service-type and qos-profile together."""
        tokens = line.split()
        prefix, rest = " ".join(tokens[:3]), tokens[3:]
        split, index = [], 0
        while index < len(rest):
            negate = rest[index] == "no"
            key_index = index + 1 if negate else index
            if key_index >= len(rest) or rest[key_index] not in ("service-type", "qos-profile"):
                return [line]
            if negate or key_index + 1 >= len(rest):
                split.append("%s %s%s" % (prefix, "no " if negate else "", rest[key_index]))
                index = key_index + 1
            else:
                split.append("%s %s %s" % (prefix, rest[key_index], rest[key_index + 1]))
                index = key_index + 2
        return split or [line]
