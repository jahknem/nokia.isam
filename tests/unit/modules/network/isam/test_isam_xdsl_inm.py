"""isam_xdsl_inm / isam_xdsl_onts / isam_xdsl_system: unclaimed xDSL regions.

configure xdsl imp-noise-sensor near-end|far-end <line>, configure xdsl ont
interface <ont> and configure xdsl system.
"""
import pathlib
import re
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_inm, isam_xdsl_onts, isam_xdsl_system
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import Xdsl_inmTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_onts import Xdsl_ontsTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_system import Xdsl_systemTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import ATTRS as INM_CLI, parse_attributes
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True
CAPTURE = lab_captures.DETAIL

INM_DEFAULTS = "no inm-mode no inm-eq-inp-mode no ins-sensitivity no inm-cluster-cont no inm-iat-offset no inm-iat-step"
INM_ATTRS = ("inm_mode", "inm_eq_inp_mode", "ins_sensitivity", "inm_cluster_cont", "inm_iat_offset", "inm_iat_step")


class _Conn(object):
    def __init__(self, text):
        self.text, self.commands = text, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        return self.text


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
        conn = _Conn(dedent(text))
        self.facts_connection.return_value = conn
        return conn

    def run_state(self, state, changed, **args):
        set_module_args(dict(args, state=state), ignore_provider_arg)
        return self.execute_module(changed=changed)


# ---------------------------------------------------------------- templates

def test_inm_template_packed_line_and_defaults():
    got = Xdsl_inmTemplate(lines=[
        "configure xdsl imp-noise-sensor near-end 1/1/3/1 " + INM_DEFAULTS,
        "configure xdsl imp-noise-sensor far-end 1/1/3/1 inm-mode 2 inm-eq-inp-mode 1 ins-sensitivity 10 "
        "inm-cluster-cont 4 inm-iat-offset 5 inm-iat-step 6",
        "xdsl imp-noise-sensor near-end 1/1/3/2 inm-iat-step 3",
    ]).parse()
    assert got["near_end"]["1/1/3/1"] == {"name": "1/1/3/1"}
    assert got["near_end"]["1/1/3/2"] == {"name": "1/1/3/2", "inm_iat_step": "3"}
    assert got["far_end"]["1/1/3/1"] == {
        "name": "1/1/3/1", "inm_mode": "2", "inm_eq_inp_mode": "1", "ins_sensitivity": "10",
        "inm_cluster_cont": "4", "inm_iat_offset": "5", "inm_iat_step": "6",
    }


def test_parse_attributes_reports_unknown_tokens():
    entry = {}
    unknown = parse_attributes("dpbo-profile 3 bogus no other", entry, {"dpbo-profile": "dpbo_profile"})
    assert entry == {"dpbo_profile": "3"}
    assert unknown == ["bogus", "no", "other"]


def test_inm_render_set_and_reset():
    assert Xdsl_inmTemplate.render_attr("near_end", {"name": "1/1/3/1", "inm_iat_offset": "5"}, "inm_iat_offset") == \
        "configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-iat-offset 5"
    assert Xdsl_inmTemplate.render_attr("far_end", {"name": "1/1/3/1"}, "inm_mode") == \
        "configure xdsl imp-noise-sensor far-end 1/1/3/1 no inm-mode"


def test_onts_and_system_templates():
    onts = Xdsl_ontsTemplate(lines=[
        "configure xdsl ont interface 1/1/2/1/1 no dpbo-profile",
        "configure xdsl ont interface 1/1/2/1/2 dpbo-profile 3",
    ]).parse()
    assert onts == {"1/1/2/1/1": {"ont_idx": "1/1/2/1/1"}, "1/1/2/1/2": {"ont_idx": "1/1/2/1/2", "dpbo_profile": "3"}}
    assert Xdsl_systemTemplate(lines=["configure xdsl system auto-port-reset no enable"]).parse() == \
        {"auto_port_reset": {"enable": False}}
    assert Xdsl_systemTemplate(lines=["configure xdsl system auto-port-reset enable"]).parse() == \
        {"auto_port_reset": {"enable": True}}


