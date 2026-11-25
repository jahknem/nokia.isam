# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the xdsl_profiles family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "dpbo_profiles": {"identity": "id", "scope": "shared_profile"},
        "service_profiles": {"identity": "id", "scope": "shared_profile"},
        "spectrum_profiles": {"identity": "id", "scope": "shared_profile"},
        "vce_profiles": {"identity": "id", "scope": "shared_profile"},
        "vect_profiles": {"identity": "id", "scope": "shared_profile"},
    },
}
