# Guarded PPO navigation v4 results

The declared pre-PPO controller and the final controller each reached 0/8 original-large development goals, with eight collisions and no timeouts. This correction did not solve navigation.

The experiment completed 32,768 additional transitions, bringing the substantive ledger to 688,128. Seven of eight collected-rollout updates were accepted; nine candidate attempts were rejected and rolled back. The maximum retained mean Gaussian KL was 0.00374085 and maximum retained per-observation KL was 0.0400242, within the declared 0.01 and 0.05 limits. These limits concern collected observations, not unseen states.

Losses were finite and checkpoint reload matched. Independent SHA-256 checks confirmed the declared source checkpoint, source metadata and all six original launcher aliases unchanged. Detailed hashes and status are retained in private/guarded-navigation-v4-audit.json.

The eight development seeds 430000 through 430007 have been reused. Their results do not establish independent generalization. No reserved final test was evaluated, no alias was promoted, and no biological benefit is claimed. The pre-PPO failure shows that controlling PPO update size alone is insufficient.
