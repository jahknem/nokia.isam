import os
from pathlib import Path
from typing import Tuple

from ssh_helper import send_direct_ssh_command


def load_env(env_path: Path) -> Tuple[str, str]:
    user = None
    password = None
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('user'):
                # supports formats like: user = value or user=value
                _, val = line.split('=', 1)
                user = val.strip().strip('"\'')
            elif line.startswith('password'):
                _, val = line.split('=', 1)
                password = val.strip().strip('"\'')
    if not user or not password:
        raise RuntimeError("Missing user or password in .env")
    return user, password


def main():
    env_path = Path(__file__).with_name('.env')
    user, password = load_env(env_path)
    ok, out = send_direct_ssh_command(
        host='10.190.1.40',
        username=user,
        password=password,
        command='?',
        interactive=True,
    )
    if not ok:
        print(out)
        raise SystemExit(2)
    print(out)


if __name__ == '__main__':
    main()
