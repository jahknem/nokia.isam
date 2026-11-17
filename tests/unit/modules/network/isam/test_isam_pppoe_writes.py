"""Write states of the PPPoE resources compare against the device (they used to compare against nothing)."""
from ansible.module_utils import basic
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from ansible_collections.nokia.isam.plugins.modules import (
    isam_pppoe_client_interface,
    isam_pppoe_client_ppp_profile,
    isam_pppoel2_statistics,
)
from .isam_module import TestIsamModule, set_module_args

CONFIG = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.%s.%s.get_resource_connection"


class _Device(object):
    """Answers the whole-resource read; any other read is a device error."""

    def __init__(self, outputs):
        self.outputs, self.commands = outputs, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if command not in self.outputs:
            raise Exception("Error : invalid token")
        return self.outputs[command]


class _Base(TestIsamModule):
    package = None
    read = None
    output = ""

    def device(self, outputs):
        device = _Device(outputs)
        patcher = patch(CONFIG % (self.package, self.package), return_value=device)
        patcher.start()
        self.addCleanup(patcher.stop)
        return device

    def commands(self, state, config=None, expected=(), output=None):
        """Run state in check mode against a device holding output; assert the exact commands."""
        device = self.device({self.read: self.output if output is None else output})
        args = {"state": state, "_ansible_check_mode": True}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        result = self.execute_module(changed=bool(expected))
        self.assertIn(self.read, device.commands)
        self.assertEqual(result["commands"], list(expected))
        return result

    def failure(self, state, config=None, output=None):
        self.device({} if output is None else {self.read: output})
        args = {"state": state, "_ansible_check_mode": True}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        return self.execute_module(failed=True)


class TestPppProfileWrites(_Base):
    module = isam_pppoe_client_ppp_profile
    package = "pppoe_client"
    read = "info configure pppoe-client ppp-profile flat"
    output = (
        "configure pppoe-client ppp-profile home ipversion dual authproto pap mru 1492\n"
        "configure pppoe-client ppp-profile plain\n"
    )

    def test_merged_is_idempotent(self):
        self.commands("merged", [{"name": "home", "ipversion": "dual"}, {"name": "plain"}])
        # defaults are omitted by "info ... flat"
        self.commands("merged", [{"name": "plain", "ipversion": "ipv4", "authproto": "auto", "mru": 1500}])

    def test_merged_changes_and_creates(self):
        self.commands("merged", [{"name": "home", "mru": 1400}, {"name": "new", "authproto": "chap"}], [
            "configure pppoe-client ppp-profile home ipversion dual authproto pap mru 1400",
            "configure pppoe-client ppp-profile new authproto chap",
        ])

    def test_replaced_negates_unnamed_attributes(self):
        # used to delete and recreate the profile ("configure pppoe-client no profile home": invalid CLI)
        self.commands("replaced", [{"name": "home", "ipversion": "dual"}], [
            "configure pppoe-client ppp-profile home ipversion dual no authproto no mru"])
        self.commands("replaced", [{"name": "home", "ipversion": "dual", "authproto": "pap", "mru": 1492}])

    def test_overridden_removes_unnamed_profiles(self):
        self.commands("overridden", [{"name": "home", "ipversion": "dual", "authproto": "pap", "mru": 1492}], [
            "configure pppoe-client no ppp-profile plain"])

    def test_deleted_named_and_all(self):
        self.commands("deleted", [{"name": "plain"}, {"name": "absent"}], ["configure pppoe-client no ppp-profile plain"])
        self.commands("deleted", None, [
            "configure pppoe-client no ppp-profile home",
            "configure pppoe-client no ppp-profile plain",
        ])
        self.commands("deleted", None, output="")

    def test_device_error_fails(self):
        result = self.failure("deleted")
        self.assertIn("invalid token", result["msg"])


