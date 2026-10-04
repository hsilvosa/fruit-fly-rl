# Perception diagnosis and visible fan correction

## Measured information deficit

At the original large spawn, the nearest partition face is 8.3167 units away. Proximity rays stop at eight units. On 16 optimization-layout counterfactuals, changing the first aperture's position produced exactly identical original sensor observations. In four measured examples, the geometry-aware teacher action differed by 1.159-2.0 despite those identical observations. At episode initialization the brain and history also reset identically, so a deterministic learned policy cannot reproduce both immediate teacher labels. This identifies a supervision/observation mismatch. It does not show that navigation with short-range sensing is impossible: an information-seeking exploration strategy could first reveal the opening, and the successful earlier single-wall policy remains a distinct measured result.

Extending only the existing 128 rays to 24 units still left seven of the 16 aperture changes undetected. A denser target-bearing scan distinguished all 16. These are geometry counterfactuals used to test sensing, not newly generated optimizer or test episodes, and no traversability or optimality claim is made for the modified counterfactual certificate.

## Versioned correction

`sensors-v5-v3-plus-589-goal-fan-rays-range24` preserves all 269 sensors-v3 values and adds 589 distance rays and their approach speeds. The 31 azimuth columns span -75 to +75 degrees and 19 elevation rows span -45 to +45 degrees around the already supplied target bearing. Rays stop at their nearest obstacle, room boundary or 24 units. They do not read apertures, paths, map profiles or certificates. These are artificial geometric sensors, not a claim about fruit-fly optics.

The whole-connectome input retains the old seeded input assignments and output pooling, and adds a separate seeded fan projection. Distances are centered at 0.5, approach speeds at zero; two signed extra sensor values per neuron are added to the sensory drive at scale 0.25. Seed 123457 fixes the projection. This is a changed sensory contract and an explicit fingerprint, not a silent reinterpretation of old checkpoint weights. Explicit migration creates a new byte-identical ZIP copy with new metadata; successful navigation still requires retraining and measurement.

## Verification

Twenty-one focused tests cover aperture discrimination on all 16 counterfactuals, beam directions and occlusion, independence from the route certificate, unchanged original sensing/physics, projection neutrality and shape checks, and explicit byte-preserving migration. The corrected migration also passes the existing deadline-transfer tests.

The full annotated graph was verified on CUDA. Four aperture counterfactual pairs produced nonzero maximum changes in pooled brain activity: 0.008751, 0.010665, 0.013859 and 0.013530. This confirms that new visible information reaches the policy's actual brain-feature input, without a raw-sensor bypass. A 20.063-second constant-input benchmark at batch four achieved 279.12 brain transitions/second and 0.318 GiB peak allocated VRAM. This excludes world sensing/rendering overhead and is not training throughput.

An untrained two-second original-large demo completed 40 steps with finite activity, 717 displayed rays, 1,447 sensor values and no optimizer. The rendered scene was inspected. Its numerical archive passed integrity inspection and a one-second replay showed the saved fan without executing the brain or policy. These checks establish implementation; they do not establish navigation improvement.

## Next bounded correction, pending budget approval

The prepared `guided-navigation-v2` draft requests 65,536 additional environment transitions beyond the exhausted 524,288 budget. It uses sensors-v5, 32,768 teacher transitions, two separate 8,192-transition student-only collections from original starts, and 16,384 PPO transitions. Unlike the previous per-action 80% teacher mixture, student-only collection exposes sustained mistakes and supplies corrective labels on states the student actually visits. Teacher labels remain privileged optimization supervision; the teacher is absent in evaluation and demo.

Actor fits are bounded at 3,072 initial and 1,536 total corrective updates; critic fit is capped at 768. The same eight development validation layouts are measured only after the final budget. Source/configuration and alias hashes are frozen. No reserved final test or alias promotion occurs automatically. The draft is executable only after explicit approval of the additional budget; invoking it while draft refuses before brain allocation or training. No training process remains running.
