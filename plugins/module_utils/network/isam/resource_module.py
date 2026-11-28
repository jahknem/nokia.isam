# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Base class of the nokia.isam resource modules (config classes).

netcommon's ResourceModule with the ISAM CLI adaptations:

* removal: a parser's ``remval`` renders the removal form as is; ``no_remval: True``
  marks an attribute without removal form (nothing is rendered, with a warning);
  ``read_only: True`` marks a value derived by the device (never rendered). netcommon's
  fallback, prefixing the whole command with ``no``, is never valid ISAM CLI and fails.
* rendered: an explicit ``False`` renders the ``no`` form; netcommon's compare()
  skips False when there is no device value, i.e. always in ``rendered``.
* compaction: ``COMPACT_COMMAND_SCOPES`` packs the per-attribute commands of one CLI
  node into one command (the form the device prints), before commands are shown or sent.
* command safety: before commands are shown (every state, including rendered and the
  offline renders) or sent, a command containing a control character fails the module
  (``cli_safety``); a new line in a value would otherwise inject a second CLI command.
* offline action states: an action state (merged/replaced/overridden/deleted) given
  ``running_config`` renders against that configuration instead of reading the device,
  and never sends commands. ``running_config`` is the current state, either as CLI text
  (parsed like ``parsed``) or as the canonical resource JSON. With ``deleted`` and no
  ``config`` this renders the removal of everything in ``running_config`` — the offline
  counterpart of ``rendered`` for deletions (e.g. NOC previews a move/copy/delete).
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    emit_warnings,
    get_from_dict,
    remove_empties,
    to_list,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import get_path
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.cli_safety import (
    UnsafeCliCommandError,
    check_cli_commands,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    compact_cli_commands,
    covers_entry,
    requested_sections,
)


def _offline_config(resource):
    """An action state given ``running_config``: render against it, never touch the device.

    A module-level helper (not a property) so the lifecycle methods also work when invoked
    with a lightweight stand-in object in tests.
    """
    params = getattr(getattr(resource, "_module", None), "params", None) or {}
    return resource.state in getattr(resource, "ACTION_STATES", ()) and bool(params.get("running_config"))


def _offline_unknown_fields(value, spec, path="config"):
    """Field paths in a canonical running_config that the config argspec does not know.

    Without this check a wrong or renamed field silently yields zero removal commands;
    here it is reported so the caller can fix the snapshot instead of deleting nothing.
    """
    unknown = []
    kind = spec.get("type", "str")
    if kind == "dict" and isinstance(value, dict):
        options = spec.get("options") or {}
        valid = set(options)
        for sub in options.values():
            valid.update(sub.get("aliases") or [])
        for key, item in value.items():
            if key not in valid:
                unknown.append("%s.%s" % (path, key))
            elif key in options:
                unknown += _offline_unknown_fields(item, options[key], "%s.%s" % (path, key))
    elif kind == "list" and isinstance(value, list):
        element = {"type": spec.get("elements", "str"), "options": spec.get("options")}
        for index, item in enumerate(value):
            unknown += _offline_unknown_fields(item, element, "%s[%d]" % (path, index))
    return unknown


def _without_aliases(value, spec):
    """Drop alias keys the argspec validator keeps next to the canonical option name."""
    kind = spec.get("type", "str")
    options = spec.get("options") or {}
    if kind == "dict" and isinstance(value, dict) and options:
        aliases = set()
        for sub in options.values():
            aliases.update(sub.get("aliases") or [])
        return dict((key, _without_aliases(item, options[key]) if key in options else item)
                    for key, item in value.items() if key not in aliases or key in options)
    if kind == "list" and isinstance(value, list) and options:
        element = {"type": spec.get("elements", "str"), "options": options}
        return [_without_aliases(item, element) for item in value]
    return value


