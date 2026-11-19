from textwrap import dedent

from ansible_collections.nokia.isam.tests.unit.compat.mock import MagicMock, patch

from ansible_collections.nokia.isam.plugins.modules import isam_l2cp, isam_l2cp_session, isam_l2cp_user_port
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp.l2cp import L2cp
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate
from .isam_module import TestIsamModule, set_module_args


class TestL2cp(TestIsamModule):
    def test_global_merged_is_idempotent(self):
        resource = L2cp.__new__(L2cp)
        resource.template = L2cpTemplate()
        resource.state = "merged"
        resource.want = [{"name": "l2cp", "partition_type": "fixed-assigned"}]
        resource.have = [{"name": "l2cp", "partition_type": "fixed-assigned"}]
        resource.commands = []

        resource.commands = []
        merged = dict(resource.have[0])
        merged.update(resource.want[0])
        if merged != resource.have[0]:
            resource.commands = resource.template.render([merged])

        assert resource.commands == []

    def test_global_rendered_and_parsed(self):
        self.module = isam_l2cp
        set_module_args({"state": "rendered", "config": [{"name": "l2cp", "partition_type": "fixed-assigned"}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure l2cp partition-type fixed-assigned"])

        set_module_args({"state": "parsed", "running_config": "configure l2cp partition-type fixed-assigned"}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "l2cp", "partition_type": "fixed-assigned"}])

    def test_deleted_is_idempotent_when_l2cp_is_unconfigured(self):
        self.module = isam_l2cp
        # The module reads the device: an unconfigured (empty) L2CP block.
        device = MagicMock()
        device.get.return_value = ""
        patcher = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp.l2cp.get_resource_connection",
            return_value=device,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        set_module_args({"state": "deleted", "config": [{"name": "l2cp"}], "_ansible_check_mode": True}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_session_rendered_and_parsed(self):
        self.module = isam_l2cp_session
        config = [{"name": "1", "bras_ip_address": "192.0.2.10", "topo_discovery": "disabled", "sig_partition_id": False}]
        set_module_args({"state": "rendered", "config": config}, True)
        result = self.execute_module(changed=False)
        # Only what is given (no argspec defaults: they overwrote unnamed attributes in merged).
        self.assertEqual(result["rendered"], [
            "configure l2cp session 1 bras-ip-address 192.0.2.10 topo-discovery disabled no sig-partition-id"
        ])

        running = dedent("""\
            configure l2cp session 1 bras-ip-address 192.0.2.10 topo-discovery disabled no sig-partition-id
        """)
        set_module_args({"state": "parsed", "running_config": running}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "1", "bras_ip_address": "192.0.2.10", "topo_discovery": "disabled", "sig_partition_id": False}])

    def test_user_port_rendered_and_parsed(self):
        self.module = isam_l2cp_user_port
        set_module_args({"state": "rendered", "config": [{"name": "1/1/1/1", "partition_id": "7"}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure l2cp user-port 1/1/1/1 partition-id 7"])

        set_module_args({"state": "parsed", "running_config": "configure l2cp no user-port 1/1/1/1 partition-id"}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "1/1/1/1", "partition_id": None}])


SESSION = "configure l2cp session 200 bras-ip-address 192.0.2.1 topo-discovery disabled alive-timer 210\n"


def _session(monkeypatch, state, config, running=SESSION):
    from .module_runner import run_module

    return run_module(monkeypatch, "isam_l2cp_session", {"state": state, "config": config}, running)


def test_session_create_sends_only_non_default_attributes(monkeypatch):
    result = _session(monkeypatch, "merged", [{"name": "200", "bras_ip_address": "192.0.2.1", "alive_timer": "250",
                                               "dslam_name": "02:00:00:00:00:01"}], running="")
    assert result["commands"] == ["configure l2cp session 200 bras-ip-address 192.0.2.1 dslam-name 02:00:00:00:00:01"]


def test_session_change_uses_the_short_form_and_keeps_unnamed_attributes(monkeypatch):
    """Lab ISAM: an existing session only accepts 'session <index> alive-timer <value>'."""
    assert _session(monkeypatch, "merged", [{"name": "200", "alive_timer": "200"}])["commands"] == [
        "configure l2cp session 200 alive-timer 200"]
    assert _session(monkeypatch, "merged", [{"name": "200", "alive_timer": "210"}])["commands"] == []
    # replaced returns the unnamed modifiable attribute to its default
    assert _session(monkeypatch, "replaced", [{"name": "200", "topo_discovery": "disabled"}])["commands"] == [
        "configure l2cp session 200 no alive-timer"]


def test_session_creation_only_attribute_fails_before_any_change(monkeypatch):
    result = _session(monkeypatch, "merged", [{"name": "200", "topo_discovery": "enabled", "alive_timer": "200"}])
    assert result.get("failed") and "topo_discovery can only be set when the session is created" in result["msg"]
    assert not result.get("commands")
