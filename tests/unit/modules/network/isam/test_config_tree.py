"""Root config tree: lossless nested parse of 'info configure [detail] flat'."""
import importlib.util
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    _known_secrets,
    _tokens,
    gap_report,
    nesting_stats,
    parse_config_tree,
    redacted_token_lines,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_grammar import CONFIG_GRAMMAR


def redacted_source(text):
    return ["configure " + " ".join(tokens) for tokens in redacted_token_lines(text) if tokens]


REPO = pathlib.Path(__file__).resolve().parents[5]
CAPTURE = REPO / "local_captures/DS-LIN-TEST-01/info_configure_flat.txt"
ROOT_CAPTURES = [REPO.parent / "pon-migration-planner/.local" / name for name in ("root-flat.txt", "root-detail-flat.txt")]

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


def all_values(node):
    """Every key and scalar value anywhere in the tree (for secret checks)."""
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            out.append(key)
            out.extend(all_values(value))
    elif isinstance(node, list):
        for value in node:
            out.extend(all_values(value))
    else:
        out.append(node)
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
    assert node["source"] == "grammar" and node["node"] == "qos tca queue"


def test_secret_community_is_redacted_but_masked_password_kept():
    tree = parse_config_tree(SAMPLE)
    # Both parts of the composite community identity belong to the CLI path.
    community = tree["system"]["security"]["snmp"]["community"]
    assert list(community) == ["<redacted>"]
    leaf = community["<redacted>"]["host-address"]["10.0.0.1/32"]["__config__"]
    assert leaf["attrs"] == {}
    assert leaf["source"] == "resource"
    assert "public" not in all_values(tree)
    ont = tree["equipment"]["ont"]["interface"]["1/1/5/1/3"]["__config__"]
    assert ont["attrs"]["log-auth-pwd"] == "plain:******"  # device-masked, kept


def test_redaction_cleartext_and_encrypted_masked_placeholders_kept():
    text = "\n".join([
        "configure system security snmp community s3cr3t host-address 10.0.0.1/32",
        "configure system security operator isadmin password encrypted:aa:bb prompt %i",
        "configure system security operator other password plain:****",
        "configure system security radius auth-server 1 secret topsecret",
        "configure pppoe-client interface 1/1/1/1 client-id 1 username u password hunter2",
    ])
    tree = parse_config_tree(text)
    values = all_values(tree)
    for secret in ("s3cr3t", "topsecret", "hunter2", "encrypted:aa:bb"):
        assert secret not in values
        assert not any(secret in str(v) for v in values)
    op = tree["system"]["security"]["operator"]["isadmin"]["__config__"]
    assert op["attrs"] == {"password": "<redacted>", "prompt": "%i"}
    assert tree["system"]["security"]["operator"]["other"]["__config__"]["attrs"]["password"] == "plain:****"
    pppoe = tree["pppoe-client"]["interface"]["1/1/1/1"]["client-id"]["1"]["__config__"]
    assert pppoe["attrs"]["password"] == "<redacted>" and pppoe["source"] == "grammar"


def test_resource_schema_nests_lowercase_identity_and_stays_lossless():
    line = "configure system security operator isadmin password encrypted:aa:bb prompt %i"
    tree = parse_config_tree(line)
    leaf = tree["system"]["security"]["operator"]["isadmin"]["__config__"]
    assert leaf["lines"] == [line.replace("encrypted:aa:bb", "<redacted>")]
    assert leaf["node"] == "system security operator"


