# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule


class Isam_bridge_learned_mac(IsamActionModule):
    """Remove a learned unicast MAC address from a bridge VLAN port (CLI guide 219.2).

    ``admin bridge learned-unicast-mac <vlan-port> unicast-mac-address <mac> delete``
    removes one learned unicast MAC address. ``delete`` is the operation: a bare
    ``admin bridge learned-unicast-mac <vlan-port> unicast-mac-address <mac>`` only
    navigates to the entry in the admin hierarchy and performs no action, so it is
    rejected rather than reported as a change. The vlan-port is a ``vlan-port:...`` path
    and the MAC is six colon-separated hex bytes (aa:bb:cc:dd:ee:ff).
    """

    def build_commands(self):
        commands = []
        for entry in self._module.params.get("config") or []:
            if not entry.get("delete"):
                self._module.fail_json(
                    msg="An explicit operation is required: delete must be true. "
                    "A bare admin bridge learned-unicast-mac <vlan-port> unicast-mac-address "
                    "<mac> only navigates to the entry and performs no action.",
                    vlan_port=entry.get("vlan_port"),
                )
            vlan_port = self.validate_identifier(entry["vlan_port"], "vlan_port")
            mac = self.validate_mac(entry["mac_address"], "mac_address")
            commands.append(
                "admin bridge learned-unicast-mac %s unicast-mac-address %s delete" % (vlan_port, mac)
            )
        return commands
