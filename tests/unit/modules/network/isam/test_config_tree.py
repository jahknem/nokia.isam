"""Root config tree: lossless nested parse of 'info configure [detail] flat'."""
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    parse_config_tree,
    gap_report,
    _redact_tokens,
    _tokens,
)


def redacted_source(text):
    return ["configure " + " ".join(_redact_tokens(_tokens(l.strip())[1:]))
            for l in text.splitlines() if l.strip().startswith("configure ")]

CAPTURE = pathlib.Path(__file__).resolve().parents[5] / "local_captures/DS-LIN-TEST-01/info_configure_flat.txt"

SAMPLE = "\n".join([
    "configure equipment ont interface 1/1/5/1/3 sw-ver-pland auto admin-state up log-auth-pwd plain:******",
    "configure qos tca 1/1/5/1/3/1/1 queue 0 no tca-enable load-thresh 80",
    "configure system security snmp community public host-address 10.0.0.1/32",
    "configure bridge port 1/1/5/1/3/1/1 max-unicast-mac 5 pvid 99",
])


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


def test_every_line_is_kept():
    tree = parse_config_tree(SAMPLE)
    kept = [line for leaf in leaves(tree) for line in leaf["lines"]]
    assert sorted(kept) == sorted(redacted_source(SAMPLE))


def test_grammar_node_nests_path_and_attributes():
    tree = parse_config_tree(SAMPLE)
    node = tree["qos"]["tca"]["1/1/5/1/3/1/1"]["queue"]["0"]["__config__"]
    assert node["attrs"]["tca-enable"] is False  # 'no tca-enable'
    assert node["attrs"]["load-thresh"] == "80"


def test_secret_community_is_redacted_but_masked_password_kept():
    tree = parse_config_tree(SAMPLE)
    # system security has no grammar yet: stored at branch granularity, secrets masked
    leaf = tree["system"]["security"]["__config__"]
    assert ["snmp", "community", "<redacted>", "host-address", "10.0.0.1/32"] in leaf["raw_tokens"]
    ont = tree["equipment"]["ont"]["interface"]["1/1/5/1/3"]["__config__"]
    assert ont["attrs"]["log-auth-pwd"] == "plain:******"  # device-masked, kept


def test_ungrammared_region_is_lossless_at_branch_granularity():
    tree = parse_config_tree("configure system security operator isadmin password encrypted:aa:bb prompt %i")
    leaf = tree["system"]["security"]["__config__"]
    assert leaf["raw_tokens"] == [["operator", "isadmin", "password", "encrypted:aa:bb", "prompt", "%i"]]
    assert leaf["lines"] == ["configure system security operator isadmin password encrypted:aa:bb prompt %i"]  # hashed, kept


def test_gap_report_flags_unclaimed_and_unmodelled():
    report = gap_report(parse_config_tree(SAMPLE))
    assert report["system security"]["unclaimed"] is False or report["system security"].get("no_grammar")
    # qos tca is a grammar node not claimed by any family prefix
    assert any(k.startswith("qos tca") for k in report)


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_real_capture_is_lossless():
    text = CAPTURE.read_text()
    kept = [line for leaf in leaves(parse_config_tree(text)) for line in leaf["lines"]]
    assert sorted(kept) == sorted(redacted_source(text))


def test_facts_subset_reads_flat_and_detail():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.configuration.configuration import Config_treeFacts

    class Connection:
        def __init__(self):
            self.commands = []

        def get(self, command):
            self.commands.append(command)
            return SAMPLE

    class Module:
        params = {"config_tree_detail": False}

    connection = Connection()
    facts = Config_treeFacts(Module()).populate_facts(connection)
    assert connection.commands == ["info configure flat"]
    assert "qos" in facts["config_tree"]

    Module.params = {"config_tree_detail": True}
    Config_treeFacts(Module()).populate_facts(connection)
    assert connection.commands[-1] == "info configure detail flat"
