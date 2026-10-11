"""Autonomous students that use the certified-route direction only as a TRAINING signal.

The environment (`waypoint_diagnostic.WaypointBrainEnv`, privileged=True) appends the route direction as 3 extra observation
columns. These policies make sure the ACTOR never reads them:
 - 'critic' arm: the actor's first-layer weights for those columns are zero and their gradient is masked, so the actor is
   exactly blind to them. The critic (value network) reads them, which can only improve value estimates during training.
 - 'aux' arm: actor and critic are both blind to the columns, and an auxiliary head on the actor's last hidden layer is trained
   to predict the route direction (cosine loss), which shapes the actor's representation. The columns serve as a label only.
At test time the three columns can be anything, including zeros: the actor output does not depend on them. See
docs/AUXILIARY_STUDENT_PROTOCOL.md."""
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.utils import explained_variance
from gymnasium import spaces

from fly_rl.training.waypoint_diagnostic import EXTRA


def _blind(layer, width):
    with torch.no_grad():
        layer.weight[:, width:].zero_()
    mask = torch.ones_like(layer.weight)
    mask[:, width:] = 0
    layer.weight.register_hook(lambda grad, m=mask: grad * m)


class BlindWaypointPolicy(ActorCriticPolicy):
    def __init__(self, *args, aux_head=False, actor_blind=True, critic_blind=False, blind_columns=EXTRA, **kwargs):
        self.aux_head_enabled = bool(aux_head)
        self.actor_blind = bool(actor_blind)
        self.critic_blind = bool(critic_blind)
        self.blind_columns = int(blind_columns)
        super().__init__(*args, **kwargs)

    def _get_constructor_parameters(self):
        data = super()._get_constructor_parameters()
        data.update(dict(aux_head=self.aux_head_enabled, actor_blind=self.actor_blind, critic_blind=self.critic_blind,
                         blind_columns=self.blind_columns))
        return data

    def _build(self, lr_schedule):
        super()._build(lr_schedule)
        width = self.observation_space.shape[0] - self.blind_columns
        if self.actor_blind:
            _blind(self.mlp_extractor.policy_net[0], width)
        if self.critic_blind:
            _blind(self.mlp_extractor.value_net[0], width)
        if self.aux_head_enabled:
            self.aux_head = nn.Sequential(nn.Linear(self.mlp_extractor.latent_dim_pi, 64), nn.Tanh(), nn.Linear(64, self.blind_columns))
        self.optimizer = self.optimizer_class(self.parameters(), lr=lr_schedule(1), **self.optimizer_kwargs)

    def aux_loss(self, obs):
        features = self.extract_features(obs)
        latent_pi, _ = self.mlp_extractor(features)
        prediction = self.aux_head(latent_pi)
        target = obs[:, -self.blind_columns:]
        return (1.0 - F.cosine_similarity(prediction, target, dim=1)).mean()


class AuxPPO(PPO):
    """PPO with an optional auxiliary loss `aux_coef * policy.aux_loss(obs)`. Otherwise identical to stable-baselines3 2.7.0 PPO.train."""
    def __init__(self, *args, aux_coef=1.0, **kwargs):
        self.aux_coef = float(aux_coef)
        super().__init__(*args, **kwargs)

    def train(self):
        self.policy.set_training_mode(True)
        self._update_learning_rate(self.policy.optimizer)
        clip_range = self.clip_range(self._current_progress_remaining)
        use_aux = getattr(self.policy, 'aux_head_enabled', False)
        entropy_losses, pg_losses, value_losses, clip_fractions, aux_losses = [], [], [], [], []
        continue_training = True
        approx_kl_divs = []
        for epoch in range(self.n_epochs):
            approx_kl_divs = []
            for data in self.rollout_buffer.get(self.batch_size):
                values, log_prob, entropy = self.policy.evaluate_actions(data.observations, data.actions)
                values = values.flatten()
                advantages = data.advantages
                if self.normalize_advantage and len(advantages) > 1:
                    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
                ratio = torch.exp(log_prob - data.old_log_prob)
                policy_loss = -torch.min(advantages * ratio, advantages * torch.clamp(ratio, 1 - clip_range, 1 + clip_range)).mean()
                pg_losses.append(policy_loss.item())
                clip_fractions.append(torch.mean((torch.abs(ratio - 1) > clip_range).float()).item())
                value_loss = F.mse_loss(data.returns, values)
                value_losses.append(value_loss.item())
                entropy_loss = -torch.mean(-log_prob) if entropy is None else -torch.mean(entropy)
                entropy_losses.append(entropy_loss.item())
                loss = policy_loss + self.ent_coef * entropy_loss + self.vf_coef * value_loss
                if use_aux:
                    aux = self.policy.aux_loss(data.observations)
                    aux_losses.append(aux.item())
                    loss = loss + self.aux_coef * aux
                with torch.no_grad():
                    log_ratio = log_prob - data.old_log_prob
                    approx_kl_div = torch.mean((torch.exp(log_ratio) - 1) - log_ratio).cpu().numpy()
                    approx_kl_divs.append(approx_kl_div)
                if self.target_kl is not None and approx_kl_div > 1.5 * self.target_kl:
                    continue_training = False
                    break
                self.policy.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
                self.policy.optimizer.step()
            self._n_updates += 1
            if not continue_training:
                break
        explained = explained_variance(self.rollout_buffer.values.flatten(), self.rollout_buffer.returns.flatten())
        self.logger.record('train/entropy_loss', np.mean(entropy_losses))
        self.logger.record('train/policy_gradient_loss', np.mean(pg_losses))
        self.logger.record('train/value_loss', np.mean(value_losses))
        self.logger.record('train/approx_kl', np.mean(approx_kl_divs))
        self.logger.record('train/clip_fraction', np.mean(clip_fractions))
        self.logger.record('train/explained_variance', explained)
        if aux_losses:
            self.logger.record('train/aux_loss', np.mean(aux_losses))
        self.logger.record('train/n_updates', self._n_updates, exclude='tensorboard')


def build_student(source, env, seed, arm, learning_rate=3e-4):
    """Student over `features + 3` inputs from a 256-input source policy. All shared weights are copied and the new columns start at
    zero, so before training the student computes exactly what the source computed."""
    if arm not in ('aux', 'critic'):
        raise ValueError('arm must be aux or critic')
    new = AuxPPO(BlindWaypointPolicy, env, device='cpu', seed=seed, verbose=0, learning_rate=learning_rate, n_steps=128,
                 batch_size=256, n_epochs=3, gamma=.995, gae_lambda=.95, clip_range=.1, target_kl=0.02, aux_coef=1.0,
                 policy_kwargs={'net_arch': {'pi': [128, 128], 'vf': [128, 128]}, 'aux_head': arm == 'aux',
                                'actor_blind': True, 'critic_blind': arm == 'aux'})
    old = dict(source.policy.named_parameters()); fresh = dict(new.policy.named_parameters())
    width = source.observation_space.shape[0]
    with torch.no_grad():
        for name, tensor in fresh.items():
            if name.startswith('aux_head'):
                continue
            src = old[name]
            if src.shape == tensor.shape:
                tensor.copy_(src)
            elif tensor.ndim == 2 and tensor.shape[1] == width + EXTRA and src.shape[1] == width and tensor.shape[0] == src.shape[0]:
                tensor.zero_(); tensor[:, :width] = src
            else:
                raise ValueError(f'Cannot expand {name}')
    new.num_timesteps = source.num_timesteps
    return new
