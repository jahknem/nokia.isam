"""Root config tree masking and line-completeness, on a handwritten synthetic root.

Runs in CI without private captures: tests/fixtures/config_tree/synthetic-root is
handwritten (every cleartext secret contains 'Leak' or 'Hash'). Line-completeness
is checked against the raw input, not against the module's own redacted output.
"""
import json
import pathlib
import re

import pytest
import yaml

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    _is_secret,
    parse_config_tree,
    redacted_token_lines,
)

BUNDLE = pathlib.Path(__file__).resolve().parents[4] / "fixtures" / "config_tree" / "synthetic-root"
TEXT = (BUNDLE / "output.txt").read_text()
SECRETS = ("SanitizedHashOne", "OperatorLeakOne", "FusedLeakTwo", "Quoted LeakThree", "LeakThree",
           "CommunityLeakFour", "CommunityLeakFive", "AuthLeakSix", "PrivLeakSeven", "SanitizedHashTwo",
           "SanitizedHashThree", "RadiusLeakEight", "SanitizedHashFour", "PppoeLeakNine", "NtpKeyLeakTen",
           "Md5KeyLeakEleven", "DashedLeakTwelve", "SecretKeyLeakThirteen")
PLACEHOLDER = re.compile(r"<redacted:\d+>")


def leaves(tree):
    out = []

    def walk(node):
        for key, value in node.items():
            if key == "__config__":
                out.append(value)
            else:
                walk(value)

    walk(tree)
    return out


def stored_lines(tree):
    return [line for leaf in leaves(tree) for line in leaf["lines"]]


def _line_regex(stored):
    """A stored (masked) line as a pattern over the raw line: each placeholder stands
    for a non-empty secret value or part of one; everything else must match exactly."""
    parts = []
    for token in stored.split(" "):
        pieces = re.split(r"(<redacted:\d+>)", token)
        parts.append("".join(r".+?" if PLACEHOLDER.fullmatch(p) else re.escape(p) for p in pieces))
    return re.compile(r"\s+".join(parts))


def test_fixture_is_a_synthetic_descriptor():
    descriptor = yaml.safe_load((BUNDLE / "fixture.yml").read_text())
    assert descriptor["source"] == "synthetic-regression"
    assert descriptor["command"] == "info configure flat"


def test_no_cleartext_or_encrypted_secret_survives_anywhere():
    tree = parse_config_tree(TEXT)
    output = json.dumps(tree)
    lines = "\n".join(" ".join(tokens) for tokens in redacted_token_lines(TEXT))
    for secret in SECRETS:
        assert secret not in output and secret not in lines, secret
    assert "Leak" not in output and "Hash" not in output
    assert "encrypted:" not in output
    assert not re.search(r"plain:(?!\*+[\" ])", output)  # only device-masked plain:****** remains


def test_device_masked_placeholders_are_kept():
    tree = parse_config_tree(TEXT)
    assert tree["system"]["security"]["operator"]["viewer"]["__config__"]["attrs"]["password"] == "plain:******"
    ont = tree["equipment"]["ont"]["interface"]["1/1/5/1/3"]["__config__"]
    assert ont["attrs"]["log-auth-pwd"] == "plain:******"


def test_prefixed_credentials_keep_their_algorithm_but_not_the_value():
    lines = stored_lines(parse_config_tree(TEXT))
    user1 = next(line for line in lines if "snmpuser1" in line)
    user2 = next(line for line in lines if "snmpuser2" in line)
    assert re.fullmatch(r".* authentication md5:<redacted:\d+> privacy des:<redacted:\d+>", user1)
    assert re.fullmatch(r".* authentication sha1:<redacted:\d+> privacy aes-128:<redacted:\d+>", user2)


def test_password_prompt_is_not_a_secret_and_is_not_masked_elsewhere():
    operators = parse_config_tree(TEXT)["system"]["security"]["operator"]
    noc = operators["noc"]["__config__"]
    assert noc["attrs"] == {"password": "prompt", "prompt": "%n>"}
    assert "unparsed" not in noc
    isadmin = operators["isadmin"]["__config__"]
    assert PLACEHOLDER.fullmatch(isadmin["attrs"]["password"]) and isadmin["attrs"]["prompt"] == "%n%d%c "
    assert "configure vlan id 200 name prompt-vlan mode residential-bridge" in stored_lines(parse_config_tree(TEXT))


