"""isam_topology_discovery module: read outcomes must never become false absence."""
from pathlib import Path
from ansible_collections.nokia.isam.plugins.modules import isam_topology_discovery
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

PON = "1/1/5/1"
ONT = PON + "/3"

ONT_TABLE = "\n".join([
    "===================================================================================================================",
    "interface table",
    "===================================================================================================================",
    "             |            |          |actual   |              |             |            |cfgfile1|cfgfile2|actual ",
    "ont-idx      |eqpt-ver-num|sw-ver-act|num-slots|version-number|sernum       |yp-serial-no|ver-act |ver-act |us-rate",
    "-------------+------------+----------+---------+--------------+-------------+------------+--------+--------+-------",
    "%-13s G2110BV2D0   AN03110R   1         G2110BV2D0     XXXX:SANIT  unknown                        1.25g  " % ONT,
    "interface count : 1",
])


class TestTopologyDiscoveryModule(TestIsamModule):
    module = isam_topology_discovery

    def setUp(self):
        super(TestTopologyDiscoveryModule, self).setUp()
        self.mock_conn = patch(
            "ansible_collections.nokia.isam.plugins.modules.isam_topology_discovery.get_resource_connection")
        self.get_conn = self.mock_conn.start()

    def tearDown(self):
        super(TestTopologyDiscoveryModule, self).tearDown()
        self.mock_conn.stop()

    def _conn(self, reply=None, exc=None):
        class Conn:
            def get(self, command):
                if exc is not None:
                    raise exc
                return reply
        self.get_conn.return_value = Conn()

    def test_populated_ont_enumeration_is_ok_and_device_scoped(self):
        self._conn(reply=ONT_TABLE)
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        disc = result["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["read_scope"], "device")
        self.assertEqual(disc["children"], [ONT])

    def test_invalid_token_is_unsupported_not_empty(self):
        self._conn(reply="invalid token")
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        disc = result["discovery"]
        self.assertEqual(disc["status"], "unsupported")
        self.assertEqual(disc["children"], [])
        self.assertIn("unsupported", disc["error"])

    def test_absent_error_is_not_confirmed_absence(self):
        self._conn(reply="specified instance does not exist")
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["discovery"]["status"], "unsupported")

    def test_transport_error_is_reported_as_error(self):
        self._conn(exc=RuntimeError("connection reset"))
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        disc = result["discovery"]
        self.assertEqual(disc["status"], "error")
        # sanitized: error class and exception type, never the raw exception text
        self.assertEqual(disc["error"], "connection_error (RuntimeError)")

    def test_empty_table_confirms_absence(self):
        self._conn(reply="\n".join(ONT_TABLE.splitlines()[:6] + ["interface count : 0"]))
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        disc = result["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["children"], [])

    def test_check_mode_enumerates_like_a_normal_run(self):
        # read-only: check mode returns the same evidence
        self._conn(reply=ONT_TABLE)
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True, _ansible_check_mode=True),
                        ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["discovery"]["status"], "ok")
        self.assertTrue(result["discovery"]["children"])

    def test_device_text_in_exceptions_is_not_returned(self):
        self._conn(exc=RuntimeError("configure system security snmp community secret123"))
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertNotIn("secret123", str(result))
        self.assertEqual(result["discovery"]["error"], "device_error (RuntimeError)")

    def test_invalid_parent_identity_fails(self):
        self._conn(reply=ONT_TABLE)
        set_module_args(dict(kind="pon", identity="not-a-pon", child_kind="ont"), ignore_provider=True)
        result = self.failed()
        self.assertTrue(result["failed"])

    def test_broad_source_needs_explicit_permission_before_connection(self):
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont"), ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "unsupported")
        self.assertEqual(disc["error"], "broad_enumeration_requires_allow_broad_read")
        self.assertEqual(disc["read_scope"], "device")
        self.get_conn.assert_not_called()

    def test_wrong_parent_child_relation_is_rejected_before_connection(self):
        set_module_args(dict(kind="ont", identity=ONT, child_kind="pon", allow_broad_read=True), ignore_provider=True)
        self.failed()
        self.get_conn.assert_not_called()

    def test_blank_or_unrecognized_source_cannot_confirm_absence(self):
        for reply in ("", "unexpected response", "ont table without columns"):
            self._conn(reply=reply)
            set_module_args(dict(kind="pon", identity=PON, child_kind="ont", allow_broad_read=True), ignore_provider=True)
            self.failed()

    def test_transceiver_inventory_enumeration_is_device_scoped(self):
        table = "\n".join([
            "====================================================================================================",
            "transceiver-inventory table",
            "====================================================================================================",
            "index                 |inventory-status  |nokia-part-num|tx-wavelength|fiber-type   |rssi-sfptype   ",
            "----------------------+------------------+--------------+-------------+-------------+---------------",
            "nt-a:xfp:1             no-error           3FE62600AA     \"1310 nm\"     single-mode   10gbase_lr     ",
            "nt-a:xfp:2             cage-empty         not-available  not-available not-available not-available  ",
            "nt-b:xfp:1             cage-empty         not-available  not-available not-available not-available  ",
            "----------------------------------------------------------------------------------------------------",
            "transceiver-inventory count : 3",
            "====================================================================================================",
        ])
        self._conn(reply=table)
        set_module_args(dict(kind="card", identity="nt-a", child_kind="transceiver", allow_broad_read=True),
                      ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["read_scope"], "device")
        self.assertEqual(disc["children"], ["nt-a:xfp:1", "nt-a:xfp:2"])

    def test_transceiver_inventory_without_permission_never_reads(self):
        set_module_args(dict(kind="card", identity="nt-a", child_kind="transceiver"), ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["error"], "broad_enumeration_requires_allow_broad_read")
        self.get_conn.assert_not_called()

    def test_uni_bridge_port_enumeration_returns_tuple_identities(self):
        uni = "1/1/5/1/3/1/1"
        table = "\n".join([
            "===============================================================================================",
            "stack table",
            "===============================================================================================",
            "higher                                         |lower                                          ",
            "-----------------------------------------------+-----------------------------------------------",
            "%-47s %-47s" % ("bridge-port:%s" % uni, "uni:%s" % uni),
            "-----------------------------------------------------------------------------------------------",
            "stack count : 1",
            "===============================================================================================",
        ])
        self._conn(reply=table)
        set_module_args(dict(kind="uni", identity=uni, child_kind="bridge_port", allow_broad_read=True),
                      ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["read_scope"], "device")
        self.assertEqual(disc["children"], [("uni", uni)])

    def test_bridge_port_parent_identity_encoding_and_vlan_children(self):
        uni = "1/1/5/1/3/1/1"
        table = "\n".join([
            "===============================================================================================",
            "stack table",
            "===============================================================================================",
            "higher                                         |lower                                          ",
            "-----------------------------------------------+-----------------------------------------------",
            "%-47s %-47s" % ("vlan-port:%s:99" % uni, "bridge-port:%s" % uni),
            "%-47s %-47s" % ("vlan-port:%s:100" % uni, "bridge-port:%s" % uni),
            "-----------------------------------------------------------------------------------------------",
            "stack count : 2",
            "===============================================================================================",
        ])
        self._conn(reply=table)
        set_module_args(dict(kind="bridge_port", identity="uni:%s" % uni, child_kind="vlan_port",
                             allow_broad_read=True), ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["parent"], '["bridge_port",["uni","%s"]]' % uni)
        self.assertEqual(disc["children"], [("uni", uni, "100"), ("uni", uni, "99")])

    def test_unsupported_channel_pair_source_is_not_absence(self):
        self._conn(reply="invalid token")
        set_module_args(dict(kind="card", identity="lt:1/1/3", child_kind="channel_pair", allow_broad_read=True),
                      ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "unsupported")
        self.assertEqual(disc["children"], [])

    def test_ihub_optical_ports_require_permission_before_connection(self):
        set_module_args(dict(kind="card", identity="nt-a", child_kind="uplink"), ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["error"], "broad_enumeration_requires_allow_broad_read")
        self.assertEqual(disc["command"], "show port")
        self.get_conn.assert_not_called()

    def test_ihub_optical_ports_use_separate_ihub_command(self):
        table = (Path(__file__).parents[4] / "fixtures/ihub_ports/multisection/output.txt").read_text()
        commands = []

        class Conn:
            def get(self, command):
                commands.append(command)
                return table

        self.get_conn.return_value = Conn()
        set_module_args(dict(kind="card", identity="nt-a", child_kind="uplink", allow_broad_read=True),
                        ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "ok")
        self.assertEqual(disc["children"], ["nt-a:xfp:1", "nt-a:xfp:2"])
        self.assertEqual(disc["read_scope"], "device")
        self.assertEqual(commands, ["show port"])

    def test_malformed_ihub_inventory_is_not_an_empty_discovery(self):
        self._conn(reply="Ports on NT-A\ntruncated")
        set_module_args(dict(kind="card", identity="nt-a", child_kind="uplink", allow_broad_read=True),
                        ignore_provider=True)
        self.failed()

    def test_unsupported_ihub_command_does_not_confirm_absence(self):
        self._conn(reply="invalid token")
        set_module_args(dict(kind="card", identity="nt-a", child_kind="uplink", allow_broad_read=True),
                        ignore_provider=True)
        disc = self.execute_module(changed=False)["discovery"]
        self.assertEqual(disc["status"], "unsupported")


