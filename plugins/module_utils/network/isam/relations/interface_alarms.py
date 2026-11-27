# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the interface_alarms family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "read_scope": "whole_node",
    "sections": {
        # Whole-node catalog family: per-instance, but the firmware exposes no single-instance
        # read, so the targeted read is the whole node (device-wide settings, no physical owner).
        "config": {"identity": "name", "scope": "device_global"},
    },
}
