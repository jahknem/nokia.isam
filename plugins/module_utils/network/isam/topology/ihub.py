"""Strict IHUB operational port inventory; not the access interface namespace.

The repeated whitespace tables have no count footer. Require their complete
section/header/separator structure and terminal delimiter, and reject every
unrecognized row (including rows outside the requested parent's scope). The
successful transport read remains part of the completeness evidence; a delimiter
alone is not an independent inventory count or configuration certificate.
"""

import re

from ..ihub_config import READS
from .identity import UnknownIdentity, decode

# IHUB families are whole-source reads, NOT targeted-gather promises.
READ_CAPABILITIES = {
    resource: dict(source, instance_selection="whole_source_filter_only", states=["gathered", "parsed"])
    for resource, source in READS.items()
}


def optical_ports(output, owner=None):
    """Return the evidenced NT/NTIO sfp/xfp ports, regardless of admin/link state.

Known internal/virtual rows are validated but excluded from optical physical
children: nt:vp/mc, LT links, and NT eth/AI ports. Unknown identity forms reject
the whole source, never certify a partial inventory as an empty child set.
LAG membership and service configuration are deliberately not inferred here.
"""
    if not isinstance(output, str) or not output.strip():
        raise UnknownIdentity("IHUB port inventory is blank")
    lines = [line.strip() for line in output.splitlines() if line.strip()]

    def separator(line, char):
        return re.fullmatch(re.escape(char) + r"{10,}", line) is not None

    if not separator(lines[0], "="):
        raise UnknownIdentity("IHUB port inventory has no opening delimiter")
    index, seen, ports, sections = 1, set(), set(), set()
    while index < len(lines):
        section = re.fullmatch(r"Ports on (NT|NT-A|NT-B|LT|NTIO-[12])", lines[index])
        if section is None:
            raise UnknownIdentity("IHUB port inventory has an unknown section")
        section_owner = section[1].lower()
        if (index + 4 >= len(lines) or not separator(lines[index + 1], "=")
                or lines[index + 2].split() != "Port Admin Link Port Cfg Oper LAG/ Port Port Port".split()
                or lines[index + 3].split() != "Id State State MTU MTU Bndl Mode Encp Type".split()
                or not separator(lines[index + 4], "-")):
            raise UnknownIdentity("IHUB port inventory has a malformed section header")
        index += 5
        sections.add(section_owner)
        while index < len(lines) and not separator(lines[index], "="):
            row = re.fullmatch(
                r"(\S+)\s+(Up|Down)\s+(Yes|No)\s+(Link Up|Up|Down)\s+"
                r"([0-9]+)\s+([0-9]+)\s+(-|[0-9]+)\s+(\S+)\s+(\S+)\s+(\S+)", lines[index])
            if row is None:
                raise UnknownIdentity("IHUB port inventory has a malformed row")
            identity = row[1]
            if identity in seen:
                raise UnknownIdentity("IHUB port inventory has a duplicate identity")
            seen.add(identity)
            if identity.split(":", 1)[0] != section_owner:
                raise UnknownIdentity("IHUB port identity does not match its section")
            try:
                decode("uplink", identity)
            except UnknownIdentity:
                if not re.fullmatch(r"nt:(?:vp|mc):[0-9]+|lt:[0-9]+/[0-9]+/[0-9]+|nt-[ab]:(?:eth|AI):[0-9]+", identity):
                    raise UnknownIdentity("Unsupported IHUB port identity: %s" % identity)
            else:
                ports.add(identity)
            index += 1
        if index == len(lines):
            raise UnknownIdentity("IHUB port inventory has no terminal delimiter")
        index += 1
    if not sections or not seen:
        raise UnknownIdentity("IHUB port inventory has no recognized rows")
    if owner is not None and owner.split(":", 1)[0] not in sections:
        # In an uncounted, multi-section inventory a missing entire controller
        # section is not proof that its optical child set is empty.
        raise UnknownIdentity("IHUB port inventory has no section for the requested owner")
    return sorted(ports)


def sap_endpoint(identity):
    from .identity import _valid_vlan
    if not isinstance(identity, str):
        raise UnknownIdentity("Unsupported IHUB SAP identity")
    port, _, vlan = identity.rpartition(":")
    # The lab contains nt-a:xfp:4:0 and nt-a:eth:1:0 SAPs. Accept the
    # evidenced IHUB encapsulation token without inventing an access VLAN 0.
    if vlan != "0" and not _valid_vlan(vlan):
        raise UnknownIdentity("Unsupported IHUB SAP encapsulation")
    if port.startswith("lag-"):
        return decode("ihub_lag", port[4:])
    return decode("ihub_port", port)
