"""isam_qos_tca: per-port/queue threshold crossing alarms (composite name+queue)."""
from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_qos_tca
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True


class TestIsamQosTcaModule(TestIsamModule):
    module = isam_qos_tca

    def setUp(self):
        super(TestIsamQosTcaModule, self).setUp()
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
        super(TestIsamQosTcaModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_parsed_defaults_and_values(self):
        running = dedent("""
            configure qos tca 1/1/5/1/3/1/1 queue 0 no tca-enable no load-thresh no dis-frame-th no qpeak-usage-th
            configure qos tca 1/1/5/1/3/1/1 queue 1 tca-enable load-thresh 80 qpeak-usage-th 90
        """)
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        parsed = self.execute_module(changed=False)["parsed"]
        q0 = next(e for e in parsed if e["queue"] == 0)
        q1 = next(e for e in parsed if e["queue"] == 1)
        assert q0["tca_enable"] is False
        assert "load_thresh" not in q0
        assert q1["tca_enable"] is True
        assert q1["load_thresh"] == 80
        assert q1["qpeak_usage_th"] == 90

    def test_rendered(self):
        set_module_args(dict(state="rendered", config=[
            {"name": "1/1/5/1/3/1/1", "queue": 0, "tca_enable": True, "load_thresh": 80},
        ]), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert "configure qos tca 1/1/5/1/3/1/1 queue 0 tca-enable" in rendered
        assert "configure qos tca 1/1/5/1/3/1/1 queue 0 load-thresh 80" in rendered

    def test_merged_idempotent(self):
        class FakeConn:
            def get(self, cmd):
                return "configure qos tca 1/1/5/1/3/1/1 queue 0 tca-enable load-thresh 80\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="merged", config=[
            {"name": "1/1/5/1/3/1/1", "queue": 0, "tca_enable": True, "load_thresh": 80},
        ]), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_merged_changes_only_changed_attr(self):
        class FakeConn:
            def get(self, cmd):
                return "configure qos tca 1/1/5/1/3/1/1 queue 0 tca-enable load-thresh 80\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="merged", config=[
            {"name": "1/1/5/1/3/1/1", "queue": 0, "tca_enable": True, "load_thresh": 90},
        ]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure qos tca 1/1/5/1/3/1/1 queue 0 load-thresh 90"]

    def test_deleted_resets_attributes(self):
        class FakeConn:
            def get(self, cmd):
                return "configure qos tca 1/1/5/1/3/1/1 queue 0 tca-enable load-thresh 80\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="deleted", config=[
            {"name": "1/1/5/1/3/1/1", "queue": 0},
        ]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert "configure qos tca 1/1/5/1/3/1/1 queue 0 no tca-enable" in result["commands"]
        assert "configure qos tca 1/1/5/1/3/1/1 queue 0 no load-thresh" in result["commands"]

    # review M4: tca_enable False is the device default ('no tca-enable', printed for
    # every queue); deleted resets only named attributes and is idempotent.
    def _device(self, text):
        class FakeConn:
            def get(self, cmd):
                return text
        self.get_resource_connection_facts.return_value = FakeConn()

    DEFAULT_QUEUES = (
        "configure qos tca 1/1/6/10 queue 0 no tca-enable no load-thresh no dis-frame-th no qpeak-usage-th\n"
        "configure qos tca 1/1/6/10 queue 1 no tca-enable no load-thresh no dis-frame-th no qpeak-usage-th\n"
    )
    CONFIGURED = "configure qos tca 1/1/6/10 queue 0 tca-enable load-thresh 50 dis-frame-th 10 qpeak-usage-th 90\n"

    def test_deleted_all_on_default_queues_is_idempotent(self):
        self._device(self.DEFAULT_QUEUES)
        set_module_args(dict(state="deleted"), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_deleted_identity_on_default_queue_is_idempotent(self):
        self._device(self.DEFAULT_QUEUES)
        set_module_args(dict(state="deleted", config=[{"name": "1/1/6/10", "queue": 0}]), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_deleted_named_attribute_resets_only_it(self):
        self._device(self.CONFIGURED)
        set_module_args(dict(state="deleted", config=[{"name": "1/1/6/10", "queue": 0, "load_thresh": 50}]),
                        ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure qos tca 1/1/6/10 queue 0 no load-thresh"]

    def test_deleted_identity_resets_all_non_default(self):
        self._device(self.CONFIGURED)
        set_module_args(dict(state="deleted", config=[{"name": "1/1/6/10", "queue": 0}]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure qos tca 1/1/6/10 queue 0 no tca-enable",
            "configure qos tca 1/1/6/10 queue 0 no load-thresh",
            "configure qos tca 1/1/6/10 queue 0 no dis-frame-th",
            "configure qos tca 1/1/6/10 queue 0 no qpeak-usage-th",
        ]

    def test_replaced_and_overridden_default_queues_are_idempotent(self):
        self._device(self.DEFAULT_QUEUES)
        for state in ("replaced", "overridden"):
            set_module_args(dict(state=state, config=[{"name": "1/1/6/10", "queue": 0},
                                                       {"name": "1/1/6/10", "queue": 1}]), ignore_provider_arg)
            self.execute_module(changed=False)

    def test_merged_explicit_false_on_default_is_idempotent(self):
        self._device(self.DEFAULT_QUEUES)
        set_module_args(dict(state="merged", config=[{"name": "1/1/6/10", "queue": 0, "tca_enable": False}]),
                        ignore_provider_arg)
        self.execute_module(changed=False)

    def test_rendered_explicit_false(self):
        set_module_args(dict(state="rendered", config=[{"name": "1/1/6/10", "queue": 0, "tca_enable": False}]),
                        ignore_provider_arg)
        assert self.execute_module(changed=False)["rendered"] == ["configure qos tca 1/1/6/10 queue 0 no tca-enable"]
