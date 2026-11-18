# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Base class of the nokia.isam resource modules (config classes).

netcommon's ResourceModule with the ISAM CLI adaptations:

* removal: a parser's ``remval`` renders the removal form as is; ``no_remval: True``
  marks an attribute without removal form (nothing is rendered, with a warning);
  ``read_only: True`` marks a value derived by the device (never rendered). netcommon's
  fallback, prefixing the whole command with ``no``, is never valid ISAM CLI and fails.
* rendered: an explicit ``False`` renders the ``no`` form; netcommon's compare()
  skips False when there is no device value, i.e. always in ``rendered``.
* compaction: ``COMPACT_COMMAND_SCOPES`` packs the per-attribute commands of one CLI
  node into one command (the form the device prints), before commands are shown or sent.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    get_from_dict,
    to_list,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    compact_cli_commands,
)


class IsamResourceModule(ResourceModule):
    """ResourceModule for ISAM CLI resources (see the module docstring)."""

    # Regexes with named groups ``scope`` and ``suffix`` (see compact_cli_commands).
    COMPACT_COMMAND_SCOPES = ()

    def compare(self, parsers, want=None, have=None):
        if self.state != "rendered":
            return super(IsamResourceModule, self).compare(parsers, want=want, have=have)
        want = self.want if want is None else want
        for parser in to_list(parsers):
            compval = self._tmplt.get_parser(parser).get("compval") or parser
            if get_from_dict(want, compval) is False:
                self.addcmd(want, parser, True)
            else:
                super(IsamResourceModule, self).compare([parser], want=want, have=have)

    def addcmd(self, data, tmplt, negate=False):
        parser = self._tmplt.get_parser(tmplt) if hasattr(self._tmplt, "get_parser") else {}
        if parser.get("read_only"):
            return
        if not negate:
            super(IsamResourceModule, self).addcmd(data, tmplt, negate)
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
        super(IsamResourceModule, self).addcmd(data, tmplt, negate)
        invalid = [command for command in self.commands[before:] if command.startswith("no configure ")]
        if invalid:
            del self.commands[before:]
            self._module.fail_json(
                msg="%s: parser %s has no removal form; refusing to render %r" % (self.__class__.__name__, tmplt, invalid[0])
            )

    def _compact(self):
        if self.COMPACT_COMMAND_SCOPES:
            self.commands[:] = compact_cli_commands(self.commands, self.COMPACT_COMMAND_SCOPES)

    @property
    def result(self):
        self._compact()
        return super(IsamResourceModule, self).result

    def run_commands(self):
        self._compact()
        return super(IsamResourceModule, self).run_commands()
