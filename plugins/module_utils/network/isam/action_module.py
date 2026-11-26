# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""Base class of the nokia.isam operational action modules.

An action module performs a one-shot device operation (an ``admin ...`` command such
as clearing counters, rebooting an ONT or triggering a line test). It is distinct from:

* an Ansible **action plugin** (``plugins/action/``) -- a controller-side execution
  helper, not a device operation; and
* a **resource module** (:class:`IsamResourceModule`) -- declarative persistent
  configuration with the states merged/replaced/overridden/deleted/gathered/parsed/
  rendered and idempotence.

An action writes to the device but has no desired state to converge to and nothing to
gather back, so it has no resource states and is not idempotent: running it is an event.
This base keeps only the execution mechanics; device-specific behaviour belongs to each
module.

Three outcomes must stay distinct throughout the API:

* **sent** -- the command was handed to the device (``commands``);
* **accepted** -- the device answered without a recognised error (``response``); the
  terminal plugin raises on the device error patterns it knows (``Error:``, ``invalid
  token``, ``command is not complete``, ...), which surfaces here as a failure; and
* **completed** -- the operation actually took effect, which only the module can judge
  (``verify``). A clean transport return is *not* proof of completion.

Execution contract:

* ``build_commands`` (required) returns the command strings and MUST validate that an
  explicit operation is given. A bare resource identifier without an operation only
  navigates the ISAM admin hierarchy (CLI guide, global commands) and is not an action;
  reject it rather than reporting a change. Validate identifiers with
  :meth:`validate_identifier` before interpolating them into a command.
* Commands are sent **one per transaction**, so a failure reports exactly which
  operations completed, which failed (outcome unknown -- it may have executed) and which
  were never sent. This matters for non-idempotent operations: a retry must not blindly
  re-run completed ones. The cost is a fresh shell per command (the connection resets its
  transport after each ``edit_config``).
* ``send_command`` (optional override) sends one command. Override it for operations that
  expect a **transport loss** (a reboot drops the SSH session before returning) or an
  **interactive confirmation prompt**: those must be handled *during* execution, not in
  ``verify``, which only runs after a clean return. A transport failure is an unknown
  outcome, not proof the operation did not occur.
* ``verify`` (optional override) inspects the responses for completion; the default trusts
  the transport. Override it for operations whose success is not reflected in the immediate
  response (a follow-up read, a reconnect, a confirmation).

