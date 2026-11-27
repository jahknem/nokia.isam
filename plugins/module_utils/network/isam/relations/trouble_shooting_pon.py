# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the trouble_shooting_pon family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "interfaces": {"identity": "name", "object": "pon"},
        # Exists with every PON: 'info configure trouble-shooting pon statistics threshold interface
        # <pon> flat detail' prints "no bw-th-up no bw-th-dn" for PONs never configured there, also
        # the empty PON 1/1/7/16 (DS-LIN-TEST-01, 2026-11-26); flat prints nothing.
        "threshold.interfaces": {"identity": "name", "object": "pon",
                                 "created_with": [{"prefix": None, "object": "pon", "default": {}}]},
    },
}
