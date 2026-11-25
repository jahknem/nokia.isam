# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the epon_interfaces family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # EPON interface configuration is addressed by the PON index
        # (rack/shelf/slot/PonId, Epon Configuration Commands 69.2).
        "config": {"identity": "name", "object": "pon"},
    },
}
