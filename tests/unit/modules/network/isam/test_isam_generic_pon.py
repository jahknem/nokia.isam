from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_generic_pon
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.generic_pon.generic_pon import Generic_ponFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import Generic_ponTemplate
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamGenericPonModule(TestIsamModule):
    module = isam_generic_pon

    def setUp(self):
        super(TestIsamGenericPonModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamGenericPonModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_isam_generic_pon_parsed(self):
        running = dedent(
            """\
            configure generic-pon dpinteg-threshold 50
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["dpinteg_threshold"], 50)

    def test_isam_generic_pon_gathered(self):
        sample = dedent(
            """\
            configure generic-pon dpinteg-threshold 75
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["dpinteg_threshold"], 75)

    def test_isam_generic_pon_parses_packed_supported_flags(self):
        # 'no <kw>' is the device default: read as unset (values, not flags; CLI guide)
        running = (
            "configure generic-pon utilization no pon-pmcollect ont-pmcollect enable\n"
            "configure generic-pon ont slid-mode hexa-dec sn-bundle-timer 30 no sw-ver-mis-block no sn-autounlock\n"
            "configure generic-pon alarmflag no ponlos-alarm-ctrl"
        )
        result = Generic_ponTemplate(lines=Generic_ponFacts._split_packed_lines(running)).parse()
        self.assertEqual(result["utilization"], {"ont_pmcollect": "enable"})
        self.assertEqual(result["ont"]["slid_mode"], "hexa-dec")
        self.assertEqual(result["ont"]["sn_bundle_timer"], 30)
        self.assertIsNone(result.get("alarmflag", {}).get("ponlos_alarm_ctrl"))

    def test_isam_generic_pon_parses_utilization_thresholds(self):
        running = (
            "configure generic-pon utilization threshold txmcutilhi 80 "
            "txucdropfrmhi disabled numtcint 60"
        )
        threshold = Generic_ponTemplate(lines=Generic_ponFacts._split_packed_lines(running)).parse()["utilization"]["threshold"]
        # raw template output (netcommon turns numeric strings into ints; the facts type them per argspec)
        self.assertEqual(str(threshold["txmcutilhi"]), "80")
        self.assertEqual(threshold["txucdropfrmhi"], "disabled")
        self.assertEqual(str(threshold["numtcint"]), "60")

    def test_isam_generic_pon_rendered(self):
        set_module_args(
            dict(
                config=dict(dpinteg_threshold=50),
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure generic-pon dpinteg-threshold 50"],
        )

    def test_isam_generic_pon_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)

    def test_isam_generic_pon_dpinteg_threshold_has_no_removal_form(self):
        """CLI guide: 'configure generic-pon dpinteg-threshold <value>', mandatory, no 'no' form."""
        parser = Generic_ponTemplate().get_parser("dpinteg_threshold")
        assert parser.get("no_remval") and "remval" not in parser


GPON_DEVICE = ("configure generic-pon dpinteg-threshold 0\n"
               "configure generic-pon utilization pon-pmcollect pm-enable\n"
               "configure generic-pon utilization threshold txmcutilhi 80\n"
               "configure generic-pon ont slid-mode hexa-dec sn-bundle-timer 30\n")


def _gp(monkeypatch, state, config=None, running=GPON_DEVICE):
    from .module_runner import run_module

    args = {"state": state} if config is None else {"state": state, "config": config}
    return run_module(monkeypatch, "isam_generic_pon", args, running)


def test_values_are_read_and_written_as_values(monkeypatch):
    """Data loss before: slid-mode hexa-dec and sn-bundle-timer 30 were read as True."""
    assert _gp(monkeypatch, "gathered")["gathered"] == {
        "dpinteg_threshold": 0, "utilization": {"pon_pmcollect": "pm-enable", "threshold": {"txmcutilhi": "80"}},
        "ont": {"slid_mode": "hexa-dec", "sn_bundle_timer": 30}}
    assert _gp(monkeypatch, "merged", {"ont": {"sn_bundle_timer": 48}})["commands"] == [
        "configure generic-pon ont sn-bundle-timer 48"]
    assert _gp(monkeypatch, "merged", {"ont": {"slid_mode": "hexa-dec"}})["commands"] == []


def test_deleted_touches_named_sections_and_settings_only(monkeypatch):
    assert _gp(monkeypatch, "deleted", {"utilization": {"pon_pmcollect": "pm-enable"}})["commands"] == [
        "configure generic-pon utilization no pon-pmcollect"]
    assert _gp(monkeypatch, "deleted", {"ont": {}})["commands"] == [
        "configure generic-pon ont no slid-mode no sn-bundle-timer"]
    assert _gp(monkeypatch, "deleted")["commands"] == [
        "configure generic-pon utilization no pon-pmcollect", "configure generic-pon utilization threshold no txmcutilhi",
        "configure generic-pon ont no slid-mode no sn-bundle-timer"]


def test_table_argspec_and_documentation_agree():
    import yaml

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import Generic_ponArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import GENERIC_PON_NODES
    from ansible_collections.nokia.isam.plugins.modules import isam_generic_pon

    spec = Generic_ponArgs.argument_spec["config"]["options"]
    docs = yaml.safe_load(isam_generic_pon.DOCUMENTATION)["options"]["config"]["suboptions"]
    for path, _node, attrs in GENERIC_PON_NODES:
        s, d = spec, docs
        for key in path:
            s, d = s[key]["options"], d[key]["suboptions"]
        assert set(s) - {"threshold"} == set(d) - {"threshold"} == set(option for option, _c, _k, _d in attrs), path
        for option, _cli, kind, _default in attrs:
            assert s[option]["type"] == d[option]["type"] == ("int" if kind == "int" else "str"), (path, option)
