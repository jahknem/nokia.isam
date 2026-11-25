"""Explicit identity syntax, not CLI-tree or string-prefix ownership guesses."""

import re


class UnknownIdentity(ValueError):
    """No supported, unambiguous device relationship for this identity."""


DEPTHS = {"rack": 1, "shelf": 2, "pon": 4, "ont": 5, "ont_slot": 6,
          "uni": 7, "xdsl_line": 4, "ethernet_port": 4, "bonding_group": 4, "lag": 4,
          "channel_pair": 4}

# Documented transceiver cage types (Equipment Status Commands, transceiver
# inventory / diagnostics sfp position syntax).
CAGE_TYPES = ("sfp", "xfp", "qsfp", "cfp", "sfp1", "sfp2", "xfp1", "xfp2")

# Optical IHUB port forms observed through `show port` on FANT-F/FANT-G.
# This is a different namespace from access-side `show interface port`, even
# when an equipment transceiver position has exactly the same spelling.
IHUB_OPTICAL_TYPES = ("sfp", "xfp")


def _valid_vlan(value):
    return re.fullmatch(r"[0-9]+", value) is not None and 1 <= int(value) <= 4094


# Interface kinds a bridge port can stack on. Live-verified across the whole
# lab device (show interface stack, 1103 rows): bridge ports sit on la-group
# when a LAG exists at the address, otherwise on the line's ethernet facet
# (ethernet-line:, the EFM alias of an xDSL line), and on uni: for UNIs.
# Bonding groups never carry bridge ports (bonding: lower = no-interface).
BRIDGE_PARENT_KINDS = ("uni", "xdsl_line", "ethernet_port", "lag")


def candidate_owners(decoder, value, known_ports=()):
    """Known objects that could own an ambiguous bare service-port identity.

    Returns the candidate ``(kind, identity)`` list when several object kinds
    share one numeric address (line / Ethernet port / bonding group / LAG).
    Ownership is then reported as unresolved with these candidates, never
    guessed. Empty when the identity is not a bare LT port or has no claimant.
    """
    if decoder == "qos_tca" and isinstance(value, (tuple, list)) and len(value) == 2:
        return candidate_owners("qos_interface", value[0], known_ports)
    if decoder in ("user_port", "qos_interface") and isinstance(value, str) and numeric(value, 4):
        candidates = sorted((kind, ident) for kind, ident in known_ports
                            if ident == value and kind in _bare_port_kinds(decoder))
        return _qos_owner(candidates) if decoder == "qos_interface" else candidates
    return []


def _bare_port_kinds(decoder):
    """Object kinds a bare four-part port address can name for this decoder.

    A QoS interface index is "the physical port or la-group of a user-port" (device help),
    and the device accepts only the bare form for QoS (xdsl-line:, bonding:, la-group: are
    invalid tokens; DS-LIN-TEST-01, 2026-11-25). A bare QoS address is therefore never a
    bonding group, and where a LAG exists it is the LAG (see _qos_owner). Other user-port
    families keep every candidate.
    """
    if decoder == "qos_interface":
        return ("xdsl_line", "ethernet_port", "lag")
    return ("xdsl_line", "ethernet_port", "bonding_group", "lag")


def _qos_owner(candidates):
    """The owner of a bare QoS index among the objects known at that address.

    Where a LAG exists at the address, the QoS belongs to the LAG, not to the Ethernet
    port: live write DS-LIN-TEST-01 2026-11-25, port 1/1/8/6 moved into LAG 1/1/8/5 and
    back. While it was a member, LAG 1/1/8/5's QoS bandwidth doubled (2 Gbit/s), the entry
    1/1/8/6 dropped to 0 and a QoS write on 1/1/8/6 was refused with "QOS MGT error 216:
    QoS cannot be configured on the lag without physical port". The device keeps a LAG
    for every Ethernet port, so on an Ethernet card the bare QoS index is the LAG.
    """
    lags = [candidate for candidate in candidates if candidate[0] == "lag"]
    return lags if lags else candidates


def bridge_owner(value, known_ports=()):
    """The port object a bridge port at this address stacks on.

    This is the documented + live-verified attachment rule, not a preference:
    a LAG at the address owns the bridge port; otherwise the single line object
    does. Ambiguous or unknown addresses remain gaps.
    """
    if numeric(value, 7):
        return "uni", value
    if numeric(value, 4):
        if ("lag", value) in known_ports:
            return "lag", value
        candidates = [(kind, ident) for kind, ident in known_ports
                      if ident == value and kind in ("xdsl_line", "ethernet_port")]
        if len(candidates) == 1:
            return candidates[0]
    raise UnknownIdentity("No evidenced bridge-port owner for %s" % value)


