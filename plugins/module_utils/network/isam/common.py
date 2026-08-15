# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def canonical_key(key):
    return key.replace("-", "_")


def normalize_resource_keys(data, aliases=None):
    """Return a copy of data with canonical resource keys added.

    Resource args may arrive using CLI spellings such as ``admin-up`` while
    templates compare against Python identifiers such as ``admin_up``. Keep the
    original keys intact for compatibility and add canonical aliases once at the
    resource boundary.
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)
    for key, value in data.items():
        result.setdefault(canonical_key(key), value)

    for source, target in aliases or ():
        if source in result and target not in result:
            result[target] = result[source]

    return result


def normalize_resource_list(data, aliases=None):
    return [normalize_resource_keys(entry, aliases=aliases) for entry in data or []]
