# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the ntp_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # Live-verified on DS-LIN-TEST-01 (R6.2): the device creates the entry itself with the ONT.
        "config": {
            "identity": "ont_id", "object": "ont",
            "created_with": [{"prefix": None, "object": "ont", "default": {}}],
        },
    },
}
