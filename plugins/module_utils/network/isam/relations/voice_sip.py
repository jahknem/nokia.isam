# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the voice_sip family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": ("statistics",),
    "sections": {
        "cas_nsm_prof": {"identity": "name", "scope": "shared_profile"},
        "lineid_syn_prof": {"identity": "name", "scope": "shared_profile"},
        "redundancy": {"identity": "name", "scope": "shared_profile"},
        "redundancy_cmd": {"identity": "name", "scope": "shared_profile"},
        "register": {"identity": "name", "scope": "shared_profile"},
        "vsp": {"identity": "name", "scope": "shared_profile"},
    },
}
