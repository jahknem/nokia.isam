"""isam_xdsl_profiles gathered/parsed go through the config class (they used to bypass it in the module)."""
import sys

from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_profiles
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_profiles.xdsl_profiles import Xdsl_profiles
from .isam_module import TestIsamModule, set_module_args

SERVICE = "configure xdsl service-profile 11 name YPLAY-30-Privat version 1 max-bitrate-down 33000\n"


class _Device(object):
    def __init__(self, outputs=None, error=None):
        self.outputs, self.error, self.commands = outputs or {}, error, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if self.error:
            raise Exception(self.error)
        return self.outputs.get(command, "")


class TestXdslProfilesGathered(TestIsamModule):
    module = isam_xdsl_profiles

    def run_module(self, args, device=None, failed=False):
        # Like targeted_harness: every loaded module that obtains the connection gets the fake device.
        patchers = [patch.object(loaded, "get_resource_connection", return_value=device)
                    for name, loaded in list(sys.modules.items())
                    if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection")]
        patchers.append(patch.object(Xdsl_profiles, "execute_module", autospec=True, side_effect=Xdsl_profiles.execute_module))
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
        set_module_args(args, True)
        result = self.execute_module(failed=failed)
        if not failed:  # a device error fails while the config class reads the device (before execute_module)
            self.assertTrue(Xdsl_profiles.execute_module.called, "the module bypassed the config class")
        return result

    def test_gathered_uses_the_config_class(self):
        device = _Device({"info configure xdsl service-profile flat": SERVICE})
        result = self.run_module({"state": "gathered"}, device)
        self.assertEqual(result["gathered"]["service_profiles"][0]["id"], 11)
        self.assertNotIn("commands", result)

    def test_targeted_gathered_reads_only_the_named_profile(self):
        device = _Device({"info configure xdsl service-profile 11 flat": SERVICE})
        result = self.run_module({"state": "gathered", "config": {"service_profiles": [{"id": 11}]}}, device)
        self.assertEqual(device.commands, ["info configure xdsl service-profile 11 flat"])
        self.assertEqual([item["id"] for item in result["gathered"]["service_profiles"]], [11])

    def test_gathered_device_error_fails(self):
        result = self.run_module({"state": "gathered"}, _Device(error="Error : connection to the device was lost"), failed=True)
        self.assertIn("connection to the device was lost", result["msg"])

    def test_parsed_uses_the_config_class(self):
        result = self.run_module({"state": "parsed", "running_config": SERVICE})
        self.assertEqual(result["parsed"]["service_profiles"][0]["name"], "YPLAY-30-Privat")
