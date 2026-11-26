"""Single lookup for the private lab root captures used by the capture tests.

`info configure flat` (root-flat.txt) and `info configure detail flat`
(root-detail-flat.txt) of a real ISAM are never committed. The capture tests
read them only from the directory named by the ISAM_ROOT_CAPTURES environment
variable (tox passes it through):

    ISAM_ROOT_CAPTURES=/path/to/captures .venv/bin/tox -e py312

* ISAM_ROOT_CAPTURES unset: every capture test is skipped, with a reason that
  names the variable.
* ISAM_ROOT_CAPTURES set: a missing or unreadable capture file fails the test,
  so a misconfigured run cannot pass silently with the capture tests skipped.

There is no fallback location (no sibling checkout, no in-repository folder).
"""
import os
import pathlib

import pytest

ENV_VAR = "ISAM_ROOT_CAPTURES"
CONFIGURED_NAME = "root-flat.txt"
DETAIL_NAME = "root-detail-flat.txt"
# Both captures, detail first (the parametrized tests use these as ids).
NAMES = (DETAIL_NAME, CONFIGURED_NAME)

SKIP_REASON = "lab captures not configured: set %s to the directory holding %s and %s" % (
    ENV_VAR, CONFIGURED_NAME, DETAIL_NAME)


def capture_dir():
    """The configured capture directory, or None when ISAM_ROOT_CAPTURES is unset/empty."""
    value = os.environ.get(ENV_VAR, "").strip()
    return pathlib.Path(value).expanduser() if value else None


def path(name):
    """Path of capture `name`; skips without ISAM_ROOT_CAPTURES, fails when it is set but the file is missing."""
    directory = capture_dir()
    if directory is None:
        pytest.skip(SKIP_REASON)
    candidate = directory / name
    if not candidate.is_file():
        pytest.fail("%s is set but %s does not exist in that directory" % (ENV_VAR, name), pytrace=False)
    return candidate


def read(name):
    """Text of capture `name` (undecodable bytes replaced); see path() for skip/fail rules."""
    return path(name).read_text(errors="replace")


def configured():
    """Text of root-flat.txt (`info configure flat`)."""
    return read(CONFIGURED_NAME)


def detail():
    """Text of root-detail-flat.txt (`info configure detail flat`)."""
    return read(DETAIL_NAME)
