# Relations

One file per resource family, named after the family's facts name. It is the only
place that says what the family relates to. `targeted.py`, the topology catalog
(`topology.export_catalog()`), the graph of an MSAN and the write order are derived
from these files.

The files are pure data without imports, so tools outside Ansible can read them.
A new file must be added to the import list in `__init__.py`; a test fails otherwise.

```python
RELATIONS = {
    # Family level, all optional except "sections":
    "targeted_writes": True,        # merged/replaced/deleted compare only the named instances
    "read_scope": "whole_node",     # no single-instance read on the device
    "source": "ihub",               # whole-source IHUB read, no targeted gathering
    "settings": ("ageing_time",),   # device-wide settings outside the instance lists
    "profile_references": "qos_profiles",   # options of this family name QoS profiles
    "sections": {
        # One entry per instance list: "config" when the config itself is the list,
        # otherwise the key in the config (dotted for nested keys).
        "interfaces": {
            "identity": "ont_idx",      # field, or list of fields
            "object": "ont",            # address decoder in topology/identity.py
            "creates": True,            # this command creates the object
        },
    },
}
```

A section names an `"object"` or a `"scope"`:

| Key | Meaning |
| --- | --- |
| `"object"` | The instances address a device object. The value is the address decoder; one decoder can yield several kinds (`interface`: `pon:`, `ont:`, `uni:`, `vlan-port:` ...). |
| `"scope": "device_global"` | Device-wide instances without a physical owner. |
| `"scope": "shared_profile"` | Named definitions other configuration refers to. |

Relations to other things:

| Key | Meaning |
| --- | --- |
| `"creates": True` | The command creates the object. Every other family addressing that kind configures an existing object and is written after it. At most one section per kind. |
| `"created_with": [{"prefix", "object", "default"}]` | The device creates the entry itself with the named object (and removes it with it). An entry applies to the instances addressing that object; `prefix` is their address prefix where they have one. Only an entry equal to `default` may be left out of a change set; any other was customized. `"default": None`: the default is not recorded (e.g. card-specific), so no entry counts as default. |
| `"references": {option: "family.section"}` | The option names an instance of that section. |
| `"requires": [{"section", "kind", "for", "evidence"}]` | That section must be written first and removed last: optionally only its instances addressing object kind `kind`, and only for this section's instances addressing kind `for`. The evidence is data: it is shown on the edge of the dependency graph. |
| `"refuses": {kind: {option: reason}}` | Options the device never accepts on instances addressing that kind of object (conditional refusals are not listed). The module refuses them before writing, so check mode reports them. |

A family without instance lists has `"sections": {}`: one device-wide settings block.

State the evidence in a comment above the entry: the command syntax of the device
help, the document section, or the live check with device and date. An entry
without evidence does not belong here; what cannot be placed is refused by the
consumers, never guessed.
