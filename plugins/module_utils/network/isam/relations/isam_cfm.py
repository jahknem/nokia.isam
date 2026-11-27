# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_cfm family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "domains": {"identity": "domain_index", "scope": "device_global"},
        "y1731pm": {"identity": ["domain_index", "association", "mep", "session_id"], "scope": "device_global"},
    },
}
