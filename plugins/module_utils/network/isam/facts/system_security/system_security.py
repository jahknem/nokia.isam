# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    requested_identities,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import (
    Isam_system_securityArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    Isam_system_securityTemplate,
    register_embedded_secrets,
)

_SSH_COMMAND = "info configure system security ssh flat"
_SSH_PREFIX = "configure system security ssh "

# section -> single-instance read command (identity per TARGETED_GATHER); the SNMP
# views are selected by name only (all subtrees of the view are read)
_TARGETED = {
    "operators": "info configure system security operator %s flat",
    "profiles": "info configure system security profile %s flat",
    "snmp_communities": "info configure system security snmp community %s flat",
    "snmp_views": "info configure system security snmp view %s flat",
    "snmp_managers": "info configure system security snmp manager %s flat",
    "snmp_notify_profiles": "info configure system security snmp notify-profile %s flat",
    "radius_auth_servers": "info configure system security radius auth-server %s flat",
    "radius_policies": "info configure system security radius policy %s flat",
    "radius_dyn_auth_clients": "info configure system security radius dyn-auth-client %s flat",
    "snmp_notify_views": "info configure system security snmp notify-view %s flat",
    "domains": "info configure system security domain %s flat",
    "slots": "info configure system security slot %s flat",
    # The device rejects 'ssh sftp-user <name>' (invalid token): read the small ssh
    # node and keep only the named users' lines (get_config -> _only_sftp_users).
    "ssh.sftp_users": lambda name: [_SSH_COMMAND],
    "filetransfer.servers": "info configure system security filetransfer server %s flat",
    "peripheral_mgnt.mac_filters": "info configure system security peripheral-mgnt mac-filter %s flat",
    # one 802.1X port is spread over three nodes
    "pae.ports": lambda port: [
        "info configure system security pae port %s flat" % port,
        "info configure system security pae authenticator %s flat" % port,
        "info configure system security pae ext-authenticator %s flat" % port,
    ],
}


def _is_sftp_user_line(line, user):
    wanted = "%ssftp-user %s" % (_SSH_PREFIX, user)
    line = line.strip()
    return line == wanted or line.startswith(wanted + " ")


def _has_sftp_user(reply, user):
    return any(_is_sftp_user_line(line, user) for line in str(reply or "").splitlines())


def _only_sftp_users(data, users):
    """Of the ssh node's lines (read for targeted sftp users), keep the named users only.

    Lines of other targeted sections pass unchanged.
    """
    kept = [line for line in str(data or "").splitlines()
            if not line.strip().startswith(_SSH_PREFIX)
            or any(_is_sftp_user_line(line, user) for user in users)]
    return "\n".join(kept) + ("\n" if kept else "")


class Isam_system_securityFacts(object):
    """The isam_system_security facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_system_securityArgs.argument_spec

    def get_config(self, connection):
        data = get_targeted_config(self._module, connection, "isam_system_security",
                                   "info configure system security flat", _TARGETED,
                                   # sftp users are read from the shared ssh node: a user is
                                   # present when its line is there, otherwise unknown.
                                   instance_checks={"ssh.sftp_users": _has_sftp_user})
        users = requested_identities(self._module, "isam_system_security", "ssh.sftp_users")
        if users and self._module.params.get("state") == "gathered":
            data = _only_sftp_users(data, users)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        parser = Isam_system_securityTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = parser.parse()
        register_embedded_secrets(self._module, objs)

        ansible_facts["ansible_network_resources"].pop("isam_system_security", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["isam_system_security"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
