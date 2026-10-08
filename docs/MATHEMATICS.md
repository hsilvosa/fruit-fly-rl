# Mathematical model and optimization

This guide describes the implemented controller as of October 2, 2026. Equations are engineering choices in Fly RL unless a published algorithm is cited. MaleCNS supplies connectivity and annotations; it does not supply these sensor mappings, activity dynamics, rewards, or navigation rules. See [data assumptions](DATA_AND_MODEL.md) and [source credits](REFERENCES.md).

## From sensors to actions

One decision follows this sequence:

```text
269 sensor values -> fixed whole-connectome activity -> 256 pooled features
                 -> learned actor -> four commands -> flight step and reward
```

Let x_t be the sensor vector, h_t the neuron activities, z_t the pooled features, and a_t the four commands. The critic estimates future discounted reward from z_t. Both actor and critic use separate two-layer networks with 128 units per layer and tanh activations. The graph, sensory projection, and pooling remain fixed. There is no gradient through the brain, no synaptic learning, and no planner route in the observations. The reservoir runs on CUDA and the current actor/critic run on CPU.

The feature vector is an observation with recurrent history; it is not guaranteed to be a complete Markov state. PPO itself uses an ordinary MLP, not a learned recurrent policy.

## Connectome weights and activity

Implementation: [data processing](../fly_rl/connectome/data.py) and [brain](../fly_rl/connectome/brain.py).

Let C_ij be the retained synapse count from presynaptic neuron j to postsynaptic neuron i. Duplicate directed pairs are summed. Let sigma_j = -1 for the modeled GABA sources and +1 otherwise. The matrix has postsynaptic rows and presynaptic columns:

$$
W_{ij}=0.9\frac{\sigma_j C_{ij}}{\max(1,\sum_k C_{ik})}.
$$

Thus every row's absolute sum is at most 0.9. A zero-input row remains zero. This sign rule is an approximation; a positive sign does not establish that every biological connection is excitatory.

For each neuron i, seed 42 fixes two sensor indices q_i1, q_i2 and two signs e_i1, e_i2 in {-1,+1}. Its synthetic sensory input is

$$
u_{i,t}=\tfrac12(e_{i1}x_{q_{i1},t}+e_{i2}x_{q_{i2},t}).
$$

One brain step uses

$$
h_{t+1}=0.5h_t+0.5\tanh(Wh_t+u_t).
$$

The tanh operates elementwise. Each episode resets its own activity column to zero. Starting within [-1,1], every update remains in that interval. For identical sensor inputs, the infinity-norm Lipschitz bound is at most 0.5 + 0.5(0.9) = 0.95, because tanh is 1-Lipschitz. This supports numerical stability of the fixed update; it does not guarantee stable closed-loop flight or successful navigation when sensor inputs change.

Each neuron has a seeded bucket b_i in {0,...,255} and a seeded sign eta_i. If n_k is the number assigned to bucket k, pooling is

$$
z_{k,t+1}=\frac{\sum_{i:b_i=k}\eta_i h_{i,t+1}}{\sqrt{\max(n_k,1)}}.
$$

An empty bucket is zero. The features are not clipped to [-1,1]; they can exceed that range. The normalization controls bucket-size scale but does not make the features independent or unit variance.

## Sensor formulas and target information

Implementation: [world observations](../fly_rl/simulation/world.py) and [ray directions](../fly_rl/simulation/sensors.py).

Let p be position, g the target, v world velocity, and R(psi) the yaw rotation taking local column vectors into world coordinates. For a unit local ray d_k, its world direction is D_k = R d_k. The distance l_k is the first hit on room walls or an obstacle, capped at 8 units. Rays measure from the fly center against raw boxes; they do not inflate obstacles by body radius.

For the original v2 interface, the 269 values are the concatenation below, finally clipped componentwise to [-1,1]:

$$
x=\operatorname{clip}_{[-1,1]}\left[
\{l_k/8\}_{k=1}^{128},\ \{D_k^T v/3\}_{k=1}^{128},\
\frac{R^T(g-p)}{\max(\|g-p\|,10^{-6})},\ \|g-p\|/18,\ R^Tv/3,\ a_{t-1},\ p_z/6,\ a_{t-1,\mathrm{yaw}}
\right].
$$

The target is known through its relative direction and distance, not discovered visually. Positive ray approach speed means movement toward that ray's direction, not a measured time-to-contact. Dense-room distances above 18 and altitudes above 6 saturate. The final value repeats the previous yaw command, not measured yaw rate. These inherited choices are recorded in the sensor version; changing them requires a new interface and evaluated checkpoints.

For [sensors v3](SENSORS_V3.md), three values change: target distance becomes norm(g-p)/norm(room size - 2(0.16)); altitude becomes p_z/current room height; the last value becomes measured yaw rate/2.6. The 269-value ordering and all other readings stay identical. Coordinated yaw rate is the filtered state; legacy rate is 2.1 times the applied yaw command. Checkpoint versions prevent silent reinterpretation.

## Flight and collisions

Implementation: [coordinated dynamics](../fly_rl/simulation/flight.py) and [world step](../fly_rl/simulation/world.py). A decision advances dt = 0.05 seconds. Let commands (a_f,a_l,a_z,a_y) be clipped to [-1,1]. Coordinated yaw rate omega and heading psi evolve as

$$
\omega^*=1.8a_y+0.8a_l,\qquad
\omega'=\omega+\min(1,5dt)(\omega^*-\omega),\qquad
\psi'=\operatorname{wrap}_{[-\pi,\pi)}(\psi+dt\,\omega').
$$

