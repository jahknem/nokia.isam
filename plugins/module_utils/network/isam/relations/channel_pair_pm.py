# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the channel_pair_pm family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # NGPON2 channel pairs are wavelength interfaces on the LT slot
        # (rack/shelf/slot/ChannelPairId, Channel Pair Commands 68.4). Channel-group
        # membership is a logical association, not physical containment.
        "config": {"identity": "name", "object": "channel_pair"},
    },
}
