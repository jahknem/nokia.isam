# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the ethernet_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # The device creates the entry with the ONT slot (live write DS-LIN-TEST-01 2026-11-25,
        # scratch ONT 1/1/6/7/10); 'configure ethernet ont' before the slot is refused (invalid token).
        "config": {
            "identity": "uni_idx", "object": "uni",
            "created_with": [{"prefix": None, "object": "uni", "default": None}],
        },
    },
}
