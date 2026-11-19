# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule


class Isam_security_ext_authenticator(IsamActionModule):
    """Run the 802.1X port authentication administrative action (CLI guide 227.2).

    ``admin security ext-authenticator <port> clear-statistics`` clears the port's
    non-accounting authentication statistics. ``clear-statistics`` is the operation:
    a bare ``admin security ext-authenticator <port>`` only navigates to the port in
    the admin hierarchy and performs no action, so it is rejected rather than reported
    as a change.
    """

    def build_commands(self):
        commands = []
        for entry in self._module.params.get("config") or []:
            if not entry.get("clear_statistics"):
                self._module.fail_json(
                    msg="An explicit operation is required: clear_statistics must be true. "
                    "A bare admin security ext-authenticator <port> only navigates to the "
                    "port and performs no action.",
                    port=entry.get("port"),
                )
            commands.append("admin security ext-authenticator %s clear-statistics" % entry["port"])
        return commands