class IsamResourceModule(ResourceModule):
    """ResourceModule for ISAM CLI resources (see the module docstring)."""

    # Regexes with named groups ``scope`` and ``suffix`` (see compact_cli_commands).
    COMPACT_COMMAND_SCOPES = ()

    def _get_connection(self):
        if _offline_config(self):
            return None
        return super(IsamResourceModule, self)._get_connection()

    def gather_current(self):
        if _offline_config(self):
            running_config = self._module.params["running_config"]
            if running_config.strip()[:1] in ("{", "["):
                return self._offline_json(running_config)
            return deepcopy(self.get_facts(self._empty_fact_val, data=running_config))
        return super(IsamResourceModule, self).gather_current()

    def _offline_json(self, running_config):
        """The canonical resource JSON of an offline running_config, validated like config.

        It goes through the config argspec (type coercion, choices, required fields) and
        remove_empties, so it compares exactly like the facts read from a device: "100"
        and 100 are the same VLAN, an unset option is absent rather than None.
        """
        try:
            parsed = json.loads(running_config)
        except ValueError as exc:
            self._module.fail_json(msg="running_config is neither CLI text nor valid JSON: %s" % exc)
        spec = (getattr(self._module, "argument_spec", None) or {}).get("config") or {}
        unknown = _offline_unknown_fields(parsed, spec)
        if unknown:
            self._module.fail_json(
                msg="running_config contains fields unknown to the argspec: %s" % ", ".join(sorted(set(unknown)))
            )
        if not spec:
            return deepcopy(parsed)
        # Explicit nulls mean "unset" (as in gathered output); the validator would check
        # them against choices, so they are dropped first.
        result = ArgumentSpecValidator({"config": spec}).validate(remove_empties({"config": parsed}))
        if result.error_messages:
            self._module.fail_json(
                msg="running_config does not match the config argspec: %s" % "; ".join(result.error_messages)
            )
        return remove_empties({"config": _without_aliases(result.validated_parameters.get("config"), spec)}).get(
            "config", self._empty_fact_val)

    def execute_module(self):
        """Common lifecycle; families override only for a different execution path."""
        if self.state not in ("parsed", "gathered"):
            self.generate_commands()
            if self.state != "rendered" and not _offline_config(self):
                self.run_commands()
        return self.result

    def compare(self, parsers, want=None, have=None):
        if self.state != "rendered":
            return super(IsamResourceModule, self).compare(parsers, want=want, have=have)
        want = self.want if want is None else want
        for parser in to_list(parsers):
            compval = self._tmplt.get_parser(parser).get("compval") or parser
            if get_from_dict(want, compval) is False:
                self.addcmd(want, parser, True)
            else:
                super(IsamResourceModule, self).compare([parser], want=want, have=have)

    def addcmd(self, data, tmplt, negate=False):
        parser = self._tmplt.get_parser(tmplt) if hasattr(self._tmplt, "get_parser") else {}
        if parser.get("read_only"):
            return
        if not negate:
            super(IsamResourceModule, self).addcmd(data, tmplt, negate)
            return
        remval = parser.get("remval")
        if remval:
            command = self._tmplt._render(remval, data, False)
            if command:
                self.commands.extend(command if isinstance(command, list) else [command])
            return
        if parser.get("no_remval"):
            self._module.warn(
                "%s has no standalone removal form in ISAM CLI; it is retained until its parent object is removed" % tmplt
            )
            return
        before = len(self.commands)
        super(IsamResourceModule, self).addcmd(data, tmplt, negate)
        invalid = [command for command in self.commands[before:] if command.startswith("no configure ")]
        if invalid:
            del self.commands[before:]
            self._module.fail_json(
                msg="%s: parser %s has no removal form; refusing to render %r" % (self.__class__.__name__, tmplt, invalid[0])
            )

    def _compact(self):
        if self.COMPACT_COMMAND_SCOPES:
            self.commands[:] = compact_cli_commands(self.commands, self.COMPACT_COMMAND_SCOPES)
        # Every path that shows or sends commands passes here (result, run_commands and
        # family overrides of run_commands), so this is the central safety check.
        self._check_commands()

    def _check_commands(self):
        """Fail the module, before any command is shown or sent, when a command contains a
        control character (a new line in a value would inject a second CLI command; see
        cli_safety). The message names positions only, never command text (secrets)."""
        try:
            check_cli_commands(self.commands, self.__class__.__name__)
        except UnsafeCliCommandError as exc:
            del self.commands[:]
            self._module.fail_json(msg=str(exc))

    @property
    def result(self):
        self._compact()
        if _offline_config(self):
            # Offline preview: commands and the supplied before-state, no device after-read.
            result = {"warnings": self.warnings}
            emit_warnings(self._module, result)
            result["commands"] = self.commands
            result["before"] = self.before
            result["changed"] = False
            return result
        result = super(IsamResourceModule, self).result
        self._attach_read_outcomes(result)
        return result

    def _attach_read_outcomes(self, result):
        """Attach sanitized read_outcomes for a targeted gathered read (central).

        The facts class stashes the outcomes on the module during gathering (see
        finish_targeted_outcomes); whole-family and write-state reads stash none, so only
        an explicit targeted C(gathered) read surfaces them here.
        """
        if self.state != "gathered":
            return
        outcomes = getattr(self._module, "_isam_read_outcomes", None)
        if outcomes and outcomes.get("outcomes"):
            result["read_outcomes"] = outcomes

    def run_commands(self):
        """Send the commands one per transaction; report a partial execution on failure.

        netcommon sends the whole list in one edit_config call: when the device refuses a
        command, the failure names only the device message, and which commands were
        already applied is lost (a NOC apply could not tell what to read back). Here a
        failure carries the shared partial-execution schema (as action_module and the ONT
        deletion): ``accepted`` (sent and accepted), ``failed_command`` (outcome unknown)
        and ``pending`` (never sent); ``changed`` is true once a command was sent, since
        the failed one may have taken effect (as in the ONT deletion).
        """
        self._compact()
        if _offline_config(self):
            # Offline preview: commands are rendered, never sent (also covers families
            # that override execute_module and call run_commands directly).
            return
        if not self.commands or self.state not in self.ACTION_STATES:
            return
        if self._module.check_mode:
            self.changed = True
            return
        accepted = []
        for index, command in enumerate(self.commands):
            try:
                self._connection.edit_config(candidate=[command])
            except Exception as exc:
                self._module.fail_json(
                    msg="%s: command %d of %d failed: %s. Accepted before it: %d; not sent: %d. Read back the "
                        "device state before retrying; the failed command may have taken effect."
                        % (self.__class__.__name__, index + 1, len(self.commands), exc, len(accepted),
                           len(self.commands) - index - 1),
                    changed=True,
                    commands=self.commands,
                    accepted=list(accepted),
                    failed_command=command,
                    pending=self.commands[index + 1:],
                    failure_phase="execution",
                    completion_status="unknown",
                )
            accepted.append(command)
        self.changed = True


