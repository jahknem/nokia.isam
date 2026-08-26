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
        self.get_resource_connection.stop()
        self.get_config.stop()

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
        result = self.execute_module(changed=True)
        self.assertTrue(any("queue 0" in command for command in result["commands"]))
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
        result = self.execute_module(changed=True)
        self.assertTrue(any("no scheduler-node" in command for command in result["commands"]))
        self.assertFalse(any("queue " in command for command in result["commands"]))
