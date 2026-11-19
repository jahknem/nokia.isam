"""Checks that a table family's attribute table, argument spec and DOCUMENTATION agree."""
import yaml


def assert_table_matches(table, argument_spec, documentation):
    """Every node's options, types and choices are the same in the table, the argspec
    (``argument_spec["config"]["options"]``) and the module documentation."""
    spec = argument_spec["config"]["options"]
    docs = yaml.safe_load(documentation)["options"]["config"]["suboptions"]
    assert spec == table.argument_spec()
    for node in table.nodes:
        s, d = spec, docs
        for key in node.path:
            s, d = s[key]["options"], d[key]["suboptions"]
        own = set(attr.option for attr in node.attrs) | ({node.identity} if node.identity else set())
        if node.path:
            # the node's own options; nested sections are checked as their own nodes
            nested = set(key for key, value in s.items() if value.get("options"))
            assert set(s) - nested == set(d) - nested == own, node.cli
        else:
            # top-level attributes share the level with the other sections
            assert own <= set(s) and own <= set(d), node.cli
        for attr in node.attrs:
            assert d[attr.option]["type"] == s[attr.option]["type"], (node.cli, attr.option)
            assert d[attr.option].get("choices") == s[attr.option].get("choices"), (node.cli, attr.option)
