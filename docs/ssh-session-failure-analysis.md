# SSH Session Failure Analysis

Date: 2026-08-10

Target: `DS-LIN-TEST-01`

All tests were read-only. Interactive probes requested
`info configure ani ont flat`; no configuration or administrative command was
issued.

## Device Behavior

The synchronized OpenSSH probe used Debian 11, OpenSSH 8.4, and an interactive
PTY. ISAM does not accept SSH exec requests; those fail with `exec request
failed on channel 0` and are not a transient session error.

| Concurrent sessions | Result |
| --- | --- |
| 1 | 1 success |
| 5 | 5 successes |
| 10 | 10 successes |
| 15 | 13 successes, 2 `Max. Sessions Reached.` |
| 20, run 1 | 15 successes, 4 TCP connect timeouts, 1 authentication rejection |
| 20, run 2 | 16 successes, 4 TCP connect timeouts |
| 20, run 3 | 16 successes, 4 TCP connect timeouts |

Available capacity varies with sessions opened by other clients. During a
deliberately filled pool, OpenSSH received:

```text
Max. Sessions Reached.
Connection to 10.190.1.40 closed by remote host.
```

After repeated high-concurrency bursts, port 22 temporarily returned
`Connection refused`. It recovered without intervention after approximately
two minutes.

## Paramiko Translation

With the pool full, direct Paramiko testing established and authenticated the
SSH transport, then failed in `invoke_shell()` with an empty `EOFError`.
Paramiko discards the device's `Max. Sessions Reached.` text in this path.

Standard `ansible.netcommon.network_cli` consequently exposed several symptoms
under load:

- `Error reading SSH protocol banner ... Connection reset by peer` during SSH
  banner exchange.
- `Failed to authenticate` during password authentication.
- `timed out` or `Unable to connect to port 22` before authentication.
- `Internal error` when the empty `EOFError` escaped initial persistent
  connection setup.
- `list index out of range` when a closed pre-prompt session reached resource
  parsing as an empty response.

`Internal error` is Ansible JSON-RPC's generic wrapper, not an ISAM error and
must not be used as a retry classifier.

## Retry Policy

### Why A Custom Connection

Most Ansible network collections use only a terminal plugin and the standard
`ansible.netcommon.network_cli` connection. That is insufficient for this ISAM
behavior. Standard `network_cli` retries some exceptions raised while opening
the TCP/SSH connection, but its connection process does not recover the
post-authentication `invoke_shell()` path. Paramiko raises an empty `EOFError`
when ISAM rejects a shell because `Max. Sessions Reached.`.

The collection therefore provides the opt-in
`nokia.isam.isam_network_cli` wrapper. It must reset private `network_cli`
shell and transport state before reconnecting, because the public connection
API has no operation for recovering a failed shell request. The wrapper retries
connection setup only; it never replays a command. If `ansible.netcommon` adds
equivalent post-authentication lifecycle recovery, this vendor wrapper should
be removed in favor of the upstream implementation.

The optional `nokia.isam.isam_network_cli` connection retries only connection
establishment. Every retry discards the shell and SSH transport first.

Retryable by default when `ansible_isam_connect_retries` is greater than zero:

- Paramiko `EOFError` during shell creation.
- `Max. Sessions Reached.` if a transport exposes the device text.
- Closed channel before the first CLI prompt.
- TCP refusal or timeout.
- SSH banner reset or timeout.

Not retried by default:

- Authentication failures. Set `ansible_isam_retry_authentication: true` only
  where valid credentials are known and the device exhibits transient overload
  rejection. This can increase account-lockout risk.
- Host-key and configuration errors.
- Any `info`, `show`, or configuration command after connection setup. Commands
  are never replayed automatically.
- SSH exec rejection; ISAM requires an interactive shell.

The ISAM-specific retry count defaults to zero. Delays are exponential: 2, 4,
8, 16 seconds, and so on. Standard `ansible_network_cli_retries` remains a
separate ansible.netcommon setting.

## Recovery Validation

A controlled test filled the available CLI pool with interactive sessions.
Raw clients received session rejection, while
`nokia.isam.isam_network_cli` with `ansible_isam_connect_retries: 1` waited and
established a fresh transport after capacity became available. The gathered ANI
ONT request succeeded after 13 seconds.
