"""igmp / mcast-control: package list and system settings (isam_igmp, isam_mcast_control, isam_multicast)."""
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_igmp, isam_mcast_control, isam_multicast
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.multicast.multicast import MulticastFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import (
    MulticastTemplate,
    parse_line,
)

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True
CAPTURE = lab_captures.DETAIL

DEVICE = "\n".join([
    "configure igmp mcast-svc-context Default",
    "configure igmp system query-interval 60 robustness 3 start no forking cdr-export remote-logging",
    "configure igmp system cdr-type periodic period 30",
    "configure igmp package 5 name basic template-name tmpl template-version 2",
    'configure igmp package 7 name "Premium TV"',
    "configure mcast-control mcast-svc-context Default",
    "configure mcast-control system v6-src-ip-address fe80::1 user-mld-version 1 vlan-selection",
    "configure mcast-control package 9 name sports",
]) + "\n"


def _parse(text):
    facts = {"ansible_network_resources": {}}
    MulticastFacts(None).populate_facts(None, facts, text)
    return facts["ansible_network_resources"]


def test_template_parses_packages_and_system():
    got = _parse(DEVICE)
    igmp = got["igmp"]
    assert igmp["packages"] == [
        {"index": 5, "name": "basic", "template_name": "tmpl", "template_version": 2},
        {"index": 7, "name": "Premium TV"},
    ]
    assert igmp["system"]["query_interval"] == 60
    assert igmp["system"]["robustness"] == 3
    assert igmp["system"]["start"] is True
    assert igmp["system"]["forking"] is False
    assert igmp["system"]["cdr_export"] == "remote-logging"
    assert igmp["system"]["cdr_type"] == {"periodic": True, "period": 30}
    assert got["mcast_control"]["packages"] == [{"index": 9, "name": "sports"}]
    assert got["mcast_control"]["system"] == {"v6_src_ip_address": "fe80::1", "user_mld_version": "1", "vlan_selection": True}
    assert got["multicast"]["igmp"]["packages"] == igmp["packages"]


def test_default_packages_are_not_gathered():
    lines = ["configure igmp package 1 no name no template-name no template-version",
             "configure mcast-control package 2 no name no template-name no template-version"]
    assert not MulticastTemplate(lines=lines, module=None).parse()


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_every_package_and_system_line_is_parsed():
    lines = [line.strip() for line in CAPTURE.read_text().splitlines()
             if line.strip().startswith(("configure igmp ", "configure mcast-control "))]
    packages = [line for line in lines if " package " in line]
    assert len(packages) == 2048
    unparsed = []
    for line in lines:
        parsed = parse_line(line)
        if parsed is None or parsed[4]:
            unparsed.append(line)
    # Only the service-context selectors are left; the regex parsers own them.
    assert unparsed == ["configure igmp mcast-svc-context Default", "configure mcast-control mcast-svc-context Default"]
    got = _parse("\n".join(lines))
    assert got["igmp"]["mcast_svc_context"] == "Default"
    assert "packages" not in got["igmp"]  # all 1024 slots are at their defaults on the lab device
    assert got["igmp"]["system"]["start"] is False
    assert got["mcast_control"]["system"]["cdr_type"]["periodic"] is False


class _Base(TestIsamModule):
    def setUp(self):
        super(_Base, self).setUp()
        self.patches = [patch(target) for target in (
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )]
        mocks = [p.start() for p in self.patches]
        self.get_resource_connection_facts = mocks[2]

        class FakeConn(object):
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                prefix = command[len("info "):-len(" flat")]
                return "\n".join(line for line in DEVICE.splitlines() if line.startswith(prefix + " ")) + "\n"

        self.conn = FakeConn()
        self.get_resource_connection_facts.return_value = self.conn

    def tearDown(self):
        super(_Base, self).tearDown()
        for p in self.patches:
            p.stop()

    def run_module(self, changed, **args):
        set_module_args(args, ignore_provider_arg)
        return self.execute_module(changed=changed)


