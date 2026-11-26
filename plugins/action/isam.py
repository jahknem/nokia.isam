#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function


__metaclass__ = type


from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.action.network import (
    ActionModule as ActionNetworkModule,
)


display = Display()


class ActionModule(ActionNetworkModule):
    # Action states given running_config render against it offline (no device). Run them
    # in-process without opening the persistent connection, exactly like rendered. These are
    # the resource modules' action states (IsamResourceModule.ACTION_STATES); no module has
    # a "purged" state.
    OFFLINE_ACTION_STATES = ("merged", "replaced", "overridden", "deleted")

    def run(self, tmp=None, task_vars=None):
        del tmp  # tmp no longer has any effect

        module_name = self._task.action.split(".")[-1]
        self._config_module = True if module_name in ["isam_config", "config"] else False

        if self._task.args.get("state") in self.OFFLINE_ACTION_STATES and self._task.args.get("running_config"):
            return self._run_offline(task_vars)

        persistent_connection = self._play_context.connection.split(".")[-1]
        warnings = []

        if persistent_connection not in ("network_cli", "isam_network_cli"):
            return {
                "failed": True,
                "msg": "Connection type %s is not valid for this module"
                % self._play_context.connection,
            }

        # netcommon direct execution bypasses the normal module argument
        # transport, so propagate check mode explicitly.
        self._task.args["_ansible_check_mode"] = bool(self._task.check_mode)
        result = super(ActionModule, self).run(task_vars=task_vars)
        if warnings:
            if "warnings" in result:
                result["warnings"].extend(warnings)
            else:
                result["warnings"] = warnings
        return result

    def _run_offline(self, task_vars=None):
        """Execute an offline action state in-process, never opening the device connection.

        Reuses netcommon's module loader and in-process executor but skips its connection
        setup (``_patch_update_module`` hands the module the persistent connection's socket,
        and any use of it starts the SSH session). The module's own offline path renders the commands from
        ``running_config`` without a device. The ``_ansible_*`` arguments (check and diff mode,
        no_log, verbosity, ...) are set exactly as for any other module run.
        """
        import copy

        from ansible.module_utils.basic import AnsibleModule as _AnsibleModule

        _filename, module = self._find_load_module()
        if getattr(module, "AnsibleModule", None) is None:
            return {"failed": True, "msg": "%s does not support offline execution" % self._task.action}

        class _OfflineModule(_AnsibleModule):
            def _load_params(self):
                from ansible.module_utils import basic as _basic
                if getattr(_basic, "_PARSED_MODULE_ARGS", None) is None:
                    _basic._PARSED_MODULE_ARGS = {}

            def _record_module_result(self, o):
                module._raw_result = o

        args = copy.deepcopy(self._task.args)
        self._update_module_args(self._task.action, args, task_vars or {})
        # No device socket: an offline run must never reach the persistent connection (a
        # socket path would let a stray connection lookup log in to the device).
        args["_ansible_socket"] = None
        _OfflineModule.params = args
        module.AnsibleModule = _OfflineModule
        return self._exec_module(module)
