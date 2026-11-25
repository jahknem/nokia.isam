# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the ntp_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # The device creates the entry with the ONT and removes it with the ONT. Live write
        # DS-LIN-TEST-01 2026-11-25: 'configure ntp ont <ont>' before the ONT exists is accepted
        # and does nothing (written too early, it is silently lost); 'configure ntp no ont <ont>'
        # is accepted and removes nothing.
        "config": {
            "identity": "ont_id", "object": "ont",
            "created_with": [{"prefix": None, "object": "ont", "default": {}}],
        },
    },
}