PREFIXES = {
    "configure xdsl imp-noise-sensor ": Xdsl_inmTemplate,
    "configure xdsl ont interface ": Xdsl_ontsTemplate,
    "configure xdsl system ": Xdsl_systemTemplate,
}


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_every_capture_line_of_the_regions_parses():
    """Every line of the three prefixes in the detail capture parses completely."""

    counts = dict((prefix, 0) for prefix in PREFIXES)
    for line in CAPTURE.read_text().splitlines():
        for prefix, template in PREFIXES.items():
            if not line.startswith(prefix):
                continue
            counts[prefix] += 1
            assert template(lines=[line]).parse(), line
            # every clause is understood: the rest after the identity leaves no unknown tokens
            if template is Xdsl_inmTemplate:
                rest = re.sub(r"^configure xdsl imp-noise-sensor (near|far)-end \S+ ?", "", line)
                assert parse_attributes(rest, {}, dict((c, a) for a, c in INM_CLI)) == [], line
            elif template is Xdsl_ontsTemplate:
                rest = re.sub(r"^configure xdsl ont interface \S+ ?", "", line)
                assert parse_attributes(rest, {}, {"dpbo-profile": "dpbo_profile"}) == [], line
            else:
                rest = re.sub(r"^configure xdsl system auto-port-reset ?", "", line)
                assert parse_attributes(rest, {}, {"enable": "enable"}, ("enable",)) == [], line
    assert counts == {
        "configure xdsl imp-noise-sensor ": 192,
        "configure xdsl ont interface ": 75,
        "configure xdsl system ": 1,
    }


# ---------------------------------------------------------------- isam_xdsl_inm

class TestIsamXdslInm(_Base):
    module = isam_xdsl_inm

    DEVICE = """
        configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-mode inm-eq-inp-mode 1 no ins-sensitivity no inm-cluster-cont inm-iat-offset 5 no inm-iat-step
        configure xdsl imp-noise-sensor near-end 1/1/3/2 %s
        configure xdsl imp-noise-sensor far-end 1/1/3/1 inm-cluster-cont 4
    """ % INM_DEFAULTS

    def test_parsed(self):
        parsed = self.run_state("parsed", False, running_config=dedent(self.DEVICE))["parsed"]
        assert {"name": "1/1/3/1", "inm_eq_inp_mode": "1", "inm_iat_offset": "5"} in parsed["near_end"]
        assert {"name": "1/1/3/2"} in parsed["near_end"]
        assert parsed["far_end"] == [{"name": "1/1/3/1", "inm_cluster_cont": "4"}]

    def test_rendered_is_packed_per_sensor(self):
        rendered = self.run_state("rendered", False, config={
            "near_end": [{"name": "1/1/3/1", "inm_eq_inp_mode": 1, "inm_iat_offset": 5}],
            "far_end": [{"name": "1/1/3/1", "inm_mode": "1"}],
        })["rendered"]
        assert rendered == [
            "configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-eq-inp-mode 1 inm-iat-offset 5",
            "configure xdsl imp-noise-sensor far-end 1/1/3/1 inm-mode 1",
        ]

    def test_round_trip(self):
        config = {
            "near_end": [{"name": "1/1/3/1", "inm_mode": "1", "inm_eq_inp_mode": "2", "ins_sensitivity": "3",
                          "inm_cluster_cont": "4", "inm_iat_offset": "5", "inm_iat_step": "6"}],
            "far_end": [{"name": "1/1/3/2", "inm_iat_step": "1"}],
        }
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        parsed = self.run_state("parsed", False, running_config="\n".join(rendered))["parsed"]
        assert parsed == config

    def test_merged_idempotent(self):
        self.device(self.DEVICE)
        self.run_state("merged", False, config={
            "near_end": [{"name": "1/1/3/1", "inm_eq_inp_mode": "1", "inm_iat_offset": "5"}],
            "far_end": [{"name": "1/1/3/1", "inm_cluster_cont": "4"}],
        })

    def test_merged_changes_only_changed_attr(self):
        self.device(self.DEVICE)
        result = self.run_state("merged", True, config={
            "near_end": [{"name": "1/1/3/1", "inm_eq_inp_mode": "1", "inm_iat_offset": "7"}],
        })
        assert result["commands"] == ["configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-iat-offset 7"]

    def test_replaced_resets_unlisted_attrs(self):
        self.device(self.DEVICE)
        result = self.run_state("replaced", True, config={
            "near_end": [{"name": "1/1/3/1", "inm_iat_offset": "5"}],
        })
        assert result["commands"] == ["configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-eq-inp-mode"]

    def test_overridden_resets_other_sensors(self):
        self.device(self.DEVICE)
        result = self.run_state("overridden", True, config={
            "near_end": [{"name": "1/1/3/1", "inm_eq_inp_mode": "1", "inm_iat_offset": "5"}],
        })
        assert result["commands"] == ["configure xdsl imp-noise-sensor far-end 1/1/3/1 no inm-cluster-cont"]

    def test_deleted_named(self):
        self.device(self.DEVICE)
        result = self.run_state("deleted", True, config={"near_end": [{"name": "1/1/3/1"}]})
        assert result["commands"] == [
            "configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-eq-inp-mode no inm-iat-offset",
        ]

    def test_deleted_all(self):
        self.device(self.DEVICE)
        result = self.run_state("deleted", True)
        assert result["commands"] == [
            "configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-eq-inp-mode no inm-iat-offset",
            "configure xdsl imp-noise-sensor far-end 1/1/3/1 no inm-cluster-cont",
        ]

    def test_deleted_defaults_is_idempotent(self):
        self.device("configure xdsl imp-noise-sensor near-end 1/1/3/2 %s\n" % INM_DEFAULTS)
        self.run_state("deleted", False)

    def test_gathered_targeted_reads_only_named(self):
        conn = self.device(self.DEVICE)
        self.run_state("gathered", False, config={"far_end": [{"name": "1/1/3/1"}]})
        assert conn.commands == ["info configure xdsl imp-noise-sensor far-end 1/1/3/1 flat"]

    def test_gathered_whole(self):
        conn = self.device(self.DEVICE)
        self.run_state("gathered", False)
        assert conn.commands == ["info configure xdsl imp-noise-sensor flat"]


