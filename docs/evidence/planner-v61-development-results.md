# Frozen v60/v61 paired development results

These are fresh development measurements of frozen controllers, not a reserved final test.

| Arm | Goals / 16 | Collisions | Timeouts | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| v60 | 15 | 1 | 0 | 71.7–98.9% |
| v61 | 13 | 2 | 1 | 57.0–93.4% |

Paired outcomes: 13 both succeed, 2 baseline only, 0 candidate only, 1 neither succeeds.

| Room | v60 outcome / steps / flown distance | v61 outcome / steps / flown distance |
| --- | --- | --- |
| 10000000 | goal / 1610 / 139.07 | goal / 2204 / 191.09 |
| 10000001 | goal / 2158 / 179.55 | goal / 2256 / 186.39 |
| 10000002 | goal / 1643 / 155.00 | goal / 1802 / 165.40 |
| 10000003 | goal / 1752 / 155.43 | goal / 1788 / 159.40 |
| 10000004 | goal / 2290 / 203.79 | goal / 2621 / 204.26 |
| 10000005 | collision / 698 / 56.44 | collision / 664 / 58.36 |
| 10000006 | goal / 2381 / 215.12 | goal / 1708 / 150.18 |
| 10000007 | goal / 1458 / 126.13 | goal / 1514 / 130.72 |
| 10000008 | goal / 2850 / 259.41 | collision / 684 / 55.86 |
| 10000009 | goal / 2106 / 160.03 | goal / 1817 / 149.99 |
| 10000010 | goal / 2746 / 221.25 | goal / 2984 / 239.01 |
| 10000011 | goal / 1714 / 144.27 | goal / 1733 / 137.24 |
| 10000012 | goal / 1658 / 136.64 | goal / 1564 / 138.28 |
| 10000013 | goal / 3238 / 271.58 | goal / 3284 / 278.97 |
| 10000014 | goal / 1585 / 134.09 | timeout / 3355 / 175.54 |
| 10000015 | goal / 2483 / 224.43 | goal / 2374 / 209.42 |

Physical transitions across both arms: 105,488. Zero training transitions or optimizer updates.
Original aliases and frozen sources match before/after. Initial layout and graph-data fingerprints match across arms.
Flown distance includes every scored physical step; it is not an optimal-route measurement.

Protocol SHA-256: `10ac830e075e78f5dbcef27bc42867c81a664b552ee89724eb2ddcb1d957ded2`.

Sixteen development rooms from one generator; not a final test or biological evidence.
