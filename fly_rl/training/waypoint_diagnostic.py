"""Privileged-waypoint diagnostic (not a student): a brain environment whose policy input is the 256 connectome features
plus the unit vector, in the body frame, to the certified-route point `LOOKAHEAD` metres ahead of the fly's progress.
With `privileged=False` the three extra inputs are zeros (matched control: same network, same pipeline, no information).

The certified route comes from the map generator (`world.reference_route`). Policies trained or evaluated here have runtime
route access and must never be reported as autonomous students. See docs/WAYPOINT_DIAGNOSTIC_PROTOCOL.md."""
import numpy as np
import torch
from gymnasium import spaces
from stable_baselines3 import PPO

from fly_rl.training.learning import BrainEnv

LOOKAHEAD = 4.0
EXTRA = 3


def _route(world):
    pts = [np.asarray(p, float) for p in world.reference_route]
    route = np.vstack([world.position] + pts) if pts else np.vstack([world.position, world.target])
    if np.linalg.norm(route[-1] - world.target) > 0.5:
        route = np.vstack([route, world.target])
    ln = np.linalg.norm(np.diff(route, axis=0), axis=1)
    return route, np.concatenate([[0.], np.cumsum(ln)])


def waypoint_vector(world, route, cum, lookahead=LOOKAHEAD):
    p = world.position
    seg = np.diff(route, axis=0); ln = np.maximum(np.linalg.norm(seg, axis=1), 1e-12)
    u = np.clip(((p - route[:-1]) * seg).sum(1) / ln ** 2, 0, 1)
    proj = route[:-1] + seg * u[:, None]; k = int(np.linalg.norm(p - proj, axis=1).argmin())
    s = min(cum[k] + u[k] * ln[k] + lookahead, cum[-1])
    ahead = np.array([np.interp(s, cum, route[:, a]) for a in range(3)])
    c, sn = np.cos(world.yaw), np.sin(world.yaw)
    rot = np.array([[c, -sn, 0], [sn, c, 0], [0, 0, 1.]])
    v = (ahead - p) @ rot
    return (v / max(np.linalg.norm(v), 1e-9)).astype(np.float32)


class WaypointBrainEnv(BrainEnv):
    def __init__(self, *args, privileged=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.privileged = bool(privileged)
        width = self.feature_count + EXTRA
        self.observation_space = spaces.Box(-np.inf, np.inf, (width,), dtype=np.float32)
        self._cache = [None] * self.num_envs
        self._last = np.zeros((self.num_envs, EXTRA), np.float32)

    def _extra(self):
        out = np.zeros((self.num_envs, EXTRA), np.float32)
        if not self.privileged:
            return out
        for i, w in enumerate(self.worlds):
            key = (tuple(np.round(w.target, 3)), len(w.obstacles), w.ticks == 0)
            if self._cache[i] is None or self._cache[i][0] != key[:2] or w.ticks == 0:
                route, cum = _route(w)
                self._cache[i] = (key[:2], route, cum)
            out[i] = waypoint_vector(w, self._cache[i][1], self._cache[i][2])
        return out

    def _pack_features(self, features):
        packed = super()._pack_features(features)
        extra = self._extra()
        self._last = extra.copy()
        return np.concatenate([packed, extra], axis=1)

    def step_wait(self):
        previous = self._last.copy()
        obs, rewards, dones, infos = super().step_wait()
        for i in np.flatnonzero(dones):  # terminal observation keeps the last waypoint (one step old) for the bootstrap
            terminal = infos[i].get('terminal_observation')
            if terminal is not None and len(terminal) == self.feature_count:
                infos[i]['terminal_observation'] = np.concatenate([terminal, previous[i]])
        return obs, rewards, dones, infos


def expand_policy(source, env, seed, learning_rate=3e-4):
    """New PPO over `features + 3` inputs. All weights are copied; the three new first-layer columns start at zero,
    so the expanded policy computes exactly what the source computed. Adam moments restart (same in both arms)."""
    new = PPO('MlpPolicy', env, device='cpu', seed=seed, verbose=0, learning_rate=learning_rate, n_steps=128, batch_size=256,
              n_epochs=3, gamma=.995, gae_lambda=.95, clip_range=.1, target_kl=0.02,
              policy_kwargs={'net_arch': {'pi': [128, 128], 'vf': [128, 128]}})
    old = dict(source.policy.named_parameters()); fresh = dict(new.policy.named_parameters())
    width = source.observation_space.shape[0]
    with torch.no_grad():
        for name, tensor in fresh.items():
            src = old[name]
            if src.shape == tensor.shape:
                tensor.copy_(src)
            elif tensor.ndim == 2 and tensor.shape[1] == width + EXTRA and src.shape[1] == width and tensor.shape[0] == src.shape[0]:
                tensor.zero_(); tensor[:, :width] = src
            else:
                raise ValueError(f'Cannot expand {name}: {tuple(src.shape)} -> {tuple(tensor.shape)}')
    new.num_timesteps = source.num_timesteps
    return new
