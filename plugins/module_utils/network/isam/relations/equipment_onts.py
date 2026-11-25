# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the equipment_onts family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # 'configure equipment ont ( no interface (ont-idx) ) | ( interface (ont-idx) ... )' creates
        # the ONT, '( no slot ... ) | ( slot ... )' its slot. The UNIs of a slot have no creating
        # command: they exist with the slot.
        "interfaces": {"identity": "ont_idx", "object": "ont", "creates": True},
        "slots": {
            "identity": "ont_slot_idx", "object": "ont_slot", "creates": True,
            "requires": [
                {"section": "qos_interfaces.config", "kind": "ont",
                 "evidence": "live write DS-LIN-TEST-01 2026-11-25: ds-queue-sharing of the ONT can neither be "
                             "enabled nor disabled once an ONT card is provisioned (QOS MGT errors 58, 59)"},
            ],
        },
        "sw_ctrls": {"identity": "sw_ctrl_id", "scope": "device_global"},
        "loops": {"identity": "ont_idx", "object": "ont"},
        "pm_collects": {"identity": "ont_idx", "object": "ont"},
    },
}
