from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import requested_sections
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm import CfmFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cfm import CfmTemplate


class Cfm(IsamResourceModule):
    """CFM's indexed hierarchy and explicit device-specific command forms."""

    ASSOCIATION_FIELDS = (
        "bridgeport", "vlan", "mhf_creation", "name", "ccm_interval", "ccm_aware",
        "ccm_admin_state", "mhf_location", "ltm_filtering", "dual_tag_aware",
    )
    PM_FIELDS = ("type", "target_mac", "priority", "admin_up", "interval", "size", "measurement_intvl")

    def __init__(self, module):
        super(Cfm, self).__init__(empty_fact_val={}, facts_module=CfmFacts(module), module=module, resource="isam_cfm", tmplt=CfmTemplate())

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}
        if self.state != "deleted":
            self._validate_domains(want, have)
        if self.state in ("replaced", "overridden", "deleted"):
            self._delete_missing(have, want)
        if self.state != "deleted":
            self._render(want, have if self.state not in ("rendered", "overridden") else {})

    def _validate_domains(self, want, have):
        # Device help: an MD's name and level cannot be modified. Deleting it
        # also deletes its associations/MEPs, so never invent a recreate sequence.
        current = {domain["domain_index"]: domain for domain in have.get("domains", [])}
        for domain in want.get("domains", []):
            existing = current.get(domain["domain_index"])
            if existing:
                changed = [field for field in ("name", "level")
                           if domain.get(field) is not None and domain[field] != existing.get(field)]
                if changed:
                    self._module.fail_json(msg="CFM domain %s: %s cannot be modified; remove and recreate the domain explicitly."
                                           % (domain["domain_index"], ", ".join(changed)))
            elif any(domain.get(field) is not None for field in ("name", "level")):
                if any(domain.get(field) is None for field in ("name", "level")):
                    self._module.fail_json(msg="Creating CFM domain %s requires both name and level."
                                           % domain["domain_index"])

    def _delete_missing(self, have, want):
        # CFM has explicit no forms for indexed objects; of the settings only
        # 'configure cfm slm inactivity-time' is reset (help: 'no inactivity-time').
        # Omitted domain/MEP options are left alone.
        requested = requested_sections(self._module) if self.state in ("replaced", "deleted") else set()
        have_slm = (have.get("slm") or {}).get("inactivity_time")
        if have_slm is not None and (not requested or "slm" in requested):
            reset = (want.get("slm") or {}).get("inactivity_time") is None
            if self.state == "deleted":
                reset = True
            if reset:
                self.commands.append("configure cfm slm no inactivity-time")
        if requested and "domains" not in requested:
            return
        wanted_domains = {domain["domain_index"] for domain in want.get("domains", [])}
        if self.state == "deleted":
            for domain in have.get("domains", []):
                if not wanted_domains or domain["domain_index"] in wanted_domains:
                    self.commands.append("configure cfm no domain {0}".format(domain["domain_index"]))
            return
        for domain in have.get("domains", []):
            if domain["domain_index"] not in wanted_domains:
                self.commands.append("configure cfm no domain {0}".format(domain["domain_index"]))

    def _render(self, config, have):
        for domain in config.get("domains", []):
            current_domain = next((x for x in have.get("domains", []) if x.get("domain_index") == domain.get("domain_index")), {})
            self._command("configure cfm domain {0}".format(domain["domain_index"]), domain, ("name", "level"), current_domain)
            for association in domain.get("associations", []):
                prefix = "configure cfm domain {0} association {1}".format(domain["domain_index"], association["association_index"])
                current_association = next((x for x in current_domain.get("associations", []) if x.get("association_index") == association.get("association_index")), {})
                self._command(prefix, association, self.ASSOCIATION_FIELDS, current_association)
                for mep in association.get("meps", []):
                    mp = prefix + " mep {0}".format(mep["mepid"])
                    current_mep = next((x for x in current_association.get("meps", []) if x.get("mepid") == mep.get("mepid")), {})
                    self._command(mp, mep, tuple(CfmTemplate.OPTIONS.values()), current_mep)
                    if mep.get("y1731ais") is not None:
                        self._command(mp + " y1731ais", mep["y1731ais"], tuple(CfmTemplate.OPTIONS.values()),
                                      current_mep.get("y1731ais", {}))
                    for remote in mep.get("active_remote_meps", []):
                        if remote not in current_mep.get("active_remote_meps", []):
                            self.commands.append(mp + " active-remote-mep " + str(remote))
                for remote in association.get("remote_meps", []):
                    if remote not in current_association.get("remote_meps", []):
                        self.commands.append(prefix + " remote-mep " + str(remote))
        wanted_slm = (config.get("slm") or {}).get("inactivity_time")
        if wanted_slm is not None and wanted_slm != (have.get("slm") or {}).get("inactivity_time"):
            self.commands.append("configure cfm slm inactivity-time " + str(wanted_slm))
        for pm in config.get("y1731pm", []):
            prefix = "configure cfm y1731pm domain {0} association {1} mep {2} session-id {3}".format(pm["domain_index"], pm["association"], pm["mep"], pm["session_id"])
            current = next((entry for entry in have.get("y1731pm", [])
                            if self._pm_identity(entry) == self._pm_identity(pm)), {})
            self._command(prefix, pm, self.PM_FIELDS, current)

    @staticmethod
    def _pm_identity(entry):
        return tuple(entry.get(field) for field in ("domain_index", "association", "mep", "session_id"))

    def _command(self, prefix, item, fields, have):
        parts = [prefix]
        for field in fields:
            if field not in item or item[field] == have.get(field):
                continue
            value = item[field]
            cli = field.replace("_", "-")
            if isinstance(value, bool):
                parts.append(("" if value else "no ") + cli)
            else:
                parts.extend([cli, str(value)])
        if len(parts) > 1:
            self.commands.append(" ".join(parts))
