"""Targeted gathering of bonding groups and boards."""

from .targeted_cases_j import case


CASES = {
    "xdsl_bonding:groups": case(
        "isam_xdsl_bonding", {"groups": [{"group_id": "1/1/3/1"}]},
        ["configure xdsl-bonding group 1/1/3/1 group-profile profile-one"],
        {"groups": [{"group_id": "1/1/3/2"}]},
        ["configure xdsl-bonding group 1/1/3/2 group-profile profile-two"],
        "profile-one", "profile-two"),
    "xdsl_bonding:boards": case(
        "isam_xdsl_bonding", {"boards": [{"board_id": "1/1/3"}]},
        ["configure xdsl-bonding board 1/1/3 vect-fallback group-profile profile-one"],
        {"boards": [{"board_id": "1/1/4"}]},
        ["configure xdsl-bonding board 1/1/4 vect-fallback group-profile profile-two"],
        "profile-one", "profile-two"),
}
