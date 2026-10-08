"""Learned architectural flight actions; no explicit planner in policy inference."""
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from stable_baselines3 import PPO
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

VERSION = 'learned-architecture-1.0-exp.1'
STRUCTURED_VERSION = 'learned-architecture-1.0-exp.2'


def encoder_type(version):
    if version == VERSION: return ArchitecturalHistoryEncoder
    if version == STRUCTURED_VERSION:
        from fly_rl.training.structured_architecture import StructuredArchitecturalHistory
        return StructuredArchitecturalHistory
    raise ValueError('Unknown autonomous policy version')


class ArchitecturalHistoryEncoder(BaseFeaturesExtractor):
    def __init__(self, observation_space):
        if observation_space.shape != (9, 5669):
            raise ValueError('Expected nine-frame segmented full-connectome features')
        super().__init__(observation_space, features_dim=128)
        self.frame = nn.Sequential(nn.Linear(5669, 128), nn.LayerNorm(128), nn.Tanh())
        self.memory = nn.GRU(128, 128, batch_first=True)

    def forward(self, observations):
        sequence, _ = self.memory(self.frame(observations))
        return sequence[:, -1]


def make_autonomous_policy(env, seed=42, rollout_steps=128, epochs=1, version=VERSION):
    if type(rollout_steps) is not int or rollout_steps < 2 or rollout_steps % 128:
        raise ValueError('Use rollout steps in multiples of 128')
    if type(epochs) is not int or epochs < 1:
        raise ValueError('Invalid PPO epochs')
    model = PPO('MlpPolicy', env, device=env.brain.device, seed=seed,
               n_steps=rollout_steps, batch_size=128, n_epochs=epochs,
               learning_rate=3e-4, gamma=.995, gae_lambda=.95, clip_range=.2,
               policy_kwargs=dict(features_extractor_class=encoder_type(version),
                                  net_arch=dict(pi=[128], vf=[128]), ortho_init=False),
               verbose=0)
    model.autonomous_version = version
    return model


def contract(env, version=VERSION):
    encoder_type(version)
    return dict(version=version, algorithm='PPO', planner_assistance=False,
                observation_shape=list(env.observation_space.shape),
                brain_fingerprint=env.brain.fingerprint,
                readout_version=env.brain.readout_version,
                history_frames=env.history_frames, history_stride=env.history_stride,
                sensor_version=env.brain.sensor_version,
                dynamics=env.worlds[0].dynamics,
                scene=env.architectural_scene, situation=env.architectural_situation,
                reward='existing-environment-reward', learned_navigation_verified=False)


def save_autonomous_policy(model, path, env):
    path=Path(path)
    if path.suffix != '.zip':
        raise ValueError('Use an explicit .zip checkpoint path')
    if path.exists() or path.with_suffix('.json').exists():
        raise ValueError('Do not overwrite an existing checkpoint')
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(path))
    metadata=contract(env, getattr(model,"autonomous_version",VERSION))
    metadata.update(training_transitions=model.num_timesteps, optimizer_updates=model._n_updates)
    path.with_suffix('.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')


def load_autonomous_policy(path, env):
    path=Path(path)
    metadata=json.loads(path.with_suffix('.json').read_text())
    expected=contract(env, metadata.get("version"))
    for key in ('version','algorithm','planner_assistance','brain_fingerprint','readout_version',
                'observation_shape','history_frames','history_stride','sensor_version','dynamics'):
        if metadata.get(key) != expected[key]:
            raise ValueError('Autonomous checkpoint contract mismatch: '+key)
    model = PPO.load(str(path), env=env, device=env.brain.device)
    if type(model.policy.features_extractor) is not encoder_type(metadata['version']):
        raise ValueError('Checkpoint encoder and version disagree')
    model.autonomous_version = metadata['version']
    return model
