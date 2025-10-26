#!/usr/bin/env python3
import sys
from pathlib import Path
from ssh_helper import send_direct_ssh_command

def load_env(env_path: Path):
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


def main():
    if len(sys.argv) < 2:
        print("Usage: exec_cmd.py <command>")
        sys.exit(1)
    command = ' '.join(sys.argv[1:])
    env_path = Path(__file__).with_name('.env')
    host, user, password = load_env(env_path)
    ok, out = send_direct_ssh_command(
        host=host,
        username=user,
        password=password,
        command=command,
        interactive=True,
    )
    if not ok:
        print(out, file=sys.stderr)
        sys.exit(2)
    print(out)

if __name__ == '__main__':
    main()
