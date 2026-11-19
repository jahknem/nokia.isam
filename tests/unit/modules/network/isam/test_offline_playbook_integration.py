"""Real ansible-playbook integration: offline action states never open the device connection.

Runs the actual modules through ansible-playbook (action plugin routing included) against
an unreachable TEST-NET host. A normal action state would try to connect and time out; an
offline action state (running_config) must render the commands in-process and succeed with
changed=false. Skipped when ansible-playbook is not on PATH.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ANSIBLE_PLAYBOOK = shutil.which("ansible-playbook")
pytestmark = pytest.mark.skipif(ANSIBLE_PLAYBOOK is None, reason="ansible-playbook not installed")

EQUIPMENT = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sernum": "ALCL:F0000001", "sw_ver_pland": "auto",
                             "admin_state": "up"}],
             "slots": [{"ont_slot_idx": "1/1/6/1/1/1", "planned_card_type": "ethernet",
                        "plndnumdataports": 1, "admin_state": "up"}]}


def _run_playbook(tasks, extra_vars):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        inventory = {"all": {"hosts": {"OFFLINE": {
            "ansible_host": "192.0.2.123", "ansible_connection": "ansible.netcommon.network_cli",
            "ansible_network_os": "nokia.isam.isam", "ansible_user": "x", "ansible_password": "y",
            "ansible_connect_timeout": 3, "ansible_command_timeout": 5}}}}
        (root / "inventory.json").write_text(json.dumps(inventory))
        (root / "play.yml").write_text("- hosts: OFFLINE\n  gather_facts: false\n  tasks:\n" + tasks)
        (root / "vars.json").write_text(json.dumps(extra_vars))
        env = {**os.environ, "ANSIBLE_HOST_KEY_CHECKING": "False", "ANSIBLE_LOCAL_TEMP": str(root / "tmp"),
               "ANSIBLE_INVENTORY_ENABLED": "yaml", "ANSIBLE_NOCOWS": "1"}
        done = subprocess.run([ANSIBLE_PLAYBOOK, "-i", str(root / "inventory.json"), str(root / "play.yml"),
                               "-e", "@" + str(root / "vars.json")], env=env, capture_output=True, text=True,
                              timeout=120, cwd=root)
        return done


def test_deleted_running_config_renders_offline_via_playbook():
    tasks = (
        "    - nokia.isam.isam_equipment_onts:\n"
        "        state: deleted\n"
        "        running_config: \"{{ snap }}\"\n"
        "      register: r\n"
        "    - ansible.builtin.assert:\n"
        "        that:\n"
        "          - r.changed == false\n"
        "          - \"'configure equipment ont no interface 1/1/6/1/1' in r.commands\"\n"
        "          - \"'configure equipment ont no slot 1/1/6/1/1/1' in r.commands\"\n"
    )
    done = _run_playbook(tasks, {"snap": json.dumps(EQUIPMENT)})
    assert done.returncode == 0, done.stdout + done.stderr
    assert "timed out" not in done.stdout
    assert "All assertions passed" in done.stdout


def test_rendered_still_works_via_playbook():
    tasks = (
        "    - nokia.isam.isam_bridges:\n"
        "        state: rendered\n"
        "        config: {port: [{port: '1/1/6/1/1/1/1', max_unicast_mac: 5}]}\n"
        "      register: r\n"
        "    - ansible.builtin.assert:\n"
        "        that: \"'configure bridge port 1/1/6/1/1/1/1 max-unicast-mac 5' in r.rendered\"\n"
    )
    done = _run_playbook(tasks, {})
    assert done.returncode == 0, done.stdout + done.stderr