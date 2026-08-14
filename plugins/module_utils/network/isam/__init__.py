from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)


_resource_module_addcmd = ResourceModule.addcmd


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


ResourceModule.addcmd = _isam_addcmd
