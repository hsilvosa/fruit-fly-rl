# Frozen v60/v65 paired development results

These are fresh development measurements of frozen controllers, not a reserved final test.

| Arm | Goals / 16 | Collisions | Timeouts | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| v60 | 15 | 0 | 1 | 71.7–98.9% |
| v65 | 15 | 0 | 1 | 71.7–98.9% |

Paired outcomes: 15 both succeed, 0 baseline only, 0 candidate only, 1 neither succeeds.

| Room | v60 outcome / steps / flown distance | v65 outcome / steps / flown distance |
| --- | --- | --- |
| 13000000 | goal / 2648 / 251.32 | goal / 2657 / 255.30 |
| 13000001 | goal / 1413 / 130.04 | goal / 1413 / 130.04 |
| 13000002 | goal / 1663 / 146.11 | goal / 1677 / 146.84 |
| 13000003 | goal / 2038 / 175.44 | goal / 1993 / 176.28 |
| 13000004 | goal / 1511 / 132.69 | goal / 1558 / 130.28 |
| 13000005 | goal / 1897 / 153.75 | goal / 1897 / 153.75 |
| 13000006 | goal / 1618 / 136.21 | goal / 1618 / 136.21 |
| 13000007 | goal / 1569 / 134.36 | goal / 1589 / 134.77 |
| 13000008 | goal / 1313 / 124.92 | goal / 1313 / 124.92 |
| 13000009 | goal / 1734 / 147.47 | goal / 1734 / 147.47 |
| 13000010 | goal / 1795 / 149.45 | goal / 1721 / 148.25 |
| 13000011 | goal / 1779 / 152.22 | goal / 1781 / 152.46 |
| 13000012 | goal / 2006 / 178.96 | goal / 3103 / 239.42 |
| 13000013 | timeout / 3499 / 287.65 | timeout / 3499 / 291.89 |
| 13000014 | goal / 1348 / 121.42 | goal / 1348 / 121.42 |
| 13000015 | goal / 2180 / 192.23 | goal / 2120 / 187.76 |

Physical transitions across both arms: 111,968. Zero training transitions or optimizer updates.
Original aliases and frozen sources match before/after. Initial layout and graph-data fingerprints match across arms.
Flown distance includes every scored physical step; it is not an optimal-route measurement.

Protocol SHA-256: `1f01a244654a24fa2b79222a704e8447ea45dd2a039266eb5b2fc879b481faa7`.

Sixteen development rooms from one generator; not a final test or biological evidence.