# ---------------------------------------------------------------- isam_xdsl_onts

class TestIsamXdslOnts(_Base):
    module = isam_xdsl_onts

    DEVICE = """
        configure xdsl ont interface 1/1/2/1/1 dpbo-profile 3
        configure xdsl ont interface 1/1/2/1/100 no dpbo-profile
        configure xdsl ont interface 1/1/2/2/100 dpbo-profile 4
    """

    def test_parsed(self):
        parsed = self.run_state("parsed", False, running_config=dedent(self.DEVICE))["parsed"]
        assert parsed == [
            {"ont_idx": "1/1/2/1/1", "dpbo_profile": "3"},
            {"ont_idx": "1/1/2/1/100"},
            {"ont_idx": "1/1/2/2/100", "dpbo_profile": "4"},
        ]

    def test_round_trip(self):
        config = [{"ont_idx": "1/1/2/1/1", "dpbo_profile": "3"}]
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        assert rendered == ["configure xdsl ont interface 1/1/2/1/1 dpbo-profile 3"]
        assert self.run_state("parsed", False, running_config="\n".join(rendered))["parsed"] == config

    def test_merged_idempotent(self):
        self.device(self.DEVICE)
        self.run_state("merged", False, config=[{"ont_idx": "1/1/2/1/1", "dpbo_profile": "3"}])

    def test_merged_changes(self):
        self.device(self.DEVICE)
        result = self.run_state("merged", True, config=[{"ont_idx": "1/1/2/1/100", "dpbo_profile": "1"}])
        assert result["commands"] == ["configure xdsl ont interface 1/1/2/1/100 dpbo-profile 1"]

    def test_replaced(self):
        self.device(self.DEVICE)
        result = self.run_state("replaced", True, config=[{"ont_idx": "1/1/2/1/1"}])
        assert result["commands"] == ["configure xdsl ont interface 1/1/2/1/1 no dpbo-profile"]

    def test_overridden(self):
        self.device(self.DEVICE)
        result = self.run_state("overridden", True, config=[{"ont_idx": "1/1/2/1/1", "dpbo_profile": "3"}])
        assert result["commands"] == ["configure xdsl ont interface 1/1/2/2/100 no dpbo-profile"]

    def test_deleted_named_and_all(self):
        self.device(self.DEVICE)
        result = self.run_state("deleted", True, config=[{"ont_idx": "1/1/2/2/100"}])
        assert result["commands"] == ["configure xdsl ont interface 1/1/2/2/100 no dpbo-profile"]
        result = self.run_state("deleted", True)
        assert result["commands"] == [
            "configure xdsl ont interface 1/1/2/1/1 no dpbo-profile",
            "configure xdsl ont interface 1/1/2/2/100 no dpbo-profile",
        ]

    def test_gathered_targeted(self):
        conn = self.device(self.DEVICE)
        self.run_state("gathered", False, config=[{"ont_idx": "1/1/2/1/1"}])
        assert conn.commands == ["info configure xdsl ont interface 1/1/2/1/1 flat"]


