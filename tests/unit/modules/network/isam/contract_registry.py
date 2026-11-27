"""Contract scope: which module families satisfy the full module contract.

The contract tests (resource state contract, offline action equivalence,
targeted gathered, CLI-safety family scans, docs-vs-argspec, module layout)
iterate the module inventory. During the PR split of the feature stack, a PR
that lands a subset of the families adds exactly its modules to
``CONTRACT_MODULES`` and makes every contract test pass for them. Modules not
listed are excluded from the contract tests until their PR lands.

The final integration PR of the split replaces the exception with a
completeness test: ``CONTRACT_MODULES`` must equal the module inventory.
"""

CONTRACT_MODULES = frozenset({
    "isam_ani_onts",
    "isam_bridges",
    "isam_equipment",
    "isam_equipment_onts",
    "isam_equipment_replan",
    "isam_ethernet_onts",
    "isam_generic_pon",
    "isam_interface_alarms",
    "isam_l2uni_onts",
    "isam_ntp_onts",
    "isam_pon_global",
    "isam_pon_interfaces",
    "isam_trouble_shooting_pon",
    "isam_uni_onts",
    "isam_vlan_global",
})


def module_in_scope(name):
    """True when the module (e.g. 'isam_vlans') satisfies the contract."""
    return name in CONTRACT_MODULES


def case_in_scope(key):
    """True for a targeted-case key ('vlans', 'alarm:custom_profiles', ...) whose
    family belongs to a module in CONTRACT_MODULES. Case keys are facts-family
    names: a module name with the 'isam_' prefix stripped (aliases resolved by
    the family PR that adds the module)."""
    family = key.split(":")[0]
    return any(family in (m, m[len("isam_"):]) for m in CONTRACT_MODULES)


# Cross-cutting enforcement that lands with a specific integration PR:
#   'cli-safety-cliconf'    the connection plugin refuses control characters
#   'cli-safety-targeted'   facts_base targeted reads refuse control characters
#   'return-docs-everywhere' generated RETURN docs exist for every module
FEATURES = frozenset()


def feature(name):
    return name in FEATURES


def requires(*modules):
    """Skip decorator: the test needs these modules to satisfy the contract."""
    import pytest
    missing = [m for m in modules if m not in CONTRACT_MODULES]
    return pytest.mark.skipif(bool(missing), reason="contract pending for: %s" % ", ".join(missing))