def _vlan_suffix(rest):
    """Unstacked ``<vlan>`` or ``stacked:<svlan>:<cvlan>``; None when malformed.

    ATM vpi:vci variants are intentionally not modeled here; they remain
    explicit ownership gaps until their port identity is evidenced.
    """
    if ":stacked:" in rest:
        port, stacked = rest.split(":stacked:", 1)
        svlan, _, cvlan = stacked.partition(":")
        if _valid_vlan(svlan) and _valid_vlan(cvlan):
            return port, "stacked:%s:%s" % (svlan, cvlan)
        return None
    port, _, vlan = rest.rpartition(":")
    if port and _valid_vlan(vlan):
        return port, vlan
    return None


def numeric(value, depth):
    return isinstance(value, str) and re.fullmatch(r"[0-9]+(?:/[0-9]+){%d}" % (depth - 1), value) is not None


def decode(decoder, value, known_ports=()):
    """Return (kind, identity); ambiguous bare LT port IDs need typed evidence.

    known_ports is a set of exact (kind, identity) pairs discovered from typed
    resources, never a board-name/port-count heuristic.
    """
    if decoder == "qos_profile":
        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, str) and v for v in value):
            return decoder, value
    elif decoder == "qos_tca":
        if isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], int) and not isinstance(value[1], bool):
            return decode("qos_interface", value[0], known_ports)
    elif decoder in DEPTHS and numeric(value, DEPTHS[decoder]):
        return decoder, value
    elif decoder == "lt_card" and numeric(value, 3):
        return "card", "lt:" + value
    elif decoder == "card" and isinstance(value, str):
        if re.fullmatch(r"(?:lt|vlt):[0-9]+/[0-9]+/[0-9]+|nt-[ab]", value):
            return "card", value
    elif decoder == "cage" and isinstance(value, str):
        if re.fullmatch(r"lt:[0-9]+/[0-9]+/[0-9]+:cage:[0-9]+", value):
            return "cage", value
    elif decoder == "transceiver" and isinstance(value, str):
        # Owners: LT cards, controller cards and NT appliques. The active-NT
        # alias (nt:...), acu/iont/remote-sfp and bare slot forms are runtime or
        # platform identities without a fixed physical owner here; they stay gaps.
        if re.fullmatch(r"(?:lt:[0-9]+/[0-9]+/[0-9]+|nt-[ab]|ntio-[12]):(?:%s):[0-9]+" % "|".join(CAGE_TYPES), value):
            return "transceiver", value
    elif decoder == "uplink" and isinstance(value, str):
        if re.fullmatch(r"(?:nt-[ab]|ntio-[12]):(?:%s):[0-9]+" % "|".join(IHUB_OPTICAL_TYPES), value):
            return "uplink", value
    elif decoder == "ihub_port" and isinstance(value, str):
        try:
            return decode("uplink", value)
        except UnknownIdentity:
            pass
        if re.fullmatch(r"nt:(?:vp|mc):[0-9]+", value):
            return "ihub_virtual_port", value
        if re.fullmatch(r"lt:[0-9]+/[0-9]+/[0-9]+|nt-[ab]:(?:eth|AI):[0-9]+", value):
            return "ihub_port", value
    elif decoder in ("ihub_lag", "ihub_customer") and isinstance(value, str) and value.isascii() and value.isdigit():
        return decoder, value
    elif decoder == "ihub_service" and isinstance(value, (list, tuple)) and len(value) == 2:
        if value[0] in ("vpls", "ies") and isinstance(value[1], str) and value[1].isascii() and value[1].isdigit():
            return decoder, tuple(value)
    elif decoder == "applique" and isinstance(value, str):
        if re.fullmatch(r"ntio-[0-9]+", value):
            return "applique", value
    elif decoder == "port_layer" and isinstance(value, str):
        # Port-layer services (e.g. MSTP ports, documented as the aggregate's
        # interface index) attach to the port object itself. Live counter-
        # example: xstp port 1/1/8/6 exists with a LAG but no bridge port.
        return bridge_owner(value, known_ports)
    elif decoder == "bridge_port" and isinstance(value, str):
        # Canonical module encoding "<port kind>:<port identity>"; the graph
        # itself uses the (kind, identity) tuple form below.
        prefix, _, rest = value.partition(":")
        if prefix in BRIDGE_PARENT_KINDS:
            decode(prefix, rest, known_ports)
            return "bridge_port", (prefix, rest)
        owner = bridge_owner(value, known_ports)
        return "bridge_port", owner
    elif decoder == "bridge_port" and isinstance(value, (tuple, list)) and len(value) == 2:
        kind, port = value
        if kind in BRIDGE_PARENT_KINDS and isinstance(port, str):
            decode(kind, port, known_ports)
            return "bridge_port", tuple(value)
        raise UnknownIdentity("Unsupported bridge_port identity")
    elif decoder == "vlan_port" and isinstance(value, (tuple, list)) and len(value) == 3:
        kind, port, vlan = value
        if kind in BRIDGE_PARENT_KINDS and isinstance(port, str) and isinstance(vlan, str):
            decode(kind, port, known_ports)
            if vlan.startswith("stacked:"):
                parts = vlan.split(":")
                if len(parts) == 3 and _valid_vlan(parts[1]) and _valid_vlan(parts[2]):
                    return "vlan_port", tuple(value)
            elif _valid_vlan(vlan):
                return "vlan_port", tuple(value)
        raise UnknownIdentity("Unsupported vlan_port identity")
    elif decoder in ("interface", "qos_interface", "user_port") and isinstance(value, str):
        prefixes = {"pon": "pon", "ont": "ont", "uni": "uni", "xdsl-line": "xdsl_line",
                    "bonding": "bonding_group", "la-group": "lag", "chpair": "channel_pair",
                    "epon": "pon"}
        prefix, _, rest = value.partition(":")
        if prefix in prefixes:
            return decode(prefixes[prefix], rest, known_ports)
        if prefix == "ethernet-line":
            # The ethernet-line interface is the physical line's ethernet facet
            # (EFM on xDSL). Aggregates are separate interfaces with their own
            # typed names (bonding:, la-group:), never ethernet-line:.
            if numeric(rest, 4):
                candidates = [(kind, ident) for kind, ident in known_ports
                              if ident == rest and kind in ("xdsl_line", "ethernet_port")]
                if len(candidates) == 1:
                    return candidates[0]
            raise UnknownIdentity("Unsupported or ambiguous ethernet-line identity")
        if prefix in ("vlan", "vlan-port") and ":" in rest:
            suffix = _vlan_suffix(rest)
            if suffix:
                # A VLAN port stacks on the bridge port at the same address;
                # the bridge port's owner follows the verified attachment rule.
                parent = bridge_owner(suffix[0], known_ports)
                return "vlan_port", (parent[0], parent[1], suffix[1])
        if decoder != "interface":
            if numeric(value, 7):
                return "uni", value
            if numeric(value, 4):
                # A bare LT address can name a line, a bonding group or a LAG
                # group at the same time. Without typed evidence the owner is
                # ambiguous; never prefer one object kind over another.
                candidates = [(kind, ident) for kind, ident in known_ports
                              if ident == value and kind in _bare_port_kinds(decoder)]
                if decoder == "qos_interface":
                    candidates = _qos_owner(candidates)
                if len(candidates) == 1:
                    return candidates[0]
    raise UnknownIdentity("Unsupported or ambiguous %s identity" % decoder)


