# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the xstp family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "settings": ("general",),
    "sections": {
        # STP port config is addressed by the aggregate's interface index (MSTP
        # Commands 55.5) and belongs to the port object, not the bridge port:
        # live counterexample xstp 1/1/8/6 has a LAG but no bridge-port interface.
        "ports": {"identity": "port", "object": "port_layer"},
    },
}
