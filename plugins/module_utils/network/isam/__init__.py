from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    compact_cli_commands,
)


_resource_module_addcmd = ResourceModule.addcmd
_resource_module_result = ResourceModule.result.fget
_resource_module_run_commands = ResourceModule.run_commands
ResourceModule.COMPACT_COMMAND_SCOPES = ()


def _compact_resource_commands(resource):
    scopes = resource.COMPACT_COMMAND_SCOPES
    if scopes:
        resource.commands[:] = compact_cli_commands(resource.commands, scopes)


def _isam_addcmd(self, data, tmplt, negate=False):
    """Render ISAM removal templates without netcommon's command prefix."""
    if negate and self.__class__.__module__.startswith(
        "ansible_collections.nokia.isam."
    ):
        remval = self._tmplt.get_parser(tmplt).get("remval")
        if remval:
            command = self._tmplt._render(remval, data, False)
            if command:
                self.commands.extend(command if isinstance(command, list) else [command])
            return
    _resource_module_addcmd(self, data, tmplt, negate)


def _isam_result(self):
    """Compact fully generated commands before exposing rendered output."""
    _compact_resource_commands(self)
    return _resource_module_result(self)


def _isam_run_commands(self):
    """Compact fully generated commands immediately before device execution."""
    _compact_resource_commands(self)
    return _resource_module_run_commands(self)


ResourceModule.addcmd = _isam_addcmd
ResourceModule.result = property(_isam_result)
ResourceModule.run_commands = _isam_run_commands
