"""IHUB bindings are whole-family read units, NOT targeted-gather promises."""

from ...ihub_config import READS


BINDINGS: list[dict] = [
    {"resource": "ihub_ports", "section": "config", "identity": "id", "decoder": "ihub_port", "read_scope": "all"},
    {"resource": "ihub_lags", "section": "config", "identity": "id", "decoder": "ihub_lag", "read_scope": "all"},
    {"resource": "ihub_services", "section": "customers", "identity": "id", "decoder": "ihub_customer", "read_scope": "all"},
    {"resource": "ihub_services", "section": "services", "identity": ["service_type", "id"],
     "decoder": "ihub_service", "read_scope": "all"},
]
DISCOVERY = {
    "ihub_port": {"children": [], "configuration_status": "partial"},
    "ihub_virtual_port": {"children": [], "configuration_status": "partial"},
    "ihub_lag": {"children": [], "configuration_status": "partial"},
    "ihub_service": {"children": [], "configuration_status": "partial"},
    "ihub_customer": {"children": [], "configuration_status": "partial"},
}
READ_CAPABILITIES = {
    resource: dict(source, instance_selection="whole_source_filter_only", states=["gathered", "parsed"])
    for resource, source in READS.items()
}


def sap_endpoint(identity):
    from ..identity import UnknownIdentity, _valid_vlan, decode
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
