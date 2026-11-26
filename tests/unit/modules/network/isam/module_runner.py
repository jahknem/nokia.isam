"""Run a resource module end to end against a fake device (shared test helper).

run_module() executes the real module main(): facts are read from the fake device,
commands are generated in check mode, nothing is sent. The device answers every read
command from one of:

* a string: the same reply for every command;
* a dict: reply per exact command (unknown commands get only the header, as the
  device does for an instance without configuration);
* a callable(command) -> reply, e.g. capture_device().
"""
import importlib
import os
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
from .isam_module import set_module_args

MODULES = "ansible_collections.nokia.isam.plugins.modules."
HEADER = "#-------------------------------------------------------------------------------\necho \"x\"\n"


def module_for(resource):
    """The module name of a resource ('vlans' -> 'isam_vlans', 'isam_cfm' -> 'isam_cfm'), or None."""
    for name in (resource, "isam_" + resource):
        try:
            importlib.import_module(MODULES + name)
        except ImportError:
            continue
        return name
    return None


def _answer(device, command):
    if callable(device):
        return device(command)
    if isinstance(device, dict):
        return device.get(command, HEADER)
    return device


def run_module(monkeypatch, module_name, args, device=""):
    """Run module_name with args in check mode; the module's result dict plus

    _warnings (module.warn messages), _sent (read commands) and _no_log_values (values
    Ansible masks in the output).
    """
    sent = []
    warnings = []

    class Connection(object):
        def get(self, command, *a, **k):
            sent.append(command)
            reply = _answer(device, command)
            if isinstance(reply, Exception):
                raise reply
            return reply

        get_config = get

    def exit_json(self, **result):
        result["_no_log_values"] = set(self.no_log_values)
        raise AnsibleExitJson(result)

    def fail_json(self, **result):
        result["failed"] = True
        result["_no_log_values"] = set(self.no_log_values)
        raise AnsibleExitJson(result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
    monkeypatch.setattr(basic.AnsibleModule, "warn", lambda self, msg: warnings.append(msg))
    module = importlib.import_module(MODULES + module_name)
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", lambda *a, **k: Connection())
    set_module_args(dict(args, _ansible_check_mode=True), True)
    with pytest.raises(AnsibleExitJson) as raised:
        module.main()
    result = raised.value.args[0]
    result["_warnings"] = warnings
    result["_sent"] = sent
    return result


def capture_device(flat, detail):
    """A device answering 'info configure <path> [flat|flat detail]' from capture texts:
    the capture lines under <path>, from the detail capture when 'detail' is asked for."""
    flat_lines = [line for line in flat.splitlines() if line.startswith("configure ")]
    detail_lines = [line for line in detail.splitlines() if line.startswith("configure ")]

    def answer(command):
        words = command.split()
        path = " ".join(word for word in words[1:] if word not in ("flat", "detail"))
        lines = detail_lines if "detail" in words else flat_lines
        return "\n".join(line for line in lines if line == path or line.startswith(path + " ")) + "\n"
    return answer


def lab_capture_device():
    """capture_device() over the lab captures (skip/fail rules: lab_captures.path)."""
    from . import lab_captures

    return capture_device(lab_captures.configured(), lab_captures.detail())
