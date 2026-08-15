# Resource Parser Helpers

This collection keeps resource modules, argspecs, config logic, facts, and templates separate. Parser helpers in `plugins/module_utils/network/isam/common.py` are the shared boundary for small CLI spelling and token parsing rules. Use them instead of adding new local `replace("-", "_")` calls or hand-written token walkers.

## Key Normalization

Use `canonical_key()` when converting one Nokia CLI field name to an internal resource key.

```python
canonical_key("admin-up") == "admin_up"
```

Use `normalize_resource_keys()` at resource boundaries when input may contain CLI-style aliases or argspec aliases. It returns a copy, preserves the original keys, and adds canonical keys.

```python
entry = normalize_resource_keys(entry, aliases=(("id", "name"),))
```

Use `normalize_resource_list()` for lists of resource entries.

## Token Parsers

Use `parse_cli_fields()` for known compact CLI fields where the parser has explicit field lists.

It handles:

- boolean flags: `admin-up`
- negated boolean flags: `no admin-up`
- value fields: `timer-b 500`
- optional negated value fields: `no response-intvl` -> `None`
- simple type coercion for fields declared as `"int"`

```python
item.update(
    parse_cli_fields(
        tokens,
        bool_fields=("admin-up", "passive-mode"),
        value_fields={"keep-alive-intvl": "str", "response-intvl": "str"},
        none_for_negated_values=True,
    )
)
```

Use `parse_cli_key_values()` when the parser accepts arbitrary key/value pairs and only needs generic canonicalization.

```python
entry.update(
    parse_cli_key_values(
        tokens,
        bool_fields=("mac-learn-off",),
        infer_numeric=True,
    )
)
```

Use `iter_cli_fields()` when flattening packed CLI lines into individual parser lines. It yields `(negate, key, value)` triples and leaves command formatting to the caller.

```python
for negate, key, value in iter_cli_fields(tokens, bool_fields=flags, value_fields=values):
    if value is None:
        lines.append("  {0}{1}".format("no " if negate else "", key))
    else:
        lines.append("  {0}{1} {2}".format("no " if negate else "", key, value))
```

## When Not To Use Them

Do not use these helpers for command rendering where the CLI spelling must remain hyphenated. Rendering code should usually translate internal names back to CLI names explicitly.

Do not use these helpers for parser schema maps that intentionally map one CLI name to a different internal name. Keep explicit maps when the mapping is semantic rather than just hyphen-to-underscore spelling.

Do not refactor multi-line or context-sensitive parsers without characterization tests. Examples include tree flattening, indentation handling, sibling preservation, and resource-specific dependency ordering.

## Testing Expectations

Before changing a parser, add or confirm tests for the exact CLI form being changed:

- `state=parsed` for flat `configure ...` lines
- packed multi-field lines when the parser splits them
- negated fields such as `no admin-up`
- idempotent `merged` or `replaced` behavior when facts feed config comparison

Run targeted tests first, then the full unit suite:

```bash
python -m pytest tests/unit/modules/network/isam/test_isam_<resource>.py -q
python -m pytest tests/unit/modules/network/isam -q
```
