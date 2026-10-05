# Frozen v60/v64 paired development results

These are fresh development measurements of frozen controllers, not a reserved final test.

| Arm | Goals / 16 | Collisions | Timeouts | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| v60 | 15 | 0 | 1 | 71.7–98.9% |
| v64 | 12 | 0 | 4 | 50.5–89.8% |

Paired outcomes: 11 both succeed, 4 baseline only, 1 candidate only, 0 neither succeeds.

| Room | v60 outcome / steps / flown distance | v64 outcome / steps / flown distance |
| --- | --- | --- |
| 11000000 | goal / 2478 / 207.49 | goal / 3246 / 262.36 |
| 11000001 | goal / 1469 / 137.15 | goal / 1482 / 135.24 |
| 11000002 | goal / 3125 / 249.80 | timeout / 3573 / 116.23 |
| 11000003 | goal / 2065 / 164.61 | timeout / 3170 / 98.16 |
| 11000004 | goal / 1840 / 165.09 | goal / 1977 / 170.39 |
| 11000005 | timeout / 3467 / 294.95 | goal / 2819 / 235.81 |
| 11000006 | goal / 1720 / 143.31 | goal / 2237 / 189.70 |
| 11000007 | goal / 1948 / 164.70 | goal / 1883 / 158.75 |
| 11000008 | goal / 2209 / 178.22 | goal / 2205 / 187.37 |
| 11000009 | goal / 1874 / 151.76 | goal / 2036 / 163.88 |
| 11000010 | goal / 1963 / 159.51 | goal / 1785 / 145.78 |
| 11000011 | goal / 1489 / 141.36 | goal / 1453 / 138.15 |
| 11000012 | goal / 2221 / 193.73 | goal / 2360 / 196.02 |
| 11000013 | goal / 2989 / 272.73 | goal / 3513 / 309.59 |
| 11000014 | goal / 2754 / 260.35 | timeout / 3595 / 173.23 |
| 11000015 | goal / 1521 / 132.41 | timeout / 3318 / 81.68 |

Physical transitions across both arms: 112,992. Zero training transitions or optimizer updates.
Original aliases and frozen sources match before/after. Initial layout and graph-data fingerprints match across arms.
Flown distance includes every scored physical step; it is not an optimal-route measurement.

Protocol SHA-256: `ff6a164e5c878036a2f1e313de5f8d800ae78aaeac42d7d00739726fa23a57fc`.

Sixteen development rooms from one generator; not a final test or biological evidence.
