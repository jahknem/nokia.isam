# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Every module's DOCUMENTATION, EXAMPLES and RETURN agree with the argspec it really uses.

The argument spec is captured from the ``AnsibleModule(...)`` call each module's
``main()`` makes, so wiring in ``main()`` (``mutually_exclusive``, ``required_if``, ...)
is covered too, not only the argspec class. The comparison follows what
``ansible-test sanity --test validate-modules`` checks (option names, types, required,
choices, defaults, elements, aliases, suboptions, explicit ``no_log`` on secret-like
names) and additionally validates every EXAMPLES task against the argspec.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ast
import importlib
import re
from pathlib import Path

import pytest
import yaml

from ansible.module_utils import basic
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator
from ansible.module_utils.common.validation import check_type_bool, check_type_float, check_type_int, check_type_str

ROOT = Path(__file__).resolve().parents[5]
MODULES = ROOT / "plugins" / "modules"
FRAGMENTS = ROOT / "plugins" / "doc_fragments"
MODULE_NAMES = sorted(path.stem for path in MODULES.glob("*.py") if path.stem != "__init__")

# validate-modules' regex for option names that look like secrets: such options need an
# explicit no_log (True or False) in the argspec.
NO_LOG_REGEX = re.compile(r"(?:pass(?!ive)|secret|token|key)", re.I)

DOC_OPTION_KEYS = {
    "description", "type", "required", "choices", "default", "elements", "aliases",
    "suboptions", "version_added", "version_added_collection",
}
# Keys AnsibleModule understands in an argspec entry; anything else is silently ignored
# (e.g. "min"/"max" never enforced a range).
SPEC_KEYS = {
    "type", "required", "default", "choices", "elements", "options", "aliases", "no_log",
    "apply_defaults", "fallback", "removed_in_version", "removed_at_date", "removed_from_collection",
    "deprecated_aliases", "mutually_exclusive", "required_together", "required_one_of", "required_if",
    "required_by",
}
COERCE = {"int": check_type_int, "str": check_type_str, "bool": check_type_bool, "float": check_type_float}

# The standard return values of the netcommon resource-module states.
STATE_RETURNS = {
    "merged": ("before", "after", "commands"),
    "replaced": ("before", "after", "commands"),
    "overridden": ("before", "after", "commands"),
    "deleted": ("before", "after", "commands"),
    "gathered": ("gathered",),
    "rendered": ("rendered",),
    "parsed": ("parsed",),
}


class _Captured(Exception):
    def __init__(self, kwargs):
        super(_Captured, self).__init__("captured")
        self.kwargs = kwargs


def _module_kwargs(name, monkeypatch):
    """The keyword arguments main() passes to AnsibleModule (never executes the module)."""
    def _capture(self, *args, **kwargs):
        if args:
            kwargs["argument_spec"] = args[0]
        raise _Captured(kwargs)

    monkeypatch.setattr(basic.AnsibleModule, "__init__", _capture)
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.%s" % name)
    with pytest.raises(_Captured) as captured:
        module.main()
    return captured.value.kwargs


def _blocks(name):
    tree = ast.parse((MODULES / ("%s.py" % name)).read_text())
    blocks = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("DOCUMENTATION", "EXAMPLES", "RETURN"):
                blocks[node.targets[0].id] = node.value.value
    return blocks


