# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the xdsl_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # The device creates the entry with every ONT, GPON/Ethernet ones included (live read
        # DS-LIN-TEST-01 2026-11-27: ONT 1/1/5/1/3 'flat detail' prints "no dpbo-profile";
        # a free ONT index answers the header only, also with detail).
        "config": {
            "identity": "ont_idx", "object": "ont", "references": {"dpbo_profile": "xdsl_profiles.dpbo_profiles"},
            "created_with": [{"prefix": None, "object": "ont", "default": {}}],
        },
    },
}
