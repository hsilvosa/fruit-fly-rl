# Input-associated neural readout diagnosis

The guarded-PPO baseline measurement reached 0/8 autonomous development goals and eight collisions before refinement. Therefore excessive PPO updates cannot explain all the navigation failures: the fitted imitation controller is already unsuccessful in those rooms. The subsequently completed guarded run also reached 0/8 goals.

A prototype pools signed neuron activity by the existing artificial sensory-input assignments. Each neuron's state contributes to its two original and two fan-channel groups. The mean for a group uses assignment counts; no raw sensor values enter that readout calculation. The complete recurrent graph remains simulated. These are artificial input associations, not biological neuron types or a claim about fruit-fly visual circuits.

The diagnostic retained all 167,184 neurons and 25,583,622 edges. Sixteen optimization-only static counterfactuals move the nearest wall opening while retaining pose and target. For each pair, the full brain starts independently from zero and advances 40 fixed-input neural steps. No physical world steps, optimizer updates or reserved-test evaluation are performed, and counterfactual traversability is not asserted.

Changes in the grouped fan-distance activity closely align with changes in the corresponding observed rays. This tests spatial signal retention under the new grouping, not raw-distance reconstruction accuracy, learned navigation, superiority over every possible decoder of the original 256 features or a biological advantage. The existing compressed features also distinguish these scenes; this diagnostic does not prove they have lost all useful information.

Across the 16 cases, activity/ray-delta correlations range from 0.998842 to 0.999152. Sign agreement on changed rays is 100% in 15 cases and 83.3% in one case. Changed-group RMS ranges from 0.038652 to 0.077961; unchanged-group RMS ranges from 0.000201 to 0.000464. These are native activity units and must not be compared as equal-scale errors with the original signed random pooling. Detailed local records are in private/input-group-readout-diagnosis.json.

The versioned spatial readout is now implemented and undergoing the bounded v5 imitation experiment after interface tests and full-graph smoke verification. Legacy checkpoints retain their original contracts. Teacher-free original-large navigation remains unproven.