def _fragment(name):
    collection, _sep, short = name.rpartition(".")
    assert collection == "nokia.isam", "only the collection's own fragments are resolved here: %s" % name
    tree = ast.parse((FRAGMENTS / ("%s.py" % short)).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "DOCUMENTATION":
            return yaml.safe_load(node.value.value)
    raise AssertionError("fragment %s has no DOCUMENTATION" % name)


def documentation(name):
    """DOCUMENTATION with the collection's doc fragments merged (module keys win, as in ansible-doc)."""
    doc = yaml.safe_load(_blocks(name)["DOCUMENTATION"])
    fragments = doc.get("extends_documentation_fragment") or []
    if isinstance(fragments, str):
        fragments = [fragments]
    for fragment_name in fragments:
        fragment = _fragment(fragment_name)
        for key, value in fragment.items():
            if key == "options":
                options = dict(value)
                for option, spec in (doc.get("options") or {}).items():
                    merged = dict(options.get(option) or {})
                    merged.update(spec)
                    options[option] = merged
                doc["options"] = options
            elif key in ("notes", "seealso"):
                doc[key] = list(doc.get(key) or []) + list(value)
            else:
                doc.setdefault(key, value)
    return doc


def _same_value(kind, doc_value, spec_value):
    if doc_value is None or spec_value is None:
        return doc_value is None and spec_value is None
    if type(doc_value) is not type(spec_value):
        return False
    return doc_value == spec_value


def _same_default(kind, doc_value, spec_value):
    if doc_value is None or spec_value is None:
        return doc_value is None and spec_value is None
    coerce = COERCE.get(kind)
    if coerce is not None:
        try:
            return coerce(doc_value) == coerce(spec_value) and type(doc_value) is type(spec_value)
        except (TypeError, ValueError):
            return False
    return doc_value == spec_value


def _is_stub(option, description):
    """A description that only repeats the option name ("Name.", "Server host key.")."""
    text = " ".join(description) if isinstance(description, list) else str(description)
    words = lambda value: re.sub(r"[^a-z0-9]+", " ", value.lower()).split()  # noqa: E731
    return words(text) == words(option)


def compare_options(doc_options, spec_options, path=""):
    """Mismatches between documented options and an argspec (recursively)."""
    problems = []
    doc_options = doc_options or {}
    spec_options = spec_options or {}
    for option in sorted(set(spec_options) - set(doc_options)):
        problems.append("%s%s: in argspec, undocumented" % (path, option))
    for option in sorted(set(doc_options) - set(spec_options)):
        problems.append("%s%s: documented, not in argspec" % (path, option))
    for option in sorted(set(doc_options) & set(spec_options)):
        where = "%s%s" % (path, option)
        doc = doc_options[option] or {}
        spec = spec_options[option] or {}
        for key in sorted(set(doc) - DOC_OPTION_KEYS):
            problems.append("%s: invalid documentation key %r" % (where, key))
        for key in sorted(set(spec) - SPEC_KEYS):
            problems.append("%s: invalid argspec key %r (ignored by AnsibleModule)" % (where, key))
        description = doc.get("description")
        if not description or (isinstance(description, list) and not all(description)):
            problems.append("%s: no description" % where)
        elif _is_stub(option, description):
            problems.append("%s: stub description %r" % (where, description))
        kind = spec.get("type", "str")
        if doc.get("type", "str") != kind:
            problems.append("%s: type %r documented, %r in argspec" % (where, doc.get("type", "str"), kind))
        if bool(doc.get("required", False)) != bool(spec.get("required", False)):
            problems.append("%s: required %r documented, %r in argspec" % (where, doc.get("required", False), spec.get("required", False)))
        doc_choices, spec_choices = doc.get("choices"), spec.get("choices")
        if (doc_choices is None) != (spec_choices is None) or (
                doc_choices is not None and sorted(map(repr, doc_choices)) != sorted(map(repr, spec_choices))):
            problems.append("%s: choices %r documented, %r in argspec" % (where, doc_choices, spec_choices))
        element_kind = spec.get("elements") if kind == "list" else kind
        if not _same_default(element_kind if kind != "list" else None, doc.get("default"), spec.get("default")):
            problems.append("%s: default %r documented, %r in argspec" % (where, doc.get("default"), spec.get("default")))
        if kind == "list" and not spec.get("elements"):
            problems.append("%s: list without elements in argspec" % where)
        if doc.get("elements") != spec.get("elements"):
            problems.append("%s: elements %r documented, %r in argspec" % (where, doc.get("elements"), spec.get("elements")))
        if sorted(doc.get("aliases") or []) != sorted(spec.get("aliases") or []):
            problems.append("%s: aliases %r documented, %r in argspec" % (where, doc.get("aliases"), spec.get("aliases")))
        if NO_LOG_REGEX.search(option) and "no_log" not in spec and kind not in ("dict", "list", "bool"):
            problems.append("%s: secret-like name without explicit no_log in argspec" % where)
        if NO_LOG_REGEX.search(option) and "no_log" not in spec and kind in ("dict", "list") and not spec.get("options"):
            problems.append("%s: secret-like name without explicit no_log in argspec" % where)
        if spec.get("options") is None and doc.get("suboptions") is not None:
            problems.append("%s: suboptions documented, none in argspec" % where)
        elif spec.get("options") is not None:
            if doc.get("suboptions") is None:
                problems.append("%s: suboptions in argspec, undocumented" % where)
            problems += compare_options(doc.get("suboptions"), spec.get("options"), where + ".")
    return problems


def _tasks(examples):
    """Every task dict in EXAMPLES (descending into blocks)."""
    data = yaml.safe_load(examples) or []
    pending = list(data) if isinstance(data, list) else []
    while pending:
        task = pending.pop(0)
        if not isinstance(task, dict):
            continue
        for key in ("block", "rescue", "always", "tasks"):
            pending.extend(task.get(key) or [])
        yield task


def _strip_templated(value):
    """Drop Jinja-templated values: they are resolved at runtime, not validatable here."""
    if isinstance(value, dict):
        return dict((key, _strip_templated(item)) for key, item in value.items()
                    if not (isinstance(item, str) and "{{" in item))
    if isinstance(value, list):
        return [_strip_templated(item) for item in value if not (isinstance(item, str) and "{{" in item)]
    return value


def example_problems(name, kwargs):
    problems = []
    names = ("nokia.isam.%s" % name, name)
    validator = ArgumentSpecValidator(
        kwargs["argument_spec"],
        mutually_exclusive=kwargs.get("mutually_exclusive"),
        required_together=kwargs.get("required_together"),
        required_one_of=kwargs.get("required_one_of"),
        required_if=kwargs.get("required_if"),
        required_by=kwargs.get("required_by"),
    )
    count = 0
    for task in _tasks(_blocks(name).get("EXAMPLES") or ""):
        for key in names:
            if key not in task:
                continue
            count += 1
            args = _strip_templated(task[key] or {})
            if not isinstance(args, dict):
                problems.append("EXAMPLES task %r: arguments are not a mapping" % task.get("name"))
                continue
            result = validator.validate(args)
            for error in result.error_messages:
                problems.append("EXAMPLES task %r: %s" % (task.get("name"), error))
    if not count:
        problems.append("EXAMPLES: no task uses the module")
    return problems


def return_problems(name, kwargs):
    problems = []
    returns = yaml.safe_load(_blocks(name).get("RETURN") or "") or {}
    for key, entry in returns.items():
        for field in ("description", "returned", "type"):
            if not (entry or {}).get(field):
                problems.append("RETURN %s: no %s" % (key, field))
    state = kwargs["argument_spec"].get("state") or {}
    choices = state.get("choices") or ()
    for choice in choices:
        for key in STATE_RETURNS.get(choice, ()):
            if key not in returns:
                problems.append("RETURN %s: undocumented (state %s)" % (key, choice))
    config = kwargs["argument_spec"].get("config") or {}
    if "merged" in choices or "gathered" in choices and config.get("options"):
        # structured resource data has the shape of config
        for key in ("before", "after", "gathered", "parsed"):
            entry = returns.get(key) or {}
            if entry and entry.get("type") != config.get("type", "str"):
                problems.append("RETURN %s: type %r, config is %r" % (key, entry.get("type"), config.get("type")))
        for key in ("commands", "rendered"):
            entry = returns.get(key) or {}
            if entry and (entry.get("type"), entry.get("elements")) != ("list", "str"):
                problems.append("RETURN %s: must be a list of str" % key)
    return problems


def module_problems(name, monkeypatch):
    kwargs = _module_kwargs(name, monkeypatch)
    doc = documentation(name)
    problems = compare_options(doc.get("options"), kwargs["argument_spec"])
    for field in ("module", "short_description", "description", "author", "version_added"):
        if not doc.get(field):
            problems.append("DOCUMENTATION: no %s" % field)
    if doc.get("module") != name:
        problems.append("DOCUMENTATION: module %r, file %s" % (doc.get("module"), name))
    states = (kwargs["argument_spec"].get("state") or {}).get("choices") or ()
    if "merged" in states and "running_config" in kwargs["argument_spec"]:
        # action states with running_config render offline (IsamResourceModule); say so
        description = ((doc.get("options") or {}).get("running_config") or {}).get("description") or ""
        if "offline preview" not in " ".join(description if isinstance(description, list) else [description]):
            problems.append("running_config: the offline action-state meaning is undocumented")
        if any("running_config" in group and "config" in group for group in kwargs.get("mutually_exclusive") or ()):
            problems.append("main(): config and running_config must not be mutually exclusive (offline action states)")
    monkeypatch.undo()
    problems += example_problems(name, kwargs)
    problems += return_problems(name, kwargs)
    return problems


@pytest.mark.parametrize("name", MODULE_NAMES)
def test_module_docs_match_argspec(name, monkeypatch):
    problems = module_problems(name, monkeypatch)
    assert not problems, "%s:\n  %s" % (name, "\n  ".join(problems))


def test_standard_return_docs_are_in_sync():
    import subprocess
    import sys

    result = subprocess.run([sys.executable, str(ROOT / "tools" / "sync_resource_return_docs.py"), "--check"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, cwd=str(ROOT))
    assert result.returncode == 0, result.stdout
