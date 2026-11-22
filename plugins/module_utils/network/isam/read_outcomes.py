# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Sanitized read-outcome records for targeted reads.

A read has three independent axes, set by different stages:

* ``command``   -- did the CLI command run?           (set by the read path)
* ``existence`` -- does the addressed instance exist?  (set by the read path)
* ``parse``     -- was the reply fully parsed?        (set by the parser)

Only ``existence: confirmed_absent`` -- the device's explicit
"instance does not exist" signal *about the addressed instance* -- may be
treated as evidence an instance is gone. ``unknown`` (a header-only reply, an
``invalid token`` rejection, a missing-dependency reply, or a failed read) is
NEVER absence. Consumers must keep, not remove, configuration for ``unknown``.

Output is sanitized: stable enums, the selector, and an error *class*. Raw
device text is never recorded, so the result is safe to publish in a module
result or a NOC artifact (it mirrors ``noc_safe_warnings`` on the NOC side).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Command axis.
COMMAND_OK = "ok"
COMMAND_REJECTED = "rejected"
COMMAND_FAILED = "failed"

# Instance-existence axis.
EXISTENCE_PRESENT = "present"
EXISTENCE_CONFIRMED_ABSENT = "confirmed_absent"
EXISTENCE_UNKNOWN = "unknown"

# Parsing axis.
PARSE_COMPLETE = "complete"
PARSE_PARTIAL = "partial"
PARSE_FAILED = "failed"
PARSE_UNVERIFIED = "unverified"

_WHOLE = "__whole__"
_RESOURCE = "__resource__"


def error_class(text):
    """A stable, coarse error class for a failed read. Never raw device text."""
    text = str(text).lower()
    if "timeout" in text or "timed out" in text:
        return "timeout"
    if "refused" in text or "unreachable" in text or "connection" in text:
        return "connection_error"
    return "device_error"


# When one selector is addressed by several commands (a dhcp-relay port is read on
# port-stats and v6-port-stats; duplicate identities share one read), the strongest
# signal wins: a failed read is stronger than presence, presence is stronger than a
# rejection, a rejection stronger than an explicit absence, all stronger than unknown.
_OUTCOME_PRIORITY = (
    (("failed", "unknown"), 4),
    (("ok", "present"), 3),
    (("rejected", "unknown"), 2),
    (("ok", "confirmed_absent"), 1),
)


def _outcome_priority(command_status, existence):
    for (command, ex), priority in _OUTCOME_PRIORITY:
        if command_status == command and existence == ex:
            return priority
    return 0  # ok/unknown (header-only reply, missing dependency, ...)


class ReadOutcomeCollector(object):
    """Accumulates per-selector command/existence outcomes and the parse outcome.

    A collector is created by a facts class for one targeted read and threaded
    into the shared read helpers. It is stateless with respect to the device:
    it only records what one read observed, and is consumed once by the module
    to build the sanitized result.
    """

    def __init__(self, resource):
        self._resource = resource
        self._by_selector = {}
        self._parse = {}

    def record(self, selector, command_status, existence, error_class_value=None,
               dependency_gap=None):
        """Record the command/existence outcome for one selector.

        ``selector`` is the instance identity the read addressed (``None`` for a
        whole-family read). ``dependency_gap`` notes that a *dependency* (e.g. a
        lower-interface) was reported missing, which leaves the addressed
        instance's own existence unknown -- it is not a confirmed absence.
        """
        record = {
            "resource": self._resource,
            "selector": selector,
            "command": command_status,
            "existence": existence,
        }
        if error_class_value:
            record["error_class"] = error_class_value
        if dependency_gap:
            record["dependency_gap"] = dependency_gap
        key = selector if selector is not None else _WHOLE
        previous = self._by_selector.get(key)
        if previous is not None and _outcome_priority(previous["command"], previous["existence"]) >= _outcome_priority(
                command_status, existence):
            # A stronger (or equally strong, recorded first) outcome for this selector
            # already stands: keep it.
            return
        self._by_selector[key] = record

    def record_parse(self, parse_status, section=None):
        """Record the parse outcome at resource level (``section=None``) or per section."""
        self._parse[section or _RESOURCE] = parse_status

    def has_parse(self):
        """Whether any parse outcome has been recorded (resource level or per section)."""
        return bool(self._parse)

    def to_result(self):
        """Sanitized, JSON-safe result: ``{resource, outcomes, parse?}``.

        ``outcomes`` is ordered by selector (whole-read outcome, if any, first)
        so it is deterministic artifact-to-artifact.
        """
        outcomes = [self._by_selector[_WHOLE]] if _WHOLE in self._by_selector else []
        outcomes += [self._by_selector[key] for key in sorted(
            (key for key in self._by_selector if key != _WHOLE), key=lambda v: (v is None, v))]
        result = {"resource": self._resource, "outcomes": outcomes}
        if self._parse:
            if len(self._parse) == 1 and _RESOURCE in self._parse:
                result["parse"] = self._parse[_RESOURCE]
            else:
                result["parse"] = dict((key, value) for key, value in self._parse.items()
                                       if key != _RESOURCE)
        return result
