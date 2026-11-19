# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule


class Isam_dhcp_relay_port_stats(IsamActionModule):
    """Clear DHCP relay user-port statistics (CLI guide 222.2).

    ``admin dhcp-relay port-stats <vlan-port> clear-statistics`` clears the DHCP relay
    statistics of an IP user interface / VLAN port. ``clear-statistics`` is the operation:
    a bare ``admin dhcp-relay port-stats <vlan-port>`` only navigates to the port in the
    admin hierarchy and performs no action, so it is rejected rather than reported as a
    change. The vlan-port is ``rack/shelf/slot/port[:vpi:vci]`` or a ``vlan:...`` path.
    """

    def build_commands(self):
        commands = []
        for entry in self._module.params.get("config") or []:
            if not entry.get("clear_statistics"):
                self._module.fail_json(
                    msg="An explicit operation is required: clear_statistics must be true. "
                    "A bare admin dhcp-relay port-stats <port> only navigates to the "
                    "port and performs no action.",
                    port=entry.get("port"),
                )
            port = self.validate_identifier(entry["port"], "port")
            commands.append("admin dhcp-relay port-stats %s clear-statistics" % port)
        return commands
