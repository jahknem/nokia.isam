from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp_session.l2cp_session import L2cpSessionFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpSessionTemplate


# Device defaults (CLI help "configure l2cp session"): "info ... flat" omits attributes at their default.
# Device defaults (CLI guide); the device shows them as "no <attr>" (detail) or not at all (flat).
DEFAULTS = {
    "gsmp_version": "3", "gsmp_sub_version": "1", "encap_type": "tcp", "topo_discovery": "enabled",
    "layer2_oam": "enabled", "alive_timer": "250", "port_reprt_shaper": "10", "aggr_reprt_shaper": "10",
    "tcp_retry_time": "10", "gsmp_retry_time": "10", "dslam_name": "00:00:00:00:00:00", "partition_id": "0",
    "window_size": "10", "tcp_port": "6068", "router_instance": "base", "sig_partition_id": False,
}
# The only attributes an existing session accepts (lab ISAM: "session <index> alive-timer <value>";
# repeating bras-ip-address or any other attribute is an invalid token).
MODIFIABLE = ("alive_timer", "tcp_retry_time")


class L2cpSession(ResourceModule):
    def __init__(self, module):
        self.template = L2cpSessionTemplate()
        super(L2cpSession, self).__init__(empty_fact_val=[], facts_module=L2cpSessionFacts(module), module=module, resource="l2cp_session", tmplt=self)

    def get_parser(self, name):
        return {"compval": name}

    def execute_module(self):
        if self.state == "parsed":
            return {"parsed": self.template.parse(self._module.params.get("running_config")), "changed": False}
        if self.state == "rendered":
            return {"rendered": self.template.render(self._module.params.get("config")), "changed": False}
        if self.state == "gathered":
            return self.result
        desired = self.want or []
        current = dict((item["name"], item) for item in self.have or [])
        wanted_names = set(item["name"] for item in desired)
        self.commands = []
        if self.state == "deleted":
            # "configure l2cp no session <index>" removes the whole session; only existing ones.
            names = [name for name in current if not wanted_names or name in wanted_names]
            self.commands = ["configure l2cp no session %s" % name for name in names]
        else:
            if self.state == "overridden":
                self.commands.extend("configure l2cp no session %s" % name for name in current if name not in wanted_names)
            for item in desired:
                self.commands.extend(self._update(item, current.get(item["name"])))
        if self.commands:
            self.run_commands()
        return self.result

    def _update(self, want, have):
        """The commands bringing one session to want (merged keeps have's unnamed attributes,
        replaced/overridden return them to their default)."""
        given = dict((key, value) for key, value in want.items() if value is not None)
        # A negated attribute ("no alive-timer", parsed as None) is at its default.
        have_full = dict(DEFAULTS, **dict((key, value) for key, value in (have or {}).items() if value is not None))
        target = dict(have_full if self.state == "merged" else DEFAULTS, **given)
        if have is not None:
            # bras-ip-address is mandatory and has no removal form: keep it when not given.
            target.setdefault("bras_ip_address", have.get("bras_ip_address"))
            return self._modify(want["name"], target, have_full)
        if not target.get("bras_ip_address"):
            self._module.warn("l2cp session %s does not exist and has no bras_ip_address; it cannot be created" % want["name"])
            return []
        # The device fills unset attributes with their defaults.
        return self.template.render([dict((key, value) for key, value in target.items() if DEFAULTS.get(key) != value)])

    def _modify(self, name, target, have_full):
        changed = sorted(key for key in set(target) | set(have_full) if target.get(key) != have_full.get(key))
        fixed = [key for key in changed if key not in MODIFIABLE]
        if fixed:
            self._module.fail_json(msg="l2cp session %s: %s can only be set when the session is created; "
                                       "delete the session first" % (name, ", ".join(fixed)))
        commands = []
        for key in changed:
            cli = key.replace("_", "-")
            if target[key] == DEFAULTS[key]:
                commands.append("configure l2cp session %s no %s" % (name, cli))
            else:
                commands.append("configure l2cp session %s %s %s" % (name, cli, target[key]))
        return commands