``changed`` defaults to "an operation was sent", which suits state-changing operations
(counter resets, reboots). A **diagnostic** operation (e.g. a ping) does not change device
state and should report ``changed=False``; such a module overrides ``execute_module`` (or
adjusts the result) rather than inheriting this default.
"""

import re

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)

# Nokia CLI resource identifiers (rack/shelf/slot/port[:vpi:vci], PON/ONT paths, ng2:...,
# voip/vuni): letters, digits and / : . _ - only. No whitespace, control characters or
# command separators, so an identifier from inventory cannot inject extra CLI tokens.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9/:._-]+$")
# A MAC address as the ISAM prints it: six colon-separated hex bytes (aa:bb:cc:a1:02:03).
_MAC_RE = re.compile(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$")


class IsamActionModule(object):
    """Execution mechanics for one-shot ISAM operational actions (see module docstring)."""

    def __init__(self, module):
        self._module = module

    def execute_module(self):
        commands = self.build_commands()
        # An action is an event, not a convergence: sending it is a change. In check mode
        # the commands are reported as what would run, without touching the device.
        result = {"changed": bool(commands), "commands": commands}
        if commands and not self._module.check_mode:
            response = self.run_commands(commands)
            result["response"] = response
            try:
                self.verify(commands, response)
            except Exception as exc:
                self._fail(
                    "ISAM action verification failed: %s. Commands were sent and accepted, "
                    "but completion is unknown; do not blindly retry the operation." % to_text(exc),
                    commands, "verification", sent=commands, accepted=commands, completed=[],
                    failed_command=None, response=response, changed=True,
                )
            result.update(sent=commands, accepted=commands, completed=commands)
        return result

    def _trusts_transport(self):
        """Whether the module keeps the default verify, i.e. an accepted command counts as completed."""
        return getattr(type(self).verify, "__func__", type(self).verify) is IsamActionModule.verify

    def _fail(self, msg, commands, phase, sent, accepted, completed, failed_command, response, changed):
        """Fail with the one result schema shared by every failure phase.

        ``sent`` were handed to the device, ``accepted`` answered without a recognised error,
        ``completed`` are confirmed to have taken effect, ``failed_command`` has an unknown
        outcome, ``pending`` were never sent. ``failure_phase`` is ``connection``,
        ``execution`` or ``verification``.
        """
        pending = [command for command in commands[len(sent):]]
        self._module.fail_json(
            msg=msg,
            changed=changed,
            failure_phase=phase,
            completion_status="not_started" if not sent else "unknown",
            commands=commands,
            sent=sent,
            accepted=accepted,
            completed=completed,
            failed_command=failed_command,
            pending=pending,
            response=response,
        )

    def build_commands(self):
        """Return the operational command strings; validate the explicit operation here.

        Must be implemented by the module. Reject a resource identifier without an
        operation (it would only navigate the admin hierarchy, not act).
        """
        raise NotImplementedError("action modules must implement build_commands")

    def validate_identifier(self, value, label="identifier"):
        """Fail unless value is a safe Nokia CLI resource identifier (no whitespace,
        control characters or command separators). Returns the value when valid."""
        if not isinstance(value, str) or not _IDENTIFIER_RE.fullmatch(value):
            self._module.fail_json(
                msg="Invalid %s %r: expected a Nokia CLI resource identifier "
                "(letters, digits and / : . _ -), without whitespace or control characters." % (label, value),
            )
        return value

    def validate_mac(self, value, label="MAC address"):
        """Fail unless value is six colon-separated hex bytes (aa:bb:cc:dd:ee:ff)."""
        if not isinstance(value, str) or not _MAC_RE.fullmatch(value):
            self._module.fail_json(
                msg="Invalid %s %r: expected six colon-separated hex bytes (aa:bb:cc:dd:ee:ff)." % (label, value),
            )
        return value

    def run_commands(self, commands):
        """Send the commands one per transaction; return the device responses.

        On failure, report partial execution in the shared schema (see ``_fail``): the
        commands accepted before the failure, ``failed_command`` (outcome unknown) and
        ``pending`` (never sent). The accepted commands count as ``completed`` only when the
        module trusts the transport (keeps the default ``verify``); a module with its own
        completion check reports ``completed: []``, as verify never ran for them.
        Connection-acquisition and execution errors are both formatted.
        """
        connection = self._connect(commands)
        accepted, responses = [], []
        for index, command in enumerate(commands):
            try:
                response = self.send_command(connection, command)
            except Exception as exc:
                self._fail(
                    "ISAM action failed at command %d of %d (%s): %s. The outcome of this "
                    "command is unknown -- it may have executed; do not blindly retry it. "
                    "Accepted: %s. Not sent: %s."
                    % (index + 1, len(commands), command, to_text(exc), accepted, commands[index + 1:]),
                    commands, "execution", sent=commands[:index + 1], accepted=accepted,
                    completed=list(accepted) if self._trusts_transport() else [],
                    failed_command=command, response=responses, changed=True,
                )
            accepted.append(command)
            responses.extend(response or [])
        return responses

    def _connect(self, commands):
        try:
            return get_resource_connection(self._module)
        except Exception as exc:
            self._fail("ISAM action failed to acquire a connection: %s" % to_text(exc), commands, "connection",
                       sent=[], accepted=[], completed=[], failed_command=None, response=[], changed=False)

    def send_command(self, connection, command):
        """Send one action command and return its response list.

        Override for operations expecting a transport loss (reboot) or an interactive
        confirmation prompt -- handle those here, during execution, not in ``verify``.
        The default sends a single-command transaction; the device error patterns known
        to the terminal plugin raise here and are reported as failures by run_commands.
        """
        resp = connection.edit_config(candidate=[command])
        return (resp or {}).get("response", [])

    def verify(self, commands, response):
        """Optional completion check (confirmation, reconnect, follow-up read).

        The default trusts the transport (accepted != completed); override for operations
        whose success is not reflected in the immediate response.
        """
        return None
