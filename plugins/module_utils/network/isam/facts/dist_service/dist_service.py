# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dist_service.dist_service import Isam_dist_serviceArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dist_service import Isam_dist_serviceTemplate


class Isam_dist_serviceFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_dist_serviceArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure dist-service flat")

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
                lines.append(stripped)
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
