from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_link_agg
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamLinkAggModule(TestIsamModule):
    module = isam_link_agg

    def setUp(self):
        super(TestIsamLinkAggModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.link_agg.link_agg.Link_aggFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamLinkAggModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_config.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_isam_link_agg_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", lacp_mode="passive", timeout="short")],
                    groups=[
                        dict(
                            id="1/1/8/10",
                            load_sharing_policy="mac-src-dst",
                            swo_revert="enable",
                            mode="dynamic",
                            master_iwf="auto",
                            ports=["1/1/8/1"],
                        )
                    ],
                ),
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            set(result["rendered"]),
            set(
                [
                    "configure link-agg port 1/1/8/1 passive-lacp short-timeout",
                    "configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst swo-revert enable mode dynamic master-iwf auto",
                    "configure link-agg group 1/1/8/10 port 1/1/8/1",
                ]
            ),
        )

    def test_isam_link_agg_parsed_flat(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """
                    configure link-agg port 1/1/8/1 passive-lacp
                    configure link-agg port 1/1/8/1 short-timeout
                    configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst
                    configure link-agg group 1/1/8/10 swo-revert enable
                    configure link-agg group 1/1/8/10 mode dynamic
                    configure link-agg group 1/1/8/10 master-iwf auto
                    configure link-agg group 1/1/8/10 port 1/1/8/1
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["ports"][0]["id"], "1/1/8/1")
        self.assertEqual(result["parsed"]["ports"][0]["lacp_mode"], "passive")
        self.assertEqual(result["parsed"]["ports"][0]["timeout"], "short")
        self.assertEqual(result["parsed"]["groups"][0]["id"], "1/1/8/10")
        self.assertEqual(result["parsed"]["groups"][0]["ports"], ["1/1/8/1"])

    def test_isam_link_agg_parsed_packed_flat(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """
                    configure link-agg port 1/1/8/1 passive-lacp short-timeout actor-port-prio 32768
                    configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst mode dynamic port 1/1/8/1
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["ports"][0]["lacp_mode"], "passive")
        self.assertEqual(result["parsed"]["ports"][0]["timeout"], "short")
        self.assertEqual(result["parsed"]["ports"][0]["actor_port_prio"], "32768")
        self.assertEqual(result["parsed"]["groups"][0]["mode"], "dynamic")
        self.assertEqual(result["parsed"]["groups"][0]["ports"], ["1/1/8/1"])

    def test_isam_link_agg_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """
            configure link-agg port 1/1/8/1 passive-lacp
            configure link-agg port 1/1/8/1 short-timeout
            configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst
            configure link-agg group 1/1/8/10 swo-revert enable
            configure link-agg group 1/1/8/10 mode dynamic
            configure link-agg group 1/1/8/10 master-iwf auto
            configure link-agg group 1/1/8/10 port 1/1/8/1
            """
        )
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", lacp_mode="passive", timeout="short")],
                    groups=[
                        dict(
                            id="1/1/8/10",
                            load_sharing_policy="mac-src-dst",
                            swo_revert="enable",
                            mode="dynamic",
                            master_iwf="auto",
                            ports=["1/1/8/1"],
                        )
                    ],
                ),
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_link_agg_replaced_port_fields(self):
        self.get_config.return_value = dedent(
            """
            configure link-agg port 1/1/8/1 passive-lacp
            configure link-agg port 1/1/8/1 short-timeout
            configure link-agg port 1/1/8/1 actor-port-prio 32768
            """
        )
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", passive_lacp=True)],
                ),
                state="replaced",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            set(result["commands"]),
            set([
                "configure link-agg port 1/1/8/1 no short-timeout no actor-port-prio",
            ]),
        )


# -- settings without a 'no' form (lab write 2026-11-28, LAG 1/1/6/36, restored) -------------

from .module_runner import run_module  # noqa: E402

