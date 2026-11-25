# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the ani_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # The device creates the entry with the ONT and removes it with the ONT (live write
        # DS-LIN-TEST-01 2026-11-25). Before the ONT exists the command is refused (invalid token).
        "config": {
            "identity": "ont_idx", "object": "ont",
            "created_with": [{"prefix": None, "object": "ont", "default": {"tca_thresh": True}}],
        },
    },
}
