from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_system
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamSystemModule(TestIsamModule):
    module = isam_system

    def setUp(self):
        super(TestIsamSystemModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system.system.Isam_systemFacts.get_config"
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
        super(TestIsamSystemModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_system_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    id=dict(name="ISAM-01", location="Datacenter-A", contact="admin@example.com"),
                    security=dict(ssh=True, telnet=False, snmp=True),
                    sntp=dict(server="10.0.0.1", port=123, poll_interval=3600),
                    syslog=dict(server="10.0.0.2", facility="local0", severity="info"),
                    sync_if_timing=dict(mode="free-run", source="internal"),
                    transaction=dict(timeout=300),
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        rendered = result["rendered"]
        self.assertIn("configure system id name ISAM-01", rendered)
        self.assertIn("configure system id location Datacenter-A", rendered)
        self.assertIn("configure system id contact admin@example.com", rendered)
        self.assertIn("configure system security ssh enable", rendered)
        self.assertIn("configure system security snmp enable", rendered)
        self.assertIn("configure system sntp server 10.0.0.1", rendered)
        self.assertIn("configure system sntp port 123", rendered)
        self.assertIn("configure system sntp poll-interval 3600", rendered)
        self.assertIn("configure system syslog server 10.0.0.2", rendered)
        self.assertIn("configure system syslog facility local0", rendered)
        self.assertIn("configure system syslog severity info", rendered)
        self.assertIn("configure system sync-if-timing mode free-run", rendered)
        self.assertIn("configure system sync-if-timing source internal", rendered)
        self.assertIn("configure system transaction timeout 300", rendered)

    def test_isam_system_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure
                    system
                    id
                      name ISAM-01
                      location Datacenter-A
                      contact admin@example.com
                    exit
                    security
                      ssh enable
                      telnet no enable
                      snmp enable
                    exit
                    sntp
                      server 10.0.0.1
                      port 123
                      poll-interval 3600
                    exit
                    sync-if-timing
                      mode free-run
                      source internal
                    exit
                    syslog
                      server 10.0.0.2
                      facility local0
                      severity info
                    exit
                    transaction
                      timeout 300
                    exit
                    exit
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        parsed = result["parsed"]
        self.assertEqual(parsed["id"]["name"], "ISAM-01")
        self.assertEqual(parsed["id"]["location"], "Datacenter-A")
        self.assertEqual(parsed["id"]["contact"], "admin@example.com")
        self.assertEqual(parsed["security"]["ssh"], True)
        self.assertEqual(parsed["security"]["telnet"], False)
        self.assertEqual(parsed["security"]["snmp"], True)
        self.assertEqual(parsed["sntp"]["server"], "10.0.0.1")
        self.assertEqual(parsed["sntp"]["port"], 123)
        self.assertEqual(parsed["sntp"]["poll_interval"], 3600)
        self.assertEqual(parsed["sync_if_timing"]["mode"], "free-run")
        self.assertEqual(parsed["sync_if_timing"]["source"], "internal")
        self.assertEqual(parsed["syslog"]["server"], "10.0.0.2")
        self.assertEqual(parsed["syslog"]["facility"], "local0")
        self.assertEqual(parsed["syslog"]["severity"], "info")
        self.assertEqual(parsed["transaction"]["timeout"], 300)

    def test_isam_system_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure
            system
            id
              name ISAM-01
              location Datacenter-A
              contact admin@example.com
            exit
            security
              ssh enable
              telnet no enable
              snmp enable
            exit
            sntp
              server 10.0.0.1
              port 123
              poll-interval 3600
            exit
            sync-if-timing
              mode free-run
              source internal
            exit
            syslog
              server 10.0.0.2
              facility local0
              severity info
            exit
            transaction
              timeout 300
            exit
            exit
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    id=dict(name="ISAM-01", location="Datacenter-A", contact="admin@example.com"),
                    security=dict(ssh=True, telnet=False, snmp=True),
                    sntp=dict(server="10.0.0.1", port=123, poll_interval=3600),
                    syslog=dict(server="10.0.0.2", facility="local0", severity="info"),
                    sync_if_timing=dict(mode="free-run", source="internal"),
                    transaction=dict(timeout=300),
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
