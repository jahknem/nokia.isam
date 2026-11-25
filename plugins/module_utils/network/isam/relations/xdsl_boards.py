# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the xdsl_boards family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "boards": {
            "identity": "board_id",
            "object": "lt_card",
            "references": {"dpbo_profile": "xdsl_profiles.dpbo_profiles", "vce_profile": "xdsl_profiles.vce_profiles"},
        },
        "vp_boards": {"identity": "vp_board_id", "object": "lt_card", "references": {"vce_profile": "xdsl_profiles.vce_profiles"}},
    },
}
