# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the mcast_control family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": ("mcast_svc_context",),
    "sections": {
        "packages": {"identity": "index", "scope": "device_global"},
    },
}
