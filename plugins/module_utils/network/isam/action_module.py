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
This base keeps only the execution mechanics -- check mode, sending the commands,
collecting the device responses and propagating failures. Device-specific behaviour
(which operation is required, validation, confirmations, reconnects, completion checks)
belongs to each module:

* ``build_commands`` (required) returns the command strings and MUST validate that an
  explicit operation is given. A bare resource identifier without an operation only
  navigates the ISAM admin hierarchy (CLI guide, global commands) and is not an action;
  reject it rather than reporting a change.
* ``verify`` (optional) inspects the responses for completion; override it for operations
  that need a confirmation, a reconnect or a follow-up read. Do not assume an operation
  succeeded just because it was sent.
"""

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)


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
            self.verify(commands, response)
        return result

    def build_commands(self):
        """Return the operational command strings; validate the explicit operation here.

        Must be implemented by the module. Reject a resource identifier without an
        operation (it would only navigate the admin hierarchy, not act).
        """
        raise NotImplementedError("action modules must implement build_commands")

    def run_commands(self, commands):
        """Send the commands and return the device responses; fail the task on error."""
        connection = get_resource_connection(self._module)
        try:
            resp = connection.edit_config(candidate=commands)
        except Exception as exc:
            self._module.fail_json(
                msg="ISAM action failed: %s" % to_text(exc), commands=commands,
            )
        return (resp or {}).get("response", [])

    def verify(self, commands, response):
        """Optional completion check (confirmation, reconnect, follow-up read).

        The default trusts the device response; override for operations that need it.
        """
        return None
