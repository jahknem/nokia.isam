# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_traps family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "definitions": {"identity": "name", "scope": "device_global"},
        "managers": {"identity": "address", "scope": "device_global"},
        "v6managers": {"identity": "ipv6address", "scope": "device_global"},
    },
}
