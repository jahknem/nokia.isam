Config modules compare desired state (`want`) with current facts (`have`) and emit Nokia CLI commands.

Normalize external spellings at the resource boundary before comparing. Prefer shared helpers from `plugins/module_utils/network/isam/common.py`:

- `normalize_resource_keys()` for one resource dictionary.
- `normalize_resource_list()` for lists of resource dictionaries.
- `canonical_key()` only when converting one CLI token to an internal key.

Do not add new local `replace("-", "_")` blocks or resource-specific alias copies unless the mapping is semantic. See `docs/resource_parser_helpers.md` for examples and testing expectations.
