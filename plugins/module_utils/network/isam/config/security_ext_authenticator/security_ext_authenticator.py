from __future__ import absolute_import, division, print_function

import re
from ansible.module_utils.common.text.converters import to_text

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
            port = entry["port"]
            if not re.fullmatch(r"[A-Za-z0-9/:._-]+", port):
                self.module.fail_json(msg="Invalid port identifier: expected letters, digits and / : . _ - only.")
            if not entry.get("clear_statistics"):
                self.module.fail_json(msg="An explicit clear_statistics operation is required; a bare port is not an action.")
            commands.append("admin security ext-authenticator %s clear-statistics" % port)
        if commands and not self.module.check_mode:
            try:
                connection = get_resource_connection(self.module)
            except Exception as exc:
                self.module.fail_json(msg="ISAM action failed to acquire a connection: %s" % to_text(exc), commands=commands, changed=False)
            completed, responses = [], []
            for index, command in enumerate(commands):
                try:
                    response = connection.edit_config(candidate=[command])
                    responses.extend((response or {}).get("response", []))
                except Exception as exc:
                    self.module.fail_json(
                        msg="ISAM action failed: %s. The command outcome is unknown; do not blindly retry it." % to_text(exc),
                        changed=True, commands=commands, completed=completed, failed_command=command,
                        pending=commands[index + 1:], response=responses,
                    )
                completed.append(command)
        return {"changed": bool(commands), "commands": commands}
