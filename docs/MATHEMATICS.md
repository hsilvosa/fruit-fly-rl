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

[The geometry protocol](GEOMETRY_CURRICULUM.md#difficulty-measurements-and-formulas) defines certified route length, detour, occupancy, conservative body clearance and route-dependent episode limits. Its training-only curriculum stage is min(2, floor(3n/N)), with n including the transition offset across rounds and N the declared per-seed budget. Profile choice happens only at episode reset. Validation does not change the schedule, and the reward/PPO formulas remain the same. The certificate is not policy input or an optimal flight trajectory.

Completed learning measurements are summarized in [Results](RESULTS.md). These equations specify the implementation; they do not establish successful navigation or biological fidelity.
