# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_system_security family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": ("general", "default_profile", "radius_auth_super_user", "password", "ssh", "filetransfer"),
    "sections": {
        "operators": {"identity": "name", "scope": "device_global"},
        "profiles": {"identity": "name", "scope": "device_global"},
        "snmp_communities": {"identity": "name", "scope": "device_global"},
        "snmp_views": {"identity": "name", "scope": "device_global"},
        "snmp_managers": {"identity": "name", "scope": "device_global"},
        "snmp_notify_profiles": {"identity": "name", "scope": "device_global"},
        "radius_auth_servers": {"identity": "name", "scope": "device_global"},
        "radius_policies": {"identity": "name", "scope": "device_global"},
        "radius_dyn_auth_clients": {"identity": "name", "scope": "device_global"},
        "snmp_notify_views": {"identity": "name", "scope": "device_global"},
        "domains": {"identity": "name", "scope": "device_global"},
        # NT-slot security settings only address nt-a/nt-b (Security Commands 16.42).
        "slots": {"identity": "slot", "object": "card"},
        "ssh.sftp_users": {"identity": "name", "scope": "device_global"},
        "filetransfer.servers": {"identity": "server", "scope": "device_global"},
        "peripheral_mgnt.mac_filters": {"identity": "index", "scope": "device_global"},
        # 802.1X authenticator ports use the user-port identity superset; ONT
        # voip/vuni/LLId and ng2 variants stay explicit per-instance gaps.
        "pae.ports": {"identity": "port", "object": "user_port"},
    },
}