def test_learned_subnodes_nest_below_their_parent():
    text = "\n".join([
        "configure equipment ont interface 1/1/2/1/1 sw-ver-pland disabled no desc1",
        "configure equipment ont interface 1/1/2/1/1 tc-layer no olt-pm-collect no ont-pm-collect",
        "configure qos interface 1/1/2/1/1/1/1 queue 0 priority 6 weight 34",
        "configure qos interface 1/1/2/1/1/1/1 queue 1 priority 6 weight 66",
        "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit",
        "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits",
        "configure xdsl line 1/1/3/1 service-profile 13 spectrum-profile 2 no admin-up",
        "configure xdsl line 1/1/3/1 tca-line-threshold no enable no es-nearend",
    ])
    tree = parse_config_tree(text)
    ont = tree["equipment"]["ont"]["interface"]["1/1/2/1/1"]
    assert ont["__config__"]["attrs"]["sw-ver-pland"] == "disabled"
    assert ont["tc-layer"]["__config__"]["attrs"] == {"olt-pm-collect": False, "ont-pm-collect": False}
    queues = tree["qos"]["interface"]["1/1/2/1/1/1/1"]["queue"]
    assert queues["1"]["__config__"]["attrs"] == {"priority": "6", "weight": "66"}
    pm = tree["l2uni"]["ont"]["performance-monitor"]["1/1/2/1/1/1/1"]
    assert pm["__config__"]["attrs"] == {"pm-collect": False, "pm-collect-64bit": False}
    assert pm["pm-collect-ext"]["__config__"]["attrs"] == {"pm-collect": False, "p-bits": False}
    xdsl = tree["xdsl"]["line"]["1/1/3/1"]
    assert xdsl["__config__"]["attrs"]["service-profile"] == "13"
    assert xdsl["tca-line-threshold"]["__config__"]["attrs"]["enable"] is False
    kept = [line for leaf in leaves(tree) for line in leaf["lines"]]
    assert sorted(kept) == sorted(redacted_source(text))


def test_grammar_has_previously_missing_and_intact_nodes():
    assert ("l2uni", "ont", "tc-layer-threshold") in CONFIG_GRAMMAR
    assert set(CONFIG_GRAMMAR[("equipment", "ont", "pm-collect")]["attrs"]) == {"xg-pm-collect"}
    tc = CONFIG_GRAMMAR[("l2uni", "ont", "tc-layer-threshold")]
    assert set(tc["attrs"]) == {"dropped-frames-up", "dropped-frames-dn"}
    # no word-wrap artefacts: no attribute glued to 'no' or cut short
    for node in CONFIG_GRAMMAR.values():
        for name in node["attrs"]:
            assert not (name.startswith("no") and name[2:] in node["attrs"]), name


def test_gap_report_families_and_unclaimed():
    text = "\n".join(SAMPLE.splitlines() + [
        "configure qos global lt:1/1/2 no queue-stats",
        "configure bridge port 1/1/5/1/3/1/2 brand-new-knob 7 pvid 3",
    ])
    argspecs = {"qos_tca": {"tca_enable", "load_thresh"}, "bridges": {"max_unicast_mac", "pvid"}}
    prefixes = {"qos_tca": ("configure qos tca ",), "bridges": ("configure bridge ",)}
    report = gap_report(parse_config_tree(text), argspec_names=argspecs, prefixes=prefixes, excludes={})
    assert report["families"]["qos_tca"] == {"argspec": True, "lines": 1, "unmodelled": {}, "value_like": 0}
    assert report["families"]["bridges"]["unmodelled"] == {"bridge port": ["brand-new-knob"]}
    assert report["unclaimed"]["qos global"] == 1
    assert "system security snmp community host-address" in report["unclaimed"]


def test_gap_report_defaults_load_collection_argspecs():
    report = gap_report(parse_config_tree(SAMPLE))
    assert report["families"]["qos_tca"]["argspec"] is True
    assert report["families"]["isam_system_security"]["lines"] == 1
    assert not report["unclaimed"]


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_real_capture_is_lossless():
    text = CAPTURE.read_text()
    kept = [line for leaf in leaves(parse_config_tree(text)) for line in leaf["lines"]]
    assert sorted(kept) == sorted(redacted_source(text))


@pytest.mark.parametrize("capture", ROOT_CAPTURES, ids=lambda p: p.name)
def test_root_captures_are_lossless(capture):
    if not capture.exists():
        pytest.skip("root capture not available")
    text = capture.read_text(errors="replace")
    tree = parse_config_tree(text)
    kept = [line for leaf in leaves(tree) for line in leaf["lines"]]
    assert sorted(kept) == sorted(redacted_source(text))
    # Inspect keys, values and stored CLI lines without reporting credential material.
    assert not any("encrypted:" in str(value) for value in all_values(tree))
    stats = nesting_stats(text)
    assert sum(stats.values()) == len(kept)
    assert stats.get("grammar", 0) > 0


