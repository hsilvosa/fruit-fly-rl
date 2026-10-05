# Frozen v55/v60 paired development results

These are fresh development measurements of frozen controllers, not a reserved final test.

| Arm | Goals / 16 | Collisions | Timeouts | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| v55 | 12 | 0 | 4 | 50.5–89.8% |
| v60 | 14 | 0 | 2 | 64.0–96.5% |

Paired outcomes: 12 both succeed, 0 baseline only, 2 candidate only, 2 neither succeeds.

| Room | v55 outcome / steps / flown distance | v60 outcome / steps / flown distance |
| --- | --- | --- |
| 9500000 | goal / 2242 / 168.38 | goal / 1950 / 150.20 |
| 9500001 | timeout / 3310 / 0.61 | timeout / 3310 / 0.61 |
| 9500002 | goal / 2108 / 147.16 | goal / 1783 / 144.76 |
| 9500003 | goal / 1944 / 141.28 | goal / 2310 / 207.63 |
| 9500004 | goal / 1820 / 129.82 | goal / 1952 / 179.40 |
| 9500005 | goal / 2120 / 152.74 | goal / 1796 / 160.35 |
| 9500006 | goal / 2035 / 145.43 | goal / 1595 / 130.22 |
| 9500007 | timeout / 3444 / 242.97 | goal / 2350 / 207.94 |
| 9500008 | goal / 1679 / 123.65 | goal / 1425 / 129.06 |
| 9500009 | goal / 2650 / 196.39 | goal / 2073 / 187.68 |
| 9500010 | goal / 1941 / 138.47 | goal / 1946 / 163.46 |
| 9500011 | goal / 2074 / 143.59 | goal / 1642 / 137.27 |
| 9500012 | timeout / 3419 / 245.66 | goal / 2437 / 207.98 |
| 9500013 | goal / 1796 / 126.41 | goal / 1963 / 185.21 |
| 9500014 | timeout / 3480 / 219.96 | timeout / 3480 / 269.64 |
| 9500015 | goal / 2699 / 195.23 | goal / 2615 / 240.33 |

Physical transitions across both arms: 111,360. Zero training transitions or optimizer updates.
Original aliases and frozen sources match before/after. Initial layout and graph fingerprints match across arms.
Flown distance includes every scored physical step; it is not an optimal-route measurement.

Protocol SHA-256: `6f7ee07d0bb29530c8862b4a108383a1aa3959565d9c44a67e763039d29b0707`.

Sixteen development rooms from one generator; not a final test or biological evidence.
