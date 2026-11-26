# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import (
    LinetestTemplate,
    RESET_FIELDS,
)


class Linetest(IsamResourceModule):
    """The isam_linetest config class (declarative single LineTest sessions/parameters).

    LineTest is not an ordinary settings resource. A session exists only after the
    action ``session-cmd create`` and is removed with ``session-cmd destroy``
    (``configure linetest single ltsession (sessionid) [session-cmd ...]``, CLI guide
    53.5). The action states therefore create a requested session that does not
    exist before setting its attributes, and destroy only sessions that exist;
    ``rendered`` (no device) renders the declarative attributes only, never an action.
    Parameters have no delete command of their own (delete their session instead),
    and ``group-opt``/``busy-overwrite``/``force-measure`` reset with a trailing ``no``
    (``... group-opt no``). The command rules below are therefore explicit device code;
    parsing/rendering of the declarative fields lives in LinetestTemplate.
    """

    def __init__(self, module):
        super(Linetest, self).__init__(
            empty_fact_val={"sessions": [], "parameters": []},
            facts_module=Facts(module),
            module=module,
            resource="linetest",
            tmplt=LinetestTemplate(),
        )

    def generate_commands(self):
        # Ansible fills omitted options with None. Those are not reset requests:
        # merged/rendered must preserve omissions. Replaced generates supported
        # resets explicitly, against the current session, in _diff_commands.
        config = self.want or {}
        if self.state == "rendered":
            self.commands = self.template.render(config)
            return
        self.commands = self._commands(self.state, config, self.have)

    @property
    def template(self):
        return self._tmplt

    def _commands(self, state, desired, current):
        current_sessions = {item["session_id"]: item for item in current.get("sessions", [])}
        current_parameters = {
            (item["session_id"], item["test_name"]): item
            for item in current.get("parameters", [])
        }

        if state == "deleted":
            targets = desired if any(desired.values()) else current
            # Only existing sessions are destroyed: deleted is idempotent.
            destroyed = [item["session_id"] for item in targets.get("sessions") or []
                         if item["session_id"] in current_sessions]
            # A parameter has no delete command; only its session can be destroyed.
            # Parameters that do not exist, or go with a destroyed session, need nothing.
            if any((item["session_id"], item["test_name"]) in current_parameters and
                   item["session_id"] not in destroyed for item in targets.get("parameters") or []):
                self._module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
            return ["configure linetest single ltsession %s session-cmd destroy" % session_id
                    for session_id in destroyed]

        if state == "merged":
            sessions = [
                dict(current_sessions.get(item["session_id"], {}), **item)
                for item in desired.get("sessions") or []
            ]
            parameters = [
                dict(current_parameters.get((item["session_id"], item["test_name"]), {}), **item)
                for item in desired.get("parameters") or []
            ]
            return self._diff_commands(current, {"sessions": sessions, "parameters": parameters})

        commands = []
        desired_sessions = {item["session_id"] for item in desired.get("sessions") or []}
        desired_parameters = {
            (item["session_id"], item["test_name"])
            for item in desired.get("parameters") or []
        }
        if state == "overridden":
            commands.extend(
                "configure linetest single ltsession %s session-cmd destroy" % session_id
                for session_id in current_sessions
                if session_id not in desired_sessions
            )
            # Destroying a session also removes its parameters. Only parameters
            # omitted from a retained session would need an unsupported deletion.
            if any(key[0] in desired_sessions for key in set(current_parameters) - desired_parameters):
                self._module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
        return commands + self._diff_commands(current, desired)

    def _diff_commands(self, current, desired):
        commands = []
        current_sessions = {item["session_id"]: item for item in current.get("sessions", [])}
        current_parameters = {
            (item["session_id"], item["test_name"]): item
            for item in current.get("parameters", [])
        }
        requested = set(item["session_id"] for item in desired.get("sessions") or [])
        for item in desired.get("parameters") or []:
            if item["session_id"] not in current_sessions and item["session_id"] not in requested:
                self._module.fail_json(
                    msg="LineTest session %s does not exist; add it to sessions to create it before setting its parameters"
                        % item["session_id"])
        for item in desired.get("sessions") or []:
            if item["session_id"] not in current_sessions:
                # A session's attributes need the session (CLI guide 53.5).
                commands.append("configure linetest single ltsession %s session-cmd create" % item["session_id"])
            previous = current_sessions.get(item["session_id"], {})
            changed = {key: value for key, value in item.items()
                       if key != "session_id" and previous.get(key) != value}
            if self.state in ("replaced", "overridden"):
                changed.update((field.replace("-", "_"), None) for field in RESET_FIELDS
                               if item.get(field.replace("-", "_")) is None and
                               previous.get(field.replace("-", "_")) is not None)
            if changed:
                commands.extend(self.template.render({"sessions": [dict(changed, session_id=item["session_id"])]}))
        for item in desired.get("parameters") or []:
            key = (item["session_id"], item["test_name"])
            previous = current_parameters.get(key, {})
            changed = {key: value for key, value in item.items() if previous.get(key) != value}
            if changed:
                commands.extend(self.template.render({"parameters": [dict(changed, session_id=item["session_id"], test_name=item["test_name"])]}))
        return commands
