# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Auto-created instances: what the ISAM creates on its own, and at which default values.

Creating an ONT auto-creates its ``ntp``/``ani`` entries and its ``ont:`` interface; adding a
bridge VLAN auto-creates the ``vlan-port`` interface and the ``vlan:`` QoS. These exist without
being configured, so a change set must not re-emit them — unless they were customized.

An instance is the *auto-created default* when, apart from its identity and its operational
(read-only) fields, its attributes exactly equal the ``default`` below. Any deviation means it
was customized and must be copied. The check is deliberately exact: only a proven default is
skipped, anything uncertain is kept, so a customization can never be silently dropped.

Verified live on DS-LIN-TEST-01 (R6.2): applying only the minimal customer config creates these
items at exactly these values; customizing one (admin-down a vlan-port) deviates from the
default and is therefore detectable.

Pure data without imports, so tools outside Ansible can read it.

family -> {identity: the identity field, types: [{prefix, default}]}
  prefix: the instance-name prefix this default applies to (None: every instance of the family).
  default: the attribute values of the untouched auto-created instance (identity excluded).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Operational (read-only) fields never count as customization.
AUTO_CREATED_OPER_PREFIX = "oper_"

AUTO_CREATED_DEFAULTS = {
    "ntp_onts": {
        "identity": "ont_id",
        "types": [{"prefix": None, "default": {}}],
    },
    "ani_onts": {
        "identity": "ont_idx",
        "types": [{"prefix": None, "default": {"tca_thresh": True}}],
    },
    "interfaces": {
        "identity": "name",
        "types": [
            {"prefix": "ont:", "default": {"admin_up": True, "link_updown_trap": True}},
            {"prefix": "vlan-port:", "default": {"admin_up": True, "link_updown_trap": False, "severity": "no-value"}},
        ],
    },
    "qos_interfaces": {
        "identity": "name",
        "types": [
            {"prefix": "vlan:", "default": {
                "ds_num_queue": "not-applicable", "ds_num_rem_queue": "not-applicable",
                "us_num_queue": "not-applicable", "gem_sharing": "not-applicable",
                "mc_scheduler_node": "none", "bc_scheduler_node": "none"}},
        ],
    },
}

# Partial auto-creation: an instance that IS needed (so it is not skipped whole) but carries
# attributes / sub-objects the device creates on its own (e.g. the UNI QoS scheduler-node /
# cac-profile / downstream queues). Only exact default parts may be stripped; the configured
# rest (and any customized part) stays.
#
# IMPORTANT: these default values are device/card-specific and must NOT be hardcoded. They have
# to come from the device itself (its default template, or a captured reference). On the lab
# firmware the ONU provisioning template is not supported and no readable default template was
# found, so this is intentionally EMPTY: such parts are copied, never guessed (fail-safe). Populate
# it only from a trustworthy per-device source.
#
# family -> {identity, types: [{not_prefix, attrs, lists}]}
#   not_prefix: applies to instance names NOT starting with any of these (the bare UNI).
#   attrs: {attribute: default value} stripped only on an exact match.
#   lists: {sub-object list: [default entries]} each entry stripped only on an exact match
#          (operational fields ignored); the list is dropped when every entry was a default.
AUTO_CREATED_PARTS = {}