STACK = "\n".join([
    "===============================================================================================",
    "stack table",
    "===============================================================================================",
    "higher                                         |lower                                          ",
    "-----------------------------------------------+-----------------------------------------------",
    "%-47s %-47s" % ("bridge-port:1/1/3/1", "ethernet-line:1/1/3/1"),
    "%-47s %-47s" % ("vlan-port:1/1/3/1:99", "bridge-port:1/1/3/1"),
    "-----------------------------------------------------------------------------------------------",
    "stack count : 2",
    "===============================================================================================",
])


class TestTopologyDiscoveryBatch(TestIsamModule):
    """requests: several enumerations in one call, every source read once."""
    module = isam_topology_discovery

    def setUp(self):
        super(TestTopologyDiscoveryBatch, self).setUp()
        self.mock_conn = patch(
            "ansible_collections.nokia.isam.plugins.modules.isam_topology_discovery.get_resource_connection")
        self.get_conn = self.mock_conn.start()
        self.commands = []

    def tearDown(self):
        super(TestTopologyDiscoveryBatch, self).tearDown()
        self.mock_conn.stop()

    def _conn(self, replies, exc=None):
        commands = self.commands

        class Conn:
            def get(self, command):
                commands.append(command)
                if exc is not None:
                    raise exc
                return replies[command]
        self.get_conn.return_value = Conn()

    def test_one_source_is_read_once_for_every_request_and_results_keep_their_order(self):
        self._conn({"show interface stack": STACK, "info configure equipment ont interface flat": ""})
        requests = [{"kind": "xdsl_line", "identity": "1/1/3/%d" % n, "child_kind": "bridge_port"} for n in (1, 2)]
        requests.append({"kind": "bridge_port", "identity": "xdsl_line:1/1/3/1", "child_kind": "vlan_port"})
        set_module_args(dict(requests=requests, allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertNotIn("discovery", result)
        first, second, vlans = result["discoveries"]
        self.assertEqual(self.commands, ["show interface stack"])
        self.assertEqual((first["status"], first["children"]), ("ok", [("xdsl_line", "1/1/3/1")]))
        # The second line has no bridge port in the same, complete source: confirmed empty.
        self.assertEqual((second["status"], second["children"]), ("ok", []))
        self.assertEqual(second["parent"], '["xdsl_line","1/1/3/2"]')
        self.assertEqual((vlans["status"], vlans["children"]), ("ok", [("xdsl_line", "1/1/3/1", "99")]))

    def test_a_failed_source_read_is_an_error_for_every_request_on_it_and_read_once(self):
        self._conn({}, exc=ConnectionError("Error : some device text"))
        requests = [{"kind": "xdsl_line", "identity": "1/1/3/%d" % n, "child_kind": "bridge_port"} for n in (1, 2)]
        set_module_args(dict(requests=requests, allow_broad_read=True), ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(self.commands, ["show interface stack"])
        for disc in result["discoveries"]:
            self.assertEqual((disc["status"], disc["children"]), ("error", []))
            self.assertNotIn("device text", disc["error"])

    def test_an_invalid_request_fails_the_call_before_any_read(self):
        self._conn({"show interface stack": STACK})
        requests = [{"kind": "xdsl_line", "identity": "1/1/3/1", "child_kind": "bridge_port"},
                    {"kind": "xdsl_line", "identity": "not-a-line", "child_kind": "bridge_port"}]
        set_module_args(dict(requests=requests, allow_broad_read=True), ignore_provider=True)
        self.execute_module(failed=True)
        self.assertEqual(self.commands, [])
        self.get_conn.assert_not_called()

    def test_without_permission_no_request_reads(self):
        requests = [{"kind": "xdsl_line", "identity": "1/1/3/1", "child_kind": "bridge_port"}]
        set_module_args(dict(requests=requests), ignore_provider=True)
        (disc,) = self.execute_module(changed=False)["discoveries"]
        self.assertEqual(disc["error"], "broad_enumeration_requires_allow_broad_read")
        self.get_conn.assert_not_called()

    def test_requests_and_a_single_relation_are_mutually_exclusive(self):
        set_module_args(dict(kind="pon", identity=PON, child_kind="ont",
                             requests=[{"kind": "pon", "identity": PON, "child_kind": "ont"}]), ignore_provider=True)
        self.execute_module(failed=True)
        set_module_args(dict(kind="pon", identity=PON), ignore_provider=True)
        self.execute_module(failed=True)


def test_a_record_is_dated_when_its_source_was_read_not_when_it_was_parsed(monkeypatch):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import source_reads
    stamps = iter(["2026-11-27T10:00:00Z", "2026-11-27T10:09:00Z", "2026-11-27T10:09:30Z"])
    monkeypatch.setattr(source_reads, "utc_now", lambda: next(stamps))
    sources = {}

    class Conn(object):
        def get(self, command):
            return STACK
    requests = [source_reads.prepare("xdsl_line", "1/1/3/%d" % n, "bridge_port") for n in (1, 2)]
    first = source_reads.enumerate_request(sources, Conn, requests[0], True)
    second = source_reads.enumerate_request(sources, Conn, requests[1], True)
    # One read at 10:00; the second record, parsed later from the cached reply, keeps it.
    assert first["collected_at"] == second["collected_at"] == "2026-11-27T10:00:00Z"
