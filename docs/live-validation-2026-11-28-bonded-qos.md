# QoS owner of a bonded xDSL line: lab experiment, 2026-11-28 (DS-LIN-TEST-01)

Question: does a bare QoS index (`configure qos interface 1/1/x/n`) on a bonded xDSL line
belong to the line or to its bonding group? The topology model keeps both as candidates
(`ambiguous_owner`).

## Setup and safety

- Card 7 was service-free and has no board installed. It was temporarily planned as
  NDLT-F; no other card, line or global object was touched.
- Every write matched an allow-list for card 7 objects only. After each run the card
  was unplanned (removing everything on it) and its original GPON configuration
  replayed. Full `info configure flat` and `flat detail` captures matched the
  preflight with 0 differing configuration lines after each of the three runs.

## Findings

| Observation | Result |
| --- | --- |
| Bonding groups without links | exist for every line index (`group 1/1/x/n no up`), also on the equipped NDLT-F card |
| First link of group 1/1/7/5 other than line 5 | refused: XDSL MGT error 35 "Bonding is not configured yet" |
| Group 1/1/7/5 with links 1/1/7/5, then 1/1/7/6 | accepted; no group profile needed |
| Interface stack after bonding | `bonding:1/1/7/5` over the channels of lines 5 and 6; `ethernet-line:1/1/7/5` moved onto `bonding:1/1/7/5`; `ethernet-line:1/1/7/6` without lower layer |
| QoS entries of lines 5 and 6 after bonding | both kept, unchanged |
| QoS write (queue 0 weight) on 5 and on 6 after bonding | both accepted and read back |
| QoS write on an unbonded control line | accepted |
| `queue-stats-on` | refused on every line (QOS MGT error 84), not usable as a probe |

## Conclusion

The configuration plane cannot decide the owner. Every index carries a line, a bonding
group and one QoS entry, and a group's index is always also its primary line's (the
group must start with its own line). Member lines keep writable QoS entries, unlike LAG
members (QOS MGT error 216), but an empty bonding group exists at every member index as
well. The QoS command guide names the index "physical port or la-group" and no bonding
group; the bonding guide does not mention QoS. The gap therefore stays named.

Deciding it needs a board: traffic or bonding operational data
(`show xdsl-bonding operational-data group`) on an equipped NDLT card with two
service-free, connected lines, comparing which QoS entry shapes the bonded traffic.
