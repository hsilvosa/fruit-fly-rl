# Matched critic isolation v3: results

Completed 65,536 additional transitions on 2026-10-04; cumulative substantive use is 655,360. Autonomous development validation on the original large rooms reached 0/8 goals, eight collisions and no timeouts. Navigation remains unresolved. No reserved final test or automatic checkpoint promotion occurred.

The teacher completed eight training goals. Student-only corrective rounds finished 23 and 6 collisions with no goals, matching v2's counts. Teacher outcomes are not autonomous success. The full graph retained 167,184 neurons and 25,583,622 edges. Saved guided checkpoint verification confirmed separate actor/critic modules with initially identical history weights.

All recorded fit and PPO losses were finite, and checkpoint reload predictions matched. Nevertheless PPO changes were excessive: final logged approximate KL was 0.342514 against target 0.01; an earlier TensorBoard entry reached 3.486418. The installed PPO early-stop check does not undo an earlier optimizer step that crossed its threshold. Separate memories did not prevent this divergence or establish useful navigation.

The eight seeds 430000-430007 are reused development validation, not an independent final test. Initial teacher physical records match v2 exactly, but brain features differ by at most 2.14577e-6; subsequent student supervision trajectories are not bitwise identical. This is a one-seed development comparison, not a repeated-seed causal or biological benefit claim. Mean ending distance was36.852309; mean idle fraction was0.038045.

Independent SHA-256 checks confirmed the original warm source, six aliases and frozen implementation matched before the next source change. Detailed hashes and raw status are retained in private/guided-navigation-v3-audit.json. No new navigation evidence is inferred from successful software tests.
