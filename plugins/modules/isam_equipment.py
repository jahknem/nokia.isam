#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_equipment
short_description: Manages equipment shelf, slot, applique, and protection-group configuration on Nokia ISAM.
description:
  - Manages the initial core C(configure equipment) resources for shelves, slots, appliques, and protection groups.
  - C(equipment ont) is intentionally excluded and belongs in a separate resource module.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Equipment configuration grouped by resource type.
    type: dict
    suboptions:
      shelves:
        description:
          - Equipment shelf entries.
          - Shelf, slot and applique attributes are set with C(<shelf|slot|applique> <id> <attr> [<value>]) and reset with
            C(<shelf|slot|applique> <id> no <attr>); a requested device default equals an absent value. Help syntax;
            the reset forms of the attributes added for detail output are not verified on a device.
        type: list
        elements: dict
        suboptions:
          id:
            description: Shelf identifier.
            type: str
            required: true
          planned_type:
            description: Planned shelf type.
            type: str
          class:
            description: Shelf class (C(class)); device default C(main-ethernet), not reported.
            type: str
            choices: [main-ethernet, ext-ethernet]
          lock:
            description: Lock the shelf (C(lock)); C(no lock) is the default and not reported.
            type: bool
          mode:
            description:
              - Shelf mode (C(mode)), for example C(no-extended-lt-slots), C(extended-lt-slots), C(no-ntb-slot),
                C(no-extended-slots), C(no-ntio-slots), C(ngpon), C(gpon), C(ngpon-port-reduced), C(gpon-mng-ngpon),
                C(gpon-mng-reduced); device default C(no-extended-lt-slots), not reported.
              - Changing the mode reboots the NE.
            type: str
          description:
            description: Shelf location description (C(description)), at most 127 characters; quoted when it contains spaces.
            type: str
      slots:
        description: Equipment slot entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Slot identifier.
            type: str
            required: true
          planned_type:
            description: Planned slot type.
            type: str
          unlock:
            description: Convenience flag for unlocking the slot.
            type: bool
          admin_state:
            description: Administrative slot state.
            type: str
            choices: [locked, unlocked]
          power_down:
            description: Power down the board, LSM only (C(power-down)); C(no power-down) is the default and not reported.
            type: bool
          alarm_profile:
            description: Customized alarm profile, C(none) or C(name:<name>) (C(alarm-profile)); device default C(none), not reported.
            type: str
          capab_profile:
            description:
              - Capability profile of a line board (C(capab-profile)), for example C(fttu_lt) or C(8vc_default);
                device default C(not_applicable), not reported.
            type: str
          board_40gkr4:
            description: 40G KR4 operation of the board (C(board-40gkr4)); device default C(inherited), not reported.
            type: str
            choices: [inherited, disable, enable]
          operational_mode:
            description:
              - Operational mode of the cage (C(operational-mode)), for example C(gpon), C(xgs), C(mpm-gpon-xgs),
                C(dual-gpon), C(u-ngpon), C(twenty-five-g), C(ng-pon2), C(mpm-gpon-xgpon); device default C(not-set), not reported.
            type: str
          dual_host_ip:
            description: Dual host IPv4 address (C(dual-host-ip)); device default C(0.0.0.0), not reported.
            type: str
          dual_host_loc:
            description: Dual host LSM location C(<rack>/<shelf>) or C(none) (C(dual-host-loc)); device default C(none), not reported.
            type: str
      appliques:
        description: Equipment applique entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Applique identifier.
            type: str
            required: true
          planned_type:
            description: Planned applique type.
            type: str
          applique_profile:
            description: Capability profile of the applique board (C(applique-profile)); device default C(not_applicable), not reported.
            type: str
      protection_groups:
        description: Equipment protection group entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Protection group identifier.
            type: int
            required: true
          admin_status:
            description: Protection group administrative status.
            type: str
            choices: [lock, unlock]
          eps_quenchfactor:
            description: EPS quench factor.
            type: int
      diagnostics_sfp:
        description: SFP diagnostics entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: SFP position (e.g. C(ntio-1:sfp:2)).
            type: str
            required: true
          rssi_prof_id:
            description: RSSI profile index.
            type: int
          rssi_state:
            description: RSSI state.
            type: str
      protection_elements:
        description: Protection element entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Protection element identifier (e.g. C(nt-a)).
            type: str
            required: true
          redcy_ctrl_status:
            description: Redundancy control status.
            type: str
      racks:
        description: Rack entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Rack identifier.
            type: str
            required: true
          description:
            description: Rack description.
            type: str
      external_link_assigns:
        description: External link assignment entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: External link identifier.
            type: str
            required: true
          remote:
            description: Remote expansion slot index.
            type: str
      external_link_hosts:
        description: External link host entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Faceplate number.
            type: str
            required: true
          direction:
            description: External link direction.
            type: str
      envbox:
        description: Environment box settings.
        type: dict
        suboptions:
          enable_supervise:
            description: Enable environment supervision.
            type: bool
      isam:
        description: ISAM system settings.
        type: dict
        suboptions:
          description:
            description: ISAM description.
            type: str
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(shelves[].id), C(slots[].id), C(appliques[].id), C(protection_groups[].id), C(diagnostics_sfp[].id), C(protection_elements[].id), C(racks[].id), C(external_link_assigns[].id) and C(external_link_hosts[].id) (targeted gathering). The C(envbox) and C(isam) settings blocks are read whole. Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather equipment config
  nokia.isam.isam_equipment:
    state: gathered

- name: Render equipment config
  nokia.isam.isam_equipment:
    state: rendered
    config:
      shelves:
        - id: 1/1
          planned_type: nfxs-b
      slots:
        - id: lt:1/1/1
          planned_type: ndps-c
          admin_state: unlocked
      appliques:
        - id: ntio-1
          planned_type: ncnc-d
      protection_groups:
        - id: 33
          admin_status: lock
          eps_quenchfactor: 0

- name: Read only the named slots (targeted gathering)
  nokia.isam.isam_equipment:
    config:
      slots:
        - id: lt:1/1/5
    state: gathered
"""

RETURN = """
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured equipment data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured equipment data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.isam_equipment.isam_equipment import (
    Isam_equipmentArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.isam_equipment.isam_equipment import (
    Isam_equipment,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_equipmentArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Isam_equipment(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
