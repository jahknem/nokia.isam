# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the system family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": (
        "id", "security", "sntp", "syslog", "loop_id_syntax", "relay_id_syntax", "max_lt_link_speed", "transaction",
        "sync_if_timing.mode", "sync_if_timing.source", "sync_if_timing.revert", "sync_if_timing.wait_time",
        "sync_if_timing.output_ql_thresh", "sync_if_timing.ssmout_en_bits", "sync_if_timing.ssmout_ceiling",
        "sync_if_timing.ais_sensitivity", "sync_if_timing.bits", "sync_if_timing.bits_bind",
        "sync_if_timing.force_reference", "sync_if_timing.ref_order",
    ),
    "sections": {
        "sntp.servers": {"identity": "ip_address", "scope": "device_global"},
        "syslog.destinations": {"identity": "name", "scope": "device_global"},
        "syslog.routes": {"identity": "destination", "scope": "device_global"},
        "sync_if_timing.ssm": {"identity": "reference", "scope": "device_global"},
        "sync_if_timing.synce": {"identity": "reference", "scope": "device_global"},
        # SSM output per SyncE faceplate port: nt-a/nt-b/ntio cage identities
        # (System Commands 15.35). The active-NT alias (nt:...) has no fixed owner.
        "sync_if_timing.ssmout_synce": {"identity": "port", "object": "transceiver"},
    },
}