Using the updated heading, transform v into local velocity v_local = R(psi')^T v. Thrust and local drag are

$$
f=[c(a_f)a_f,\ 0.35a_l,\ 2.5a_z]^T,\qquad
c(a_f)=\begin{cases}3,&a_f\geq0\\1.2,&a_f<0,\end{cases}
$$

$$
v_{local}'=v_{local}+dt\left(f-[0.6,2.8,0.8]^T\odot v_{local}\right),\qquad
\tilde v=R(\psi')v_{local}',\qquad
v'=\tilde v\min\left(1,\frac{3}{\max(\|\tilde v\|,10^{-12})}\right).
$$

The candidate position is p_candidate = p + dt v'. Legacy dynamics instead update heading directly by 2.1 dt a_y and use world acceleration R(psi') (3 a_f, 3 a_l, 3 a_z), with drag 0.6 v. Checkpoint metadata distinguishes these profiles.

Coordinated visual bank approaches clip(-0.3 a_l - 0.12 omega', -0.55, 0.55), and pitch approaches clip(atan2(tilde_v_z, max(norm(tilde_v_xy),0.2)), -0.6, 0.6), using velocity before the world speed cap, both with interpolation factor min(1,6 dt). These are display orientations, not aerodynamic lift forces.

A collision occurs if the candidate center exits [0.16, room_size - 0.16] or the entire old-to-candidate segment intersects an obstacle box inflated by 0.16 along each axis. This uses a box inflation approximation, not exact sphere-versus-box geometry. The stored position is clipped to room bounds. Arrival requires distance < 0.45 and no collision. Timeout occurs at the episode limit only if neither arrival nor collision already ended it.

## Navigation reward

With d_t = norm(g-p_t), the implemented reward is

$$
r_t=2(d_t-d_{t+1})-0.02
 +20\,\mathbf1_{\mathrm{arrival}}
 -5\,\mathbf1_{\mathrm{collision}}
 -5\,\mathbf1_{\mathrm{timeout}}.
$$

These outcomes are mutually exclusive. A 0.10-unit distance reduction produces 0.18 before a terminal term; standing still produces -0.02. At 20 decisions per simulated second, the time cost is 0.4 per second. Progress uses the actual stored next position, including room-bound clipping. Distance reward encourages approach but cannot guarantee detours or arrival. Discounting also means it should not be treated as an undiscounted telescoping-distance objective.

## PPO: what is optimized

Project configuration: [learning.py](../fly_rl/training/learning.py). Algorithms: Schulman et al., [PPO](https://arxiv.org/abs/1707.06347) and [generalized advantage estimation](https://arxiv.org/abs/1506.02438). Implementation details follow the installed [Stable-Baselines3 2.7.0 PPO](https://stable-baselines3.readthedocs.io/en/v2.7.0/modules/ppo.html), rather than assuming every PPO implementation has identical defaults.

The desired objective is expected discounted reward:

$$
J(\theta)=\mathbb E_{\pi_\theta}\left[\sum_{t\geq0}\gamma^t r_t\right],\qquad \gamma=0.995.
$$

The actor produces a diagonal Gaussian over four raw action components, with learned means and learned log standard deviations. Training samples raw actions; deterministic viewing uses the means. Commands sent to the environment are clipped to [-1,1]. PPO stores and evaluates the raw sampled action density, not a Gaussian density for the clipped command. This is SB3's unsquashed continuous-action behavior.

Let V_phi(z_t) be the critic prediction and m_t = 0 at an episode boundary, 1 otherwise. The rollout computes backward in time:

$$
\delta_t=\tilde r_t+\gamma m_t V_\phi(z_{t+1})-V_\phi(z_t),\qquad
\hat A_t=\delta_t+\gamma\lambda m_t\hat A_{t+1},\qquad
\lambda=0.95,\qquad \hat R_t=\hat A_t+V_\phi(z_t).
$$

At a normal rollout boundary, the critic supplies the next-value bootstrap. At arrival/collision, it does not. For a time-limit truncation, SB3 first adds gamma V_phi(z_terminal) to the environment reward, giving tilde r_t, and then stops advantage recursion across the reset. The logged environment return still uses the original reward, including the timeout penalty. Terminal features are captured before the individual reservoir column resets.

Within each minibatch, SB3 normalizes advantages with its sample standard deviation:

$$
\bar A_t=\frac{\hat A_t-\operatorname{mean}(\hat A)}{\operatorname{std}(\hat A)+10^{-8}}.
$$

With rho_t = exp(log pi_theta(a_t|z_t) - log pi_old(a_t|z_t)) and epsilon = 0.2, the minimized actor loss is

$$
L_{actor}=-\operatorname{mean}\left[\min\left(\rho_t\bar A_t,\operatorname{clip}(\rho_t,0.8,1.2)\bar A_t\right)\right].
$$

Clipping limits the surrogate incentive for large ratio changes; it is not a hard bound on policy change. The critic and total losses are

$$
L_{value}=\operatorname{mean}[(V_\phi(z_t)-\hat R_t)^2],\qquad
L_{entropy}=-\operatorname{mean}[H(\pi_\theta(\cdot|z_t))],\qquad
L=L_{actor}+0.5L_{value}+0L_{entropy}.
$$

There is no explicit entropy bonus in the present configuration, even though entropy is logged. Value predictions are not clipped. The Gaussian still supplies stochastic exploration during training. Logged losses are optimizer diagnostics, not success measures.

Fresh policy settings are:

| Setting | Value |
| --- | --- |
| Learning rate | 0.0003 |
| Steps per environment per rollout | 512; 128 for smoke check |
| Minibatch size | 128 transitions |
| Passes over each rollout | 5; 1 for smoke check |
| Discount / GAE | 0.995 / 0.95 |
| Policy ratio clip | 0.2 |
| Value / entropy coefficients | 0.5 / 0.0 |
| Gradient norm limit | 0.5 |
| Optimizer | Adam; beta1 = 0.9, beta2 = 0.999, epsilon = 0.00001 |
| KL early-stop target | None |

For batch B, a full rollout contains 512 B transitions. The bounded dense runner requires complete rollouts; at B = 8, each is 4,096 transitions. A 32,768-transition round therefore has eight rollouts, each with five optimizer passes. This differs from a smoke check's single update.

Before Adam, the combined parameter gradient g is norm-clipped to approximately g min(1,0.5/norm(g)). Adam then accumulates moments

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,\qquad
v_k=\beta_2v_{k-1}+(1-\beta_2)g_k^2,
$$

$$
\hat m_k=m_k/(1-\beta_1^k),\qquad \hat v_k=v_k/(1-\beta_2^k),\qquad
w_{k+1}=w_k-0.0003\,\hat m_k/(\sqrt{\hat v_k}+0.00001).
$$

Squares and division are componentwise. PyTorch uses a small numerical epsilon in gradient-norm clipping. Checkpoint resumes restore saved policy/optimizer settings; the table describes fresh construction, not a promise to override arbitrary checkpoint parameters. Viewing never runs this optimization.

## Model selection and evaluation

Implementation: [dense rounds](../fly_rl/training/dense_training.py), [seed selection](../fly_rl/training/experiment_selection.py), [evaluation](../fly_rl/training/evaluation.py), and [summaries](../fly_rl/training/generalization.py).

Candidates are ranked lexicographically by (validation success rate, negative collision rate, negative mean ending distance). This is not the PPO training loss. Validation chooses the round and adaptation seed; final-test outcomes never select a candidate. Frozen hashes and the exposure ledger protect the declared protocol, but do not prove the complete absence of overfitting or data leakage.

For n final episodes and k successes, p_hat = k/n. With z = 1.959963984540054, the reported Wilson 95% interval is center plus or minus margin:

$$
\mathrm{center}=\frac{\hat p+z^2/(2n)}{1+z^2/n},\qquad
\mathrm{margin}=\frac{z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n}.
$$

It describes success uncertainty under the binomial episode model; it does not measure variability across training seeds or transfer to another generator.

Flown length is sum_t norm(p_(t+1)-p_t), and arrival time is steps times 0.05. The reference planner inflates boxes by 0.16 + 0.02 and minimizes sum of Euclidean edge lengths over its sampled visibility graph using Dijkstra. It is an approximate feasible geometric path to the goal center, with separately labeled certified fallback, not a global optimum or a dynamically executable flight plan.

For successful episodes with a reference, report mean(L_flown/L_reference), not the ratio of pooled total lengths. Failed episodes never enter this mean; missing successful references and coverage are separate fields. The 0.45 arrival radius can yield a ratio below one. See [route protocol and measured results](GENERALIZATION_AND_ROUTES.md).

## Reading the recorded results

The latest bounded experiment added 131,072 transitions across two warm-start adaptation seeds. Validation selected seed 42's second round before the fresh final comparison. It reached 43/64 goals, with 15 collisions and 6 timeouts; its successful flown/reference ratio averaged 1.219. These measurements are outcomes of the optimization, not guarantees implied by the formulas. The 80% goal remains open. The original launcher alias uses an earlier checkpoint and different evaluated rooms.

The subsequent matched sensor comparison completed 262,144 added transitions across v2/v3 seeds 42 and 73. Validation selected v2; the winner reached 50/64 fresh final goals (78.1%). See [sensor comparison](SENSORS_V3.md) for seed results, uncertainty and limitations. Earlier numerical results above remain historical.

## Optional observed-ray risk training objective

The tested `observed-ray-risk-v1` wrapper subtracts 0.05 times a pre-action risk estimate based on visible distance and closing speed, with a 0.75-second horizon. [The complete equations and limitations](COLLISION_RISK.md#formula-and-objective) distinguish this changed training objective from the ordinary evaluation reward. This is not potential-based shaping and may affect optimal behavior.

## Progressive geometry and curriculum formulas

[The geometry protocol](GEOMETRY_CURRICULUM.md#difficulty-measurements-and-formulas) defines certified route length, detour, occupancy, conservative body clearance and route-dependent episode limits. The historical v1 stage was min(2, floor(3n/N)), with n including the transition offset across rounds and N the declared per-seed budget.

The corrected v2 stage starts at s = 0. After round r, let g_(r,1) and g_(r,2) be goal counts in the two distinct eight-layout training-practice batches at stage s. The next stage is:

$$
s_{r+1}=\begin{cases}\min(s_r+1,K-1),&g_{r,1}\geq7\ \mathrm{and}\ g_{r,2}\geq7,\\s_r,&\mathrm{otherwise}.\end{cases}
$$

Here K is the number of frozen profiles. At stage zero the reset distribution places all mass on the first profile. At s > 0, probability 0.8 selects the current profile and probability 0.2/s selects each earlier profile; harder profiles have probability zero. Practice layouts are withheld from optimizer rollouts in both arms. They adapt the training schedule, so their success is not independent test evidence. Checks add inference decisions, not optimizer transitions.

Profile choice happens only at episode reset. Validation and test do not change progression. V2 selection excludes initialization, requires positive target validation success before a final assessment, and rounds ending distance to six decimals when ranking tied success/collision counts. The reward/PPO formulas remain unchanged. The certificate is not policy input or an optimal flight trajectory.

Completed learning measurements are summarized in [Results](RESULTS.md). These equations specify the implementation; they do not establish successful navigation or biological fidelity.


## Versioned navigation deadline

The opt-in sensors-v4 contract adds q_t = max(0, 1 - t/T), where t is elapsed decisions and T is the declared episode deadline. Its seeded clock projection adds c_i q_t to neuron i's existing sensory drive. Weights c_i belong to {-0.25, 0, 0.25}; the original sensory assignments and pooling stay fixed. The policy still consumes only pooled recurrent activity. This is a synthetic sensory projection, not an anatomical claim.

For per-decision discount gamma and decision duration dt, the effective discount horizon is dt/(1-gamma). At dt=0.05, gamma=0.995 corresponds to 10 seconds and gamma=0.9995 to 100 seconds. An arrival reward R after n decisions contributes gamma^n R. The longer horizon is a candidate setting, not a proven performance improvement.

An exhausted attempt can be configured as a task failure through --timeout-as-terminal. In that case PPO does not add gamma V(s_terminal) to the final reward. Ordinary external truncations should continue to bootstrap. The physical timeout remains recorded independently of that learning flag. See [Gymnasium time-limit semantics](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) and [the verified timeout diagnosis](evidence/large-timeout-diagnosis.md).


## Training-only obstacle-aware progress correction

The opt-in `certified-route-progress-v1` objective is described in [the bounded correction protocol](evidence/route-progress-correction-v1-plan.md). For each episode, sample its fixed certified polyline at intervals of at most one unit. Let S(v) be suffix length from sampled vertex v to the final goal. Define D(p) as the minimum of ||p-v|| + S(v) over vertices connected to position p by a segment free of obstacles inflated by body radius plus 0.02. This is an approximate feasible route length, not an optimal geodesic. Its fixed field has no waypoint index or irreversible progress counter.

For valid visible connections, reward is r = 2(D(p_t)-D(p_(t+1))) - 0.02 + B, where B is +20 for arrival, -5 for collision or failed deadline, and zero otherwise. This replaces the former Euclidean-progress term rather than adding both. If no sample is visible, retain the last valid field value, grant zero progress and record a fallback. Collisions always grant zero route progress, without resetting D to zero. Closed visible-state loops telescope to zero undiscounted progress; time cost remains negative.

Geometry and route samples are privileged training supervision used only to compute rewards in optimizer layouts. Sensors, graph activity and policy input dimensions are unchanged. Ordinary demo and evaluation do not compute this field. This intentionally changes the training objective: unlike gamma Phi(next)-Phi(previous), this expression is not discount-correct potential shaping and makes no policy-invariance claim. See [Ng, Harada and Russell (1999)](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf). Correctness of these equations does not prove successful navigation.


## Long-range visible scan and its brain projection

Sensors-v5 retains all sensors-v3 values. The new 589-beam grid scans target-relative azimuth theta+alpha and elevation phi+beta, with alpha spanning -75 to 75 degrees in 31 columns and beta spanning -45 to 45 degrees in 19 rows. Elevation is clipped just inside the poles. Each unit direction is (cos(elevation) cos(azimuth), cos(elevation) sin(azimuth), sin(elevation)). The world rotation transforms these local directions before standard ray-box intersection. Distances are divided by 24 and approach speeds by three. The scan is centered on the already supplied synthetic target bearing, without using a hidden aperture or route.

Neuron i receives an extra drive 0.25 times the sum of two signed fan values, with distance channels centered at 0.5 and approach channels at zero. Seed 123457 fixes extra input indices and signs. Its recurrent update, matrix and output pooling retain the existing equations. No raw fan channel is appended to policy inputs; policy features remain 256 values, optionally with their recorded history. Versioned fingerprints require explicit transfer. [Measured observation aliases and full-brain verification](evidence/visible-fan-v5.md) distinguish sensor correctness from successful learned navigation.


## PPO update rollback gate

The [guarded PPO protocol](evidence/guarded-navigation-v4-plan.md) checks the actual resulting policy instead of relying only on a pre-step sampled stopping estimate. For independent Gaussian action coordinates, KL(old || new) is the sum over coordinates of log(new_std / old_std) + (old_std squared + (old_mean - new_mean) squared) / (2 new_std squared) - 1/2. Evaluate that quantity on every collected rollout observation. Retain an update only when the observed mean is at most 0.01 and observed maximum is at most 0.05. Rejected candidates restore policy and optimizer state and re-use the same rollout with half the learning rate, up to eight attempts. These constraints apply to the observed rollout distribution, not all possible future states. Successful navigation must still be measured separately.


## Input-associated neural readout

For channel c, let A_c contain the neuron assignments whose seeded input index is c, with signs s_ic. The new output is g_c(t) = sum_(i in A_c) s_ic h_i(t) / max(1, |A_c|). Both original and fan assignments contribute. A neuron can belong to several channel groups. This formula reads the recurrent neuron state h, not the raw sensor x. The existing recurrent matrix and updates are unchanged. The groups describe artificial projections and do not identify biological cell populations.

The v5 spatial actor encodes the two 19 by 31 neural fan planes with convolutions, encodes the remaining 269 neural groups with a linear layer, and uses a GRU across nine sampled frames. It minimizes the existing weighted imitation loss on optimization-world teacher labels; no PPO update is used in the substantive spatial experiment. The 128-transition smoke checks that the learning interface remains usable. See [frozen scope](evidence/spatial-neural-v5-plan.md).


## Learned waypoint auxiliary, implementation verified

The new head predicts a four-component local waypoint description from the neural history encoder. Training labels are u = (delta R / max(norm(delta), epsilon), min(norm(delta)/24, 1)), where delta points from the training world position to the teacher's current route vertex and R converts world vectors to body coordinates. These privileged labels are targets, not policy inputs. The runtime predictor only receives neural histories.

If e is the existing 128-feature encoder output and q_hat is the learned four-component estimate, the motor features are e + A q_hat + b. A and b start at zero, so explicit transfer preserves the existing actor output before fitting. The supervised objective is the existing weighted action MSE plus lambda times waypoint MSE, with lambda = 2 in verification. Rows without retained waypoint labels are masked out of the auxiliary loss and can still contribute action supervision. The fourth prediction is an estimate; the head does not mathematically enforce a positive distance.

The maneuver/start sampler assigns a quarter of a batch to strong turns, a quarter to strong vertical labels, a quarter to empty recent neural-history slots, and leaves the final quarter uniformly sampled. Empty groups retain uniform draws. Groups can overlap and draws can repeat. This is an optimization choice whose navigation benefit remains unverified. Legacy turn-balanced sampling remains unchanged by default.

Focused tests and a three-update full-connectome auxiliary smoke passed, with zero physical transitions, initially identical motor outputs, unchanged brain state and source checkpoint, and exact reload. The subsequent waypoint v6 experiment completed, but its autonomous development result was 0/8. Verification of the objective and successful optimization do not establish navigation.


## Body-centered panoramic neural control

Sensors-v6 retains the 269 v3 measurements and replaces the target-centered fan with 1,800 body-centered rays. The grid has 72 azimuths at five-degree spacing around the full circle and 25 elevations from minus 84 to plus 84 degrees. Directions are rotated by body yaw and measure the nearest surface to a maximum range of 24. No waypoint or aperture coordinate determines the scan. The fixed graph receives two signed visual assignments per neuron, with gain 0.25 and distance centering 0.5, as in the preceding projection. Its signed row-normalized recurrent matrix remains unchanged.

The input-associated output has 3,869 neural groups. Multiplying these groups by a fixed factor of ten changes the numerical scale used by the learned encoder; it neither appends raw sensors nor changes the graph. The visual encoder uses circular horizontal padding because the first and last azimuth columns are adjacent. Vertical padding repeats edge values. Two convolution layers encode the two 25 by 72 neural planes. Proprioceptive features and visual features feed a 192-feature GRU across the same nine-frame history. A four-component waypoint head adds a learned residual to this latent representation.

The objective remains weighted action mean squared error plus twice waypoint mean squared error on training-world labels. This version starts a fresh controller because the sensory and feature dimensions changed; it does not claim output-preserving transfer. The bounded panoramic run uses supervised optimization without PPO updates. Runtime inference consumes only recurrent neural activity; privileged geometry is restricted to the training collector. These equations and interface checks do not prove autonomous navigation.

## Directional visual attention

The directional head keeps a score for each of the 1,800 body-centered ray directions d_i. Shared circular convolutions produce visual scores b_i from the neural panorama. The normalized existing goal-bearing neural groups provide g. Logits are z_i = b_i + 3 d_i dot g, and weights are p_i = exp(z_i) / sum_j exp(z_j). The predicted direction is normalize(sum_i p_i d_i). The distance component still comes from the history encoder. Goal groups and panorama groups are readings of recurrent neuron activity, not raw sensor values or a supplied aperture location.

Training chooses the directional class c with the largest dot product between d_c and the optimization teacher's target direction. The total objective is weighted action MSE plus twice waypoint MSE plus eta times cross entropy, where cross entropy is -log(p_c). Eta is one in the first directional correction and 0.25 in the look-ahead correction. This extra target is privileged training supervision. It is never appended to runtime observations.

An angular rotation check verifies the coordinate behavior of the attention head. It does not establish that rotating the world rotates the biological graph's activity exactly. The graph uses artificial seeded projections, and successful navigation must be measured separately. Matching learned tensors can be transferred between the visual encoders; that partial transfer does not preserve their initial outputs.

## Look-ahead teacher correction

The earlier teacher waited until the fly came within 0.06 units of a hidden route vertex before advancing. The new training-only teacher projects position onto its current certified path segment and aims along the polyline by a look-ahead length ell = 0.5 + 0.5 min(distance to the next vertex / 2, 1). It advances the segment after passing its projection or approaching its endpoint within 0.35 units. The target can continue beyond the corner, so reaching an exact six-centimeter neighborhood is no longer required to obtain a forward target.

For heading error e and target distance D, desired speed is min(1.2, 1.5 D) times max(0, cos(e)) to the fourth power. Horizontal and altitude acceleration use the existing proportional velocity and drag compensation. This is a piecewise path follower, not a mathematical guarantee of collision-free flight. Oracle geometry checks and teacher arrivals are separate from autonomous student performance. Old exact-vertex examples are not replayed into the new look-ahead fit because their control targets use a different convention.

## Sparse and distance-only visual variants

The sparse visual variant retains only the nine largest ray logits before applying softmax. Its direction estimate and pooled visual features use those selected weights. Empty history frames retain a uniform score distribution and an explicitly zero direction, so tied empty scores do not invent a heading. This changes inference even when every learned tensor is identical to the source checkpoint; it is not output-preserving transfer.

The distance-only variant zeros the 1,800 approach-speed neural groups in the visual panorama. Distance groups and the original 269 neural groups remain available. The complete graph and all sensory projections still run; neurons and synapses are not removed. This tests an explicit visual velocity shortcut while retaining motor-state features. It does not remove every possible velocity influence from recurrent neural activity, and improvement cannot be assumed from the implementation alone.

## Learned portal perception and explicit flight feedback

The portal pilots learn a body-frame spatial reference delta and local velocity v from current and recent grouped neural activity. They do not append training route or aperture coordinates to runtime observations. For unit bearing u = delta / max(norm(delta), epsilon), heading error e = atan2(delta_y, delta_x), and distance D = norm(delta), desired speed is min(1.2, 1.5 D) max(0, cos(e))^4. Desired velocity is u times this speed.

Horizontal thrust is clip(3(norm(desired_xy) - v_x) + 0.6 norm(desired_xy), -1.2, 3), normalized by 3 for positive thrust and 1.2 for braking. Vertical action is clip((3(desired_z - v_z) + 0.8 desired_z)/2.5, -1, 1). Yaw action is clip(2e/1.8, -1, 1); lateral action is zero. This control is explicit physics feedback, not a learned action regression or a collision-free guarantee.

The attention target is a soft angular distribution proportional to exp(dot(training bearing, ray direction)/0.006). Supervised loss is 0.3 cross entropy against that distribution, plus mean angular loss 1 - dot(predicted bearing, target bearing), plus 0.5 times squared distance error normalized by 12, plus twice velocity MSE. Adam uses a learning rate of 0.0003 and gradient norm clipping at one. The perception fit is separate from PPO optimization.

V14 removes fixed horizontal ray coordinates from CNN inputs. Shared circular convolutions score depth activity, goal alignment, elevation and the neural goal-distance group. The direction is the normalized softmax-weighted sum of ray directions. Its cyclic yaw equivariance concerns this bearing calculation; the velocity and range decoder and the biological reservoir do not acquire an exact rotation symmetry from that test. See the [portal protocol](evidence/portal-feedback-protocol.md) for sampling, exposure and observed failures.

## Projection whitening and the information diagnostic

Let A be the known synthetic sensory projection, c its fixed visual-centering drive, W the complete signed recurrent matrix and h the neuron state. The brain update is h_t = 0.5 h_(t-1) + 0.5 tanh(W h_(t-1) + A x_t - c). From the full previous and current activities, z_t = atanh(2 h_t - h_(t-1)) + c recovers the combined input and recurrent drive, subject to floating-point precision and saturation.

The information upper-bound diagnostic solves A x_hat = z_t - W h_(t-1) by stabilized least squares. It explicitly cancels recurrent computation and must not be interpreted as a beneficial connectome readout. The navigation candidate instead solves A f_t = z_t, retaining f_t approximately equal to x_t + A^+ W h_(t-1). It corrects cross-talk between the seeded projections while retaining their projected recurrent context. These are derived neuron-activity features, not values appended from the world observation.

Columns of A are normalized by their Euclidean norm before forming the Gram matrix. A diagonal ridge of 0.000001 stabilizes its Cholesky factorization. Activity inversion clamps tanh arguments to [-1 + 0.000001, 1 - 0.000001]; saturated values are therefore approximate. Tests verify the projection algebra and that retaining recurrent drive changes the decoded features. Actual diagnostics use the full graph, with no graph reduction.

In a short 128-transition optimization diagnostic, the recurrence-canceling bound reconstructed panorama distances with approximately 0.000045 metre RMSE. The recurrence-retaining candidate had 0.824 metre RMSE. An affine fit of the preceding grouped readout, fitted and measured on those same observations, had 1.724 metre RMSE. This is a small, favorable diagnostic sample and does not establish navigation performance, independent generalization, a unique failure cause or biological advantage. Its two 128-transition checks and the separate 128-transition PPO smoke are verification, not substantive training.


The v32 contrast readout retains an explicit recurrent fraction:

\[
y_{\mathrm{contrast}} = A^+\left[z - 0.95Wh_{t-1}\right]
\approx x_t + 0.05A^+Wh_{t-1}.
\]

The neural matrix, projection, and updates of all states are preserved. This is an engineering choice to reduce interference in sensory coordinates; it does not reproduce an established mechanism in the fly. The contract has its own fingerprint and requires explicit transfer from the previous reader. Algebra checks the recurrent fraction, and checkpoint reload checks actions.

Perception context reduces the full panorama to a 5-by-12 grid and uses a network predicting scale and bias for local channels. These parameters condition opening scores before selecting a local maximum. Its supervised objective retains angular cross-entropy, direction error, and distance error; it does not modify the connectome or itself constitute PPO training.


To separate approach from crossing, a horizontal wall normal \(n\) is learned from the neural image. Orientation labels come only from training poses. With estimated center \(c\), decompose \(c=n(n^Tc)+c_\perp\). During approach, the reference is \(c-1.3n\); after alignment, it is \(c+1.2n\). Near the goal, its existing neural direction and distance are used. The orientation head is fitted with loss \(1-\hat n^Tn^*\), preserving earlier perception weights.

V35 limits the longitudinal approach component using the median short distances projected onto the learned normal. Rays are below 7.7 meters, nearly horizontal, and aligned with the normal in a cone with minimum cosine 0.9. If no usable measurement exists, the learned estimate is retained. This is a control heuristic with uncertainty, not a safety guarantee or weight modification.


## Temporal image alignment and inspection basis

For current and previous horizontal neuronal goal bearings g and g_old, the image warp uses delta = atan2(g_old_y, g_old_x) - atan2(g_y, g_x). Each current panorama column samples the previous image at column + 72 delta/(2 pi), with circular interpolation. Empty bearings use zero shift. This approximates camera yaw and includes translational error; no exact pose or fixed history age is assumed.

With normalized sensory projection B = A N^-1 and Gram G = B^T B + ridge I, the drive readout is f = N^-1 G^-1 B^T z. For a policy gradient q = d(action)/df, its local drive sensitivity is B G^-1 N^-1 q. The anatomical inspector plots that quantity for projection readers, holding previous state and previous history fixed. It is a derivative with respect to reconstructed drive, not with respect to the recurrent neuron state or a causal intervention. The trace metadata names the basis. Group-mean and legacy readers use their own state sensitivity mapping.

The trajectory guard projects each reconstructed distance endpoint p onto the horizontal motion direction u. It uses the smallest positive p^T u with norm(p - u p^T u) <= 0.28 m. Vertical guards use endpoints inside a horizontal radius of 0.28 m. This avoids braking for some side obstacles, but sparse rays and reconstruction errors can miss surfaces. The eight optimization flights showed no improvement over the preceding controller.


## Motion-stable projection reader

The motion-stable variant computes f = A^+(z - W h_previous) + D A^+ W h_previous. D is diagonal: zero for the first 269 base distance, target and motor channels, and 0.05 for the 3,600 panorama distance and approach channels. It decodes previous and current modeled neuron states; no world sensor values are appended in reconstruction. All neuron states and recurrent edges still advance. Canceling recurrence in synthetic motion coordinates supports odometry, while panorama coordinates retain the declared recurrent fraction. This remains an engineered readout, with its own checkpoint fingerprint.

The experimental planner-1.2-exp.1 distance-stable reader changes that diagonal to zero for coordinates 0–2068 and 0.05 for coordinates 2069–3868. Base channels and all 1,800 panoramic ranges therefore cancel projected recurrence; panoramic closing speeds retain the declared context. The fixed graph, neural update, sensory projection, and stabilized inverse are unchanged. A contextual perturbation is not a literal physical distance: the [known-case audit](evidence/planner-readout-v61-v63.md) found that the preceding reader could produce false braking. This reader has a separate version and incompatible checkpoint fingerprint. It is an engineered reconstruction, not evidence of biological perception.

A 128-transition check using the full graph measured normalized base-channel RMSE 0.00000567, yaw-rate RMSE 0.00000472 rad/s and panorama-distance RMSE 0.0419 m. It took 0.682 seconds after initialization and used 560 MiB peak allocated VRAM. This short check describes numerical reconstruction and does not establish navigation. A separate temporary 128-transition, one-update PPO smoke had finite losses and maximum CPU reload action error 0.000000358; its checkpoint was removed.


## Observed-map planning and flight control

The map uses 0.6 m voxels in an initial body-relative frame. A free ray reduces cell evidence by one, down to -8; observed surface samples increase it by three, up to 12. Evidence at least two marks a solid cell. Free cost is 1, unknown cost 2.8, and observed solids plus one axial safety shell are impassable. If the current cell lies inside that shell, non-solid margin cells in a local five-by-five-by-five region temporarily cost 8, allowing escape without opening solid cells.

The search considers 26 neighbors, checks axial intermediate cells before diagonal moves, and uses priority g + 4.5 h, where g sums cell cost times step length and h is Euclidean distance to the goal cell in voxel units. This weighted, bounded search is not a shortest-path guarantee. It stops at the exact goal cell, appends the continuous goal, and after 12,000 expansions uses the best remaining open frontier. Route following advances past reached cells and uses an observed-clear look-ahead of 3 m, reduced to 1 m in a tight margin.

For waypoint delta d and distance D = norm(d), u = d / max(D, 1e-6). Each reconstructed ray endpoint p contributes clearance l = p^T u when l > 0 and norm(p - l u) < 0.25 m. The nearest such endpoint gives L. Requested speed is min(v_max, 1.5 D, sqrt(2.4 max(L - 0.27, 0))), with v_max = 1.8 m/s normally and 0.8 m/s in the margin. Sparse rays and map discretization do not guarantee collision avoidance.

Horizontal desired velocity is u_xy times requested speed times max(cos(yaw_error), 0)^4. Vertical desired velocity is u_z times requested speed, independently of the horizontal heading. With observed body-forward velocity v_x, thrust is clip(3 (norm(desired_xy) - v_x) + 0.6 norm(desired_xy), -1.2, 3), normalized by 3 for positive thrust and 1.2 for braking. Vertical command is clip((3 (desired_z - v_z) + 0.8 desired_z) / 2.5, -1, 1). Yaw command is clip(2 yaw_error / 1.8, -1, 1). Lateral command is zero in coordinated flight. These are explicit proportional controls and planning costs, not optimization of learned movement weights.

The anatomical window can display actual modeled activity and change for this planner. Its decision logic includes discrete search and stateful memory; no PPO action gradient is computed or presented as planner sensitivity. Archived traces mark sensitivity unavailable.

The experimental planner-1.2-exp.4 momentum guard applies the same endpoint tube to measured velocity direction, not only the desired waypoint. With measured speed s and nearest forward motion clearance L_motion, the guard activates when s > 0.1 and s > sqrt(2.4 max(L_motion - 0.27, 0)). Desired horizontal and vertical velocity then become zero; existing proportional control and steering remain. This approximate braking rule does not guarantee safety under sparse rays or turning inertia. The trace records pre-guard requested speed and post-guard effective desired speed separately.

planner-1.2 separates these physical safety coordinates from occupancy input. From the same decoded clean signal c = A^+(z - W h_previous) and context r = A^+ W h_previous, its feature vector is concatenate(c + D r, c[269:2069]), where D is planner-1.1's original motion-stable diagonal. Mapping uses the original 3,869-coordinate prefix; requested-direction and momentum braking substitute the appended 1,800 clean ranges. The graph advances once and world sensor count remains 3,869, while feature width becomes 5,669. Its distinct readout fingerprint and declared feature width prevent silent interface transfer. Numerical stabilization and inverse-activation clipping still apply; this is an engineered information construction, not biological vision.


## Experimental opening references and execution vetoes

The room-aware goal normalization, plane/ray intersection, portal clustering, approach/crossing references, and temporary grid veto are explained with their constants in [maze navigation](MAZE_NAVIGATION.md#relevant-formulas). These are explicit planning rules, not an optimization objective or a learned movement policy. A temporary veto changes traversal cost while leaving observed occupancy evidence untouched.


## Observed-clearance opening reference

Exp.18 returns to exp.11 surface selection, grid, speed, guards and stronger-support refinement. Let `C` be through-ray intersections belonging to an observed opening cluster, and `W` be observed endpoints on its fitted surface. Both are represented in the wall tangent/height plane. The new reference is `argmax(p in C) min(w in W) ||p - w||`, followed by the existing projection onto the fitted plane. This replaces the median of visible through-rays, which can be biased toward the visible edge of a partially observed opening. It uses no known aperture size or hidden mesh.

The distance to sparse wall endpoints is a reference-selection heuristic, not a guaranteed continuous clearance radius. The actual fly body, collision model, range braking, momentum braking and episode deadlines remain unchanged. Three reference tests pass, including a fixture with the actual maze opening width 2.4 and height 2.8. The selected point lies inside that fixture with body clearance; this does not prove arbitrary sampled surfaces safe. The eight-layout retained full-connectome check completed at five goals without collisions and was rejected because it missed the declared gate. No optimizer or reserved final evaluation was involved.

## Repeatable full-connectome execution

The experimental index-add and segmented readouts retain every matrix value, including its sign. For CSR row offsets `p`, column indices `c`, weights `w` and a dense batch of neuron states `H`, both compute row `i` as `sum(w[k] * H[c[k]] for k in range(p[i], p[i+1]))`. Empty rows sum to zero. The sensory projection uses the same sparse operation. The recurrence, leak, inverse-activation reconstruction, centering and dual feature formulas remain unchanged. Floating-point accumulation order changes, so these kernels have separate readout fingerprints. Short repeated-input probes establish repeatability on the tested runtime and device; they do not establish cross-hardware equality or improved navigation.

## Clearance-aware goal handover

Planner-1.3-exp.25 starts from exp.23 and excludes exp.24's rejected wall survey. Let the decoded local goal vector be `g`, its distance `D = ||g||` and its direction `u = g / D`. For each reconstructed range `r_i` and body-relative ray direction `d_i`, define its endpoint `q_i = r_i d_i`, longitudinal projection `a_i = q_i dot u`, and transverse distance `b_i = ||q_i - a_i u||`.

A nonsaturated endpoint vetoes direct handover when all four conditions hold:

- `r_i < R_i - 0.05`, where the maximum range `R_i` is 8 for short rays and 24 for panoramic rays;
- `a_i > 0`;
- `a_i < D + 0.3`;
- `b_i < 0.25`.

This uses the same endpoint corridor radius as requested-direction braking. Maximum-range returns mean no observed hit within range and are excluded as surfaces. The original four-nearest-panoramic-ray visibility test must also pass: `0.45 < D < 23`, each ray aligns with the goal by more than 0.98, and each projected range extends beyond `D + 0.3`. An active opening approach/crossing prevents goal handover until that reference completes or expires under its existing rule.

This corrects an observed inconsistency: in an exp.23 retained failure, sparse panoramic goal visibility stayed true while near-body braking requested zero speed. It is still a sampled-ray heuristic. It does not prove that the entire continuous body corridor is obstacle-free, does not change collision geometry, and does not optimize learned policy weights. Its full-flight checks reached 7/8 retained goals, then 5/8 fresh development goals with no collisions and three timeouts. It failed the fresh criterion and is not promoted.


## Experimental maze recovery and visit coverage

Exp.28 samples its estimated position every 20 controller decisions. A visit cell is `floor(position / 2)`, with a two-unit cell width. A sample is novel if its cell has not appeared earlier in the episode. Recovery becomes eligible after three consecutive samples whose complete 16-sample window contains fewer than four novel cells, provided no opening reference is active. The parent recovery also requires 320 decisions without more than one unit of additional progress along the initial horizontal goal direction. This is a development heuristic fitted to inspected failures, not an independent generalization result.

Exp.29 retains that gate. It chooses between two tangent directions along an observed wall. Let `q` be the projected near-side position, `n` the fitted horizontal wall normal, `t` its horizontal tangent, and `c_j = 2 * (cell_j + 0.5)` the centers of previously visited cells. For direction `d` in {-1, +1}, coverage is the number of centers satisfying both `abs(dot(c_j - q, n)) < 3` and `2 < d * dot(c_j - q, t) < 18`. All heights contribute to this horizontal coverage count.

The candidate penalty is `coverage + 20 * failed_or_reached_target_visits`. The lower penalty wins; the original goalward direction breaks a tie. A candidate still needs mapped reference clearance and the existing current-ray clearance checks. Targets are three units along the tangent, at half the room height. A target expires after 100 decisions without the required distance improvement; the complete recovery expires after 400 decisions. These limits do not extend the physical episode deadline.

Visit history and wall fits use estimated position and observations. Hidden wall geometry and certified routes are not controller inputs. The recovery rules perform explicit planning and do not update neural or policy weights. Full-flight results and the promotion gates are recorded in [maze navigation](MAZE_NAVIGATION.md).


## Completed-crossing normal consensus

Planner-1.3-exp.31 uses exp.29 and excludes exp.30's rejected unreachable-reference release. For recorded completed crossing normals `n_i`, define `A_ij = 1(abs(dot(n_i, n_j)) > 0.98)` and `a_i = sum_j A_ij`. Choose the observed normal with the largest `a_i` as the consensus candidate. It is eligible only with at least three recorded crossings, `a_i >= 3`, and `a_i >= 0.75 * N`, where `N` is the number of recorded crossings. The absolute dot product makes the test independent of the normal sign.

Let `u` be the normalized horizontal direction from estimated position to the initial decoded goal. The consensus filter applies only if `abs(dot(n_i, u)) >= 0.8`. While eligible, a proposed opening normal `m` is rejected when `abs(dot(m, n_i)) < 0.98`. Otherwise the inherited detector and reference execution remain unchanged. Completed crossing observations, estimated pose and the decoded goal are the only inputs to this additional rule. World yaw, hidden boxes and route metadata are unavailable to it.

The rule is a retained-data hypothesis about repeated observed surfaces. It can suppress a differently oriented opening that is actually necessary; the goal-alignment condition does not prove this cannot happen. It is not a general architectural-navigation contract. Focused tests verify the declared conditions, but full retained flights, regression checks and a separately frozen fresh suite determine acceptance. No optimization formula is added: this controller performs explicit planning and does not train weights.

The preceding exp.30 rule released a cross-phase reference after 100 sustained decisions with no observed-map route and temporarily rejected a nearby aligned estimate for 600 decisions. Its full-flight check regressed to 5/8 retained goals and it was rejected. An unavailable route alone is insufficient evidence that an opening is invalid.
