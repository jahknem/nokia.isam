"""Location of the lab root captures used by the capture tests.

`info configure flat` (root-flat.txt) and `info configure detail flat`
(root-detail-flat.txt) of a real ISAM are kept outside the repository. Set
ISAM_ROOT_CAPTURES to their directory; by default the sibling
pon-migration-planner checkout is used. Tests skip when the files are absent.
"""
import os
import pathlib

CAPTURE_DIR = pathlib.Path(
    os.environ.get("ISAM_ROOT_CAPTURES")
    or pathlib.Path(__file__).resolve().parents[6] / "pon-migration-planner" / ".local"
)
CONFIGURED = CAPTURE_DIR / "root-flat.txt"
DETAIL = CAPTURE_DIR / "root-detail-flat.txt"
