from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.efm_oam.efm_oam import EfmOamFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.efm_oam import EfmOamTemplate


# Device defaults (CLI guide): a port shows them as "no <attr>" (detail) or not at all (flat).
DEFAULTS = {"admin_up": False, "passive_mode": False, "keep_alive_intvl": "300", "response_intvl": "5"}


class EfmOam(IsamResourceModule):
    def __init__(self, module):
        self.template = EfmOamTemplate()
        super(EfmOam, self).__init__(
            empty_fact_val=[], facts_module=EfmOamFacts(module), module=module,
            resource="efm_oam_interface", tmplt=self,
        )

    def get_parser(self, name):
        return {"compval": name}

    def execute_module(self):
        if self.state == "parsed":
            return {"parsed": self.template.parse(self._module.params.get("running_config")), "changed": False}
        elif self.state == "rendered":
            return {"rendered": self.template.render(self._module.params.get("config")), "changed": False}
        else:
            self.commands = self._commands(self._module.params.get("config") or [])
            if self.commands:
                self.run_commands()
        return self.result

    def _commands(self, config):
        """One command per port with only the attributes that differ from the device
        (merged keeps unnamed attributes, replaced/overridden/deleted return them to the
        default)."""
        have = dict((item["name"], dict(DEFAULTS, **dict((k, v) for k, v in item.items() if v is not None)))
                    for item in self.have or [])
        named = dict((item["name"], item) for item in config)
        targets = []
        if self.state == "deleted":
            # an identity alone resets the port, named settings reset only themselves
            for name, current in have.items():
                if named and name not in named:
                    continue
                fields = [k for k, v in named.get(name, {}).items() if k != "name" and v is not None]
                targets.append((name, dict(current, **dict((k, DEFAULTS[k]) for k in fields)) if fields else dict(DEFAULTS)))
        else:
            for name, item in named.items():
                given = dict((k, v) for k, v in item.items() if k != "name" and v is not None)
                base = have.get(name, DEFAULTS) if self.state == "merged" else DEFAULTS
                targets.append((name, dict(base, **given)))
            if self.state == "overridden":
                targets.extend((name, dict(DEFAULTS)) for name in have if name not in named)
        commands = []
        for name, target in targets:
            current = have.get(name, DEFAULTS)
            changed = [key for key in DEFAULTS if str(target[key]) != str(current[key])]
            if changed:
                # an interval back at its default is reset ("no <attr>"; render: None)
                values = [(key, None if DEFAULTS[key] is not None and str(target[key]) == DEFAULTS[key] else target[key])
                          for key in changed]
                commands.extend(self.template.render([dict([("name", name)] + values)], resets=True))
        return commands

