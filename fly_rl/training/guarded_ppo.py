"""Reject excessive Gaussian policy changes after a complete PPO update.

The gate measures exact distribution KL on every collected rollout observation.
It is an empirical trust region, not a guarantee on unseen observations.
"""
import copy
import numpy as np
import torch
from stable_baselines3 import PPO


class GuardedPPO(PPO):
    def _rollout_observations(self):
        if not self.rollout_buffer.full:
            raise ValueError('KL guard requires a complete rollout')
        return self.rollout_buffer.observations.reshape(-1, *self.observation_space.shape)

    @torch.no_grad()
    def _gaussian_parameters(self, observations):
        means, scales = [], []
        self.policy.set_training_mode(False)
        for start in range(0, len(observations), 256):
            obs = torch.as_tensor(observations[start:start + 256], device=self.device)
            distribution = self.policy.get_distribution(obs).distribution
            if not isinstance(distribution, torch.distributions.Normal):
                raise ValueError('KL guard supports diagonal Gaussian policies only')
            means.append(distribution.loc.detach().clone())
            scales.append(distribution.scale.detach().clone())
        return torch.cat(means), torch.cat(scales)

    @torch.no_grad()
    def _kl_statistics(self, observations, reference):
        mean, scale = self._gaussian_parameters(observations)
        old_mean, old_scale = reference
        divergence = torch.distributions.kl_divergence(
            torch.distributions.Normal(old_mean, old_scale),
            torch.distributions.Normal(mean, scale),
        ).sum(-1).clamp_min(0)
        return float(divergence.mean()), float(divergence.max())

    def train(self):
        observations = self._rollout_observations()
        original_mode = self.policy.training
        before = copy.deepcopy(self.policy.state_dict())
        optimizer_before = copy.deepcopy(self.policy.optimizer.state_dict())
        updates_before = self._n_updates
        numpy_before = np.random.get_state()
        torch_before = torch.get_rng_state()
        cuda_before = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
        original_schedule = self.lr_schedule
        reference = self._gaussian_parameters(observations)
        attempts = []

        def restore():
            self.policy.load_state_dict(before)
            self.policy.optimizer.load_state_dict(copy.deepcopy(optimizer_before))
            self._n_updates = updates_before
            np.random.set_state(numpy_before)
            torch.set_rng_state(torch_before)
            if cuda_before is not None:
                torch.cuda.set_rng_state_all(cuda_before)

        accepted = False
        try:
            for _ in range(self.kl_guard_max_attempts):
                restore()
                scale = self.kl_guard_lr_scale
                self.lr_schedule = lambda progress, scale=scale: original_schedule(progress) * scale
                PPO.train(self)
                mean_kl, max_kl = self._kl_statistics(observations, reference)
                finite_parameters = all(bool(torch.isfinite(p).all()) for p in self.policy.parameters())
                accepted = (finite_parameters and np.isfinite([mean_kl, max_kl]).all()
                            and mean_kl <= self.kl_guard_mean_limit and max_kl <= self.kl_guard_max_limit)
                attempts.append({'lr_scale':scale,'mean_kl':mean_kl,'max_kl':max_kl,
                                 'accepted':bool(accepted)})
                if accepted:
                    break
                self.kl_guard_lr_scale *= .5
            if not accepted:
                restore()
                mean_kl = max_kl = 0.
            self.kl_guard_history.append({'attempts':attempts,'accepted':bool(accepted),
                                          'observations':len(observations),
                                          'retained_mean_kl':mean_kl,'retained_max_kl':max_kl})
            self.logger.record('train/guard_accepted', float(accepted))
            self.logger.record('train/guard_attempts', len(attempts))
            self.logger.record('train/guard_mean_kl', mean_kl)
            self.logger.record('train/guard_max_kl', max_kl)
            self.logger.record('train/n_updates', self._n_updates, exclude='tensorboard')
        except Exception:
            restore()
            raise
        finally:
            self.lr_schedule = original_schedule
            self.policy.set_training_mode(original_mode)


def configure_kl_guard(model, mean_limit=.01, max_limit=.05, max_attempts=8):
    if not 0 < mean_limit <= max_limit or type(max_attempts) is not int or not 1 <= max_attempts <= 12:
        raise ValueError('Invalid bounded KL guard configuration')
    model.__class__ = GuardedPPO
    model.kl_guard_mean_limit = float(mean_limit)
    model.kl_guard_max_limit = float(max_limit)
    model.kl_guard_max_attempts = max_attempts
    model.kl_guard_lr_scale = 1.
    model.kl_guard_history = []
    return model
