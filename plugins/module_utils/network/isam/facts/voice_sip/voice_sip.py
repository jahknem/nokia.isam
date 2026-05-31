# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import (
    Isam_voice_sipArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
)


class Isam_voice_sipFacts(object):
    """The isam voice sip facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_voice_sipArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure voice sip")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        data = self._flatten_config(data)
        parser = Isam_voice_sipTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "registrar": parsed.get("registrar", {}),
            "proxy": parsed.get("proxy", {}),
            "codec": list(parsed.get("codec", {}).values()),
            "sip_profile": list(parsed.get("sip_profile", {}).values()),
        }

        for codec in objs["codec"]:
            codec["priority"] = int(codec["priority"])

        for profile in objs["sip_profile"]:
            if "timer_t1" in profile:
                profile["timer_t1"] = int(profile["timer_t1"])
            if "timer_t2" in profile:
                profile["timer_t2"] = int(profile["timer_t2"])
        if "port" in objs["registrar"]:
            objs["registrar"]["port"] = int(objs["registrar"]["port"])
        if "port" in objs["proxy"]:
            objs["proxy"]["port"] = int(objs["proxy"]["port"])

        ansible_facts["ansible_network_resources"].pop("voice_sip", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["voice_sip"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure voice sip "):
                flat_config.append(line)

        return flat_config
