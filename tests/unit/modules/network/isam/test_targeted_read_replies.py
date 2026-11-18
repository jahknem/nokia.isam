"""Targeted (single-instance) reads, modelled on real replies of the lab ISAM.

* The terminal wraps the echoed command at its width, also mid-word; the echo must not
  make an empty reply look non-empty.
* An instance without configured attributes answers a single 'flat' read with only the
  header, although the whole read lists it as a bare line ('configure ntp ont X').
  Lists whose whole read does that re-check with 'flat detail'.
* 'info configure system security ssh sftp-user <name> flat' is rejected with
  'invalid token'; sftp users are read from the ssh node and filtered.
"""
import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    _targeted_reply,
    get_scoped_config,
)
from .module_runner import HEADER, run_module


class Device(object):
    """Replies per exact command (header only otherwise); records the commands."""

    def __init__(self, replies):
        self.replies = replies
        self.commands = []

    def get(self, command, *a, **k):
        self.commands.append(command)
        return self.replies.get(command, HEADER)


class Module(object):
    params = {"state": "gathered"}


@pytest.mark.parametrize("command,reply,expected", [
    ("info configure ani ont tca-thresh 1/1/2/1/100 flat",
     "info configure ani ont tca-thresh 1/1/2/1/100 fl\nat\n" + HEADER, ""),
    ("info configure ani ont tca-thresh 1/1/2/1/1 flat detail",
     "info configure ani ont tca-thresh 1/1/2/1/1 flat\n detail\nconfigure ani ont tca-thresh 1/1/2/1/1 no x\n" + HEADER,
     "configure ani ont tca-thresh 1/1/2/1/1 no x\n"),
    ("info configure system security snmp notify-profile tl1 flat",
     "info configure system security snmp notify-profi\nle tl1 flat\nconfigure system security snmp notify-profile tl1 snmp-version v3\n",
     "configure system security snmp notify-profile tl1 snmp-version v3\n"),
    ("info configure ntp ont 1/1/2/1/1 flat", "configure ntp ont 1/1/2/1/1 client-state enable\n",
     "configure ntp ont 1/1/2/1/1 client-state enable\n"),
])
def test_wrapped_command_echo_is_removed(command, reply, expected):
    assert _targeted_reply(command, reply) == expected


def test_bare_instance_is_found_with_detail_and_returned_without_defaults():
    single = "info configure ani ont tca-thresh 1/1/2/1/100 flat"
    device = Device({
        single: "info configure ani ont tca-thresh 1/1/2/1/100 fl\nat\n" + HEADER,
        single + " detail": "configure ani ont tca-thresh 1/1/2/1/100 no lower-optical-th no rssi-profile\n" + HEADER,
    })
    data = get_scoped_config(Module(), device, None, "info configure ani ont flat", [single], bare_commands=[single])
    assert data.strip() == "configure ani ont tca-thresh 1/1/2/1/100"
    assert device.commands == [single, single + " detail"]


def test_absent_and_configured_instances_need_no_second_read():
    configured = "info configure ntp ont 1/1/2/1/2 flat"
    absent = "info configure ntp ont 1/1/2/1/9 flat"
    device = Device({configured: "configure ntp ont 1/1/2/1/2 client-state enable\n"})
    data = get_scoped_config(Module(), device, None, "info configure ntp flat", [absent, configured],
                             bare_commands=[absent, configured])
    assert data.strip() == "configure ntp ont 1/1/2/1/2 client-state enable"
    assert configured + " detail" not in device.commands


def test_without_opt_in_an_empty_reply_is_not_rechecked():
    command = "info configure qos tca 1/1/1/1 queue 0 flat"
    device = Device({})
    get_scoped_config(Module(), device, None, "info configure qos tca flat", [command])
    assert device.commands == [command]


def test_identical_reads_are_sent_once():
    command = "info configure system security ssh flat"
    device = Device({command: "configure system security ssh access protocol ftp\n"})
    get_scoped_config(Module(), device, None, "unused", [command, command])
    assert device.commands == [command]


@pytest.mark.parametrize("module_name,config,single,bare", [
    ("isam_ntp_onts", [{"ont_id": "1/1/2/1/1"}], "info configure ntp ont 1/1/2/1/1 flat", "configure ntp ont 1/1/2/1/1"),
    ("isam_ani_onts", [{"ont_idx": "1/1/2/1/1"}], "info configure ani ont tca-thresh 1/1/2/1/1 flat",
     "configure ani ont tca-thresh 1/1/2/1/1"),
    ("isam_qos_maps", {"up_ctrl_pkt": [{"protocol": "arp"}]}, "info configure qos up-ctrl-pkt arp flat",
     "configure qos up-ctrl-pkt arp"),
    ("isam_alarm", {"custom_profiles": [{"name": "test"}]}, "info configure alarm custom-profile test flat",
     "configure alarm custom-profile test"),
])
def test_modules_return_bare_instances_like_the_whole_read(monkeypatch, module_name, config, single, bare):
    device = {single + " detail": HEADER + bare + " no some-default no other-default\n"}
    targeted = run_module(monkeypatch, module_name, {"state": "gathered", "config": config}, device)["gathered"]
    whole = run_module(monkeypatch, module_name, {"state": "parsed", "running_config": bare})["parsed"]
    assert targeted and targeted == whole


def test_sftp_users_are_read_from_the_ssh_node_and_filtered(monkeypatch):
    ssh = HEADER + "\n".join([
        "configure system security ssh server-profile server-host-key rsa",
        "configure system security ssh access protocol ftp cli ssh tl1 none",
        "configure system security ssh sftp-user user-one password encrypted:aa",
        "configure system security ssh sftp-user user-two password encrypted:bb",
    ]) + "\n"
    config = {"ssh": {"sftp_users": [{"name": "user-two"}, {"name": "user-three"}]}}
    result = run_module(monkeypatch, "isam_system_security", {"state": "gathered", "config": config},
                        {"info configure system security ssh flat": ssh})
    gathered = result["gathered"]
    assert [user["name"] for user in gathered["ssh"]["sftp_users"]] == ["user-two"]
    assert set(gathered) == {"ssh"} and set(gathered["ssh"]) == {"sftp_users"}
    assert result["_sent"] == ["info configure system security ssh flat"]  # once, never 'sftp-user <name>'