def parent_of(kind, identity):
    """Only the direct physical parent. No references, service ownership or NVTs."""
    if kind == "rack":
        return "msan", ""
    if kind == "applique":
        return "msan", ""
    if kind == "shelf":
        return "rack", identity.rsplit("/", 1)[0]
    if kind == "card":
        if identity in ("nt-a", "nt-b"):
            return "msan", ""
        return "shelf", identity.split(":", 1)[1].rsplit("/", 1)[0]
    if kind in ("pon", "xdsl_line", "ethernet_port", "bonding_group", "lag", "channel_pair"):
        return "card", "lt:" + identity.rsplit("/", 1)[0]
    if kind == "cage":
        return "card", identity.split(":cage:", 1)[0]
    if kind in ("transceiver", "uplink"):
        owner = identity.split(":", 1)[0]
        if owner == "lt":
            return "card", "lt:" + identity.split(":")[1]
        if owner in ("nt-a", "nt-b"):
            return "card", owner
        return "applique", owner
    if kind == "ihub_port":
        return "card", identity if identity.startswith("lt:") else identity.split(":")[0]
    if kind in ("ont", "ont_slot", "uni"):
        return {"ont": "pon", "ont_slot": "ont", "uni": "ont_slot"}[kind], identity.rsplit("/", 1)[0]
    if kind == "bridge_port":
        return identity[0], identity[1]
    if kind == "vlan_port":
        return "bridge_port", (identity[0], identity[1])
    return None
