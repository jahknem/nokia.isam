from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import copy

from ansible import constants as C
from ansible_collections.arista.eos.plugins.module_utils.network.eos.eos import (
    eos_provider_spec,
)
from ansible_collections.ansible.netcommon.plugins.action.network import (
    ActionModule as ActionNetworkModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    load_provider,
)
from ansible.utils.display import Display

display = Display()

CLI_SUPPORTED_MODULES = []

class ActionModule(ActionNetworkModule):
    def run(self, tmp=None, task_vars=None):
        del tmp  # tmp no longer has any effect

        module_name = self._task.action.split(".")[-1]
        self._config_module = (
            True if module_name in ["isam_config", "config"] else False
        )
        persistent_connection = self._play_context.connection.split(".")[-1]
        warnings = []    
        if persistent_connection == "network_cli":
            provider = self._task.args.get("provider", {})
            if any(provider.values()):
                display.warning(
                    "provider is unnecessary when using network_cli and will be ignored",
                )
                del self._task.args["provider"]
            if persistent_connection == 'network_cli' and module_name not in CLI_SUPPORTED_MODULES:
                return {'failed': True, 'msg': "Connection type '%s' is not valid for '%s' module."
                        % (self._play_context.connection, self._task.action)}
        elif self._play_context.connection == "local":
            return {
                'failed': True,
                'msg': "connection local support for this module has been removed use either 'network_cli' or 'ansible.netcommon.network_cli' connection"
            }
            provider = load_provider(isam_provider_spec, self._task.args)
            pc = copy.deepcopy(self._play_context)
            pc.connection = "ansible.netcommon.network_cli"
            pc.network_os = "nokia.isam.isam"
            pc.remote_addr = provider["host"] or self._play_context.remote_addr
            pc.port = int(provider["port"] or self._play_context.port or 22)
            pc.remote_user = provider["username"] or self._play_context.connection_user
            pc.password = provider["password"] or self._play_context.password
            pc.private_key_file = provider["ssh_keyfile"] or self._play_context.private_key_file
            pc.become = provider["authorize"] or False
            if pc.become:
                pc.become_method = "enable"
            pc.become_pass = provider["auth_pass"]

            connection = self._shared_loader_obj.connection_loader.get(
                "ansible.netcommon.persistent",
                pc,
                sys.stdin,
                task_uuid=self._task._uuid,
            )

            # TODO: Remove below code after ansible minimal is cut out
            if connection is None:
                pc.connection = "network_cli"
                pc.network_os = "isam"
                connection = self._shared_loader_obj.connection_loader.get(
                    "persistent",
                    pc,
                    sys.stdin,
                    task_uuid=self._task._uuid,
                )

            display.vvv(
                "using connection plugin %s (was local)" % pc.connection,
                pc.remote_addr,
            )

            command_timeout = (
                int(provider["timeout"])
                if provider["timeout"]
                else connection.get_option("persistent_command_timeout")
            )
            connection.set_options(
                direct={"persistent_command_timeout": command_timeout},
            )

            socket_path = connection.run()
            display.vvvv("socket_path: %s" % socket_path, pc.remote_addr)
            if not socket_path:
                return {
                    "failed": True,
                    "msg": "unable to open shell. Please see: "
                    + "https://docs.ansible.com/ansible/network_debug_troubleshooting.html#unable-to-open-shell",
                }

            task_vars["ansible_socket"] = socket_path
            warnings.append(
                [
                    "connection local support for this module is deprecated and will be removed in version 2.14, use connection %s"
                    % pc.connection,
                ],
            )
        else:
            return {
                "failed": True,
                "msg": "Connection type %s is not valid for this module"
                % self._play_context.connection,
            }

        result = super(ActionModule, self).run(task_vars=task_vars)
        if warnings:
            if "warnings" in result:
                result["warnings"].extend(warnings)
            else:
                result["warnings"] = warnings
        return result