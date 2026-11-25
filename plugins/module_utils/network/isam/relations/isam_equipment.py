# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_equipment family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "appliques": {"identity": "id", "object": "applique"},
        "protection_groups": {"identity": "id", "scope": "device_global"},
        "shelves": {"identity": "id", "object": "shelf"},
        "slots": {"identity": "id", "object": "card"},
        "diagnostics_sfp": {"identity": "id", "object": "transceiver"},
        "protection_elements": {"identity": "id", "scope": "device_global"},
        "racks": {"identity": "id", "object": "rack"},
        "external_link_assigns": {"identity": "id", "scope": "device_global"},
        "external_link_hosts": {"identity": "id", "scope": "device_global"},
    },
}