# ---------------------------------------------------------------- isam_xdsl_system

class TestIsamXdslSystem(_Base):
    module = isam_xdsl_system

    def test_parsed_and_round_trip(self):
        parsed = self.run_state("parsed", False, running_config="configure xdsl system auto-port-reset no enable")["parsed"]
        assert parsed == {"auto_port_reset": {"enable": False}}
        config = {"auto_port_reset": {"enable": True}}
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        assert rendered == ["configure xdsl system auto-port-reset enable"]
        assert self.run_state("parsed", False, running_config=rendered[0])["parsed"] == config

    def test_merged_idempotent_detail_and_plain(self):
        self.device("configure xdsl system auto-port-reset no enable\n")
        self.run_state("merged", False, config={"auto_port_reset": {"enable": False}})
        # output without detail omits the default
        conn = self.device("")
        self.run_state("merged", False, config={"auto_port_reset": {"enable": False}})
        assert conn.commands == ["info configure xdsl system flat"]

    def test_merged_changes(self):
        self.device("configure xdsl system auto-port-reset no enable\n")
        result = self.run_state("merged", True, config={"auto_port_reset": {"enable": True}})
        assert result["commands"] == ["configure xdsl system auto-port-reset enable"]

    def test_deleted_resets(self):
        self.device("configure xdsl system auto-port-reset enable\n")
        result = self.run_state("deleted", True)
        assert result["commands"] == ["configure xdsl system auto-port-reset no enable"]
        self.device("configure xdsl system auto-port-reset no enable\n")
        self.run_state("deleted", False)

    def test_replaced(self):
        self.device("configure xdsl system auto-port-reset enable\n")
        result = self.run_state("replaced", True, config={"auto_port_reset": {"enable": False}})
        assert result["commands"] == ["configure xdsl system auto-port-reset no enable"]


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_lines_are_all_matched_by_the_snapshot_tracker():
    """gather_configuration path: no 'unmatched configuration' warning for these regions."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts import facts_base

    data = CAPTURE.read_text()
    for prefix, template in PREFIXES.items():
        selected = [line for line in data.splitlines() if line.startswith(prefix)]
        with facts_base.track_network_template_matches() as matched:
            template(lines=selected).parse()
        assert matched.observed
        assert set(selected) <= set(matched), prefix


class TestCaptureParsed(_Base):
    module = isam_xdsl_inm

    @pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
    def test_parsed_capture(self):
        lines = [line for line in CAPTURE.read_text().splitlines() if line.startswith("configure xdsl imp-noise-sensor ")]
        parsed = self.run_state("parsed", False, running_config="\n".join(lines))["parsed"]
        assert len(parsed["near_end"]) == 96 and len(parsed["far_end"]) == 96
        assert all(set(entry) == {"name"} for entry in parsed["near_end"] + parsed["far_end"])

    @pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
    def test_parsed_capture_onts_and_system(self):
        text = CAPTURE.read_text().splitlines()
        self.module = isam_xdsl_onts
        onts = [line for line in text if line.startswith("configure xdsl ont interface ")]
        assert len(self.run_state("parsed", False, running_config="\n".join(onts))["parsed"]) == 75
        self.module = isam_xdsl_system
        system = [line for line in text if line.startswith("configure xdsl system ")]
        assert self.run_state("parsed", False, running_config="\n".join(system))["parsed"] == {"auto_port_reset": {"enable": False}}