def _compiler():
    path = REPO / "tools/compile_config_grammar.py"
    if not path.exists():
        pytest.skip("compiler not available")
    spec = importlib.util.spec_from_file_location("compile_config_grammar", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _help(*syntax_lines):
    return "\r\n".join(["help configure x", "Command Syntax", "--------------", "",
                        "The command has the following syntax:"] + list(syntax_lines)
                       + ["", "Command Parameters", "------------------"])


def test_compiler_rejoins_hard_and_soft_wraps():
    c = _compiler()
    first = "> configure equipment ont pm-collect (ont-idx) [ no xg-pm-collect | xg-pm-collec"
    assert len(first) == 80
    text = _help(first, "t <Gpon::OntPmCollect> ]")
    (syntax,) = c.extract_syntaxes(text)
    path, attrs = c.parse_syntax(syntax)
    assert attrs == {"xg-pm-collect": {"value": True, "negatable": True}}
    assert path == [("kw", "equipment"), ("kw", "ont"), ("kw", "pm-collect"), ("id",)]
    # full-width line ending in a blank: joined with a space, not glued
    line = "> configure alarm custom-profile (name) [ no visible2 | visible2 <A::B> ] [ no "
    line = line + " " * (80 - len(line))
    (syntax,) = c.extract_syntaxes(_help(line, "polarity2 | polarity2 <A::C> ]"))
    assert set(c.parse_syntax(syntax)[1]) == {"visible2", "polarity2"}
    # a hard-wrapped line may start with the '>' that closes a <Type>
    first = "> configure linetest single ltline (sessionid) lineid <Itf::LineTestSingleLineId"
    assert len(first) == 80
    (syntax,) = c.extract_syntaxes(_help(first, "> [ line-status <LineTest::LineStatusForConfig> ]"))
    path, attrs = c.parse_syntax(syntax)
    assert path[-2:] == [("kw", "lineid"), ("val",)] and "line-status" in attrs


def test_compiler_alternations_and_required_parameters():
    c = _compiler()
    path, attrs = c.parse_syntax(
        "> configure cfm ( no domain (domain-index) ) | ( domain (domain-index) name <Cfm::Name> "
        "level <Cfm::Level> [ no mhf-creation | mhf-creation <Cfm::Mhf> ] )")
    assert path == [("kw", "cfm"), ("kw", "domain"), ("id",)]
    assert attrs["name"] == {"value": True, "negatable": False, "required": True}
    assert attrs["mhf-creation"] == {"value": True, "negatable": True}
    # keys in the 'no' branch are identity, extra create-branch keys are attributes
    path, attrs = c.parse_syntax(
        "> configure ces ont ( no service (uni-idx) service-nbr <Ces::N> ) | ( service (uni-idx) "
        "service-nbr <Ces::N> [ no vlan | vlan <Ces::V> ] )")
    assert path == [("kw", "ces"), ("kw", "ont"), ("kw", "service"), ("id",), ("kw", "service-nbr"), ("val",)]
    assert set(attrs) == {"vlan"}
    # outside an alternation: chained after an identity -> identity, else attribute
    path, attrs = c.parse_syntax("> configure qos tca (index) queue <Qos::TcaQueues> [ [ no ] tca-enable ]")
    assert path[-2:] == [("kw", "queue"), ("val",)]
    assert attrs["tca-enable"] == {"value": False, "negatable": True}
    path, attrs = c.parse_syntax("> configure alarm log-sev-level <Alarm::Sev> log-full-action <Alarm::A>")
    assert path == [("kw", "alarm")] and set(attrs) == {"log-sev-level", "log-full-action"}
    assert c.node_key(c.parse_syntax("> configure ipoa/e-iw ( no port (p) ) | ( port (p) )")[0]) == ("ipoa/e-iw", "port")


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


def test_gap_report_never_shows_values():
    """A value parsed into a name position (e.g. a hash) is counted, never shown."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import config_tree

    tree = {"x": {"__config__": {"lines": ["configure system security ssh sftp-user u1 password encrypted:aa:bb"],
                                 "node": "system security ssh sftp-user U1User",
                                 "attrs": {"encrypted:aa:bb": True, "password": "x", "Secret Value": True}}}}
    report = config_tree.gap_report(tree, argspec_names={"isam_system_security": set()},
                                    prefixes={"isam_system_security": ("configure system security ",)}, excludes={})
    text = repr(report)
    assert "encrypted:aa:bb" not in text and "Secret Value" not in text and "U1User" not in text
    entry = report["families"]["isam_system_security"]
    assert entry["value_like"] == 2
    assert entry["unmodelled"] == {"system security ssh sftp-user <value>": ["password"]}


def test_alarm_names_ending_in_auth_or_key_are_not_secrets():
    tree = parse_config_tree("configure alarm entry reg-auth severity major\nconfigure alarm entry ground-key severity minor")
    lines = [line for leaf in leaves(tree) for line in leaf["lines"]]
    assert "configure alarm entry reg-auth severity major" in lines
    assert "configure alarm entry ground-key severity minor" in lines


def test_secret_keywords_are_still_masked():
    tree = parse_config_tree("\n".join([
        "configure system security snmp community public host-address 10.0.0.1/32",
        "configure system security radius auth-server R1 secret clear-text-secret",
        "configure ntp ont 1/1/5/1/3 key clear-key-value",
        "configure equipment ont interface 1/1/5/1/3 log-auth-pwd plain:******",
    ]))
    text = repr(tree)
    assert "public" not in text and "clear-text-secret" not in text and "clear-key-value" not in text
    assert "plain:******" in text


def test_encrypted_credentials_are_removed_even_at_unknown_paths():
    import json

    tree = parse_config_tree("\n".join([
        'configure system security ssh sftp-user user1 password "encrypted:hash-one"',
        'configure unknown node encrypted:hash-two no enabled',
        'configure unknown node "ENCRYPTED:hash-three" no enabled',
        'configure system security operator user2 password plain:clear-password',
    ]))
    output = json.dumps(tree)
    assert "encrypted:" not in output
    assert "hash-one" not in output and "hash-two" not in output and "hash-three" not in output
    assert "clear-password" not in output
    assert "<redacted>" in output


def test_resource_paths_do_not_depend_on_identity_spelling_or_line_order():
    text = "\n".join([
        "configure system security ssh sftp-user lowercase password encrypted:private-hash",
        "configure system security snmp view lowercase subtree * type include",
        "configure system security filetransfer protocol ftp",
        "configure system security radius policy lowercase servers 2 auth-server server-two priority 2",
        "configure system security radius policy lowercase servers 1 auth-server server-one priority 1",
        "configure system syslog route lowercase msg-type log facility local0 emergency no debug",
        "configure system sync-if-timing synce synce-1 none",
    ])
    tree = parse_config_tree(text)
    security = tree["system"]["security"]
    user = security["ssh"]["sftp-user"]["lowercase"]["__config__"]
    assert user["attrs"] == {"password": "<redacted>"}
    assert user["node"] == "system security ssh sftp-user"
    assert security["snmp"]["view"]["lowercase"]["subtree"]["*"]["__config__"]["attrs"] == {"type": "include"}
    assert security["filetransfer"]["__config__"]["attrs"] == {"protocol": "ftp"}
    servers = security["radius"]["policy"]["lowercase"]["servers"]
    assert servers["1"]["__config__"]["attrs"]["auth-server"] == "server-one"
    assert servers["2"]["__config__"]["attrs"]["auth-server"] == "server-two"
    route = tree["system"]["syslog"]["route"]["lowercase"]["__config__"]
    assert route["node"] == "system syslog route"
    assert route["attrs"] == {"msg-type": "log", "facility": "local0", "emergency": True, "debug": False}
    assert tree["system"]["sync-if-timing"]["synce"]["synce-1"]["__config__"]["attrs"] == {"port": "none"}


def test_password_policy_is_not_redacted_as_a_password_value():
    line = "configure system security password min-length 12 min-num-numeric-char 2 no mixed-case"
    tree = parse_config_tree(line)
    leaf = tree["system"]["security"]["password"]["__config__"]
    assert leaf["lines"] == [line]
    assert leaf["attrs"] == {"min-length": "12", "min-num-numeric-char": "2", "mixed-case": False}


def test_explicit_profile_nodes_preserve_values_without_detail_negations():
    line = "configure xdsl spectrum-profile 1 vdsl vdsl-band-plan annex-b-998ade adsl-band allow-adsl"
    tree = parse_config_tree(line)
    leaf = tree["xdsl"]["spectrum-profile"]["1"]["vdsl"]["__config__"]
    assert leaf["attrs"] == {"vdsl-band-plan": "annex-b-998ade", "adsl-band": "allow-adsl"}
    assert leaf["node"] == "xdsl spectrum-profile vdsl"
    assert leaf["source"] == "resource"
    root = parse_config_tree("configure mcast general fast-change")
    assert root["mcast"]["general"]["__config__"]["attrs"] == {"fast-change": True}


def test_explicit_system_id_accepts_node_identity_and_legacy_forms():
    for line, identity in (("configure system id node-name name node-name", True),
                           ("configure system id name node-name", False)):
        root = parse_config_tree(line)["system"]["id"]
        leaf = (root["node-name"] if identity else root)["__config__"]
        assert leaf["node"] == "system id"
        assert leaf["attrs"] == {"name": "node-name"}


def test_every_explicit_cli_name_mapping_targets_an_existing_option():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import load_argspec_names
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree_metadata import OPTION_NAMES, modelled_name

    specs = load_argspec_names({family for family, _node, _attr in OPTION_NAMES})
    for (family, node, attr), target in OPTION_NAMES.items():
        assert target in specs[family]
        assert modelled_name(family, node, attr, specs[family])
        assert not modelled_name(family, "unrelated node", attr, specs[family])


def test_gap_report_mappings_are_node_scoped_and_require_an_option():
    tree = parse_config_tree("configure cwmp plt adminstate locked")
    report = gap_report(tree, argspec_names={"cwmp_plt": {"admin_state"}},
                        prefixes={"cwmp_plt": ("configure cwmp ",)}, excludes={})
    assert report["families"]["cwmp_plt"]["unmodelled"] == {}
    missing = gap_report(tree, argspec_names={"cwmp_plt": set()},
                         prefixes={"cwmp_plt": ("configure cwmp ",)}, excludes={})
    assert missing["families"]["cwmp_plt"]["unmodelled"] == {"cwmp plt": ["adminstate"]}
    future = parse_config_tree("configure cwmp plt future-setting new-value")
    report = gap_report(future, argspec_names={"cwmp_plt": {"admin_state"}},
                        prefixes={"cwmp_plt": ("configure cwmp ",)}, excludes={})
    assert report["families"]["cwmp_plt"]["unmodelled"] == {"cwmp plt": ["future-setting"]}


@pytest.mark.parametrize("capture", ROOT_CAPTURES, ids=lambda p: p.name)
def test_lab_gap_report_has_no_unclaimed_or_unmodelled_fields(capture):
    if not capture.exists():
        pytest.skip("root capture not available")
    report = gap_report(parse_config_tree(capture.read_text(errors="replace")))
    assert not report["unclaimed"]
    # Counts only: assertion failures must not print identities or credentials.
    assert all(entry["argspec"] and not entry["unmodelled"] for entry in report["families"].values())


def test_community_embedded_in_snmp_version_is_masked():
    import json
    text = "\n".join([
        "configure system security snmp community privcomm host-address 10.0.0.1/32 context base",
        "configure system security snmp notify-profile prof1 snmp-version v2c:privcomm",
        "configure system security snmp notify-profile prof2 snmp-version v1:other-only-here",
        "configure system security snmp notify-profile prof3 snmp-version v3",
        "configure equipment ont interface 1/1/1/1/1 desc1 note-privcomm-ref",
    ])
    out = json.dumps(parse_config_tree(text))
    assert "privcomm" not in out and "other-only-here" not in out
    assert "v2c:<redacted>" in out and "v1:<redacted>" in out
    assert '"snmp-version": "v3"' in out  # a plain version stays readable


@pytest.mark.parametrize("capture", ROOT_CAPTURES, ids=lambda p: p.name)
def test_root_capture_tree_contains_no_known_secret(capture):
    """No cleartext secret seen behind a secret keyword survives anywhere in the tree."""
    import json

    if not capture.exists():
        pytest.skip("root capture not available")
    text = capture.read_text(errors="replace")
    known = _known_secrets(_tokens(l.strip())[1:] for l in text.splitlines() if l.strip().startswith("configure "))
    out = json.dumps(parse_config_tree(text))
    leaked = sum(1 for secret in known if secret in out)
    assert leaked == 0, "%d known secret value(s) leaked" % leaked  # count only
