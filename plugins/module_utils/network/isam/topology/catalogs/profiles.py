"""Typed shared-reference fields; neither name suffixes nor ID prefixes imply a relation."""

# source resource, source section, field -> target resource, target section.
# Identities and definitions are taken from TARGETED_GATHER, not redeclared here.
REFERENCES = (
    ("xdsl_lines", "config", "service_profile", "xdsl_profiles", "service_profiles"),
    ("xdsl_lines", "config", "spectrum_profile", "xdsl_profiles", "spectrum_profiles"),
    ("xdsl_lines", "config", "dpbo_profile", "xdsl_profiles", "dpbo_profiles"),
    ("xdsl_lines", "config", "vect_profile", "xdsl_profiles", "vect_profiles"),
    ("xdsl_boards", "boards", "dpbo_profile", "xdsl_profiles", "dpbo_profiles"),
    ("xdsl_boards", "boards", "vce_profile", "xdsl_profiles", "vce_profiles"),
    ("xdsl_boards", "vp_boards", "vce_profile", "xdsl_profiles", "vce_profiles"),
    ("xdsl_onts", "config", "dpbo_profile", "xdsl_profiles", "dpbo_profiles"),
    ("pppoe_client_interface", "config", "profile_name", "pppoe_client_ppp_profile", "config"),
)
