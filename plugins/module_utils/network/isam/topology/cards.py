# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""What a line card of each planned type contains and which card sections apply.

Pure data without imports. A refresh of a card (or of a PON/ONT below it) reads the
planned type of the owning card and of the NT slots first ("isam_equipment" slots);
these rules then decide, per type:

  children   the child kinds the card has, with the number the device creates with the
             card (a discovered count that differs is a gap). A child kind of the card
             not listed here is not applicable to this type: it is never enumerated.
  sections   the card-level sections ("resource.section") that apply to the card; the
             others are not applicable.
  created    the card-level sections whose entry the device creates with the card: a
             successful read that shows nothing (flat omits defaults) means defaults.
  pon_not_applicable / port sections not applicable to the card's ports.

A planned type not listed here is unknown: nothing is assumed, the refresh reads every
section as without rules and names the gap "card_type_unknown".

Evidence (read-only unless stated): a survey of the production fleet, 2026-11-26
(planned LT types fglt-d, ndlt-f, fglt-b, ndps-c, nelt-b; NT nant-e, fant-f, nant-a);
per-type reads on DS-LIN-TEST-01 and six production MSANs covering every planned card
and NT type.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Card-level sections (refresh.applicable_sections("card")).
EQUIPMENT = "isam_equipment.slots"
QOS = "qos_global.line_cards"
XDSL_BOARD = "xdsl_boards.boards"
VP_BOARD = "xdsl_boards.vp_boards"
BONDING_BOARD = "xdsl_bonding.boards"
IPV6 = "isam_ipv6_antispoofing_slot.config"
NT_SECURITY = "isam_system_security.slots"  # "NT slot index (nt-a | nt-b)" (guide 16.42): never an LT card
# Transceiver sections.
DIAGNOSTICS = "isam_equipment.diagnostics_sfp"
# SSM output takes NT and NT-applique ports only (nt-a:xfp:<n>, ntio-1:sfp:<n>, ...; guide
# 15.35); every lt:<card>:sfp:<n> answers "invalid token" (DS-LIN-TEST-01 2026-11-26).
LT_TRANSCEIVER_NOT_APPLICABLE = ("system.sync_if_timing.ssmout_synce",)

_GPON = {
    "class": "gpon",
    # 16 pon:, 16 cages (operational-mode gpon), 16 SFP cages in the transceiver inventory.
    "children": {"pon": 16, "cage": 16, "transceiver": 16},
    # 'qos global lt:<card> flat detail' prints the default line; flat prints nothing.
    "sections": (EQUIPMENT, QOS, IPV6),
    "created": (QOS,),
    # 'equipment diagnostics sfp lt:<card>:sfp:<n> flat detail' prints the default line.
    "transceiver_created": (DIAGNOSTICS,),
    # EPON on a GPON board: 'info configure epon interface <pon> flat' answers
    # "Error : not support for gpon board." (L6GPAA62.713, FANT-F) or "invalid token"
    # (no epon node, L6GPAA62.652). Channel pairs are NG-PON2 only (operational-mode
    # gpon on every GPON card of the fleet; the node is "invalid token" on 62.652).
    "pon_not_applicable": ("epon_interfaces.config",),
}

# Port and VLAN-port sections the device refuses on cards other than GPON.
_NOT_GPON = (
    # 'pppoel2 statistics vlan-port:<port>:<vlan>' -> "PPPOERELAY MGNT error 6 : Only valid
    # for GPON LT card" (NELT-B VLAN ports, DS-LIN-TEST-01 2026-11-26).
    "pppoel2_statistics.config",
)

CARD_TYPES = {
    "fglt-b": dict(_GPON),
    "fglt-d": dict(_GPON),
    "ndlt-f": {
        "class": "xdsl",
        # 48 xdsl-line:, 48 bonding: and 48 ethernet-line: (the EFM/PTM facet of each line,
        # stack: bridge-port -> ethernet-line -> xdsl-channel -> xdsl-line), 1 SFP.
        "children": {"xdsl_line": 48, "bonding_group": 48, "transceiver": 1},
        # 'xdsl board <card> flat detail' and 'xdsl-bonding board <card> flat detail' print
        # the default line; 'xdsl vp-board <card>' is header-only here as on every non-NDPS
        # card (indistinguishable from "no entry": the rule, not a read, decides).
        "sections": (EQUIPMENT, QOS, XDSL_BOARD, BONDING_BOARD, IPV6),
        "created": (QOS, XDSL_BOARD, BONDING_BOARD),
        "below_not_applicable": _NOT_GPON,
        # 'diagnostics sfp lt:<card>:sfp:1 flat detail' is header-only: no entry.
        "transceiver_not_applicable": (DIAGNOSTICS,),
    },
    "nelt-b": {
        "class": "ethernet",
        # 36 ethernet-line:, 36 la-group: (one per port, created with the card; live write
        # 2026-11-26), 36 SFP. 'interface cage' answers "Cage mode retrieval is only allowed
        # for GPON boards".
        "children": {"ethernet_port": 36, "lag": 36, "transceiver": 36},
        "sections": (EQUIPMENT, QOS, IPV6),
        "created": (QOS,),
        "transceiver_created": (DIAGNOSTICS,),
        # 'l2cp user-port <port>' -> "The specified interface index is invalid".
        "below_not_applicable": _NOT_GPON + ("l2cp_user_port.config",),
    },
    "ndps-c": {
        "class": "vectoring",
        # Vectoring processor: no user ports; 4 SFP (vp links). 'qos global lt:<card> flat
        # detail' is header-only (as for an unplanned slot): no QoS line-card entry.
        "children": {"transceiver": 4},
        "sections": (EQUIPMENT, XDSL_BOARD, VP_BOARD, IPV6),
        "created": (XDSL_BOARD, VP_BOARD),
        "transceiver_not_applicable": (DIAGNOSTICS,),  # header-only with detail, all 4
    },
}

# Rules that depend on the system (the NT), not on the line card.
NT_TYPES = {
    # 'ipv6-antispoofing slot <card>' answers "L2USERIPV6 MGNT error 14 : This configuration
    # is NOT supported on this board" for every LT type and for unplanned slots under NANT-E
    # (DS-LIN-TEST-01 and two production MSANs) and NANT-A (one production MSAN); under
    # FANT-F (one production MSAN) it shows the slot with defaults.
    "nant-e": {"not_applicable": (IPV6,)},
    "nant-a": {"not_applicable": (IPV6,)},
    "fant-f": {"not_applicable": ()},
}


def card_of(kind, identity):
    """'lt:<rack>/<shelf>/<slot>' of the line card that holds the object, or None."""
    if kind == "card":
        return identity if isinstance(identity, str) and identity.startswith("lt:") else None
    address = identity[1] if isinstance(identity, (list, tuple)) else identity
    if not isinstance(address, str):
        return None
    if address.startswith("lt:"):  # cages and transceivers: lt:<card>:cage:<n>, lt:<card>:sfp:<n>
        return address.split(":")[0] + ":" + address.split(":")[1]
    if ":" in address:
        return None
    parts = address.split("/")
    return "lt:" + "/".join(parts[:3]) if len(parts) >= 4 else None
