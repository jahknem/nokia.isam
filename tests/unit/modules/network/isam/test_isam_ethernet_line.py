from textwrap import dedent
from unittest import result
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ethernet_line.ethernet_line import (
    Ethernet_line,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line import (
    Ethernet_lineFacts,
)
from ansible_collections.isam.isam.plugins.modules import isam_ethernet_line
from ansible_collections.isam.isam.tests.unit.compat.mock import patch
from ansible_collections.isam.isam.tests.unit.modules.utils import AnsibleFailJson

from .isam_module import TestIsamModule, load_fixture, set_module_args
import debugpy


ignore_provider_arg = True

class TestIsamEthernetLineModule(TestIsamModule):
    module = isam_ethernet_line

    def setUp(self):
        super(TestIsamEthernetLineModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.isam.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line.Ethernet_lineFacts.get_config"
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
        super(TestIsamEthernetLineModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_isam_ethernet_line_merged(self):
        # test merged
        self.get_config.return_value = dedent("""configure ethernet
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        echo "ethernet"
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        line 1/1/8/1
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        """)
        set_module_args(
            dict(
                config=[
                    dict(
                        if_index="1/1/8/1",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    ),
                    dict(
                        if_index="1/1/8/2",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure ethernet line 1/1/8/2 port-type uni",
            "configure ethernet line 1/1/8/2 mau 1 type 1000basebx10d",
            "configure ethernet line 1/1/8/2 mau 1 power up",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(set(result["commands"]), set(commands))

    def test_isam_ethernet_line_merged_idempotent(self):
        # test merged idempotent
        self.get_config.return_value = dedent("""configure ethernet
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        echo "ethernet"
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        line 1/1/8/1
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        line 1/1/8/2
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        """)
        set_module_args(
            dict(
                config=[
                    dict(
                        if_index="1/1/8/1",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    ),
                    dict(
                        if_index="1/1/8/2",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )
        commands = []
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], commands)

    def test_isam_ethernet_line_parsed(self):
        # test parsed
        set_module_args(
            dict(
                running_config=dedent("""configure ethernet
                #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                echo "ethernet"
                #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                line 1/1/8/1
                  port-type uni
                  admin-up
                  mau 1
                    type 1000basebx10d
                    power up
                  exit
                exit
                #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                """),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        parsed = [
            dict(
                if_index="1/1/8/1",
                port_type="uni",
                mau=[
                    dict(
                        index=1,
                        mau_type="1000basebx10d",
                        power="up"
                    )
                ]
            )
        ]
        result = self.execute_module(changed=False)
        #self.assertEqual(True, False, f"{dir(result)}\n{len(result)}\n{result}\n")
        self.assertEqual(set(result["parsed"][0]), set(parsed[0]), (dir(result),'\n',len(result),'\n',result,'\n',result["parsed"]))

    def test_isam_ethernet_line_gathered(self):
        # test parsed
        self.get_config.return_value = dedent("""configure ethernet
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        echo "ethernet"
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        line 1/1/8/1
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        line 1/1/8/2
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        """)
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        gathered = [
            dict(
                if_index="1/1/8/1",
                port_type="uni",
                mau=[
                    dict(
                        index=1,
                        mau_type="1000basebx10d",
                        power="up"
                    )
                ]
            ),
            dict(
                if_index="1/1/8/2",
                port_type="uni",
                mau=[
                    dict(
                        index=1,
                        mau_type="1000basebx10d",
                        power="up"
                    )
                ]
            )
        ]

        result = self.execute_module(changed=False)
        self.assertEqual(set(result["gathered"][0]), set(gathered[0]))
        self.assertEqual(set(result["gathered"][1]), set(gathered[1]))

    def test_isam_ethernet_line_rendered(self):
        # test rendered

        set_module_args(
            dict(
                config=[
                    dict(
                        if_index="1/1/8/1",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    ),
                    dict(
                        if_index="1/1/8/2",
                        port_type="uni",
                        mau=[
                            dict(
                            index=1,
                            mau_type="1000basebx10d",
                            power="up"
                            )
                        ]
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure ethernet line 1/1/8/1 port-type uni",
            "configure ethernet line 1/1/8/1 mau 1 type 1000basebx10d",
            "configure ethernet line 1/1/8/1 mau 1 power up",
            "configure ethernet line 1/1/8/2 port-type uni",
            "configure ethernet line 1/1/8/2 mau 1 type 1000basebx10d",
            "configure ethernet line 1/1/8/2 mau 1 power up",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(set(result["rendered"]), set(commands))

    def test_isam_ethernet_line_overridden(self):
        # test overridden
        self.get_config.return_value = dedent("""configure ethernet
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        echo "ethernet"
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        line 1/1/8/1
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        line 1/1/8/2
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        """),
        set_module_args(
            dict(
                config=[
                    dict(
                        if_index="1/1/8/2",
                        port_type="uni",
                        mau=[
                            dict(
                                index=1,
                                mau_type="1000basebx10d",
                                power="up"
                            )
                        ]
                    ),
                ],
                state="overridden",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure ethernet line 1/1/8/2 port-type uni",
            "configure ethernet line 1/1/8/2 mau 1 type 1000basebx10d",
            "configure ethernet line 1/1/8/2 mau 1 power up",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(set(result["commands"]), set(commands))

    def test_isam_ethernet_line_deleted(self):
        # test deleted
        self.get_config.return_value = dedent("""configure ethernet
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        echo "ethernet"
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        line 1/1/8/1
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        line 1/1/8/2
          port-type uni
          admin-up
          mau 1
            type 1000basebx10d
            power up
          exit
        exit
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        """)
        set_module_args(
            dict(
                config=[
                    dict(
                        if_index="1/1/8/1"
                    ),
                ],
                state="deleted",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure ethernet no line 1/1/8/1 port-type uni",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(set(result["commands"]), set(commands))

    def test_isam_ethernet_line_gathered_empty(self):
        # test parsed
        self.get_config.return_value = """\
            
            """
        set_module_args(
            dict(
                state="gathered",
            ),
            ignore_provider_arg,
        )
        gathered = []
        result = self.execute_module(changed=False)
        self.assertEqual(set(result["gathered"]), set(gathered))
