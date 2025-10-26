#!/usr/bin/env python3
"""
Capture real device configuration examples for example files.
"""

import json
import sys
from pathlib import Path
from ssh_helper import send_direct_ssh_command


def load_env(env_path: Path):
    """Load device credentials from .env file."""
    user = None
    password = None
    host = None
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('user'):
                _, val = line.split('=', 1)
                user = val.strip().strip('"\'')
            elif line.startswith('password'):
                _, val = line.split('=', 1)
                password = val.strip().strip('"\'')
            elif line.startswith('host'):
                _, val = line.split('=', 1)
                host = val.strip().strip('"\'')
    if not user or not password:
        raise RuntimeError("Missing user or password in .env")
    host = host or '10.190.1.40'
    return host, user, password


def run_cmd(host: str, username: str, password: str, command: str):
    """Execute a command on the device."""
    try:
        ok, out = send_direct_ssh_command(
            host=host,
            username=username,
            password=password,
            command=command,
            interactive=True,
        )
        if ok:
            return out
        else:
            print(f"ERROR: {out}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return None


def main():
    env_path = Path(__file__).with_name('.env')
    host, user, password = load_env(env_path)

    # Get real configuration examples from device
    examples = {}

    # Port examples - use real port from device
    print("[*] Getting port configuration...", file=sys.stderr)
    cmd = "info configure interface port 1/1/2"
    out = run_cmd(host, user, password, cmd)
    if out:
        examples['port_before'] = out

    # Alarm examples
    print("[*] Getting alarm configuration...", file=sys.stderr)
    cmd = "info configure interface alarm ethernetCsmacd"
    out = run_cmd(host, user, password, cmd)
    if out:
        examples['alarm_before'] = out

    # Cage examples
    print("[*] Getting cage configuration...", file=sys.stderr)
    cmd = "info configure interface cage 1/1"
    out = run_cmd(host, user, password, cmd)
    if out:
        examples['cage_before'] = out

    # ATM-PVC examples
    print("[*] Getting atm-pvc configuration...", file=sys.stderr)
    cmd = "info configure interface atm-pvc 1/1/atm:0/0"
    out = run_cmd(host, user, password, cmd)
    if out:
        examples['atm_pvc_before'] = out

    # Statistics examples
    print("[*] Getting statistics configuration...", file=sys.stderr)
    cmd = "info configure interface statistics sliding-win-stats"
    out = run_cmd(host, user, password, cmd)
    if out:
        examples['statistics_before'] = out

    print(json.dumps(examples, indent=2))


if __name__ == '__main__':
    main()
