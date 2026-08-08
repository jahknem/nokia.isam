from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.security_ext_authenticator import (
    Isam_security_ext_authenticatorTemplate,
)


class Isam_security_ext_authenticator(object):
    """Render and parse the documented, non-persistent 802.1X command."""

    def __init__(self, module):
        self.module = module
        self.template = Isam_security_ext_authenticatorTemplate(module=module)

    def execute_module(self):
        if self.module.params["state"] == "parsed":
            template = Isam_security_ext_authenticatorTemplate(
                lines=self.module.params.get("running_config", "").splitlines(),
                module=self.module,
            )
            parsed = template.parse()
            return {"changed": False, "parsed": parsed}

        commands = []
        for entry in self.module.params.get("config") or []:
            command = "admin security ext-authenticator %s" % entry["port"]
            if entry.get("clear_statistics"):
                command += " clear-statistics"
            commands.append(command)
        return {"changed": False, "rendered": commands, "commands": commands}
