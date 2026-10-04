# Obstacle-aware reward correction

The diagnostic comparison found no original-large validation goals in either temporal readout arm. A geometric audit of 16 optimization layouts measured a mean 5.154 units of necessary travel away from the final target along their certified paths, with a maximum of 7.917. The original reward penalizes these portions by a mean 10.307 progress-reward units, before time cost. This demonstrates a conflicting local training signal; it does not establish that this is the only failure cause. A diagnostic physical route follower also collided on 12 of 16 layouts, so the geometric certificate alone is not evidence that arbitrary flight controls safely execute its corners.

## Correction

The opt-in certified-route-progress-v1 objective replaces Euclidean progress with change in a sampled, obstacle-aware route-distance field. At position p, D(p) is the minimum of ||p-v|| plus certified-route suffix length over sampled vertices v with collision-free connections. It uses body radius plus 0.02 clearance. This is an approximate feasible length, not an optimal geodesic. If no route sample is visible, the previous field value is retained and the transition is counted as a fallback; collision never grants a spurious distance jump. The field has no waypoint ratchet. A closed loop over visible states earns zero undiscounted progress before time cost.

The training reward is 2(D(previous)-D(next)) - 0.02, with the existing success +20 and collision/timeout -5 bonuses. It intentionally changes the training objective. It is not gamma-correct potential shaping and does not carry a policy-invariance guarantee. See [Ng, Harada and Russell (1999)](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf) for the distinction.

## Information boundary

This is privileged geometry supervision through training rewards only. Only declared optimization layouts can instantiate the wrapper. The original goal, map generator, collision boxes, physics, observations, sensor projection and full connectome are unchanged. Policy inputs contain only pooled brain features. Ordinary demo and validation environments neither instantiate the wrapper nor calculate its distance field. The geometry certificate, route nodes and reward components are never appended to observations. This is stronger training assistance than the previous Euclidean objective and must be disclosed in result comparisons; it is not a biological claim or a demonstration that sensors alone provide this reward signal.

## Bounded experiment

One warm-start seed 42 receives 32,768 added transitions in four continuous 8,192-transition chunks, batch eight, entirely on the unchanged original large map. Source is the preserved large-continuous-v4 round-23 controller, sensors-v3. Gamma 0.9995, existing PPO/GAE and timeout bootstrapping remain unchanged to isolate the objective change. The final checkpoint is measured once on the existing eight development validation seeds 430000-430007. These have already informed development, so results are validation, not independent-test evidence. No reserved final test or alias promotion occurs.

Previous substantive use was 450,560. This experiment can bring it to 483,328 of the existing 524,288 cap, leaving 40,960. The runner stops after its declared budget and never restarts or expands it automatically. Freeze code/configuration and original aliases before launch. Report finished-episode outcomes, finite losses, route fallback counts, continuity, actual exposure and validation outcomes even if success remains zero.