def test_known_secret_reuse_is_masked_only_as_token_or_colon_segment():
    lines = stored_lines(parse_config_tree(TEXT))
    # 'public' is a community, yet the VLAN name sharing it as a '-' part stays intact.
    assert "configure vlan id 100 name public-internet mode residential-bridge" in lines
    # A numeric 'key 100' is masked at its keyword but never propagates to VLAN 100.
    assert "configure bridge port 1/1/5/1/3/1/1 max-unicast-mac 5 pvid 100" in lines
    assert any(re.fullmatch(r"configure ntp ont 1/1/5/1/4 key <redacted:\d+>", line) for line in lines)
    # Whole-token and ':' segment reuse of a secret is masked with the same number.
    radius = next(line for line in lines if "auth-server R1" in line).rsplit(" ", 1)[1]
    ont = next(line for line in lines if line.startswith("configure equipment ont interface 1/1/5/1/3 "))
    assert ont.endswith("desc1 " + radius)
    ops = next(line for line in lines if line.startswith("configure system security operator ops ")).rsplit(" ", 1)[1]
    assert any(line.endswith("desc1 ref:" + ops) for line in lines)


def test_bare_reuse_of_a_plain_prefixed_secret_is_masked():
    text = "\n".join(["configure system security radius auth-server R1 secret plain:Hunter2xyz",
                      "configure equipment ont interface 1/1/1/1/1 desc1 Hunter2xyz"])
    assert "Hunter2xyz" not in json.dumps(parse_config_tree(text))


def test_communities_sharing_a_host_address_stay_distinct_leaves():
    snmp = parse_config_tree(TEXT)["system"]["security"]["snmp"]
    communities = snmp["community"]
    assert len(communities) == 3 and all(PLACEHOLDER.fullmatch(name) for name in communities)
    shared = [name for name in communities if "10.0.0.1/32" in communities[name]["host-address"]]
    assert len(shared) == 2
    # The embedded community refers to the same placeholder as its community entry.
    version = snmp["notify-profile"]["prof1"]["__config__"]["attrs"]["snmp-version"]
    assert version.startswith("v2c:") and version[len("v2c:"):] in shared
    assert snmp["notify-profile"]["prof3"]["__config__"]["attrs"]["snmp-version"] == "v3"


def test_quoted_and_fused_secrets_leave_no_fragment():
    lines = stored_lines(parse_config_tree(TEXT))
    assert any(re.fullmatch(r"configure system security operator ops2 password=<redacted:\d+>", line) for line in lines)
    assert any(re.fullmatch(r"configure system security operator ops3 password <redacted:\d+>", line) for line in lines)
    assert not any('Leak"' in line or "Three" in line for line in lines)


def test_tree_is_line_complete_against_the_raw_input():
    """Every raw configure line is kept, in input order, differing only by masked secrets.

    Compared against the raw text (not the module's redacted output): whitespace is
    normalised and non-configure lines (echo, delimiters, blanks) are not part of the
    tree, which is what "line-complete (masked)" promises.
    """
    raw = [line.strip() for line in TEXT.splitlines() if line.strip().startswith("configure ")]
    tree = parse_config_tree(TEXT)
    kept = stored_lines(tree)
    assert len(kept) == len(raw) == sum(len(leaf["lines"]) for leaf in leaves(tree))
    unmatched = list(kept)
    for line in raw:
        match = next((stored for stored in unmatched if _line_regex(stored).fullmatch(" ".join(line.split()))), None)
        assert match is not None, line.split()[:4]  # identity prefix only, never a secret
        unmatched.remove(match)
    assert unmatched == []
    assert not any(line.startswith(("echo", "#")) for line in kept)


@pytest.mark.parametrize("word", ["password", "pass-word", "pass_word", "passwd", "secret", "secret-key",
                                  "md5-key", "sha1-key", "auth-key", "priv-key", "pre-shared-key", "community",
                                  "read-community", "log-auth-pwd", "auth-password", "shared-secret", "psk", "key"])
def test_secret_keywords(word):
    assert _is_secret(word)


@pytest.mark.parametrize("word", ["key-type", "key-id", "ground-key", "reg-auth", "public-key", "password-timeout",
                                  "prompt", "keyword", "authentication", "privacy", "community-string-length"])
def test_non_secret_keywords(word):
    assert not _is_secret(word)
