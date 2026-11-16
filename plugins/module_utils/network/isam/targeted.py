# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Targeted gathering: which resources read single instances, by which identity field.

When ``config`` names instances, ``state: gathered`` reads only those instances (and
``merged``/``replaced``/``deleted`` compare against only those). Without ``config`` the
whole resource is read, as before. Only identity fields matter for the selection; absent
instances are simply missing from the result.

Pure data without imports, so tools outside Ansible can read it.
resource (facts name) -> {list in config ("config": config itself is the list): identity field}
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

TARGETED_GATHER = {
    "ani_onts": {"config": "ont_idx"},
    "bridges": {"port": "port"},
    "efm_oam_interface": {"config": "name"},
    "equipment_onts": {"interfaces": "ont_idx", "slots": "ont_slot_idx"},
    "ethernet_onts": {"config": "uni_idx"},
    "interfaces": {"config": "name"},
    "isam_arp_relay": {"config": "name"},
    "isam_dhcp_relay": {"config": "name"},
    "ntp_onts": {"config": "ont_id"},
    "pon_interfaces": {"config": "name"},
    "qos_interfaces": {"config": "name"},
}
