# Flight and anatomical inspection

## Why the fly used to move sideways

Legacy controls allowed substantial independent lateral acceleration. A policy could reach a target while its displayed body pointed sideways. Coordinated controls favor forward movement, reduce lateral acceleration, add lateral drag, smooth yaw, and derive bank/pitch for the animated body. Inertia still permits some lateral drift; perfect heading/velocity alignment is not an acceptance requirement.

The four policy outputs are forward, bank/lateral, vertical, and yaw commands. They operate at the same fixed 0.05-second timestep. Coordinated flight is simplified and does not model wing forces or validate real fly biomechanics. It changed the controller contract, so a fresh coordinated policy was trained rather than silently applying the old one.

## Where the brain drawing comes from

The anatomical viewer joins the retained body IDs with official `somaLocation`, soma-neuromere, and superclass annotations. It displays 140,033 usable positions. The remaining 27,151 neurons remain in the recurrent graph but cannot be placed from these annotations. Missing positions and labels are not inferred.

Coordinates are uniformly scaled to fit the view, with a display-axis reflection. They are soma locations, not meshes, neurite branches, or rendered synaptic pathways. Neuromere/class filtering uses official labels, including explicit unassigned values, and does not infer anatomical borders from geometry.

The brain opens in a separate Panda3D window, sharing the same simulation and graph. No additional recurrent model or training process runs for that view. Closing its window leaves flight running. B in the fly window can recreate it; closing/recreating also starts a new in-memory selection history.

## Activity, change, and sensitivity

M cycles three color modes:

- **Activity:** the signed current value in the engineered recurrent state.
- **Recent change:** the difference from the preceding sampled observation.
- **Local action sensitivity:** a local derivative of a selected policy action through the signed feature pooling.

These values are not biological firing rates. Orange/blue signs do not label actual excitation or inhibition. Sensitivity describes the current mathematical controller locally; it does not trace future recurrent effects or prove that a biological neuron causes a movement.

G changes the soma-neuromere filter, H changes superclass, and Shift reverses either sequence. A clears filters. Clicking a visible soma selects its real body ID. Drag rotates; the wheel zooms. Space pauses the shared simulation; Shift accelerates it; Escape/B minimizes this view.

## Selected-neuron timeline

Observations are sampled every five decisions, normally 4 Hz of simulated time, before the action is applied. A selected-neuron record includes body ID, activity/change/sensitivity, all four normalized actions, speed, bank, yaw rate, target distance, episode, and simulated time. The in-memory history holds at most 240 samples, approximately 60 seconds of simulated activity. Reset or sampling gaps break the chart rather than joining unrelated episodes.

The chart overlays signed activity with forward, bank/lateral, vertical, and yaw commands. It shows association in the modeled controller, not a causal biological mapping. When the brain view is inactive, sampling can stop unless full recording is requested. Inspect phase metadata when combining old and new recordings.

```powershell
.\launch-dense.cmd --brain-region T1 --trace-neuron 10069
.\launch-dense.cmd --brain-region T1 --trace-neuron 10069 --record-brain
```

The second also saves complete neuron vectors every simulated second. Pooled features cannot recover those vectors. Existing archived flight replay has no anatomical snapshot playback; that is a [roadmap](../ROADMAP.md) item.

## Verified scope

A 40-decision archive contained eight selected-neuron observations and two complete 167,184-value snapshots. The observations matched recorded actions and before-action speed, bank, and target distance at their decision numbers. Later onscreen records retained filter labels, selected body ID, and sampling settings. Filtered point selection, closing/recreating the separate window, and rendered traces were briefly checked.

Shift speed scaling has a unit check for ten times as many fixed-timestep decisions. Rendered runs checked the equivalent base speed setting. Physical keyboard focus behavior, multi-monitor scaling, and extended interactive use still need broader testing. Requested speed can exceed actual throughput, especially when recording and rendering the full brain. See [Verification](VERIFICATION.md) for the distinction between these checks and performance results.
