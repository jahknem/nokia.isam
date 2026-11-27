# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Sanitized read-outcome records for targeted reads.

A read has three independent axes:

* ``command``   -- did the CLI command run?           (set by the read path)
* ``existence`` -- does the addressed instance exist?  (set by the read path)
* ``parse``     -- could the reply be parsed?         (resource level)

The parse axis is coarse: ``failed`` when the family parser raised on the reply
(whole-node reads, which parse inside the read path), otherwise ``unverified``
-- no parser records its coverage of the reply, so a read never claims a
complete parse.

Only ``existence: confirmed_absent`` may be treated as evidence an instance is
gone: the device's explicit "instance does not exist" *about the addressed
instance*, or a header-only reply to its 'flat detail' read (see
docs/targeted-read-contract.md). ``unknown`` (an ``invalid token`` rejection, a
missing-dependency reply, another instance's line, an unobservable setting, or a
failed read) is NEVER absence. Consumers must keep, not remove, configuration for
``unknown``.

Outcomes are per (config section, instance): two sections can name the same
identity value (e.g. an equipment-ont interface and loop), and those are
different instances that are never merged.

Output is sanitized: stable enums, the section, the selector, and an error
*class*. Raw device text is never recorded, so the result is safe to publish
in a module result or a NOC artifact (it mirrors ``noc_safe_warnings`` on the
NOC side).
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

# Parsing axis (see the module docstring: only these two are produced).
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


class ReadOutcomeCollector(object):
    """Accumulates per-(section, selector) command/existence outcomes and the parse
    outcome.

    A collector is created by a facts class for one targeted read and threaded
    into the shared read helpers. It is stateless with respect to the device:
    it only records what one read observed, and is consumed once by the module
    to build the sanitized result.

    When one instance is addressed by several reads (a dhcp-relay port is read on
    port-stats and v6-port-stats), the collector keeps one *conservative*
    aggregate: a failed read dominates (the module fails and the read proves
    nothing), a single present read proves presence, ``confirmed_absent`` holds
    only when *every* read of the instance confirmed absence, and anything less
    is ``unknown``. ``confirmed_absent`` is the one outcome consumers act on, so
    it must never be aggregated from a mix of absence and inconclusive reads.
    """

    def __init__(self, resource):
        self._resource = resource
        self._entries = {}
        self._parse = {}

    @property
    def resource(self):
        """The resource family this collector records outcomes for."""
        return self._resource

    def record(self, section, selector, command_status, existence, error_class_value=None,
               dependency_gap=None):
        """Record the command/existence outcome of one read of one instance.

        ``section`` is the config section that named the instance (a
        TARGETED_GATHER section, e.g. ``config``); instances in different
        sections are never merged. ``selector`` is the instance identity the
        read addressed (``None`` for a whole-family read). ``dependency_gap``
        notes that a *dependency* (e.g. a lower-interface) was reported missing,
        which leaves the addressed instance's own existence unknown -- it is not
        a confirmed absence.
        """
        record = {
            "resource": self._resource,
            "selector": selector,
            "command": command_status,
            "existence": existence,
        }
        if section is not None:
            record["section"] = section
        if error_class_value:
            record["error_class"] = error_class_value
        if dependency_gap:
            record["dependency_gap"] = dependency_gap
        key = (section, selector if selector is not None else _WHOLE)
        entry = self._entries.get(key)
        if entry is None:
            entry = self._entries[key] = {
                "failed": None,
                "present": None,
                "absent": None,
                "inconclusive": None,
                "n_absent": 0,
                "n_total": 0,
            }
        entry["n_total"] += 1
        if command_status == COMMAND_FAILED:
            if entry["failed"] is None:
                entry["failed"] = record
        elif existence == EXISTENCE_PRESENT:
            if entry["present"] is None:
                entry["present"] = record
        elif existence == EXISTENCE_CONFIRMED_ABSENT:
            entry["n_absent"] += 1
            if entry["absent"] is None:
                entry["absent"] = record
        elif entry["inconclusive"] is None:
            # ok/unknown (missing dependency, unobservable setting) or rejected:
            # the first one stands, so a dependency gap is not lost.
            entry["inconclusive"] = record

    @staticmethod
    def _resolve(entry):
        """The conservative aggregate of one instance's reads (see the class docstring)."""
        if entry["failed"] is not None:
            return entry["failed"]
        if entry["present"] is not None:
            return entry["present"]
        if entry["n_absent"] == entry["n_total"]:
            return entry["absent"]
        return entry["inconclusive"]

    def record_parse(self, parse_status, section=None):
        """Record the parse outcome at resource level (``section=None``) or per section."""
        self._parse[section or _RESOURCE] = parse_status

    def has_parse(self):
        """Whether any parse outcome has been recorded (resource level or per section)."""
        return bool(self._parse)

    def to_result(self):
        """Sanitized, JSON-safe result: ``{resource, outcomes, parse?}``.

        ``outcomes`` is ordered by (section, selector) -- a whole-read outcome,
        if any, first -- so it is deterministic artifact-to-artifact.
        """
        outcomes = [self._resolve(entry) for entry in
                    (self._entries[key] for key in sorted(
                        self._entries, key=lambda key: (key[1] != _WHOLE, key[0] or "", key[1])))]
        result = {"resource": self._resource, "outcomes": outcomes}
        if self._parse:
            if len(self._parse) == 1 and _RESOURCE in self._parse:
                result["parse"] = self._parse[_RESOURCE]
            else:
                result["parse"] = dict((key, value) for key, value in self._parse.items()
                                       if key != _RESOURCE)
        return result
