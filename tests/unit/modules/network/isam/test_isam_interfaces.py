from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_interfaces
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamInterfacesModule(TestIsamModule):
    module = isam_interfaces

    def setUp(self):
        super(TestIsamInterfacesModule, self).setUp()

        # Patch resource connection getters across RM, config and facts paths
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
        super(TestIsamInterfacesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_interfaces_parsed(self):
        # test parsed
        running = dedent(
            """
            configure interface port vlan-port:1/1/8/1 admin-up
            configure interface port vlan-port:1/1/8/1 port-type uni
            configure interface port vlan-port:1/1/8/1 user "john_doe"
            configure interface port vlan-port:1/1/8/1 severity major
            """
        )
        set_module_args(
            dict(
                running_config=running,
                state="parsed",
            ),
            ignore_provider_arg,
        )

        parsed = [
            dict(
                id="vlan-port:1/1/8/1",
                **{
                    "admin-up": True,
                    "port-type": "uni",
                    "user": "john_doe",
                    "severity": "major",
                },
            )
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["id"], parsed[0]["id"])  # id
        for k, v in parsed[0].items():
            self.assertEqual(result["parsed"][0].get(k), v)

    def test_isam_interfaces_gathered(self):
        # test gathered
        sample = dedent(
            """
            configure interface port vlan-port:1/1/8/1 admin-up
            configure interface port vlan-port:1/1/8/1 port-type uni
            configure interface port vlan-port:1/1/8/1 user "john_doe"
            configure interface port vlan-port:1/1/8/1 severity major
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()

        set_module_args(dict(state="gathered"), ignore_provider_arg)

        gathered = [
            dict(
                id="vlan-port:1/1/8/1",
                **{
                    "admin-up": True,
                    "port-type": "uni",
                    "user": "john_doe",
                    "severity": "major",
                },
            )
        ]

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"][0]["id"], gathered[0]["id"])  # id
        for k, v in gathered[0].items():
            self.assertEqual(result["gathered"][0].get(k), v)

    def test_isam_interfaces_rendered(self):
        # test rendered
        set_module_args(
            dict(
                config=[
                    dict(
                        id="vlan-port:1/1/8/1",
                        **{
                            "admin-up": True,
                            "port-type": "uni",
                            "user": "john_doe",
                            "severity": "major",
                        },
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        # Verify some representative commands were rendered
        cmds = result.get("rendered", [])
        self.assertTrue(any(cmd.startswith("configure interface port vlan-port:1/1/8/1") for cmd in cmds))
        self.assertTrue(any("admin-up" in cmd for cmd in cmds))
        self.assertTrue(any("port-type uni" in cmd for cmd in cmds))