class TableResourceModule(IsamResourceModule):
    """A resource module whose grammar is one :class:`AttributeTable` (``TABLE``).

    Implements the state contract of ``docs/development-style.md`` for every node of the
    table, so a family only declares its table and adds device-rule code where needed:

    * merged/replaced/overridden/rendered compare each instance or section with
      ``TABLE.diff_commands``; only overridden removes list instances not given.
    * replaced and deleted with config touch only the named top-level sections.
    * deleted: without config every section is reset and every list instance removed.
      With config, a list instance named by its identity alone (or as a full entry) is
      removed; named attributes reset only themselves. In a section, named attributes
      reset only themselves; a section given without any value (``ont: {}``) is reset as
      a whole, together with its sub-sections.
    * Creating a list instance requires its node's mandatory options (fails early).

    want is used raw (an explicit default means "reset to default"); have has its
    defaults removed, so a default the device already has sends nothing.
    """

    TABLE = None

    def generate_commands(self):
        want = self.want or {}
        have = self.TABLE.without_defaults(self.have)
        for node in self.TABLE.nodes:
            if not self._touches(node):
                continue
            if node.is_list:
                self._compare_instances(node, want.get(node.key) or [], have.get(node.key) or [])
            elif self.state == "deleted":
                self._reset_section(node, get_path(have, node.path))
            else:
                self.commands.extend(self.TABLE.diff_commands(
                    node, None, get_path(want, node.path), get_path(have, node.path), self.state))

    def _touches(self, node):
        if self.state not in ("replaced", "deleted"):
            return True
        requested = requested_sections(self._module)
        if not requested:
            return True
        if not node.path:
            return any(attr.option in requested for attr in node.attrs)
        return node.path[0] in requested

    def _compare_instances(self, node, want, have):
        ident = node.identity
        wantd = dict((str(entry[ident]), entry) for entry in want)
        haved = dict((str(entry[ident]), entry) for entry in have)

        if self.state == "deleted":
            for name, have_entry in haved.items():
                if wantd and name not in wantd:
                    continue
                want_entry = wantd.get(name) or {}
                if covers_entry(want_entry, have_entry, [ident]):
                    self.commands.append(self.TABLE.removal_command(node, name))
                else:
                    named = set(key for key, value in want_entry.items() if key != ident and value is not None)
                    keep = dict((key, value) for key, value in have_entry.items() if key not in named)
                    self.commands.extend(self.TABLE.diff_commands(node, name, keep, have_entry, "replaced"))
            return

        if self.state == "overridden":
            for name in haved:
                if name not in wantd:
                    self.commands.append(self.TABLE.removal_command(node, name))

        for name, want_entry in wantd.items():
            have_entry = haved.get(name, {})
            creating = not have_entry and self.state != "rendered"
            if creating:
                missing = [option for option in node.mandatory if want_entry.get(option) is None]
                if missing:
                    self._module.fail_json(
                        msg="Creating %s '%s' requires %s (mandatory at creation, no removal form)."
                        % (node.cli, name, ", ".join(missing)))
            commands = self.TABLE.diff_commands(node, name, want_entry, have_entry, self.state)
            if not commands and (self.state == "rendered" or creating):
                # an instance with only its identity is created by its bare line
                commands = [self.TABLE.creation_command(node, name)]
            self.commands.extend(commands)

    def _reset_section(self, node, have):
        scope = self._deleted_scope(node)
        if scope is None:
            return
        keep = dict((key, value) for key, value in have.items() if scope and key not in scope)
        self.commands.extend(self.TABLE.diff_commands(node, None, keep, have, "replaced"))

    def _deleted_scope(self, node):
        """deleted: None (section not named), an empty set (reset the whole section) or
        the set of named options. Read from the raw parameters, where Ansible fills every
        option not given with None: 'ont: {}' arrives as a dict of Nones."""
        section = self._module.params.get("config")
        if not section:
            return set()
        emptied = False
        for key in node.path:
            section = section.get(key) if isinstance(section, dict) else None
            if section is None:
                # a parent given without any value resets its sub-sections too
                return set() if emptied else None
            emptied = emptied or not _has_values(section)
        named = set(attr.option for attr in node.attrs if section.get(attr.option) is not None)
        if named:
            return named
        return set() if emptied else None


def _has_values(value):
    """Whether value holds anything but None (recursively; Ansible's unset options)."""
    if isinstance(value, dict):
        return any(_has_values(item) for item in value.values())
    if isinstance(value, list):
        return bool(value)
    return value is not None
