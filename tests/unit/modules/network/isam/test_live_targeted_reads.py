"""Targeted reads, modelled on real device replies (DS-LIN-TEST-01, 2026-11-18).

* An instance without configured attributes answers a single 'flat' read with only
  the header, although the whole read lists it as a bare line ('configure ntp ont X').
  Lists whose whole read does that re-check with 'flat detail'.
* 'info configure system security ssh sftp-user <name> flat' is rejected with
  'invalid token'; sftp users are read from the ssh node and filtered.
"""
import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
)
from .test_deleted_regressions import run

HEADER = "#-------------------------------------------------------------------------------\necho \"x\"\n"


class Device(object):
    """Replies keyed by exact command; unknown commands answer with the header only."""

    def __init__(self, replies):
        self.replies = replies
        self.commands = []

    def get(self, command, *a, **k):
        self.commands.append(command)
        reply = self.replies.get(command, HEADER)
        if isinstance(reply, Exception):
            raise reply
        return reply


class Module(object):
    def __init__(self, state="gathered"):
        self.params = {"state": state}


def test_bare_instance_is_found_with_detail_and_returned_without_defaults():
    device = Device({
        "info configure ntp ont 1/1/2/1/1 flat detail":
            HEADER + "configure ntp ont 1/1/2/1/1 no client-state no config-mode no key\n",
    })
    data = get_scoped_config(Module(), device, None, "info configure ntp flat",
                             ["info configure ntp ont 1/1/2/1/1 flat"], bare_commands=True)
    assert data.strip() == "configure ntp ont 1/1/2/1/1"
    assert device.commands == ["info configure ntp ont 1/1/2/1/1 flat", "info configure ntp ont 1/1/2/1/1 flat detail"]


def test_absent_instance_stays_absent_and_configured_instance_needs_no_second_read():
    device = Device({"info configure ntp ont 1/1/2/1/2 flat": HEADER + "configure ntp ont 1/1/2/1/2 client-state enable\n"})
    data = get_scoped_config(Module(), device, None, "info configure ntp flat",
                             ["info configure ntp ont 1/1/2/1/9 flat", "info configure ntp ont 1/1/2/1/2 flat"],
                             bare_commands=True)
    assert "1/1/2/1/9" not in data and "client-state enable" in data
    assert "info configure ntp ont 1/1/2/1/2 flat detail" not in device.commands


def test_without_opt_in_an_empty_reply_is_not_rechecked():
    device = Device({})
    get_scoped_config(Module(), device, None, "info configure qos tca flat", ["info configure qos tca 1/1/1/1 queue 0 flat"])
    assert device.commands == ["info configure qos tca 1/1/1/1 queue 0 flat"]


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
    replies = {single + " detail": HEADER + bare + " no some-default no other-default\n"}

    class Conn(object):
        def get(self, command, *a, **k):
            return replies.get(command, HEADER)

    targeted = _gathered(monkeypatch, module_name, config, Conn())
    whole = run(monkeypatch, module_name, {"state": "parsed", "running_config": bare}, "")["parsed"]
    assert targeted == whole and targeted


def _gathered(monkeypatch, module_name, config, conn):
    import importlib
    import sys
    from ansible.module_utils import basic
    from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
    from .isam_module import set_module_args

    def exit_json(self, **kw):
        raise AnsibleExitJson(kw)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", exit_json)
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + module_name)
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", lambda *a, **k: conn)
    set_module_args({"state": "gathered", "config": config}, True)
    with pytest.raises(AnsibleExitJson) as raised:
        module.main()
    result = raised.value.args[0]
    assert not result.get("failed"), result.get("msg")
    return result["gathered"]


def test_sftp_users_are_read_from_the_ssh_node_and_filtered(monkeypatch):
    ssh = HEADER + "\n".join([
        "configure system security ssh server-profile server-host-key rsa",
        "configure system security ssh access protocol ftp cli ssh tl1 none",
        "configure system security ssh sftp-user user-one password encrypted:aa",
        "configure system security ssh sftp-user user-two password encrypted:bb",
    ]) + "\n"
    sent = []

    class Conn(object):
        def get(self, command, *a, **k):
            sent.append(command)
            if "sftp-user" in command:
                raise Exception("invalid token")
            return ssh if command == "info configure system security ssh flat" else HEADER

    gathered = _gathered(monkeypatch, "isam_system_security", {"ssh": {"sftp_users": [{"name": "user-two"}]}}, Conn())
    assert [u["name"] for u in gathered["ssh"]["sftp_users"]] == ["user-two"]
    assert set(gathered) == {"ssh"} and set(gathered["ssh"]) == {"sftp_users"}
    assert not any("sftp-user" in c for c in sent)


@pytest.mark.parametrize("command,reply,expected", [
    # real replies: the echo wraps mid-word or at a space, depending on the id length
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
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import _targeted_reply
    assert _targeted_reply(command, reply) == expected


def test_long_id_bare_instance_is_found_despite_mid_word_wrap():
    device = Device({
        "info configure ani ont tca-thresh 1/1/2/1/100 flat": "info configure ani ont tca-thresh 1/1/2/1/100 fl\nat\n" + HEADER,
        "info configure ani ont tca-thresh 1/1/2/1/100 flat detail":
            "info configure ani ont tca-thresh 1/1/2/1/100 fl\nat detail\n"
            "configure ani ont tca-thresh 1/1/2/1/100 no lower-optical-th\n" + HEADER,
    })
    data = get_scoped_config(Module(), device, None, "info configure ani ont flat",
                             ["info configure ani ont tca-thresh 1/1/2/1/100 flat"], bare_commands=True)
    assert data.strip() == "configure ani ont tca-thresh 1/1/2/1/100"
