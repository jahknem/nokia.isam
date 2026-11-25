"""Semantic graph filters over canonical nokia.isam resource facts (no device access)."""

from ansible.errors import AnsibleFilterError
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, plan_known_reads
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.write_order import UnorderedWrite, write_steps


def isam_topology(resources, msan):
    try:
        return build_graph(resources, msan)
    except ValueError as exc:
        raise AnsibleFilterError(str(exc)) from exc


def isam_topology_read_requirements(graph, kind, identity):
    try:
        return plan_known_reads(graph, kind, identity)
    except ValueError as exc:
        raise AnsibleFilterError(str(exc)) from exc


def isam_write_steps(families, phase="create"):
    """The module calls, in device order, that create or remove these families."""
    try:
        return write_steps(families, phase)
    except UnorderedWrite as exc:
        raise AnsibleFilterError(str(exc)) from exc


class FilterModule(object):
    def filters(self):
        return {"isam_topology": isam_topology,
                "isam_topology_read_requirements": isam_topology_read_requirements,
                "isam_write_steps": isam_write_steps}
