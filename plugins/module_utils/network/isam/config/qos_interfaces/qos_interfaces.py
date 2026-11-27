# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import Qos_interfacesTemplate


UNSET_VALUES = ("none", "not-applicable")


def _without_unset_values(entry):
    """Detail's absent/unsupported fields must not become removal commands.

    Identities and queue lists are left intact; queue entries are normalized at
    their own comparison boundary. Explicit 'none' in want is handled separately
    because setting a real configured profile to none is a valid reset.
    """
    return dict((key, value) for key, value in entry.items()
                if key in ("name", "id") or value not in UNSET_VALUES)


class Qos_interfaces(IsamResourceModule):
    """The isam_qos_interfaces config class."""

    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure qos interface \S+ (?:queue|upstream-queue|ds-rem-queue) \d+) (?P<suffix>(?!no(?:\s|$)).+)$",
        r"^(?P<scope>configure qos interface \S+) (?P<suffix>(?!(?:no|queue|upstream-queue|ds-rem-queue)(?:\s|$)).+)$",
    )

    def __init__(self, module):
        super(Qos_interfaces, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="qos_interfaces",
            tmplt=Qos_interfacesTemplate(),
        )
        self.top_parsers = [
            "interface.scheduler_node",
            "interface.ingress_profile",
            "interface.cac_profile",
            "interface.ext_cac",
            "interface.ds_queue_sharing",
            "interface.us_queue_sharing",
            "interface.ds_num_queue",
            "interface.ds_num_rem_queue",
            "interface.us_num_queue",
            "interface.queue_stats_on",
            "interface.autoschedule",
            "interface.oper_weight",
            "interface.oper_rate",
            "interface.us_vlanport_queue",
            "interface.dsfld_shaper_prof",
            "interface.bandwidth_profile",
            "interface.bandwidth_sharing",
            "interface.aggr_usq_profile",
            "interface.aggr_dsq_profile",
            "interface.gem_sharing",
            "interface.scheduler_mode",
            "interface.mc_scheduler_node",
            "interface.bc_scheduler_node",
            "interface.ds_schedule_tag",
        ]
        self.list_parsers = {
            "queue": [
                "interface.queue.priority",
                "interface.queue.weight",
                "interface.queue.oper_weight",
                "interface.queue.queue_profile",
                "interface.queue.shaper_profile",
            ],
            "upstream_queue": [
                "interface.upstream_queue.priority",
                "interface.upstream_queue.weight",
                "interface.upstream_queue.bandwidth_profile",
                "interface.upstream_queue.ext_bw",
                "interface.upstream_queue.bandwidth_sharing",
                "interface.upstream_queue.queue_profile",
                "interface.upstream_queue.shaper_profile",
            ],
            "ds_rem_queue": [
                "interface.ds_rem_queue.priority",
                "interface.ds_rem_queue.weight",
            ],
        }

    def generate_commands(self):
        wantd = {entry["name"]: entry for entry in self.want}
        haved = {entry["name"]: entry for entry in self.have}

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            if not wantd:
                wantd = {}
            else:
                haved = {k: v for k, v in iteritems(haved) if k in wantd}

        if self.state == "overridden" or (self.state == "deleted" and not self.want):
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        have = _without_unset_values(have)
        if self.state == "deleted":
            self._delete_fields(want, have)
        else:
            # 'none'/'not-applicable' and an unset value are the same device state: the
            # device omits a profile set to none (lab ISAM, pon: cac-profile none).
            want = dict(want)
            for key, value in list(want.items()):
                if key in ("name", "id"):
                    continue
                if value == "not-applicable":
                    # Unsupported is not a request to remove a real target value.
                    if key in have:
                        want[key] = have[key]
                    else:
                        want.pop(key)
                elif value == "none" and have.get(key) is None:
                    want.pop(key)
            if (self.state in ("replaced", "overridden") and want.get("scheduler_node") is None
                    and have.get("scheduler_node") is not None and (have.get("queue") or want.get("queue"))):
                # Same device rule as deleted (QOS MGT error 52, lab ISAM): an interface
                # with downstream queues needs its scheduler node, so it is kept.
                self._module.warn("qos interface %s keeps scheduler-node %s: it is required while the "
                                  "interface has queues" % (have.get("name"), have["scheduler_node"]))
                want["scheduler_node"] = have["scheduler_node"]
            self.compare(parsers=self.top_parsers, want=want, have=have)
        for list_name, parsers in iteritems(self.list_parsers):
            self._compare_list(list_name, parsers, want, have)

    def _delete_fields(self, want, have):
        """Reset the named interface settings, or every setting for an identity-only
        entry (or no config). A full gathered entry takes the same path field by field."""
        requested = {
            key for key, value in want.items()
            if key not in {"name", "id", "queue", "upstream_queue", "ds_rem_queue"} and value is not None
        }
        if not any(value is not None for key, value in want.items() if key not in {"name", "id"}):
            requested = {self._tmplt.get_parser(parser)["compval"] for parser in self.top_parsers}
        name = have.get("name", want.get("name"))
        for field in sorted(requested):
            value = have.get(field)
            # 'none'/'not-applicable' mean nothing is configured; resetting them is
            # pointless and the device rejects it where the setting is unsupported
            # (lab ISAM, ONT UNI: "does not support ... Broadcast Scheduler Profile").
            if value is None or value in UNSET_VALUES:
                continue
            if field == "scheduler_node" and have.get("queue"):
                # Downstream queues always need a scheduler node and a queue profile
                # (lab ISAM: "QOS MGT error 52", "error 162"); neither can be removed.
                self._module.warn("qos interface %s keeps scheduler-node %s: it is required while the "
                                  "interface has queues" % (name, value))
                continue
            self.addcmd({"name": name, field: value}, "interface.%s" % field, True)

    def _compare_list(self, list_name, parsers, want, have):
        wantd = {entry["id"]: entry for entry in want.get(list_name, [])}
        haved = {entry["id"]: entry for entry in have.get(list_name, [])}

        targeted_delete = self.state == "deleted" and any(
            key not in {"name", "id"} for key in want
        )
        if self.state == "overridden" or (self.state == "deleted" and not targeted_delete):
            for key, have_entry in iteritems(haved):
                if key not in wantd:
                    self._compare_list_entry(parsers, {}, have_entry, have.get("name"))

        for key, want_entry in iteritems(wantd):
            self._compare_list_entry(parsers, want_entry, haved.get(key, {}), want.get("name"))

    def _compare_list_entry(self, parsers, want, have, name):
        have = _without_unset_values(have)
        # deleted removes what was requested and never sets a value: the named fields
        # of the entry, or every field when only its id is given.
        whole_entry = not any(value is not None for key, value in want.items() if key != "id")
        for parser in parsers:
            field = self._tmplt.get_parser(parser).get("compval")
            inw = want.get(field)
            inh = have.get(field)

            if inw == "not-applicable" or (inw == "none" and inh is None and self.state != "rendered"):
                continue

            if self.state == "merged" and inw is None:
                continue

            data = {"name": name, "id": want.get("id", have.get("id"))}
            if self.state == "deleted":
                if inh is not None and (whole_entry or inw is not None):
                    data[field] = inh
                    self.addcmd(data, parser, True)
                continue
            if inw is not None and inw != inh:
                data[field] = inw
                self.addcmd(data, parser, False)
            elif inw is None and inh is not None and self.state in ["replaced", "overridden", "deleted"]:
                data[field] = inh
                self.addcmd(data, parser, True)
