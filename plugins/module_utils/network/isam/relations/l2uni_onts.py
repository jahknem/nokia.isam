# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the l2uni_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "performance_monitor": {"identity": "uni_idx", "object": "uni"},
        "tc_layer_threshold": {"identity": "uni_idx", "object": "uni"},
    },
}
