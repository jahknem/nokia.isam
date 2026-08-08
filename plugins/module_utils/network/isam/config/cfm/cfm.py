from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm import CfmFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cfm import CfmTemplate


class Cfm(ResourceModule):
    def __init__(self, module):
        super(Cfm, self).__init__(empty_fact_val={}, facts_module=CfmFacts(module), module=module, resource="isam_cfm", tmplt=CfmTemplate())

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ("parsed", "gathered"):
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = deepcopy(self.want or {})
        have = deepcopy(self.have or {})
        if self.state == "merged":
            target = want
        elif self.state == "deleted":
            target = {}
        else:
            target = want
        if self.state in ("replaced", "overridden", "deleted"):
            self._delete_missing(have, want)
        self._render(target, have if self.state not in ("rendered", "overridden") else {})

    def _merge(self, have, want):
        for key, value in want.items():
            if isinstance(value, list):
                for item in value:
                    ident = self._identity(key, item)
                    existing = next((x for x in have.setdefault(key, []) if self._identity(key, x) == ident), None)
                    if existing is None: have[key].append(deepcopy(item))
                    else: self._merge(existing, item)
            elif isinstance(value, dict): self._merge(have.setdefault(key, {}), value)
            else: have[key] = value
        want.clear(); want.update(have)

    @staticmethod
    def _identity(kind, item):
        return (kind, item.get("domain_index"), item.get("association_index"), item.get("mepid"), item.get("session_id"), item.get("rmepid"), item.get("active_remote_mepid"), item.get("name"))

    def _delete_missing(self, have, want):
        # CFM has explicit no forms only for indexed objects; omitted options are left alone.
        if self.state == "deleted":
            requested = {x.get("domain_index") for x in want.get("domains", [])}
            for domain in have.get("domains", []):
                if not requested or domain.get("domain_index") in requested:
                    self.commands.append("configure cfm no domain {0}".format(domain["domain_index"]))
            return
        for domain in have.get("domains", []):
            if not any(self._identity("domains", x) == self._identity("domains", domain) for x in want.get("domains", [])):
                self.commands.append("configure cfm no domain {0}".format(domain["domain_index"]))

    def _render(self, config, have):
        for domain in config.get("domains", []):
            current_domain = next((x for x in have.get("domains", []) if x.get("domain_index") == domain.get("domain_index")), {})
            self._command("configure cfm domain {0}".format(domain["domain_index"]), domain, ("name", "level"), current_domain)
            for association in domain.get("associations", []):
                prefix = "configure cfm domain {0} association {1}".format(domain["domain_index"], association["association_index"])
                current_association = next((x for x in current_domain.get("associations", []) if x.get("association_index") == association.get("association_index")), {})
                self._command(prefix, association, ("bridgeport", "vlan", "mhf_creation", "name", "ccm_interval", "ccm_aware", "ccm_admin_state", "mhf_location", "ltm_filtering", "dual_tag_aware"), current_association)
                for mep in association.get("meps", []):
                    mp = prefix + " mep {0}".format(mep["mepid"])
                    current_mep = next((x for x in current_association.get("meps", []) if x.get("mepid") == mep.get("mepid")), {})
                    self._command(mp, mep, tuple(CfmTemplate.OPTIONS.values()), current_mep)
                    if mep.get("y1731ais") is not None: self._command(mp + " y1731ais", mep["y1731ais"], tuple(CfmTemplate.OPTIONS.values()), current_mep.get("y1731ais", {}))
                    for remote in mep.get("active_remote_meps", []): self.commands.append(mp + " active-remote-mep " + str(remote))
                for remote in association.get("remote_meps", []): self.commands.append(prefix + " remote-mep " + str(remote))
        if config.get("slm", {}).get("inactivity_time") is not None: self.commands.append("configure cfm slm inactivity-time " + str(config["slm"]["inactivity_time"]))
        for pm in config.get("y1731pm", []):
            prefix = "configure cfm y1731pm domain {0} association {1} mep {2} session-id {3}".format(pm["domain_index"], pm["association"], pm["mep"], pm["session_id"])
            self._command(prefix, pm, ("type", "target_mac", "priority", "admin_up", "interval", "size", "measurement_intvl"), {})

    def _command(self, prefix, item, fields, have):
        parts = [prefix]
        for field in fields:
            if field not in item or item[field] == have.get(field): continue
            value = item[field]
            cli = field.replace("_", "-")
            if isinstance(value, bool): parts.append(("" if value else "no ") + cli)
            else: parts.extend([cli, str(value)])
        if len(parts) > 1: self.commands.append(" ".join(parts))
