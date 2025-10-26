from ansible.module_utils.connection import Connection
from ansible.module_utils.basic import AnsibleModule

# Optional: direct SSH support when not using Ansible persistent connection
try:
    import paramiko  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    paramiko = None  # fallback if not installed

import time
from typing import Optional, Tuple


def _ssh_log(msg: str) -> None:
    ts = time.strftime('%H:%M:%S')
    try:
        print(f"[SSH {ts}] {msg}")
    except Exception:
        pass

def send_ssh_command(socket_path, command):
    """Send a command via SSH and return the output."""
    try:
        connection = Connection(socket_path)
        output = connection.run_command(command)
        return output
    except Exception as e:
        return f"Error: {str(e)}"


def _read_until_idle(channel, idle_timeout: float = 1.0, overall_timeout: float = 20.0) -> str:
    """Read from an interactive Paramiko channel until there's no data for idle_timeout seconds
    or overall_timeout is reached. Returns the collected output as string.
    """
    output = []
    channel.settimeout(0.2)
    start = time.time()
    last_data_time = time.time()
    while True:
        if channel.recv_ready():
            try:
                data = channel.recv(65535)
            except Exception:
                break
            if not data:
                break
            output.append(data.decode(errors="ignore"))
            last_data_time = time.time()
        else:
            time.sleep(0.05)

        if (time.time() - last_data_time) > idle_timeout:
            break
        if (time.time() - start) > overall_timeout:
            break
    return "".join(output)


def send_direct_ssh_command(
    host: str,
    username: str,
    password: str,
    command: str,
    port: int = 22,
    timeout: float = 15.0,
    interactive: bool = True,
) -> Tuple[bool, str]:
    """Execute a command over SSH directly using Paramiko.

    Returns (ok, output). If Paramiko is not available, returns (False, reason).
    For network devices, interactive mode is often required for commands like '?'.
    """
    if paramiko is None:
        return False, "Paramiko is not installed. Please add 'paramiko' to requirements and install dependencies."

    _ssh_log(f"one-shot connect to {host}:{port} user={username}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            allow_agent=False,
            look_for_keys=False,
            timeout=timeout,
            auth_timeout=timeout,
            banner_timeout=timeout,
        )
        _ssh_log(f"connected to {host}:{port}")
        if interactive:
            _ssh_log(f"invoke interactive shell on {host}")
            chan = client.invoke_shell()
            # Read login banner/prompt
            pre = _read_until_idle(chan)
            # Send the command and read response
            _ssh_log(f"sending (one-shot) command: {command}")
            chan.send(command + "\n")
            time.sleep(0.1)
            out = _read_until_idle(chan)
            try:
                chan.close()
            except Exception:
                pass
            client.close()
            _ssh_log(f"one-shot command completed: {host}")
            return True, (pre + out).strip()
        else:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            out = stdout.read().decode(errors="ignore")
            err = stderr.read().decode(errors="ignore")
            client.close()
            combined = (out + ("\n" + err if err else "")).strip()
            return True, combined
    except Exception as e:
        try:
            client.close()
        except Exception:
            pass
        _ssh_log(f"one-shot SSH error: {e}")
        return False, f"SSH error: {e}"


class SSHSession:
    """Persistent SSH session using Paramiko with an interactive shell channel.

    Usage:
      sess = SSHSession(host, username, password)
      ok, out = sess.send('?', interactive=True)
      sess.close()
    """
    def __init__(self, host: str, username: str, password: str, port: int = 22, timeout: float = 15.0):
        if paramiko is None:
            raise RuntimeError("Paramiko is not installed; cannot open SSHSession")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = None
        try:
            _ssh_log(f"opening persistent SSHSession to {host}:{port} user={username}")
            self.client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                allow_agent=False,
                look_for_keys=False,
                timeout=timeout,
                auth_timeout=timeout,
                banner_timeout=timeout,
            )
            self.channel = self.client.invoke_shell()
            # drain initial banner/prompt
            _read_until_idle(self.channel)
            _ssh_log(f"persistent session established to {host}")
        except Exception:
            try:
                self.client.close()
            except Exception:
                pass
            raise

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def send(self, command: str, interactive: bool = True, timeout: float = 15.0, append_newline: bool = True) -> Tuple[bool, str]:
        try:
            if interactive:
                if self.channel is None:
                    return False, 'No interactive channel'
                # send and read
                _ssh_log(f"session send: {command}")
                cmd_to_send = command + ("\n" if append_newline else "")
                self.channel.send(cmd_to_send.encode() if isinstance(cmd_to_send, str) else cmd_to_send)
                time.sleep(0.05)
                out = _read_until_idle(self.channel, overall_timeout=timeout)
                _ssh_log(f"session received {len(out)} bytes for command")
                return True, out.strip()
            else:
                stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
                out = stdout.read().decode(errors="ignore")
                err = stderr.read().decode(errors="ignore")
                combined = (out + ("\n" + err if err else "")).strip()
                return True, combined
        except Exception as e:
            _ssh_log(f"SSHSession error: {e}")
            return False, f"SSHSession error: {e}"

    def close(self) -> None:
        try:
            if self.channel is not None:
                try:
                    self.channel.close()
                except Exception:
                    pass
                self.channel = None
        finally:
            try:
                self.client.close()
            except Exception:
                pass

if __name__ == "__main__":
    # Preserve Ansible module behavior
    module = AnsibleModule(
        argument_spec={
            "socket_path": {"type": "str", "required": True},
            "command": {"type": "str", "required": True},
        }
    )

    socket_path = module.params["socket_path"]
    command = module.params["command"]

    result = send_ssh_command(socket_path, command)
    module.exit_json(changed=False, output=result)