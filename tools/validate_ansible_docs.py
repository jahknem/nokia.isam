#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import glob
import subprocess
import sys


def _module_names():
    for path in sorted(glob.glob("plugins/modules/*.py")):
        if not path.endswith("__init__.py"):
            yield path.rsplit("/", 1)[-1][:-3]


def _check_doc(plugin_type, fqcn):
    result = subprocess.run(
        ["ansible-doc", "-t", plugin_type, fqcn],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        print("OK {0} {1}".format(plugin_type, fqcn))
        return True
    print("FAIL {0} {1}".format(plugin_type, fqcn))
    if result.stderr:
        print(result.stderr.strip())
    return False


def main():
    checks = [("module", "nokia.isam." + name) for name in _module_names()]
    checks.append(("connection", "nokia.isam.isam_network_cli"))

    failed = False
    for plugin_type, fqcn in checks:
        failed = not _check_doc(plugin_type, fqcn) or failed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
