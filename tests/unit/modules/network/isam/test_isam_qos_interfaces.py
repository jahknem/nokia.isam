from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_qos_interfaces
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


QOS_CONFIG = dedent(
    """
    configure qos
    #-------------------------------------------------------------------------------
    echo "qos"
    #-------------------------------------------------------------------------------
    interface 1/1/2/1/1/1/1
      scheduler-node name:NGLT_Default
      cac-profile name:FD_ONTUniVideo
      ds-num-rem-queue not-applicable
      us-num-queue not-applicable
      oper-weight 50
      oper-rate 0
      mc-scheduler-node none
      bc-scheduler-node none
      queue 0
        priority 6
        weight 34
        oper-weight 34
        queue-profile name:NGLT_Default
        shaper-profile none
      exit
      upstream-queue 0
        bandwidth-profile name:GPONqpp1000Mbps
        bandwidth-sharing uni-sharing
      exit
    exit
    #-------------------------------------------------------------------------------
    """
)

QOS_CONFIG_WITH_QUEUE_SIBLING = QOS_CONFIG.replace(
    "    exit\n    #-------------------------------------------------------------------------------",
    "    queue 1\n"
    "      priority 7\n"
    "      queue-profile name:Sibling\n"
    "    exit\n"
    "    #-------------------------------------------------------------------------------",
)

QOS_SCOPED_CONFIG = dedent(
    """
    configure qos interface 1/1/5/1/1/1/1 scheduler-node name:NGLT_Default cac-profile name:FD_ONTUniVideo ds-num-rem-queue not-applicable us-num-queue not-applicable oper-weight 50 oper-rate 0 mc-scheduler-node none bc-scheduler-node none
    configure qos interface 1/1/5/1/1/1/1 upstream-queue 0 bandwidth-profile name:GPONqpp600Mbps bandwidth-sharing uni-sharing
    #-------------------------------------------------------------------------------
    """
)