class TestIgmpPackages(_Base):
    module = isam_igmp

    def test_rendered(self):
        rendered = self.run_module(False, state="rendered", config={
            "system": {"query_interval": 60, "verify_checksum": True, "cdr_type": {"period": 30}},
            "packages": [{"index": 3, "name": "Kids TV", "template_version": 1}],
        })["rendered"]
        assert rendered == [
            "configure igmp system verify-checksum query-interval 60",
            "configure igmp system cdr-type period 30",
            'configure igmp package 3 name "Kids TV" template-version 1',
        ]

    def test_round_trip(self):
        config = {"system": {"query_interval": 60, "robustness": 3, "start": True, "cdr_type": {"periodic": True}},
                  "packages": [{"index": 3, "name": "Kids TV", "template_name": "t", "template_version": 1}]}
        rendered = self.run_module(False, state="rendered", config=config)["rendered"]
        parsed = self.run_module(False, state="parsed", running_config="\n".join(rendered))["parsed"]
        assert parsed["system"] == config["system"]
        assert parsed["packages"] == config["packages"]

    def test_merged_idempotent(self):
        self.run_module(False, state="merged", config={
            "system": {"query_interval": 60, "robustness": 3, "start": True, "forking": False,
                       "verify_checksum": False, "cdr_type": {"periodic": True, "period": 30}},
            "packages": [{"index": 5, "name": "basic", "template_name": "tmpl", "template_version": 2},
                         {"index": 7, "name": "Premium TV"}],
        })

    def test_merged_changes_only_differences(self):
        result = self.run_module(True, state="merged", config={
            "system": {"query_interval": 90}, "packages": [{"index": 5, "name": "basic2"}]})
        assert result["commands"] == ["configure igmp system query-interval 90", "configure igmp package 5 name basic2"]

    def test_replaced_resets_omitted_fields_of_listed_package(self):
        result = self.run_module(True, state="replaced", config={"packages": [{"index": 5, "name": "basic"}]})
        assert result["commands"] == ["configure igmp package 5 no template-name no template-version"]

    def test_overridden_resets_unlisted_packages_and_system(self):
        result = self.run_module(True, state="overridden", config={
            "mcast_svc_context": "Default", "packages": [{"index": 5, "name": "basic", "template_name": "tmpl",
                                                          "template_version": 2}]})
        assert result["commands"] == [
            "configure igmp system no query-interval no robustness no start no cdr-export",
            "configure igmp system cdr-type no periodic no period",
            "configure igmp package 7 no name",
        ]

    def test_deleted_named_package_only(self):
        result = self.run_module(True, state="deleted", config={"packages": [{"index": 5}]})
        assert result["commands"] == ["configure igmp package 5 no name no template-name no template-version"]

    def test_deleted_absent_package_is_noop(self):
        self.run_module(False, state="deleted", config={"packages": [{"index": 99}]})

    def test_deleted_system(self):
        result = self.run_module(True, state="deleted", config={"system": {"start": True}})
        assert result["commands"] == [
            "configure igmp system no query-interval no robustness no start no cdr-export",
            "configure igmp system cdr-type no periodic no period",
        ]

    def test_deleted_all(self):
        result = self.run_module(True, state="deleted")
        assert "configure igmp package 5 no name no template-name no template-version" in result["commands"]
        assert 'configure igmp package 7 no name' in result["commands"]
        assert "configure igmp system cdr-type no periodic no period" in result["commands"]

    def test_gathered_targeted_reads_only_the_package(self):
        gathered = self.run_module(False, state="gathered", config={"packages": [{"index": 5}]})["gathered"]
        assert self.conn.commands == ["info configure igmp package 5 flat"]
        assert gathered["packages"] == [{"index": 5, "name": "basic", "template_name": "tmpl", "template_version": 2}]


class TestMcastControlPackages(_Base):
    module = isam_mcast_control

    def test_merged_idempotent_and_change(self):
        self.run_module(False, state="merged", config={
            "system": {"v6_src_ip_address": "fe80::1", "user_mld_version": "1", "vlan_selection": True},
            "packages": [{"index": 9, "name": "sports"}]})
        result = self.run_module(True, state="merged", config={
            "system": {"netw_mld_version": "1", "vlan_selection": False}, "packages": [{"index": 10, "name": "news"}]})
        assert result["commands"] == ["configure mcast-control system netw-mld-version 1 no vlan-selection",
                                      "configure mcast-control package 10 name news"]

    def test_deleted_named_package(self):
        result = self.run_module(True, state="deleted", config={"packages": [{"index": 9}]})
        assert result["commands"] == ["configure mcast-control package 9 no name"]

    def test_gathered_targeted(self):
        gathered = self.run_module(False, state="gathered", config={"packages": [{"index": 9}]})["gathered"]
        assert self.conn.commands == ["info configure mcast-control package 9 flat"]
        assert gathered["packages"] == [{"index": 9, "name": "sports"}]


class TestMulticastPackages(_Base):
    module = isam_multicast

    def test_merged_idempotent(self):
        self.run_module(False, state="merged", config={
            "igmp": {"packages": [{"index": 7, "name": "Premium TV"}], "system": {"robustness": 3}},
            "mcast_control": {"packages": [{"index": 9, "name": "sports"}]}})

    def test_merged_both_families(self):
        result = self.run_module(True, state="merged", config={
            "igmp": {"packages": [{"index": 8, "name": "a"}]},
            "mcast_control": {"system": {"query_interval": 30}}})
        assert result["commands"] == ["configure igmp package 8 name a", "configure mcast-control system query-interval 30"]

    def test_deleted_named_package(self):
        result = self.run_module(True, state="deleted", config={"mcast_control": {"packages": [{"index": 9}]}})
        assert result["commands"] == ["configure mcast-control package 9 no name"]

    def test_gathered_targeted(self):
        gathered = self.run_module(False, state="gathered", config={"igmp": {"packages": [{"index": 7}]}})["gathered"]
        assert self.conn.commands == ["info configure igmp package 7 flat"]
        assert gathered["igmp"]["packages"] == [{"index": 7, "name": "Premium TV"}]
