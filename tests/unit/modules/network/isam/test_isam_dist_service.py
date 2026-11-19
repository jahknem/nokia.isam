from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_dist_service
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamDistServiceModule(TestIsamModule):
    module = isam_dist_service

    def setUp(self):
        super(TestIsamDistServiceModule, self).setUp()
        self.connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        ).start()
        self.get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dist_service.dist_service.Isam_dist_serviceFacts.get_config"
        ).start()

    def tearDown(self):
        super(TestIsamDistServiceModule, self).tearDown()
        patch.stopall()

    def test_rendered(self):
        set_module_args(dict(state="rendered", config=[dict(name="100", service_type="epipe", qos_profile="gold")]), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure dist-service 100 service-type epipe", "configure dist-service 100 qos-profile gold"])

    def test_parsed_flat_and_defaults(self):
        set_module_args(dict(state="parsed", running_config=dedent("""\
            configure dist-service 100 service-type epipe
            configure dist-service 100 qos-profile gold
            configure dist-service 101 no qos-profile
        """)), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [dict(name="100", service_type="epipe", qos_profile="gold"), dict(name="101")])  # defaults (apipe, none) are not reported

    def test_gathered_hierarchical_config(self):
        self.get_config.return_value = dedent("""\
            configure dist-service 100
              service-type epipe
              qos-profile gold
            exit
        """)
        set_module_args(dict(state="gathered"), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [dict(name="100", service_type="epipe", qos_profile="gold")])

    def test_merged_check_mode(self):
        self.get_config.return_value = "configure dist-service 100 service-type epipe"
        set_module_args(dict(state="merged", config=[dict(name="100", service_type="epipe", qos_profile="gold")]), True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure dist-service 100 qos-profile gold"])

    def test_deleted_check_mode(self):
        self.get_config.return_value = "\n".join([
            "configure dist-service 100 service-type epipe",
            "configure dist-service 100 qos-profile gold",
            "configure dist-service 200 service-type epipe",
            "configure dist-service 200 qos-profile silver",
        ])
        set_module_args(dict(state="deleted", config=[dict(name="100")]), True)
        result = self.execute_module(changed=True)
        # the identity removes the service (lab ISAM: "configure no dist-service <id>"); the sibling stays
        self.assertEqual(result["commands"], ["configure no dist-service 100"])


def _ds(monkeypatch, state, config, running):
    from .module_runner import run_module

    return run_module(monkeypatch, "isam_dist_service", {"state": state, "config": config}, running)


def test_bare_service_is_read_and_removed(monkeypatch):
    """Lab ISAM: a refused create left a bare 'configure dist-service <id>' the module could not see."""
    running = "configure dist-service 2147483000\n"
    assert _ds(monkeypatch, "gathered", None, running)["gathered"] == [{"name": "2147483000"}]
    assert _ds(monkeypatch, "deleted", [{"name": "2147483000"}], running)["commands"] == [
        "configure no dist-service 2147483000"]


def test_merged_does_not_inject_defaults_and_named_delete_keeps_the_rest(monkeypatch):
    running = "configure dist-service 100 service-type epipe qos-profile gold\n"
    assert _ds(monkeypatch, "merged", [{"name": "100", "qos_profile": "silver"}], running)["commands"] == [
        "configure dist-service 100 qos-profile silver"]
    assert _ds(monkeypatch, "deleted", [{"name": "100", "qos_profile": "gold"}], running)["commands"] == [
        "configure dist-service 100 no qos-profile"]
    assert _ds(monkeypatch, "overridden", [{"name": "200"}], running)["commands"] == [
        "configure no dist-service 100", "configure dist-service 200"]


def test_targeted_gathered_finds_a_service_with_only_defaults(monkeypatch):
    """Lab ISAM: the single read of a bare service prints only the header; flat detail shows it."""
    device = {"info configure dist-service 2147483000 flat detail":
              "configure dist-service 2147483000 no service-type no qos-profile\n"}
    assert _ds(monkeypatch, "gathered", [{"name": "2147483000"}], device)["gathered"] == [{"name": "2147483000"}]