class TestIsamQosInterfacesModule(TestIsamModule):
    module = isam_qos_interfaces

    def setUp(self):
        super(TestIsamQosInterfacesModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_interfaces.qos_interfaces.Qos_interfacesFacts.get_config"
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
        super(TestIsamQosInterfacesModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_config.stop()

    def test_isam_qos_interfaces_parsed(self):
        set_module_args(dict(running_config=QOS_CONFIG, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        parsed = result["parsed"][0]

        self.assertEqual(parsed["name"], "1/1/2/1/1/1/1")
        self.assertEqual(parsed["scheduler_node"], "name:NGLT_Default")
        self.assertEqual(parsed["cac_profile"], "name:FD_ONTUniVideo")
        self.assertEqual(parsed["queue"][0]["priority"], 6)
        self.assertEqual(parsed["queue"][0]["queue_profile"], "name:NGLT_Default")
        self.assertEqual(parsed["upstream_queue"][0]["bandwidth_profile"], "name:GPONqpp1000Mbps")

    def test_isam_qos_interfaces_gathered(self):
        self.get_config.return_value = QOS_CONFIG
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        gathered = result["gathered"][0]

        self.assertEqual(gathered["name"], "1/1/2/1/1/1/1")
        self.assertEqual(gathered["oper_weight"], 50)
        self.assertEqual(gathered["upstream_queue"][0]["bandwidth_sharing"], "uni-sharing")

    def test_isam_qos_interfaces_gathered_scoped_compact_config(self):
        self.get_config.return_value = QOS_SCOPED_CONFIG
        set_module_args(
            dict(config=[dict(name="1/1/5/1/1/1/1")], state="gathered"),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)

        self.assertEqual(result["gathered"][0]["name"], "1/1/5/1/1/1/1")
        self.assertEqual(
            result["gathered"][0]["upstream_queue"][0]["bandwidth_profile"],
            "name:GPONqpp600Mbps",
        )

    def test_isam_qos_interfaces_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/8/28",
                        cac_profile="name:FD_Default",
                        queue=[dict(id=0, shaper_profile="name:qssShaperDN920Mbps")],
                        upstream_queue=[dict(id=0, bandwidth_profile="name:GPONqpp1000Mbps")],
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            set(result["rendered"]),
            set(
                [
                    "configure qos interface 1/1/8/28 cac-profile name:FD_Default",
                    "configure qos interface 1/1/8/28 queue 0 shaper-profile name:qssShaperDN920Mbps",
                    "configure qos interface 1/1/8/28 upstream-queue 0 bandwidth-profile name:GPONqpp1000Mbps",
                ]
            ),
        )

    def test_isam_qos_interfaces_renders_compact_queue_commands(self):
        set_module_args(
            dict(
                config=[{
                    "name": "1/1/8/28",
                    "queue": [{
                        "id": 0,
                        "priority": 6,
                        "weight": 34,
                        "oper_weight": 34,
                        "queue_profile": "name:NGLT_Default",
                        "shaper_profile": "none",
                    }],
                    "upstream_queue": [{
                        "id": 4,
                        "weight": 5,
                        "bandwidth_profile": "name:GPONqpp600Mbps",
                        "bandwidth_sharing": "uni-sharing",
                    }],
                }],
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], [
            # oper-weight is derived by the device and never rendered.
            "configure qos interface 1/1/8/28 queue 0 priority 6 weight 34 queue-profile name:NGLT_Default shaper-profile none",
            "configure qos interface 1/1/8/28 upstream-queue 4 weight 5 bandwidth-profile name:GPONqpp600Mbps bandwidth-sharing uni-sharing",
        ])

    def test_isam_qos_interfaces_merged_idempotent(self):
        self.get_config.return_value = QOS_CONFIG
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/2/1/1/1/1",
                        cac_profile="name:FD_ONTUniVideo",
                        queue=[dict(id=0, priority=6, queue_profile="name:NGLT_Default")],
                        upstream_queue=[dict(id=0, bandwidth_profile="name:GPONqpp1000Mbps")],
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_qos_interfaces_merged(self):
        self.get_config.return_value = QOS_CONFIG
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/2/1/1/1/1",
                        queue=[dict(id=0, shaper_profile="name:qssShaperDN920Mbps")],
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure qos interface 1/1/2/1/1/1/1 queue 0 shaper-profile name:qssShaperDN920Mbps"],
        )

    def test_isam_qos_interfaces_deleted_queue_preserves_queue_siblings(self):
        self.get_config.return_value = QOS_CONFIG_WITH_QUEUE_SIBLING
        set_module_args(
            dict(
                config=[{
                    "name": "1/1/2/1/1/1/1",
                    "queue": [{"id": 0}],
                }],
                state="deleted",
            ),
            ignore_provider_arg,
        )
        # The documented downstream queue grammar has no removal form. Do not
        # invent "no priority"/"no queue-profile"; these disappear with the UNI.
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
        self.assertFalse(any("queue 1" in command for command in result["commands"]))

    def test_isam_qos_interfaces_deleted_scheduler_preserves_queues(self):
        self.get_config.return_value = QOS_CONFIG_WITH_QUEUE_SIBLING
        set_module_args(
            dict(
                config=[{
                    "name": "1/1/2/1/1/1/1",
                    "scheduler_node": "name:NGLT_Default",
                }],
                state="deleted",
            ),
            ignore_provider_arg,
        )
        # The device refuses to remove the scheduler node of an interface with
        # queues (QOS MGT error 52, lab ISAM): it is kept, with a warning.
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_qos_interfaces_replaced_overridden_keep_scheduler_with_queues(self):
        # replaced/overridden follow the deleted rule: an interface with downstream
        # queues keeps its scheduler node (QOS MGT error 52, lab ISAM), with a warning.
        for state, config in (
            ("replaced", [{"name": "1/1/2/1/1/1/1", "cac_profile": "name:Other"}]),
            ("overridden", [{"name": "1/1/2/1/1/1/1", "cac_profile": "name:Other"}]),
            ("overridden", [{"name": "1/1/9/1/1/1/1", "cac_profile": "name:Other"}]),
        ):
            self.get_config.return_value = QOS_CONFIG
            set_module_args(dict(config=config, state=state), ignore_provider_arg)
            with patch.object(isam_qos_interfaces.AnsibleModule, "warn") as warn:
                result = self.execute_module(changed=True)
            self.assertFalse(any("scheduler-node" in command for command in result["commands"]),
                             (state, result["commands"]))
            self.assertTrue(any("scheduler-node" in call[0][0] for call in warn.call_args_list), state)


# -- settings an interface kind never accepts (live write DS-LIN-TEST-01 2026-11-25) --------

from .module_runner import run_module  # noqa: E402
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_interfaces.qos_interfaces import (  # noqa: E402
    refused_settings,
    without_read_only,
)

ONT, UNI = "1/1/5/1/3", "1/1/5/1/3/1/1"


def test_qos_settings_a_kind_never_accepts_are_refused_before_writing():
    # CAC profile not on an ONT, scheduler-node not on a VLAN port, upstream queue count only on an ONT.
    assert [f for f, _ in refused_settings("ont:" + ONT, {"cac_profile": "name:X"}, {})] == ["cac_profile"]
    assert [f for f, _ in refused_settings("vlan:%s:10" % UNI, {"scheduler_node": "name:N"}, {})] == ["scheduler_node"]
    assert [f for f, _ in refused_settings(UNI, {"us_num_queue": 8, "cac_profile": "name:X"}, {})] == ["us_num_queue"]
    # Unset values, values already on the device and unknown kinds are never refused.
    assert refused_settings("vlan:%s:10" % UNI, {"gem_sharing": "not-applicable", "mc_scheduler_node": "none",
                                                 "ds_queue_sharing": False}, {}) == []
    assert refused_settings("ont:" + ONT, {"cac_profile": "name:X"}, {"cac_profile": "name:X"}) == []
    assert refused_settings("lt:1/1/8", {"us_num_queue": 8}, {}) == []
    # A LAG shows ds-num-queue 8 but refuses to set it (error 45): never sent, never refused.
    assert refused_settings("1/1/8/6", {"ds_num_queue": "8"}, {}) == []
    assert refused_settings("1/1/8/6", {"ds_num_queue": "8"}, {"ds_num_queue": "8"}) == []
    assert [f for f, _ in refused_settings("1/1/8/6", {"ds_num_queue": "4"}, {"ds_num_queue": "8"})] == ["ds_num_queue"]
    assert without_read_only("1/1/8/6", {"name": "1/1/8/6", "ds_num_queue": "8"}, {}) == {"name": "1/1/8/6"}
    assert without_read_only("1/1/8/6", {"name": "1/1/8/6"}, {"ds_num_queue": "8"}) == {"name": "1/1/8/6", "ds_num_queue": "8"}
    assert without_read_only("pon:1/1/6/16", {"ds_num_queue": "8"}, {}) == {"ds_num_queue": "8"}
    # A bare port address (DSL line or LAG): upstream queue count only on an ONT (error 48).
    assert [f for f, _ in refused_settings("1/1/8/6", {"us_num_queue": 8}, {})] == ["us_num_queue"]
    assert refused_settings("1/1/8/6", {"scheduler_node": "name:N", "cac_profile": "name:C"}, {}) == []


def test_a_refused_setting_fails_before_anything_is_rendered_or_sent(monkeypatch):
    # QOS MGT error 42: a CAC profile cannot be assigned to an ONT interface.
    for state, device in (("rendered", None), ("merged", "")):
        args = {"state": state, "config": [{"name": "ont:" + ONT, "cac_profile": "name:FD_Default"}]}
        result = run_module(monkeypatch, "isam_qos_interfaces", args, device) if device is not None else \
            run_module(monkeypatch, "isam_qos_interfaces", args)
        assert result.get("failed") and "cac_profile" in result["msg"] and "error 42" in result["msg"], result
        assert not result.get("commands") and not result.get("rendered")


LAG_DEVICE = "\n".join([
    "configure qos interface 1/1/8/6 ds-num-queue 8",
    "configure qos interface ont:%s us-num-queue 8" % ONT,
]) + "\n"
GATHERED = [{"name": "1/1/8/6", "ds_num_queue": "8"}, {"name": "ont:" + ONT, "us_num_queue": "8"}]


def test_a_value_a_lag_only_displays_never_turns_into_a_command(monkeypatch):
    # Every LAG shows ds-num-queue 8 and refuses to set it (QOS MGT error 45). Feeding the
    # gathered entries back, or merging only the ONT (merged pulls every device entry in),
    # must stay without commands -- neither a set nor a 'no ds-num-queue'.
    for state, config in (("replaced", GATHERED), ("overridden", GATHERED), ("merged", GATHERED),
                          ("merged", GATHERED[1:]), ("replaced", [{"name": "1/1/8/6"}])):
        result = run_module(monkeypatch, "isam_qos_interfaces", {"state": state, "config": config}, LAG_DEVICE)
        assert not result.get("failed"), (state, result.get("msg"))
        assert result["commands"] == [], (state, config, result["commands"])


def test_a_different_value_a_lag_only_displays_is_refused_not_dropped(monkeypatch):
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "replaced", "config": [
        {"name": "1/1/8/6", "ds_num_queue": "4"}]}, LAG_DEVICE)
    assert result.get("failed") and "ds_num_queue" in result["msg"] and "error 45" in result["msg"], result
    assert not result.get("commands")


def test_a_value_a_lag_only_displays_is_not_rendered_without_a_device(monkeypatch):
    # Copying a gathered LAG entry renders everything else, skips ds-num-queue and says so.
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "rendered", "config": [
        {"name": "1/1/8/6", "ds_num_queue": "8", "cac_profile": "name:FD_Default"}]})
    assert not result.get("failed"), result.get("msg")
    assert result["rendered"] == ["configure qos interface 1/1/8/6 cac-profile name:FD_Default"]
    assert any("ds_num_queue" in w for w in result["_warnings"]), result["_warnings"]
