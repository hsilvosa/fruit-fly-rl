# Diagnosis during neural-waypoint-v6

This diagnosis reads optimization data already collected. It adds no flight transitions, modifies no checkpoints, and uses no reserved test. The run retains its original configuration while active.

## Control and perception

The first three autonomous batches, each with 16,384 transitions, recorded zero successes and 28, 39, and 30 collisions. These training results are not independent validation.

In the first two batches, mean squared error of executed actions against guide corrections was approximately 0.78 and 0.74 for turning, and 0.52 and 0.53 for vertical control. Neural activity was finite and varied between observations. This rules out constant input in those samples, but does not establish that the representation can resolve every state.

A later analysis of checkpoint student-round-1 on samples from those same data produced turning errors of 0.39 and 0.34. These data were used to fit the model: those errors likewise establish neither generalization nor navigation success.

## Visual coverage

In samples of 1,024 rows per batch, the local point used as the guide label fell outside the dense visual fan in 38.6% and 30.5% of autonomous observations. The fan points toward the final goal and covers 150 horizontal degrees; general sensors cover other directions at lower resolution and range. Being outside the fan does not imply that every sensor is blind or independently identify the cause of each collision.

The direction of the next geometric opening center was also checked on 128 existing observations. In 10.9%, the nearest fan ray was more than ten degrees away. A 1,800-ray panoramic prototype reduced that proportion to 0.8% with elevations from minus 60 to plus 60 degrees. This is a static coverage measurement, not a flight or learning comparison.

## Isolated prototype

The final prototype extends elevation to minus 84 and plus 84 degrees, retains 72 columns around the entire body, and uses 25 rows. Rays measure the first visible surface up to 24 units; they receive no opening centers, routes, or progress indices.

Static integration with the full MaleCNS retained 167,184 neurons and 25,583,622 connections. It produced 3,869 activity groups per observation, with finite values and independent resets. Controller dimensions, finite gradients, and circular continuity of horizontal processing were checked. No physical steps or optimizer updates were run in these checks.

The prototype lives in private and is not yet the production interface or a trained checkpoint. The next correction must check complete flights from original positions and orientations, preserve episodes between fits, and retain validation separate from the reserved test. Expanding sensors is insufficient to declare the problem resolved.
