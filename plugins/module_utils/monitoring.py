"""Small read-only monitoring parsers; no configuration/facts dispatcher imports."""
from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.tables import parse_status_table


def _table(output, required, count_name):
    if not isinstance(output, str):
        raise ValueError("Expected CLI output text")
    count = re.search(r"(?im)^\s*" + count_name + r"\s+count\s*:\s*(\d+)\s*$", output)
    if not count:
        raise ValueError("Unrecognized or incomplete %s table (missing count)" % count_name)
    header_fields = ("alarm-idx", "gpon-index", "sernum") if count_name == "unprovision-onu" else ("if-index", "adm-state", "cur-op-mode")
    if not all(field in output.lower() for field in header_fields):
        raise ValueError("Unrecognized %s table header" % count_name)
    rows = parse_status_table(output)
    if len(rows) != int(count.group(1)):
        raise ValueError("Incomplete %s table: count does not match parsed rows" % count_name)
    if any(not required <= set(row) for row in rows):
        raise ValueError("Unexpected %s table columns" % count_name)
    return rows


def parse_unprovisioned_onts(output):
    """Return only fields needed by monitoring, retaining empty fixed-width cells."""
    required = {"alarm_idx", "gpon_index", "sernum", "subscriber_locid", "actual_us_rate"}
    rows = _table(output, required, "unprovision-onu")
    for row in rows:
        if not row["alarm_idx"].isdigit() or not re.fullmatch(r"[0-9/]+", row["gpon_index"]):
            raise ValueError("Invalid unprovisioned ONT identity")
    return rows


def parse_xdsl_operational_lines(output):
    """Parse operational line data, never the similarly named configuration facts.

    ISAM variants add a tx-rate-ds column. Unknown/down rates are omitted rather
    than invented as zero; state metrics are still available for those lines.
    """
    required = {"if_index", "adm_state", "opr_state", "cur_op_mode"}
    if isinstance(output, str) and "tx-rate-ds" in output:
        # Native ISAM combines opr-state and tx-rate-ds vertically in one
        # physical column, and spans the us/ds header across two other columns.
        # It is not a regular pipe table. Parse each row once rather than build
        # the old filter's complete list-of-token-lists and reparse it later.
        count = re.search(r"(?im)^\s*line\s+count\s*:\s*(\d+)\s*$", output)
        if not count or not all(label in output for label in ("if-index", "adm-state", "opr-state", "cur-op-mode")):
            raise ValueError("Unrecognized or incomplete xDSL line table")
        widths = next(([len(part) for part in line.split("+")]
                       for line in output.splitlines()
                       if len(line.split("+")) == 6 and set(line.strip()) <= set("-+")), None)
        if not widths:
            raise ValueError("Unrecognized xDSL column boundaries")
        rows = []
        for line in output.splitlines():
            if not re.match(r"^\s*\d+(?:/\d+)+\s", line):
                continue
            fields = []
            offset = 0
            for width in widths:
                fields.append(line[offset:offset + width].strip())
                offset += width + 1
            index, admin, combined_state, us, ds, mode = fields
            if not combined_state or not mode:
                raise ValueError("Incomplete xDSL line row")
            oper = combined_state.split()[0]
            rows.append(dict(if_index=index, adm_state=admin, opr_state=oper,
                             us_rate=us, ds_rate=ds, cur_op_mode=mode))
        if len(rows) != int(count.group(1)):
            raise ValueError("Incomplete xDSL line table: count does not match parsed rows")
    else:
        rows = _table(output, required, "line")
    result = []
    for row in rows:
        if not re.fullmatch(r"[0-9/]+", row["if_index"]):
            raise ValueError("Invalid xDSL line identity")
        item = {key: row[key] for key in required}
        for direction in ("us", "ds"):
            # Common two-row header: tx-rate / us, tx-rate / ds.
            value = row.get("tx_rate_" + direction, row.get(direction + "_rate"))
            if value is None:
                raise ValueError("Missing xDSL %s rate column" % direction)
            if value in ("", "-", "--", "N/A", "n/a"):
                item[direction + "_rate"] = None
            elif re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
                item[direction + "_rate"] = value
            else:
                raise ValueError("Invalid xDSL %s rate" % direction)
        result.append(item)
    return result

