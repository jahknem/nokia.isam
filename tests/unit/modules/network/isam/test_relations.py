"""relations/<family>.py is the one place a family declares what it relates to."""
import ast
from pathlib import Path

from ansible_collections.nokia.isam.plugins.module_utils.network.isam import relations
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import FACT_RESOURCE_SUBSETS
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.relations import FAMILIES
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import decode

FILES = {path.stem: path for path in Path(relations.__file__).parent.glob("*.py") if path.name != "__init__.py"}
FAMILY_KEYS = {"sections", "targeted_writes", "read_scope", "source", "settings", "profile_references", "reference_fields"}
SECTION_KEYS = {"identity", "object", "scope", "creates", "created_with", "references", "requires"}


def test_every_family_file_is_loaded_and_every_facts_family_has_one():
    # A file missing from the import list would not ship and would silently not count.
    assert set(FILES) == set(FAMILIES)
    # isam_dhcp_server is the legacy alias of dhcp_server (same facts class).
    assert set(FACT_RESOURCE_SUBSETS) - set(FAMILIES) == {"isam_dhcp_server"}


def test_family_files_are_pure_data():
    for name, path in FILES.items():
        tree = ast.parse(path.read_text())
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        assert all(isinstance(node, ast.ImportFrom) and node.module == "__future__" for node in imports), name
        assert not [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))], name


def test_format_is_closed_and_every_section_is_placed():
    kinds = set(export_catalog()["objects"])
    for name, family in FAMILIES.items():
        assert set(family) <= FAMILY_KEYS and "sections" in family, name
        for section, spec in family["sections"].items():
            where = "%s.%s" % (name, section)
            assert set(spec) <= SECTION_KEYS and "identity" in spec, where
            # Object-owned (addresses an object) or explicitly device-wide / a shared definition.
            assert "object" in spec or spec.get("scope") in ("device_global", "shared_profile"), where
            assert spec.get("scope") in (None, "device_global", "shared_profile"), where
            if spec.get("creates"):
                assert spec["object"] in kinds, where
            for entry in spec.get("created_with", ()):
                assert set(entry) == {"prefix", "object", "default"} and entry["object"] in kinds, where
            for target in list(spec.get("references", {}).values()) + list(spec.get("requires", ())):
                resource, target_section = target.split(".", 1)
                assert target_section in FAMILIES[resource]["sections"], (where, target)
        if "profile_references" in family:
            assert FAMILIES[family["profile_references"]]["reference_fields"], name


def test_what_the_device_creates_itself_is_addressed_to_the_object_that_brings_it():
    catalog = export_catalog()
    bindings = {(b["resource"], b["section"]): b for b in catalog["bindings"]}
    samples = {"ont": "1/1/5/1/3", "vlan_port": "1/1/5/1/3/1/1:10"}
    seen = set()
    for entry in catalog["created_with"]:
        decoder = bindings[(entry["resource"], entry["section"])]["decoder"]
        kind = decode(decoder, (entry["prefix"] or "") + samples[entry["object"]])[0]
        assert kind == entry["object"], entry
        # Such an entry configures an existing object; the family creating the object is another one.
        assert catalog["creates"].get(kind) != {"resource": entry["resource"], "section": entry["section"]}
        seen.add((entry["resource"], entry["prefix"]))
    assert seen == {("ntp_onts", None), ("ani_onts", None), ("interfaces", "ont:"), ("interfaces", "vlan-port:"),
                    ("qos_interfaces", "vlan:")}
