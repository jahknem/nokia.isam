# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the xdsl_lines family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "config": {
            "identity": "name",
            "object": "xdsl_line",
            "references": {
                "service_profile": "xdsl_profiles.service_profiles",
                "spectrum_profile": "xdsl_profiles.spectrum_profiles",
                "dpbo_profile": "xdsl_profiles.dpbo_profiles",
                "vect_profile": "xdsl_profiles.vect_profiles",
            },
        },
    },
}
