# Panoramic neural v7: frozen correction protocol

The preceding waypoint run completed 81,920 new transitions but reached zero of eight goals in reused original-large development rooms. Recorded failures show large motor errors and incomplete dense visual coverage of some recovery directions. The panoramic correction tests a wider body-centered sensory interface, stronger input scaling and longer guided coverage together. It is a correction experiment, not an isolated causal comparison or evidence of a biological advantage.

## Scope and budget

The user instructed continued correction and training until autonomous navigation is solved. This concrete run allows 98,304 new world transitions: 65,536 guided transitions followed by 32,768 student-only transitions. The project has completed 868,352 substantive transitions before this run; the new cumulative cap is 966,656. Verification transitions remain separate. Supervised optimization is capped at 8,192 initial actor updates and two further sets of 2,048 updates, with minibatches of 128. There are no PPO updates, automatic retries, additional world-transition budgets or reserved-test evaluations.

The sensory contract changes to v6: 1,800 panoramic rays around the body, 128 general rays and 3,869 sensor values. The recurrent state preserves all 167,184 annotated neurons and 25,583,622 graph connections. Policy inputs are 3,869 grouped neural activities with eight historical frames plus the present frame. They contain no raw sensor bypass, map, route, aperture center or teacher progress index.

The controller starts fresh because the new neural input shape is incompatible with the earlier policy. The preceding checkpoint is preserved as a reference artifact, not silently transferred. Original aliases are hashed before and after. No alias is promoted by this runner.

## Collection and supervision

Training uses original large geometry with the pool 370000 through 370111. Each of two initial guided fragments starts eight worlds at their exact original positions and headings, without teleporting to route vertices or aligning yaw. A fragment has 32,768 transitions, or 204.8 simulated seconds per world. Physical goals, collisions and timeouts reset worlds normally and receive separate outcome counts. These guided outcomes are teacher results, not autonomous student performance.

The training-only teacher supplies motor labels and local waypoint labels. The learned output controller receives only neural histories. After initial fitting, two student-only chunks of 16,384 transitions each retain physical episodes, full brain state and histories across the intervening supervised fit. Only physical terminal events reset them. Training updates do not advance the world or the fixed brain.

Recordings include before-action pose, velocity, yaw, yaw rate, previous actions, exact layout seed and episode tick, together with executed actions, teacher use and after-action outcome flags. This makes collision and reset phases explicit. Dataset schemas preserve sensor and neural shapes.

## Verification and evaluation

Focused sensor, legacy compatibility, readout and controller tests passed. The full-connectome 128-transition collector smoke used three supervised updates, finite losses, unchanged source weights and compatible CPU/GPU reload. A two-second offscreen demo ran forty physical steps without training; its rendered scene was inspected. These are interface checks, not evidence of navigation quality.

After the fixed budget, the runner saves its own checkpoint and verifies tensors, same-device predictions and CPU/GPU reload. It evaluates eight autonomous episodes on reused development seeds 430000 through 430007 in original large rooms, from original poses and headings, with no teacher. This suite is disjoint from optimization layouts but has been reused to develop corrections. It is not an independent final test. Final-suite requirements remain unmet unless separately demonstrated under a frozen independent protocol.
