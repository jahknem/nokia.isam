"""G2: small global regions.

isam_nat, isam_error, isam_cwmp_plt, isam_pon_global, isam_pppox_relay_global,
isam_trouble_shooting_pon and the capacity dict of isam_mcast_general.
"""
import pathlib
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import (
    isam_cwmp_plt,
    isam_error,
    isam_mcast_general,
    isam_nat,
    isam_pon_global,
    isam_pppox_relay_global,
    isam_trouble_shooting_pon,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.mcast_general.mcast_general import (
    Mcast_generalFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cwmp_plt import Cwmp_pltTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.error import ErrorTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.mcast_general import (
    CAPACITY_ATTRS,
    CAPACITY_LINE,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.nat import NatTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_global import Pon_globalTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pppox_relay_global import (
    Pppox_relay_globalTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.trouble_shooting_pon import (
    LINE_REGEXES,
    THRESHOLD_ATTRS,
    Trouble_shooting_ponTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import parse_attributes
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True
LOCAL = lab_captures.CAPTURE_DIR
CAPTURES = [LOCAL / "root-detail-flat.txt", LOCAL / "root-flat.txt"]
DETAIL = CAPTURES[0]

SETTINGS = {
    # template, module, sample config, rendered set command
    "nat": (NatTemplate, isam_nat, {"aging_time": 180}, ["configure nat aging-time 180"]),
    "error": (ErrorTemplate, isam_error, {"log_full_action": "halt"}, ["configure error log-full-action halt"]),
    "cwmp_plt": (Cwmp_pltTemplate, isam_cwmp_plt, {"admin_state": "unlocked"}, ["configure cwmp plt adminstate unlocked"]),
    "pon_global": (Pon_globalTemplate, isam_pon_global, {"pwrbrst_mode": "enable", "range_mode": "alientolerant"},
                   ["configure pon pwrbrst-mode enable range-mode alientolerant"]),
    "pppox_relay_global": (
        Pppox_relay_globalTemplate, isam_pppox_relay_global,
        {"pado_timeout": 5, "pads_timeout": 6, "max_pad_attempts": 4, "trans_max_age": 100, "cc_max_age": 900},
        ["configure pppox-relay cross-connect global-session pado-timeout 5 pads-timeout 6 max-pad-attempts 4 "
         "trans-max-age 100 cc-max-age 900"]),
}
# detail lines (all defaults) and the read command of each settings block
DETAIL_LINES = {
    "nat": ("configure nat no aging-time", "info configure nat flat"),
    "error": ("configure error no log-full-action", "info configure error flat"),
    "cwmp_plt": ("configure cwmp plt no adminstate", "info configure cwmp plt flat"),
    "pon_global": ("configure pon no pwrbrst-mode no range-mode", "info configure pon flat"),
    "pppox_relay_global": (
        "configure pppox-relay cross-connect global-session no pado-timeout no pads-timeout no max-pad-attempts "
        "no trans-max-age no cc-max-age",
        "info configure pppox-relay cross-connect global-session flat"),
}

# Owned line prefixes (proposed RESOURCE_CONFIG_PREFIXES) and the lines each capture holds.
PREFIXES = {
    "configure nat ": NatTemplate,
    "configure error ": ErrorTemplate,
    "configure cwmp plt ": Cwmp_pltTemplate,
    "configure pon pwrbrst-mode ": Pon_globalTemplate,
    "configure pon no pwrbrst-mode": Pon_globalTemplate,
    "configure pon range-mode ": Pon_globalTemplate,
    "configure pon no range-mode": Pon_globalTemplate,
    "configure pppox-relay cross-connect global-session ": Pppox_relay_globalTemplate,
    "configure trouble-shooting pon ": Trouble_shooting_ponTemplate,
    "configure mcast capacity ": None,
}
EXPECTED_COUNTS = {
    "root-detail-flat.txt": {
        "configure nat ": 1, "configure error ": 1, "configure cwmp plt ": 1, "configure pon pwrbrst-mode ": 0,
        "configure pon no pwrbrst-mode": 1, "configure pon range-mode ": 0, "configure pon no range-mode": 0,
        "configure pppox-relay cross-connect global-session ": 1, "configure trouble-shooting pon ": 65,
        "configure mcast capacity ": 1,
    },
    # the capture without detail omits all of these (everything is at its default)
    "root-flat.txt": dict((prefix, 0) for prefix in PREFIXES),
}


class _Conn(object):
    def __init__(self, texts):
        self.texts, self.commands = texts, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if isinstance(self.texts, dict):
            return self.texts.get(command, "")
        return self.texts


class _Base(TestIsamModule):
    def setUp(self):
        super(_Base, self).setUp()
        self._patches = [
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"),
        ]
        self.connections = [p.start() for p in self._patches]
        self.facts_connection = self.connections[2]

    def tearDown(self):
        super(_Base, self).tearDown()
        for p in self._patches:
            p.stop()

    def device(self, text):
        conn = _Conn(dedent(text) if isinstance(text, str) else text)
        self.facts_connection.return_value = conn
        return conn

    def run_state(self, state, changed, **args):
        set_module_args(dict(args, state=state), ignore_provider_arg)
        return self.execute_module(changed=changed)


# ---------------------------------------------------------------- templates

def test_settings_templates_drop_defaults_and_ignore_unknown_keywords():
    assert NatTemplate(lines=["configure nat no aging-time"]).parse() == {}
    assert NatTemplate(lines=["configure nat aging-time 120"]).parse() == {}  # the default
    assert NatTemplate(lines=["configure nat aging-time 200 future-kw 7"]).parse() == {"aging_time": 200}
    assert NatTemplate(lines=["configure nat aging-time 200", "configure nat no aging-time"]).parse() == {}
    assert Pon_globalTemplate(lines=["configure pon no pwrbrst-mode range-mode alientolerant"]).parse() == \
        {"range_mode": "alientolerant"}
    # the per-interface node belongs to isam_pon_interfaces
    assert Pon_globalTemplate(lines=["configure pon interface 1/1/2/1 range-mode alientolerant"]).parse() == {}
    assert not Pon_globalTemplate.line_regex().match("configure pon interface 1/1/2/1 no range-mode")
    assert Pppox_relay_globalTemplate(lines=[
        "configure pppox-relay cross-connect global-session pado-timeout 7 no pads-timeout max-pad-attempts 10"
    ]).parse() == {"pado_timeout": 7}


def test_settings_render_set_and_reset():
    assert NatTemplate.render_attr("aging_time", 60) == "configure nat aging-time 60"
    assert NatTemplate.render_attr("aging_time", None) == "configure nat no aging-time"
    assert Cwmp_pltTemplate.render_attr("admin_state", None) == "configure cwmp plt no adminstate"
    assert ErrorTemplate.render_attr("log_full_action", "halt") == "configure error log-full-action halt"


def test_trouble_shooting_template():
    got = Trouble_shooting_ponTemplate(lines=[
        "configure trouble-shooting pon statistics threshold no interval",
        "configure trouble-shooting pon statistics threshold interface 1/1/2/1 no bw-th-up no bw-th-dn",
        "configure trouble-shooting pon statistics threshold interface x-pon:1/1/5/1 bw-th-up 10 bw-th-dn 0",
        "configure trouble-shooting pon statistics interface 1/1/2/3",
        "configure trouble-shooting pon statistics threshold interval 900",
    ]).parse()
    assert got == {
        "interval": 900,
        "interfaces": {"1/1/2/3": {"name": "1/1/2/3"}},
        "thresholds": {"1/1/2/1": {"name": "1/1/2/1"}, "x-pon:1/1/5/1": {"name": "x-pon:1/1/5/1", "bw_th_up": 10}},
    }
    assert Trouble_shooting_ponTemplate.render_interface("1/1/2/1", False) == \
        "configure trouble-shooting pon statistics no interface 1/1/2/1"
    assert Trouble_shooting_ponTemplate.render_threshold("1/1/2/1", "bw_th_dn", None) == \
        "configure trouble-shooting pon statistics threshold interface 1/1/2/1 no bw-th-dn"


def test_mcast_capacity_facts_parser():
    facts = Mcast_generalFacts(module=None)
    assert facts._parse_mcast_general_config(
        "configure mcast general fast-change no pkg-memb-bitmap\n"
        "configure mcast capacity no max-num-group no max-num-uncfg no cfg-res-time no uncfg-res-time\n"
    ) == {"fast_change": True}
    assert facts._parse_mcast_general_config(
        "configure mcast capacity max-num-group 512 max-num-uncfg 64 cfg-res-time 30 no uncfg-res-time bogus\n"
    ) == {"capacity": {"max_num_group": 512, "cfg_res_time": 30}}


# ---------------------------------------------------------------- captures

def _clause_rest(line, template):
    """The clause part of a line, for the unknown-token check."""
    if template is None:
        return CAPACITY_LINE.match(line).group("rest"), CAPACITY_ATTRS
    if template is Trouble_shooting_ponTemplate:
        for regex in LINE_REGEXES:
            match = regex.match(line)
            if match:
                rest = match.groupdict().get("rest")
                attrs = THRESHOLD_ATTRS if "threshold interface" in line else (("interval", "interval", "int", 300),)
                return rest, attrs
        raise AssertionError(line)
    match = template.line_regex().match(line)
    assert match, line
    return match.group("rest"), template.ATTRS


@pytest.mark.parametrize("capture", CAPTURES, ids=lambda p: p.name)
def test_every_capture_line_of_the_regions_parses(capture):
    if not capture.exists():
        pytest.skip("lab capture not available")
    counts = dict((prefix, 0) for prefix in PREFIXES)
    for line in capture.read_text().splitlines():
        for prefix, template in PREFIXES.items():
            if not line.startswith(prefix):
                continue
            counts[prefix] += 1
            rest, attrs = _clause_rest(line, template)
            cli_to_attr = dict((cli, option) for option, cli, _kind, _default in attrs)
            assert parse_attributes(rest, {}, cli_to_attr) == [], line
    assert counts == EXPECTED_COUNTS[capture.name]


def test_detail_lines_are_all_defaults():
    for name, (template, _module, _config, _rendered) in SETTINGS.items():
        assert template(lines=[DETAIL_LINES[name][0]]).parse() == {}, name


@pytest.mark.skipif(not DETAIL.exists(), reason="lab capture not available")
def test_capture_lines_are_all_matched_by_the_snapshot_tracker():
    """gather_configuration path: no 'unmatched configuration' warning for these regions."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts import facts_base

    data = DETAIL.read_text().splitlines()
    for template in set(t for t in PREFIXES.values() if t is not None):
        selected = [line for line in data if any(line.startswith(p) for p, t in PREFIXES.items() if t is template)]
        with facts_base.track_network_template_matches() as matched:
            template(lines=selected).parse()
        assert matched.observed
        assert set(selected) <= set(matched), template


# ---------------------------------------------------------------- settings blocks

@pytest.mark.parametrize("name", sorted(SETTINGS))
class TestSettingsBlocks(object):
    """The same contract for every settings block, driven through the real module."""

    def _run(self, name, state, changed, device=None, **args):
        case = _ModuleCase()
        case.module = SETTINGS[name][1]
        case.setUp()
        try:
            conn = case.device(device) if device is not None else None
            result = case.run_state(state, changed, **args)
            return result, conn
        finally:
            case.tearDown()

    def test_parsed_rendered_round_trip(self, name):
        template, _module, config, rendered = SETTINGS[name]
        result, _ = self._run(name, "rendered", False, config=config)
        assert result["rendered"] == rendered
        parsed, _ = self._run(name, "parsed", False, running_config="\n".join(result["rendered"]))
        assert parsed["parsed"] == config
        parsed, _ = self._run(name, "parsed", False, running_config=DETAIL_LINES[name][0])
        assert parsed["parsed"] == {}

    def test_merged_idempotent_and_reads_the_node(self, name):
        _template, _module, config, rendered = SETTINGS[name]
        _, conn = self._run(name, "merged", False, device="\n".join(rendered) + "\n", config=config)
        assert conn.commands == [DETAIL_LINES[name][1]]

    def test_merged_changes_from_defaults(self, name):
        _template, _module, config, rendered = SETTINGS[name]
        result, _ = self._run(name, "merged", True, device=DETAIL_LINES[name][0] + "\n", config=config)
        assert result["commands"] == rendered
        # default values requested on a default device: nothing to do (plain output omits them)
        template = SETTINGS[name][0]
        defaults = dict((option, default) for option, _cli, _kind, default in template.ATTRS)
        self._run(name, "merged", False, device="", config=defaults)
        self._run(name, "merged", False, device=DETAIL_LINES[name][0] + "\n", config=defaults)

    def test_deleted_resets_and_is_idempotent(self, name):
        template, _module, config, rendered = SETTINGS[name]
        result, _ = self._run(name, "deleted", True, device="\n".join(rendered) + "\n")
        resets = ["no " + cli for option, cli, _k, _d in template.ATTRS if option in config]
        assert result["commands"] == ["configure {0} {1}".format(template.NODE, " ".join(resets))]
        self._run(name, "deleted", False, device=DETAIL_LINES[name][0] + "\n")
        self._run(name, "deleted", False, device="")

    def test_replaced_resets_omitted(self, name):
        template, _module, config, rendered = SETTINGS[name]
        first = template.ATTRS[0][0]
        want = {first: config[first]}
        result, _ = self._run(name, "replaced", len(config) > 1, device="\n".join(rendered) + "\n", config=want)
        others = ["no " + cli for option, cli, _k, _d in template.ATTRS if option in config and option != first]
        assert result["commands"] == (["configure {0} {1}".format(template.NODE, " ".join(others))] if others else [])
        result, _ = self._run(name, "overridden", len(config) > 1, device="\n".join(rendered) + "\n", config=want)
        assert result["commands"] == (["configure {0} {1}".format(template.NODE, " ".join(others))] if others else [])

    def test_setting_the_default_value_resets(self, name):
        template, _module, config, rendered = SETTINGS[name]
        option, cli, _kind, default = template.ATTRS[0]
        result, _ = self._run(name, "merged", True, device="\n".join(rendered) + "\n", config={option: default})
        assert result["commands"] == ["configure {0} no {1}".format(template.NODE, cli)]


class _ModuleCase(_Base):
    def runTest(self):  # pragma: no cover - unittest requires a test method
        pass


@pytest.mark.skipif(not DETAIL.exists(), reason="lab capture not available")
def test_pon_global_ignores_the_pon_interface_lines_of_the_capture():
    lines = [line for line in DETAIL.read_text().splitlines() if line.startswith("configure pon ")]
    assert len(lines) > 1
    assert Pon_globalTemplate(lines=lines).parse() == {}


# ---------------------------------------------------------------- trouble-shooting pon

TS_DEVICE = """\
configure trouble-shooting pon statistics interface 1/1/2/1
configure trouble-shooting pon statistics threshold interval 900
configure trouble-shooting pon statistics threshold interface 1/1/2/1 bw-th-up 100 bw-th-dn 200
configure trouble-shooting pon statistics threshold interface 1/1/2/2 no bw-th-up no bw-th-dn
configure trouble-shooting pon statistics threshold interface 1/1/2/3 bw-th-up 300 no bw-th-dn
"""
TS_FACTS = {
    "interfaces": [{"name": "1/1/2/1"}],
    "threshold": {
        "interval": 900,
        "interfaces": [{"name": "1/1/2/1", "bw_th_up": 100, "bw_th_dn": 200}, {"name": "1/1/2/3", "bw_th_up": 300}],
    },
}
TS = "configure trouble-shooting pon statistics "


class TestIsamTroubleShootingPon(_Base):
    module = isam_trouble_shooting_pon

    def test_parsed_round_trip(self):
        parsed = self.run_state("parsed", False, running_config=TS_DEVICE)["parsed"]
        assert parsed == TS_FACTS
        rendered = self.run_state("rendered", False, config=TS_FACTS)["rendered"]
        assert rendered == [
            TS + "interface 1/1/2/1",
            TS + "threshold interval 900",
            TS + "threshold interface 1/1/2/1 bw-th-up 100 bw-th-dn 200",
            TS + "threshold interface 1/1/2/3 bw-th-up 300",
        ]
        assert self.run_state("parsed", False, running_config="\n".join(rendered))["parsed"] == TS_FACTS

    def test_gathered_whole(self):
        conn = self.device(TS_DEVICE)
        assert self.run_state("gathered", False)["gathered"] == TS_FACTS
        assert conn.commands == ["info configure trouble-shooting pon flat"]

    def test_merged_idempotent(self):
        self.device(TS_DEVICE)
        self.run_state("merged", False, config=TS_FACTS)
        self.run_state("merged", False, config={"threshold": {"interfaces": [{"name": "1/1/2/2", "bw_th_up": 0}]}})

    def test_merged_changes(self):
        self.device(TS_DEVICE)
        result = self.run_state("merged", True, config={
            "interfaces": [{"name": "1/1/2/2"}],
            "threshold": {"interval": 60, "interfaces": [{"name": "1/1/2/2", "bw_th_up": 5, "bw_th_dn": 6},
                                                          {"name": "1/1/2/1", "bw_th_up": 0}]},
        })
        assert result["commands"] == [
            TS + "interface 1/1/2/2",
            TS + "threshold interval 60",
            TS + "threshold interface 1/1/2/2 bw-th-up 5 bw-th-dn 6",
            TS + "threshold interface 1/1/2/1 no bw-th-up",
        ]

    def test_replaced(self):
        self.device(TS_DEVICE)
        result = self.run_state("replaced", True, config={
            "threshold": {"interfaces": [{"name": "1/1/2/1", "bw_th_dn": 200}]},
        })
        # interval omitted from the given threshold section: reset; interfaces section not given: untouched
        assert result["commands"] == [
            TS + "threshold no interval",
            TS + "threshold interface 1/1/2/1 no bw-th-up",
        ]

    def test_overridden(self):
        self.device(TS_DEVICE)
        result = self.run_state("overridden", True, config={
            "interfaces": [{"name": "1/1/2/4"}],
            "threshold": {"interval": 900, "interfaces": [{"name": "1/1/2/1", "bw_th_up": 100, "bw_th_dn": 200}]},
        })
        assert result["commands"] == [
            TS + "no interface 1/1/2/1",
            TS + "interface 1/1/2/4",
            TS + "threshold interface 1/1/2/3 no bw-th-up",
        ]

    def test_deleted_all_and_named(self):
        self.device(TS_DEVICE)
        result = self.run_state("deleted", True)
        assert result["commands"] == [
            TS + "no interface 1/1/2/1",
            TS + "threshold no interval",
            TS + "threshold interface 1/1/2/1 no bw-th-up no bw-th-dn",
            TS + "threshold interface 1/1/2/3 no bw-th-up",
        ]
        result = self.run_state("deleted", True, config={"threshold": {"interfaces": [{"name": "1/1/2/3"}]}})
        assert result["commands"] == [TS + "threshold interface 1/1/2/3 no bw-th-up"]
        self.device("configure trouble-shooting pon statistics threshold no interval\n")
        self.run_state("deleted", False)

    @pytest.mark.skipif(not DETAIL.exists(), reason="lab capture not available")
    def test_parsed_capture_is_all_defaults(self):
        lines = [line for line in DETAIL.read_text().splitlines() if line.startswith("configure trouble-shooting pon ")]
        assert len(lines) == 65
        assert self.run_state("parsed", False, running_config="\n".join(lines))["parsed"] == {}
        self.device("\n".join(lines))
        self.run_state("deleted", False)


# ---------------------------------------------------------------- isam_mcast_general capacity

MCAST = {
    "info configure mcast general flat": "configure mcast general fast-change\n",
    "info configure mcast capacity flat": "configure mcast capacity max-num-group 512 cfg-res-time 30\n",
}


class TestIsamMcastGeneralCapacity(_Base):
    module = isam_mcast_general

    def test_gathered_reads_general_and_capacity(self):
        conn = self.device(MCAST)
        gathered = self.run_state("gathered", False)["gathered"]
        assert gathered == {"fast_change": True, "capacity": {"max_num_group": 512, "cfg_res_time": 30}}
        assert conn.commands == ["info configure mcast general flat", "info configure mcast capacity flat"]

    def test_parsed_rendered_round_trip(self):
        config = {"capacity": {"max_num_group": 100, "max_num_uncfg": 10, "cfg_res_time": 5, "uncfg_res_time": 7}}
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        assert rendered == ["configure mcast capacity max-num-group 100 max-num-uncfg 10 cfg-res-time 5 uncfg-res-time 7"]
        assert self.run_state("parsed", False, running_config=rendered[0])["parsed"] == config

    @pytest.mark.skipif(not DETAIL.exists(), reason="lab capture not available")
    def test_parsed_capture(self):
        lines = [line for line in DETAIL.read_text().splitlines() if line.startswith("configure mcast ")]
        parsed = self.run_state("parsed", False, running_config="\n".join(lines))["parsed"]
        assert "capacity" not in parsed and parsed["fast_change"] is True

    def test_merged_idempotent_and_changes(self):
        self.device(MCAST)
        self.run_state("merged", False, config={"capacity": {"max_num_group": 512, "uncfg_res_time": 0}})
        result = self.run_state("merged", True, config={"capacity": {"max_num_group": 1024, "max_num_uncfg": 32}})
        assert result["commands"] == ["configure mcast capacity no max-num-group max-num-uncfg 32"]

    def test_deleted_resets_capacity(self):
        self.device(MCAST)
        result = self.run_state("deleted", True)
        # deleted resets every resettable attribute of the singleton, fast-change included
        assert result["commands"] == ["configure mcast general no fast-change",
                                      "configure mcast capacity no max-num-group no cfg-res-time"]

    def test_replaced_resets_omitted_capacity(self):
        self.device(MCAST)
        result = self.run_state("replaced", True, config={"fast_change": True, "capacity": {"max_num_group": 512}})
        assert result["commands"] == ["configure mcast capacity no cfg-res-time"]
