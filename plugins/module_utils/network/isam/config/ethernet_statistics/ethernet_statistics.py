# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule


class Isam_ethernet_statistics(IsamActionModule):
    """Clear Ethernet interface counters (CLI guide 218.3).

    ``admin ethernet statistics <stats-index> clear-stats`` clears the counters of an
    ethernet-like interface. ``clear-stats`` is the operation: a bare
    ``admin ethernet statistics <stats-index>`` only navigates to the interface in the
    admin hierarchy and performs no action, so it is rejected rather than reported as a
    change. The stats-index is ``rack/shelf/slot/port``, ``lt:rack/shelf/slot`` or
    ``lt-link:rack/shelf/slot/port``.
    """

    def build_commands(self):
        commands = []
        for entry in self._module.params.get("config") or []:
            if not entry.get("clear_stats"):
                self._module.fail_json(
                    msg="An explicit operation is required: clear_stats must be true. "
                    "A bare admin ethernet statistics <port> only navigates to the "
                    "interface and performs no action.",
                    port=entry.get("port"),
                )
            port = self.validate_identifier(entry["port"], "port")
            commands.append("admin ethernet statistics %s clear-stats" % port)
        return commands
