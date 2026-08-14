from __future__ import absolute_import, division, print_function

import re
import time

from ansible.errors import AnsibleConnectionFailure
from ansible_collections.ansible.netcommon.plugins.connection.network_cli import (
    Connection as NetworkCliConnection,
)
DOCUMENTATION = """
---
author: Ansible Networking Team (@ansible-network)
name: isam_network_cli
short_description: Use network_cli with Nokia ISAM session recovery
description:
  - Provides the ansible.netcommon network_cli transport with ISAM-specific
    reconnect handling for transient SSH session failures.
  - This vendor connection wrapper is intentionally unusual. Standard
    network_cli retries some socket failures, but ISAM can authenticate and
    then close invoke_shell() when its CLI session pool is full. Paramiko
    exposes that case as EOFError outside the standard retry path.
extends_documentation_fragment:
  - ansible.netcommon.connection_persistent
options:
  host: {description: Remote device address., type: string}
  port: {description: Remote SSH port., type: integer, default: 22}
  network_os: {description: Network operating system plugin., type: string}
  remote_user: {description: SSH username., type: string}
  password: {description: SSH password., type: string, no_log: true}
  private_key_file: {description: SSH private key path., type: path}
  become: {description: Enable privilege escalation., type: boolean, default: false}
  become_errors: {description: Privilege escalation error behavior., type: string, default: warn}
  become_method: {description: Privilege escalation method., type: string, default: enable}
  host_key_auto_add: {description: Automatically add host keys., type: boolean, default: false}
  host_key_checking: {description: Verify SSH host keys., type: boolean, default: true}
  persistent_buffer_read_timeout: {description: Persistent read buffer timeout., type: float, default: 0.1}
  terminal_stdout_re: {description: Terminal prompt patterns., type: list}
  terminal_stderr_re: {description: Terminal error patterns., type: list}
  terminal_initial_prompt: {description: Initial terminal prompts., type: list}
  terminal_initial_answer: {description: Answers to initial prompts., type: list}
  terminal_initial_prompt_checkall: {description: Require all initial prompts., type: boolean, default: false}
  terminal_inital_prompt_newline: {description: Send a newline after the initial prompt., type: boolean, default: true}
  network_cli_retries: {description: Reconnect attempts for transient ISAM failures., type: integer, default: 3}
  isam_connect_retries:
    description: Reconnect attempts after a transient ISAM connection failure.
    type: integer
    default: 0
    vars:
      - name: ansible_isam_connect_retries
  isam_retry_authentication:
    description: Retry authentication failures as transient ISAM overload symptoms.
    type: boolean
    default: false
    vars:
      - name: ansible_isam_retry_authentication
  ssh_type:
    description: SSH implementation.
    type: string
    default: auto
    choices: [auto, paramiko, libssh]
    vars:
      - name: ansible_network_cli_ssh_type
  single_user_mode: {description: Enable single-user command caching., type: boolean, default: false}
"""


class Connection(NetworkCliConnection):
    """network_cli connection with fresh-transport recovery for ISAM.

    Most network collections only need a terminal plugin and the standard
    network_cli connection. ISAM is different because its session-limit
    rejection occurs after authentication, during invoke_shell(), where the
    standard connection plugin does not retry. This wrapper stays opt-in and
    only retries connection establishment; it never replays a command.
    """

    transient_connect_re = re.compile(
        r"Max\. Sessions Reached\.|CLI session closed before prompt|Channel closed|"
        r"Unable to connect to port|Connection refused|Connection timed out|timed out|"
        r"Error reading SSH protocol banner|Connection reset by peer",
        re.IGNORECASE,
    )
    authentication_re = re.compile(r"Failed to authenticate", re.IGNORECASE)

    def _connect(self):
        # Legacy ISAM software may offer only the ssh-rsa host-key algorithm.
        # Paramiko 5 no longer advertises it by default, while OpenSSH-only
        # ansible_ssh_extra_args are not used by network_cli.
        try:
            import paramiko
            from paramiko.rsakey import RSAKey
            from cryptography.hazmat.primitives.hashes import SHA1

            paramiko.Transport._key_info.setdefault("ssh-rsa", RSAKey)
            RSAKey.HASHES.setdefault("ssh-rsa", SHA1)
            preferred_keys = getattr(paramiko.Transport, "_preferred_keys", ())
            if "ssh-rsa" not in preferred_keys:
                paramiko.Transport._preferred_keys = preferred_keys + ("ssh-rsa",)
        except ImportError:
            pass

        retries = self.get_option("isam_connect_retries")
        for attempt in range(retries + 1):
            try:
                return super(Connection, self)._connect()
            except Exception as exc:
                message = str(exc)
                self.queue_message(
                    "vv",
                    "isam_connect_retry: attempt=%d exception=%s message=%r"
                    % (attempt + 1, type(exc).__name__, message),
                )
                # ISAM closes the channel during invoke_shell when its CLI
                # session pool is full. Paramiko exposes that as an empty
                # EOFError and discards the device's explanatory text.
                retryable = isinstance(exc, EOFError) or self.transient_connect_re.search(message)
                authentication_failure = self.authentication_re.search(message)
                if self.get_option("isam_retry_authentication"):
                    retryable = retryable or self.authentication_re.search(message)
                elif authentication_failure:
                    raise
                if not retryable or attempt == retries:
                    raise AnsibleConnectionFailure(
                        "ISAM connection failed during connect (%s): %s"
                        % (type(exc).__name__, message or "no error message")
                    )
                self._reset_transport()
                time.sleep(2 ** (attempt + 1))

    def _reset_transport(self):
        """Discard the failed shell and SSH transport before reconnecting.

        The public connection API has no recovery operation for a failed
        invoke_shell attempt, so this compatibility wrapper resets private
        network_cli state. It can be removed if netcommon adds this lifecycle
        handling upstream.
        """
        if self._ssh_shell is not None:
            try:
                self._ssh_shell.close()
            except Exception:
                pass
        if self._ssh_type_conn is not None:
            try:
                self._ssh_type_conn.close()
            except Exception:
                pass
        self._ssh_shell = None
        self._ssh_type_conn = None
        self._connected = False
