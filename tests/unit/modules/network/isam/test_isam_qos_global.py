"""isam_qos_global: bare configure qos settings, per line card qos global, policers, pbit scheduling."""
import pathlib
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_qos_global
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_global import (
    SECTION_ATTRS,
    Qos_globalTemplate,
    strip_defaults,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures


ignore_provider_arg = True
LOCAL = lab_captures.CAPTURE_DIR
CAPTURES = [LOCAL / "root-detail-flat.txt", LOCAL / "root-flat.txt"]
OWNED_HEADS = ("global", "dsl-ctrl-pkt-policer", "nni-ctrl-pkt-policer", "ctrl-pkt-policer",
               "pbit-scheduling", "upstr-prot-dsl", "no", "atm-overhead-fact", "eth-efm-fact",
               "enable-alignment", "cac-mode", "use-dei", "set-dei")

DETAIL = dedent("""\
    configure qos no atm-overhead-fact no eth-efm-fact no enable-alignment no cac-mode no use-dei no set-dei
    configure qos tc-map-dot1p 0 tc 0 dpcolor green policer-color green
    configure qos dsl-ctrl-pkt-policer no sustained-rate no burst-size no protocol-ctrl
    configure qos nni-ctrl-pkt-policer no sustained-rate no burst-size
    configure qos global lt:1/1/2 no buffer-occ-thresh no queue-stats no dsload-tca no dsload-thresh no buffer-tca no up-buf-thresh no up-obc-thresh no dn-obc-thresh no dn-buf-thresh no part-buf-thresh
    configure qos global lt:1/1/3 no buffer-occ-thresh no queue-stats no dsload-tca no dsload-thresh no buffer-tca no up-buf-thresh no up-obc-thresh no dn-obc-thresh no dn-buf-thresh no part-buf-thresh
    configure qos pbit-scheduling no sc-xcon-us no sc-xcon-dn no sc-rb-us no sc-rb-dn
    configure qos upstr-prot-dsl no enable
""")

CONFIGURED = dedent("""\
    configure qos atm-overhead-fact 80 enable-alignment cac-mode alr
    configure qos dsl-ctrl-pkt-policer sustained-rate 20 protocol-ctrl nopolice-arprip
    configure qos nni-ctrl-pkt-policer burst-size 200
    configure qos ctrl-pkt-policer arp sustained-rate 30
    configure qos ctrl-pkt-policer igmp
    configure qos global lt:1/1/2 queue-stats dsload-thresh 50 part-buf-thresh 18446744073709551615
    configure qos pbit-scheduling sc-rb-dn svlanpbitbased
    configure qos upstr-prot-dsl enable
""")

CONFIGURED_FACTS = {
    "general": {"atm_overhead_fact": 80, "enable_alignment": True, "cac_mode": "alr"},
    "dsl_ctrl_pkt_policer": {"sustained_rate": 20, "protocol_ctrl": "nopolice-arprip"},
    "nni_ctrl_pkt_policer": {"burst_size": 200},
    "ctrl_pkt_policer": [{"protocol": "arp", "sustained_rate": 30}, {"protocol": "igmp"}],
    "line_cards": [{"name": "lt:1/1/2", "queue_stats": True, "dsload_thresh": 50,
                    "part_buf_thresh": 18446744073709551615}],
    "pbit_scheduling": {"sc_rb_dn": "svlanpbitbased"},
    "upstr_prot_dsl": {"enable": True},
}


class Conn(object):
    """Answers 'info configure qos [<node> ...] flat' from flat lines."""

    def __init__(self, text, missing=()):
        self.lines = [line for line in text.splitlines() if line.strip()]
        self.missing = missing
        self.commands = []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        path = command[len("info "):].replace(" flat", "")
        if any(node in path for node in self.missing):
            raise Exception("Error : invalid token")
        return "\n".join(line for line in self.lines if line == path or line.startswith(path + " ")) + "\n"


def _owned(line):
    tokens = line.split()
    return line.startswith("configure qos ") and len(tokens) > 2 and tokens[2] in OWNED_HEADS


def _unconsumed(line):
    """Tokens of an owned line the parser has no grammar for (empty: the line parses completely)."""
    tokens = line.split()[2:]
    head = tokens[0]
    if head in ("global", "ctrl-pkt-policer"):
        section, tokens = ("line_cards" if head == "global" else "ctrl_pkt_policer"), tokens[2:]
    elif head in ("dsl-ctrl-pkt-policer", "nni-ctrl-pkt-policer", "pbit-scheduling", "upstr-prot-dsl"):
        section, tokens = head.replace("-", "_"), tokens[1:]
    else:
        section = "general"
    spec = dict((kw, typ) for kw, _opt, typ, _d in SECTION_ATTRS[section])
    left, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "no" and i + 1 < len(tokens) and tokens[i + 1] in spec:
            i += 2
        elif tok in spec:
            i += 1 if spec[tok] == "bool" else 2
        else:
            left.append(tok)
            i += 1
    return left


class TestIsamQosGlobalModule(TestIsamModule):
    module = isam_qos_global

    def setUp(self):
        super(TestIsamQosGlobalModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamQosGlobalModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_facts.stop()

    def _device(self, text, missing=()):
        conn = Conn(text, missing)
        self.get_resource_connection_facts.return_value = conn
        return conn

    def _run(self, changed, **args):
        set_module_args(args, ignore_provider_arg)
        return self.execute_module(changed=changed)

    # ----- parsing ---------------------------------------------------------------------
    def test_parsed_detail_defaults_are_not_reported(self):
        parsed = self._run(False, running_config=DETAIL, state="parsed")["parsed"]
        assert parsed == {}

    def test_parsed_values(self):
        parsed = self._run(False, running_config=CONFIGURED + DETAIL.splitlines()[1] + "\n", state="parsed")["parsed"]
        assert parsed == CONFIGURED_FACTS

    def test_unknown_keywords_and_values_are_ignored(self):
        running = dedent("""\
            configure qos future-knob 7 cac-mode nocac
            configure qos pbit-scheduling sc-xcon-us brandnew sc-xcon-dn cvlanpbitbased
            configure qos global lt:1/1/4 new-thing 5 queue-stats
            configure qos brand-new-node foo 1
        """)
        parsed = self._run(False, running_config=running, state="parsed")["parsed"]
        assert parsed == {"pbit_scheduling": {"sc_xcon_dn": "cvlanpbitbased"},
                          "line_cards": [{"name": "lt:1/1/4", "queue_stats": True}]}

    def test_other_qos_families_are_not_claimed(self):
        running = dedent("""\
            configure qos interface 1/1/2/1 scheduler-node x
            configure qos profiles scheduler-node x
            configure qos tca 1/1/2/1 queue 0 tca-enable
            configure qos tc-map-dot1p 0 tc 0
            configure qos dscp-map-dot1p 1 dot1p-value 0
            configure qos up-ctrl-pkt arp tc 1
            configure qos dn-ctrl-pkt arp tc 1
        """)
        parsed = Qos_globalTemplate(lines=running.splitlines()).parse()
        assert parsed == {}

    # ----- rendering -------------------------------------------------------------------
    def test_rendered(self):
        rendered = self._run(False, state="rendered", config=CONFIGURED_FACTS)["rendered"]
        assert rendered == [
            "configure qos atm-overhead-fact 80 enable-alignment cac-mode alr",
            "configure qos global lt:1/1/2 queue-stats dsload-thresh 50 part-buf-thresh 18446744073709551615",
            "configure qos dsl-ctrl-pkt-policer sustained-rate 20 protocol-ctrl nopolice-arprip",
            "configure qos nni-ctrl-pkt-policer burst-size 200",
            "configure qos ctrl-pkt-policer arp sustained-rate 30",
            "configure qos ctrl-pkt-policer igmp",
            "configure qos pbit-scheduling sc-rb-dn svlanpbitbased",
            "configure qos upstr-prot-dsl enable",
        ]

    def test_round_trip(self):
        rendered = self._run(False, state="rendered", config=CONFIGURED_FACTS)["rendered"]
        parsed = self._run(False, state="parsed", running_config="\n".join(rendered))["parsed"]
        assert parsed == CONFIGURED_FACTS

    def test_short_line_card_name_is_normalized(self):
        rendered = self._run(False, state="rendered", config={"line_cards": [{"name": "1/1/5", "buffer_tca": True}]})["rendered"]
        assert rendered == ["configure qos global lt:1/1/5 buffer-tca"]

    # ----- merged ----------------------------------------------------------------------
    def test_merged_idempotent(self):
        self._device(DETAIL + CONFIGURED)
        self._run(False, state="merged", config=CONFIGURED_FACTS)

    def test_merged_default_values_are_idempotent(self):
        self._device(DETAIL)
        self._run(False, state="merged", config={
            "general": {"cac_mode": "msr", "atm_overhead_fact": 85, "use_dei": False},
            "line_cards": [{"name": "lt:1/1/2", "queue_stats": False, "dsload_thresh": 0}],
            "dsl_ctrl_pkt_policer": {"sustained_rate": 15},
            "pbit_scheduling": {"sc_rb_dn": "cvlanpbitbased"},
        })

    def test_merged_changes_only_differences(self):
        self._device(CONFIGURED)
        result = self._run(True, state="merged", config={
            "general": {"cac_mode": "nocac", "enable_alignment": True},
            "line_cards": [{"name": "lt:1/1/3", "dsload_tca": True}],
            "upstr_prot_dsl": {"enable": False},
        })
        assert result["commands"] == [
            "configure qos cac-mode nocac",
            "configure qos global lt:1/1/3 dsload-tca",
            "configure qos upstr-prot-dsl no enable",
        ]

    def test_merged_reads_only_the_named_sections(self):
        conn = self._device(CONFIGURED)
        self._run(True, state="merged", config={"pbit_scheduling": {"sc_xcon_us": "cvlanpbitbased"},
                                                 "line_cards": [{"name": "lt:1/1/2", "buffer_tca": True}]})
        assert set(conn.commands) == {"info configure qos global flat", "info configure qos pbit-scheduling flat"}

    def test_general_needs_the_qos_read(self):
        conn = self._device(CONFIGURED)
        self._run(False, state="merged", config={"general": {"cac_mode": "alr"}})
        assert set(conn.commands) == {"info configure qos flat"}

    def test_unsupported_node_does_not_fail_the_read(self):
        conn = self._device(CONFIGURED, missing=("ctrl-pkt-policer",))
        result = self._run(True, state="merged", config={"ctrl_pkt_policer": [{"protocol": "arp", "burst_size": 5}],
                                                          "upstr_prot_dsl": {"enable": True}})
        assert result["commands"] == ["configure qos ctrl-pkt-policer arp burst-size 5"]
        assert "info configure qos ctrl-pkt-policer flat" in conn.commands

    # ----- replaced / overridden -------------------------------------------------------
    def test_replaced_resets_omitted_options_of_named_sections(self):
        self._device(CONFIGURED)
        result = self._run(True, state="replaced", config={
            "general": {"cac_mode": "alr"},
            "line_cards": [{"name": "lt:1/1/2", "queue_stats": True}],
            "ctrl_pkt_policer": [{"protocol": "arp"}],
        })
        assert result["commands"] == [
            "configure qos no atm-overhead-fact no enable-alignment",
            "configure qos global lt:1/1/2 no dsload-thresh no part-buf-thresh",
            "configure qos ctrl-pkt-policer arp no sustained-rate",
        ]

    def test_overridden_resets_everything_not_given(self):
        self._device(CONFIGURED)
        result = self._run(True, state="overridden", config={"general": {"atm_overhead_fact": 80, "enable_alignment": True,
                                                                         "cac_mode": "alr"},
                                                             "ctrl_pkt_policer": [{"protocol": "arp", "sustained_rate": 30}]})
        assert result["commands"] == [
            "configure qos global lt:1/1/2 no queue-stats no dsload-thresh no part-buf-thresh",
            "configure qos dsl-ctrl-pkt-policer no sustained-rate no protocol-ctrl",
            "configure qos nni-ctrl-pkt-policer no burst-size",
            "configure qos no ctrl-pkt-policer igmp",
            "configure qos pbit-scheduling no sc-rb-dn",
            "configure qos upstr-prot-dsl no enable",
        ]

    def test_overridden_idempotent(self):
        self._device(DETAIL + CONFIGURED)
        self._run(False, state="overridden", config=CONFIGURED_FACTS)

    # ----- deleted ---------------------------------------------------------------------
    def test_deleted_all(self):
        self._device(CONFIGURED)
        result = self._run(True, state="deleted")
        assert result["commands"] == [
            "configure qos no atm-overhead-fact no enable-alignment no cac-mode",
            "configure qos global lt:1/1/2 no queue-stats no dsload-thresh no part-buf-thresh",
            "configure qos dsl-ctrl-pkt-policer no sustained-rate no protocol-ctrl",
            "configure qos nni-ctrl-pkt-policer no burst-size",
            "configure qos no ctrl-pkt-policer arp",
            "configure qos no ctrl-pkt-policer igmp",
            "configure qos pbit-scheduling no sc-rb-dn",
            "configure qos upstr-prot-dsl no enable",
        ]

    def test_deleted_named_sections_only(self):
        self._device(CONFIGURED)
        result = self._run(True, state="deleted", config={"dsl_ctrl_pkt_policer": {},
                                                           "ctrl_pkt_policer": [{"protocol": "igmp"}]})
        assert result["commands"] == [
            "configure qos dsl-ctrl-pkt-policer no sustained-rate no protocol-ctrl",
            "configure qos no ctrl-pkt-policer igmp",
        ]

    def test_deleted_on_defaults_is_idempotent(self):
        self._device(DETAIL)
        self._run(False, state="deleted")

    # ----- gathered --------------------------------------------------------------------
    def test_gathered_whole(self):
        conn = self._device(DETAIL + CONFIGURED)
        gathered = self._run(False, state="gathered")["gathered"]
        assert gathered == CONFIGURED_FACTS
        assert set(conn.commands) == {"info configure qos flat"}

    def test_gathered_named_line_card(self):
        conn = self._device(CONFIGURED + "configure qos global lt:1/1/3 buffer-tca\n")
        gathered = self._run(False, state="gathered", config={"line_cards": [{"name": "1/1/3"}]})["gathered"]
        assert gathered == {"line_cards": [{"name": "lt:1/1/3", "buffer_tca": True}]}
        assert conn.commands == ["info configure qos global lt:1/1/3 flat"]


@pytest.mark.parametrize("capture", CAPTURES, ids=lambda p: p.name)
def test_every_owned_capture_line_parses(capture):
    if not capture.exists():
        pytest.skip("lab capture not available")
    lines = [line.strip() for line in capture.read_text().splitlines() if _owned(line.strip())]
    for line in lines:
        assert _unconsumed(line) == [], line
        assert Qos_globalTemplate(lines=[line]).parse(), line
    if capture.name == "root-detail-flat.txt":
        # 1 general + 2 policers + 7 line cards + pbit-scheduling + upstr-prot-dsl, all defaults
        assert len(lines) == 12
        assert strip_defaults(Qos_globalTemplate(lines=lines).parse()) == {}
