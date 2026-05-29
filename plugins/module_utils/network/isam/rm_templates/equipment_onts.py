# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Equipment_ontsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Equipment_ontsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "interface.sw_ver_pland",
            "getval": re.compile(r"^interface\s+(?P<ont_idx>\S+)\s+sw-ver-pland\s+(?P<sw_ver_pland>\S+)\s*$"),
            "setval": "configure equipment ont interface {{ ont_idx }} sw-ver-pland {{ sw_ver_pland }}",
            "result": {"interfaces": {"{{ ont_idx }}": {"ont_idx": "{{ ont_idx }}", "sw_ver_pland": "{{ sw_ver_pland }}"}}},
        },
        {"name": "interface.sernum", "setval": "configure equipment ont interface {{ ont_idx }} sernum {{ sernum }}", "remval": "configure equipment ont interface {{ ont_idx }} no sernum"},
        {"name": "interface.subslocid", "setval": "configure equipment ont interface {{ ont_idx }} subslocid {{ subslocid }}"},
        {"name": "interface.fec_up", "setval": "configure equipment ont interface {{ ont_idx }} fec-up {{ fec_up }}", "remval": "configure equipment ont interface {{ ont_idx }} no fec-up"},
        {"name": "interface.sw_dnload_version", "setval": "configure equipment ont interface {{ ont_idx }} sw-dnload-version {{ sw_dnload_version }}", "remval": "configure equipment ont interface {{ ont_idx }} no sw-dnload-version"},
        {"name": "interface.plnd_var", "setval": "configure equipment ont interface {{ ont_idx }} plnd-var {{ plnd_var }}", "remval": "configure equipment ont interface {{ ont_idx }} no plnd-var"},
        {"name": "interface.enable_aes", "setval": "configure equipment ont interface {{ ont_idx }} enable-aes {{ enable_aes }}", "remval": "configure equipment ont interface {{ ont_idx }} no enable-aes"},
        {"name": "interface.log_auth_pwd", "setval": "configure equipment ont interface {{ ont_idx }} log-auth-pwd {{ log_auth_pwd }}", "remval": "configure equipment ont interface {{ ont_idx }} no log-auth-pwd"},
        {"name": "interface.cvlantrans_mode", "setval": "configure equipment ont interface {{ ont_idx }} cvlantrans-mode {{ cvlantrans_mode }}", "remval": "configure equipment ont interface {{ ont_idx }} no cvlantrans-mode"},
        {"name": "interface.planned_us_rate", "setval": "configure equipment ont interface {{ ont_idx }} planned-us-rate {{ planned_us_rate }}", "remval": "configure equipment ont interface {{ ont_idx }} no planned-us-rate"},
        {"name": "interface.admin_state", "setval": "configure equipment ont interface {{ ont_idx }} admin-state {{ admin_state }}"},
        {"name": "interface", "setval": "configure equipment ont interface {{ ont_idx }}", "remval": "configure equipment ont no interface {{ ont_idx }}"},
        {"name": "slot.planned_card_type", "setval": "configure equipment ont slot {{ ont_slot_idx }} planned-card-type {{ planned_card_type }}"},
        {"name": "slot.plndnumdataports", "setval": "configure equipment ont slot {{ ont_slot_idx }} plndnumdataports {{ plndnumdataports }}"},
        {"name": "slot.plndnumvoiceports", "setval": "configure equipment ont slot {{ ont_slot_idx }} plndnumvoiceports {{ plndnumvoiceports }}"},
        {"name": "slot.port_type", "setval": "configure equipment ont slot {{ ont_slot_idx }} port-type {{ port_type }}", "remval": "configure equipment ont slot {{ ont_slot_idx }} no port-type"},
        {"name": "slot.transp_mode_rem", "setval": "configure equipment ont slot {{ ont_slot_idx }} transp-mode-rem {{ transp_mode_rem }}", "remval": "configure equipment ont slot {{ ont_slot_idx }} no transp-mode-rem"},
        {"name": "slot.no_mcast_control", "setval": "configure equipment ont slot {{ ont_slot_idx }} no-mcast-control {{ no_mcast_control }}", "remval": "configure equipment ont slot {{ ont_slot_idx }} no no-mcast-control"},
        {"name": "slot.admin_state", "setval": "configure equipment ont slot {{ ont_slot_idx }} admin-state {{ admin_state }}", "remval": "configure equipment ont slot {{ ont_slot_idx }} no admin-state"},
        {"name": "slot", "setval": "configure equipment ont slot {{ ont_slot_idx }}", "remval": "configure equipment ont no slot {{ ont_slot_idx }}"},
        {"name": "sw_ctrl.hw_version", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} hw-version {{ hw_version }}"},
        {"name": "sw_ctrl.ont_variant", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} ont-variant {{ ont_variant }}", "remval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} no ont-variant"},
        {"name": "sw_ctrl.plnd_sw_version", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} plnd-sw-version {{ plnd_sw_version }}", "remval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} no plnd-sw-version"},
        {"name": "sw_ctrl.plnd_sw_ver_conf", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} plnd-sw-ver-conf {{ plnd_sw_ver_conf }}", "remval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} no plnd-sw-ver-conf"},
        {"name": "sw_ctrl.sw_dwload_ver", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} sw-dwload-ver {{ sw_dwload_ver }}", "remval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }} no sw-dwload-ver"},
        {"name": "sw_ctrl", "setval": "configure equipment ont sw-ctrl {{ sw_ctrl_id }}", "remval": "configure equipment ont no sw-ctrl {{ sw_ctrl_id }}"},
    ]
