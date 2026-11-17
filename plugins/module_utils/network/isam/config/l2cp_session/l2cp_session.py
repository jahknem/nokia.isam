from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp_session.l2cp_session import L2cpSessionArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp_session.l2cp_session import L2cpSessionFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpSessionTemplate


# Device defaults (CLI help "configure l2cp session"): "info ... flat" omits attributes at their default.
DEFAULTS = dict(
    (field, spec["default"])
    for field, spec in L2cpSessionArgs.argument_spec["config"]["options"].items()
    if "default" in spec
)
DEFAULTS["sig_partition_id"] = False


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
        """The session command bringing one session to want (merged: keep have's unnamed attributes)."""
        # A negated attribute ("no alive-timer", parsed as None) is at its default.
        have_full = dict(DEFAULTS, **dict((key, value) for key, value in (have or {}).items() if value is not None))
        if self.state == "merged":
            target = dict(have_full, **want)
        else:
            # replaced/overridden: attributes not in want go back to their default (argspec defaults
            # already fill most of want); bras-ip-address is mandatory and has no removal form, keep it.
            target = dict(DEFAULTS, **want)
            if want.get("bras_ip_address") is None and have:
                target["bras_ip_address"] = have.get("bras_ip_address")
        if not target.get("bras_ip_address"):
            self._module.warn("l2cp session %s does not exist and has no bras_ip_address; it cannot be created" % want["name"])
            return []
        if have is not None and target == have_full:
            return []
        return self.template.render([target])
