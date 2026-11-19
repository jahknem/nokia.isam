# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import (
    LinetestTemplate,
)


class Linetest(IsamResourceModule):
    """The isam_linetest config class (declarative single LineTest sessions/parameters).

    LineTest is not an ordinary settings resource: sessions are created/destroyed with
    the action command ``session-cmd create|destroy`` (never rendered as configuration),
    parameters have no delete command of their own (delete their session instead), and
    ``group-opt``/``busy-overwrite``/``force-measure`` reset with a trailing ``no``
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

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        # The raw config (not self.want) is used on purpose: Ansible fills omitted
        # options with None, and the template renders None for group-opt/busy-overwrite/
        # force-measure as their trailing-no reset form. remove_empties would drop those.
        config = self._module.params.get("config") or {}
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
            targets = desired or current
            # A parameter has no delete command; only its session can be destroyed.
            if targets.get("parameters") and not targets.get("sessions"):
                self._module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
            return [
                "configure linetest single ltsession %s session-cmd destroy" % item["session_id"]
                for item in targets.get("sessions") or []
            ]

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
            if any(key in current_parameters for key in set(current_parameters) - desired_parameters):
                self._module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
        else:  # replaced
            commands.extend(
                self.template.render({"parameters": [item]})[0]
                for item in desired.get("parameters") or []
                if (item["session_id"], item["test_name"]) in current_parameters
            )
        return commands + self._diff_commands(current, desired)

    def _diff_commands(self, current, desired):
        commands = []
        current_sessions = {item["session_id"]: item for item in current.get("sessions", [])}
        current_parameters = {
            (item["session_id"], item["test_name"]): item
            for item in current.get("parameters", [])
        }
        for item in desired.get("sessions") or []:
            previous = current_sessions.get(item["session_id"], {})
            changed = {key: value for key, value in item.items() if previous.get(key) != value}
            if changed:
                commands.extend(self.template.render({"sessions": [dict(changed, session_id=item["session_id"])]}))
        for item in desired.get("parameters") or []:
            key = (item["session_id"], item["test_name"])
            previous = current_parameters.get(key, {})
            changed = {key: value for key, value in item.items() if previous.get(key) != value}
            if changed:
                commands.extend(self.template.render({"parameters": [dict(changed, session_id=item["session_id"], test_name=item["test_name"])]}))
        return commands
