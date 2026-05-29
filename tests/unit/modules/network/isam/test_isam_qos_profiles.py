from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_qos_profiles
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamQosProfilesModule(TestIsamModule):
    module = isam_qos_profiles

    def setUp(self):
        super(TestIsamQosProfilesModule, self).setUp()

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
        super(TestIsamQosProfilesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_qos_profiles_parsed(self):
        running = dedent(
            """
            configure qos
            profiles
            queue FD_BEQ red:24:48:80
            exit
            scheduler-node NGLT_Default priority 2 weight 50 shaper-profile none
              mcast-inc-shape no-mcast-shap
            exit
            marker
              d1p FD_Marker_BE default-dot1p 0
              exit
            exit
            policer qpp5Mbps committed-info-rate 5120 committed-burst-size 256000
            exit
            session FD_Voice logical-flow-type pvc
              up-policer name:FD_Pol_Voice
              down-policer name:FD_Pol_Voice
              up-marker name:FD_Marker_Voice
            exit
            aggrqueuesconfig DefaultDnQueuesConfig
              q0-priority 6
            exit
            shaper GPONqssShaperDN10Mbps committed-info-rate 0 committed-burst-size 0
              excess-info-rate 10240
              type singletokenbucketgpon
            exit
            bandwidth GPONqpp5Mbps committed-info-rate 0 assured-info-rate 0 excessive-info-rate 5120
              delay-tolerance 32
            exit
            ingress-qos Default_TC0
              dot1-p0-tc 0
            exit
            rate-limit defaultllid
              total-rate 80
              total-burst 100
            exit
            exit
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        parsed = result.get("parsed", [])
        profiles = {(entry["profile_type"], entry["name"]): entry for entry in parsed}

        self.assertEqual(profiles[("queue", "FD_BEQ")].get("queue-type"), "red:24:48:80")
        self.assertEqual(profiles[("scheduler-node", "NGLT_Default")].get("priority"), 2)
        self.assertEqual(profiles[("scheduler-node", "NGLT_Default")].get("mcast-inc-shape"), "no-mcast-shap")
        self.assertEqual(profiles[("marker-d1p", "FD_Marker_BE")].get("default-dot1p"), 0)
        self.assertEqual(profiles[("policer", "qpp5Mbps")].get("committed-info-rate"), 5120)
        self.assertEqual(profiles[("session", "FD_Voice")].get("up-policer"), "name:FD_Pol_Voice")
        self.assertEqual(profiles[("aggrqueuesconfig", "DefaultDnQueuesConfig")].get("attributes"), ["q0-priority 6"])
        self.assertEqual(profiles[("shaper", "GPONqssShaperDN10Mbps")].get("shaper-type"), "singletokenbucketgpon")
        self.assertEqual(profiles[("bandwidth", "GPONqpp5Mbps")].get("delay-tolerance"), 32)
        self.assertEqual(profiles[("ingress-qos", "Default_TC0")].get("dot1-p0-tc"), 0)
        self.assertEqual(profiles[("rate-limit", "defaultllid")].get("total-rate"), 80)

    def test_isam_qos_profiles_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=[
                    {
                        "profile_type": "queue",
                        "name": "FD_BEQ",
                        "queue-type": "red:24:48:80",
                    }
                ],
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure qos profiles queue FD_BEQ red:24:48:80", result.get("rendered"))

    def test_isam_qos_profiles_gathered_empty(self):
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result.get("gathered"), [])
