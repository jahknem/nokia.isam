# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate, RESET_FIELDS
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)


class Linetest(object):
    """Resource implementation for safe LineTest configuration states."""

    def __init__(self, module):
        self.module = module
        self.template = LinetestTemplate()

    def execute_module(self):
        state = self.module.params["state"]
        config = self._without_unset(self.module.params.get("config") or {})
        result = {"changed": False}
        if state == "rendered":
            result["rendered"] = self.template.render(config)
        elif state == "parsed":
            result["parsed"] = self.template.parse(self.module.params.get("running_config"))
        elif state == "gathered":
            from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.linetest.linetest import LinetestFacts

            try:
                facts = LinetestFacts(self.module).populate_facts(
                    get_resource_connection(self.module), {"ansible_network_resources": {}}
                )
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self.module.fail_json(msg=to_text(exc))
            result["gathered"] = facts["ansible_network_resources"]["linetest"]
        else:
            from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.linetest.linetest import LinetestFacts

            connection = get_resource_connection(self.module)
            current = LinetestFacts(self.module).populate_facts(
                connection, {"ansible_network_resources": {}}
            )["ansible_network_resources"]["linetest"]
            desired = config
            commands = self._commands(state, desired, current)
            result["commands"] = commands
            if commands:
                if not self.module.check_mode:
                    connection.edit_config(candidate=commands)
                result["changed"] = True
        return result

    @staticmethod
    def _without_unset(config):
        """Ansible-injected None values are omissions, not explicit resets."""
        return {section: [{key: value for key, value in item.items() if value is not None} for item in entries or []]
                for section, entries in config.items()}

    def _commands(self, state, desired, current):
        current_sessions = {item["session_id"]: item for item in current.get("sessions", [])}
        current_parameters = {
            (item["session_id"], item["test_name"]): item
            for item in current.get("parameters", [])
        }

        if state == "deleted":
            targets = desired if any(desired.values()) else current
            if targets.get("parameters") and not targets.get("sessions"):
                self.module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
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
            if any(key[0] in desired_sessions for key in set(current_parameters) - desired_parameters):
                self.module.fail_json(msg="LineTest parameters have no supported delete command; delete their session instead")
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
            if self.module.params["state"] in ("replaced", "overridden"):
                changed.update((field.replace("-", "_"), None) for field in RESET_FIELDS
                               if item.get(field.replace("-", "_")) is None and previous.get(field.replace("-", "_")) is not None)
            if changed:
                commands.extend(self.template.render({"sessions": [dict(changed, session_id=item["session_id"])]}))
        for item in desired.get("parameters") or []:
            key = (item["session_id"], item["test_name"])
            previous = current_parameters.get(key, {})
            changed = {key: value for key, value in item.items() if previous.get(key) != value}
            if changed:
                commands.extend(self.template.render({"parameters": [dict(changed, session_id=item["session_id"], test_name=item["test_name"])]}))
        return commands
