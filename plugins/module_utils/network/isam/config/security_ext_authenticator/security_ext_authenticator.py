from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)


class Isam_security_ext_authenticator(object):
    """Execute the documented, non-persistent 802.1X administrative action."""

    def __init__(self, module):
        self.module = module

    def execute_module(self):
        commands = []
        for entry in self.module.params.get("config") or []:
            command = "admin security ext-authenticator %s" % entry["port"]
            if entry.get("clear_statistics"):
                command += " clear-statistics"
            commands.append(command)
        if commands and not self.module.check_mode:
            get_resource_connection(self.module).edit_config(candidate=commands)
        return {"changed": bool(commands), "commands": commands}