_LAG = ("configure link-agg group 1/1/6/36 load-sharing-policy mac-src-dst no max-active-port no swo-threshold "
        "no priority swo-revert enable mode dynamic master-iwf auto\n"
        "configure link-agg group 1/1/6/36 port 1/1/6/36\n")


def test_deleted_resets_policy_and_mode_by_setting_their_defaults(monkeypatch):
    result = run_module(monkeypatch, "isam_link_agg", {"state": "deleted", "config": {"groups": [{"id": "1/1/6/36"}]}}, _LAG)
    assert not result.get("failed"), result.get("msg")
    commands = result["commands"]
    # Packed into one line with the other resets (verified form, lab 2026-11-28).
    line = [c for c in commands if c.startswith("configure link-agg group 1/1/6/36 ") and " port " not in c]
    assert len(line) == 1 and " load-sharing-policy mac-src " in line[0] + " " and line[0].endswith(" mode static"), commands
    assert not [c for c in commands if " no load-sharing-policy" in c or " no mode" in c], commands


def test_a_group_at_its_defaults_gets_no_reset(monkeypatch):
    lag = _LAG.replace("mac-src-dst", "mac-src").replace("mode dynamic", "mode static")
    result = run_module(monkeypatch, "isam_link_agg", {"state": "deleted", "config": {"groups": [{"id": "1/1/6/36"}]}}, lag)
    assert not [c for c in result["commands"] if "load-sharing-policy" in c or " mode " in c], result["commands"]


def test_replaced_omitting_policy_and_mode_returns_them_to_their_defaults(monkeypatch):
    result = run_module(monkeypatch, "isam_link_agg", {"state": "replaced", "config": {"groups": [
        {"id": "1/1/6/36", "ports": ["1/1/6/36"]}]}}, _LAG)
    assert not result.get("failed"), result.get("msg")
    (line,) = result["commands"]
    assert line.startswith("configure link-agg group 1/1/6/36 load-sharing-policy mac-src ") and line.endswith(" mode static"), line
    # A gathered entry fed back stays without commands.
    parsed = run_module(monkeypatch, "isam_link_agg", {"state": "parsed", "running_config": _LAG})["parsed"]
    again = run_module(monkeypatch, "isam_link_agg", {"state": "replaced", "config": parsed}, _LAG)
    assert again["commands"] == [], again["commands"]


def test_settings_at_their_no_form_default_get_no_reset(monkeypatch):
    # _LAG shows 'no max-active-port no swo-threshold no priority' (read as 8/0/0).
    result = run_module(monkeypatch, "isam_link_agg", {"state": "deleted", "config": {"groups": [{"id": "1/1/6/36"}]}}, _LAG)
    assert not [c for c in result["commands"] if "max-active-port" in c or "swo-threshold" in c or "priority" in c], \
        result["commands"]


def test_a_set_value_is_still_reset_with_its_no_form(monkeypatch):
    lag = _LAG.replace("no max-active-port", "max-active-port 4").replace("no priority", "priority 7")
    result = run_module(monkeypatch, "isam_link_agg", {"state": "deleted", "config": {"groups": [{"id": "1/1/6/36"}]}}, lag)
    (line,) = [c for c in result["commands"] if " port " not in c]
    assert " no max-active-port" in line and " no priority" in line and "swo-threshold" not in line, line


def test_removing_a_member_port_stays_its_own_line(monkeypatch):
    lag = _LAG + "configure link-agg group 1/1/6/36 port 1/1/6/35\n"
    result = run_module(monkeypatch, "isam_link_agg", {"state": "replaced", "config": {"groups": [
        {"id": "1/1/6/36", "ports": ["1/1/6/36"], "load_sharing_policy": "mac-src", "mode": "static"}]}}, lag)
    assert "configure link-agg group 1/1/6/36 no port 1/1/6/35" in result["commands"], result["commands"]
    assert all(c == "configure link-agg group 1/1/6/36 no port 1/1/6/35" or " port " not in c for c in result["commands"]), \
        result["commands"]