class TestPppoeClientInterfaceWrites(_Base):
    module = isam_pppoe_client_interface
    package = "pppoe_client"
    read = "info configure pppoe-client interface flat"
    # two client ids on one port (CLI identity: ifindex + client-id); the device hides passwords
    output = (
        "configure pppoe-client interface 1/1/1/1/3:100 client-id 1 profile-name home username alice password plain:xxx pbit 3\n"
        "configure pppoe-client interface 1/1/1/1/3:100 client-id 2 profile-name home username bob password plain:xxx\n"
        "configure pppoe-client interface 1/1/1/1/4:100 client-id 1 profile-name home username carol password plain:xxx\n"
    )

    def test_gathered_keeps_every_client_id(self):
        self.device({self.read: self.output})
        set_module_args({"state": "gathered"}, True)
        result = self.execute_module()
        self.assertEqual([(item["name"], item["client_id"]) for item in result["gathered"]], [
            ("1/1/1/1/3:100", 1), ("1/1/1/1/3:100", 2), ("1/1/1/1/4:100", 1)])

    def test_merged_is_idempotent(self):
        self.commands("merged", [
            {"name": "1/1/1/1/3:100", "client_id": 1, "profile_name": "home", "username": "alice", "password": "s", "pbit": 3},
            {"name": "1/1/1/1/3:100", "client_id": 2, "username": "bob"},
            {"name": "1/1/1/1/4:100", "pbit": 0},
        ])

    def test_merged_changes_one_client_id_only(self):
        # used to key by port only: client id 2 overwrote client id 1
        self.commands("merged", [{"name": "1/1/1/1/3:100", "client_id": 2, "pbit": 5, "password": "s"}], [
            "configure pppoe-client interface 1/1/1/1/3:100 client-id 2 profile-name home username bob password s pbit 5"])

    def test_merged_creates_new_client_id(self):
        self.commands("merged", [{"name": "1/1/1/1/3:100", "client_id": 3, "profile_name": "home", "username": "dave", "password": "s"}], [
            "configure pppoe-client interface 1/1/1/1/3:100 client-id 3 profile-name home username dave password s"])

    def test_change_without_password_fails(self):
        result = self.failure("merged", [{"name": "1/1/1/1/3:100", "client_id": 2, "pbit": 5}], self.output)
        self.assertIn("password", result["msg"])

    def test_port_with_several_client_ids_needs_client_id(self):
        result = self.failure("merged", [{"name": "1/1/1/1/3:100", "pbit": 5, "password": "s"}], self.output)
        self.assertIn("client_id", result["msg"])

    def test_create_without_mandatory_attributes_is_skipped(self):
        with patch.object(basic.AnsibleModule, "warn") as warn:
            self.commands("merged", [{"name": "1/1/1/1/9:100"}])
        self.assertIn("client_id", warn.call_args[0][0])

    def test_replaced_negates_unnamed_attributes(self):
        self.commands("replaced", [{"name": "1/1/1/1/3:100", "client_id": 1, "password": "s"}], [
            "configure pppoe-client interface 1/1/1/1/3:100 client-id 1 profile-name home username alice password s no pbit"])
        self.commands("replaced", [{"name": "1/1/1/1/3:100", "client_id": 2}])

    def test_overridden_removes_unnamed_client_ids(self):
        self.commands("overridden", [{"name": "1/1/1/1/3:100", "client_id": 1, "pbit": 3}], [
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 2",
            "configure pppoe-client no interface 1/1/1/1/4:100 client-id 1",
        ])

    def test_deleted_named_and_all(self):
        # used to send "configure pppoe-client no interface <port>": the removal form needs the client id
        self.commands("deleted", [{"name": "1/1/1/1/3:100", "client_id": 2}], [
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 2"])
        self.commands("deleted", [{"name": "1/1/1/1/3:100"}], [
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 1",
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 2",
        ])
        self.commands("deleted", None, [
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 1",
            "configure pppoe-client no interface 1/1/1/1/3:100 client-id 2",
            "configure pppoe-client no interface 1/1/1/1/4:100 client-id 1",
        ])
        self.commands("deleted", [{"name": "1/1/1/1/9:100"}])


class TestPppoel2StatisticsWrites(_Base):
    module = isam_pppoel2_statistics
    package = "pppoel2"
    read = "info configure pppoel2 statistics flat"
    output = (
        "configure pppoel2 statistics vlan-port:1/1/1/1/3:100\n"
        "configure pppoel2 statistics vlan-port:1/1/1/1/4:100\n"
    )

    def test_merged_is_idempotent(self):
        self.commands("merged", [{"name": "vlan-port:1/1/1/1/3:100"}, {"name": "vlan-port 1/1/1/1/4:100", "enabled": True}])

    def test_merged_enables_and_disables(self):
        self.commands("merged", [{"name": "vlan-port:1/1/1/1/5:100"}, {"name": "vlan-port:1/1/1/1/4:100", "enabled": False}], [
            "configure pppoel2 no statistics vlan-port:1/1/1/1/4:100",
            "configure pppoel2 statistics vlan-port:1/1/1/1/5:100",
        ])

    def test_replaced_is_idempotent(self):
        # used to send "no statistics" + "statistics" for every named port present on the device
        self.commands("replaced", [{"name": "vlan-port:1/1/1/1/3:100"}])

    def test_overridden_removes_unnamed_ports(self):
        self.commands("overridden", [{"name": "vlan-port:1/1/1/1/3:100"}], [
            "configure pppoel2 no statistics vlan-port:1/1/1/1/4:100"])

    def test_deleted_named_and_all(self):
        self.commands("deleted", [{"name": "vlan-port:1/1/1/1/4:100"}, {"name": "vlan-port:1/1/1/1/9:100"}], [
            "configure pppoel2 no statistics vlan-port:1/1/1/1/4:100"])
        self.commands("deleted", None, [
            "configure pppoel2 no statistics vlan-port:1/1/1/1/3:100",
            "configure pppoel2 no statistics vlan-port:1/1/1/1/4:100",
        ])
        self.commands("deleted", None, output="")

    def test_device_error_fails(self):
        result = self.failure("overridden", [{"name": "vlan-port:1/1/1/1/3:100"}])
        self.assertIn("invalid token", result["msg"])
