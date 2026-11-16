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
    """Render ISAM removal templates without netcommon's command prefix.

    netcommon negates a parser without ``remval`` by prefixing the whole command
    with ``no``. ``no configure ...`` is never valid ISAM CLI, so:

    * ``remval`` renders the removal form as is;
    * ``no_remval: True`` marks an attribute without a removal form in the CLI
      (e.g. ``oper-weight``): removing it renders nothing, the value goes away
      with its parent object;
    Other resources retain netcommon's existing rendering behavior.
    """
    if self.__class__.__module__.startswith("ansible_collections.nokia.isam.") and not negate:
        parser = self._tmplt.get_parser(tmplt) if hasattr(self._tmplt, "get_parser") else {}
        if parser.get("read_only"):
            # Derived by the device; never set (``read_only: True`` in the template).
            return
    if negate and self.__class__.__module__.startswith(
        "ansible_collections.nokia.isam."
    ):
        parser = self._tmplt.get_parser(tmplt)
        if parser.get("read_only"):
            return
        remval = parser.get("remval")
        if remval:
            command = self._tmplt._render(remval, data, False)
            if command:
                self.commands.extend(command if isinstance(command, list) else [command])
            return
        if parser.get("no_remval"):
            self._module.warn(
                "%s has no standalone removal form in ISAM CLI; it is retained until its parent object is removed" % tmplt
            )
            return
        before = len(self.commands)
        _resource_module_addcmd(self, data, tmplt, negate)
        invalid = [command for command in self.commands[before:] if command.startswith("no configure ")]
        if invalid:
            # netcommon's fallback: never valid ISAM CLI. Fail instead of sending it.
            del self.commands[before:]
            self._module.fail_json(
                msg="%s: parser %s has no removal form; refusing to render %r" % (self.__class__.__name__, tmplt, invalid[0])
            )
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
