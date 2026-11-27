# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the alarm family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": ("log", "delta_log"),
    "sections": {
        "custom_profiles": {"identity": "name", "scope": "device_global"},
        "entries": {"identity": "index", "scope": "device_global"},
        "filters": {"identity": ["fltr_type", "filterid"], "scope": "device_global"},
        "hgutr069_custs": {"identity": "alarm_id", "scope": "device_global"},
    },
}
