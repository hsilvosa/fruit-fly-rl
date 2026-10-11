"""Autonomous-student training with a training-only route signal. See docs/AUXILIARY_STUDENT_PROTOCOL.md.
Phase 1 recipe and mix from the experiment 7 start. ARM 'aux': auxiliary waypoint-prediction head, actor and critic blind to the waypoint.
ARM 'critic': privileged critic, blind actor. ARM 'pre': aux arm whose actor trunk starts from the supervised pretraining. Usage: train_student.py <aux|critic|pre> <seed> <output-dir> <stages>"""
import hashlib, json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.buffers import RolloutBuffer
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import load_model, save_model, checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.training.waypoint_diagnostic import WaypointBrainEnv
from fly_rl.training.waypoint_students import build_student
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile

ARM, SEED, OUT, STAGES = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
assert ARM in ('aux', 'critic', 'pre')
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2'
MID = 'scripts/profiles/passages-mid.json'
ASSIGN = [None] * 8 + [MID] * 12 + ['passages'] * 4 + ['passages-wide'] * 4 + ['gate-two'] * 4
STAGE = int(os.environ.get('STAGE_OVERRIDE', 32768))
BUDGET = STAGE * STAGES
LR0, LR1 = 3e-4, 3e-5


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


os.makedirs(OUT, exist_ok=True)
src = SOURCE + '.zip'
src_hash = (sha(src), sha(SOURCE + '.json'))
sv = checkpoint_sensor_version(src)
env = WaypointBrainEnv('data', len(ASSIGN), 'cuda', seed=SEED, mode='dense', dynamics='coordinated', sensor_version=sv,
                       map_profile=None, readout_version=checkpoint_readout(src), privileged=True, **checkpoint_history(src))
env.worlds = [FlightWorld(SEED + i, 'dense', None, 'coordinated', sv, resolve_profile(p)) for i, p in enumerate(ASSIGN)]
source = load_model(src, env.brain, None, True)
model = build_student(source, env, SEED, ARM, pretrained='runs/training/pretrain/trunk.pt' if ARM == 'pre' else None)
model.set_random_seed(SEED)
model.rollout_buffer = RolloutBuffer(128, model.observation_space, model.action_space, device=model.device,
                                     gamma=0.995, gae_lambda=model.gae_lambda, n_envs=len(ASSIGN))
start = model.num_timesteps
model.lr_schedule = lambda _remaining: LR0 + (LR1 - LR0) * min(1.0, (model.num_timesteps - start) / BUDGET)
log = {'arm': ARM, 'seed': SEED, 'source': SOURCE, 'source_sha256': src_hash, 'assignment': [a or 'medium' for a in ASSIGN],
       'budget': BUDGET, 'stage': STAGE, 'lr': [LR0, LR1], 'stages': [], 'actor_route_access': False, 'training_signal': ARM}
for stage in range(1, STAGES + 1):
    t = time.time()
    model.learn(total_timesteps=STAGE, reset_num_timesteps=False)
    schedule = model.lr_schedule
    model.lr_schedule = constant_fn(float(schedule(0.0)))
    model.save(f'{OUT}/stage-{stage}.zip')
    model.lr_schedule = schedule
    losses = {k: float(v) for k, v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
    log['stages'].append({'stage': stage, 'added': model.num_timesteps - start, 'seconds': round(time.time() - t), 'losses': losses})
    print('stage', stage, model.num_timesteps - start, round(time.time() - t), 's',
          {k: round(v, 4) for k, v in losses.items() if k in ('train/approx_kl', 'train/clip_fraction', 'train/value_loss', 'train/aux_loss')}, flush=True)
    log['source_unchanged'] = (sha(src), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done; source unchanged:', log['source_unchanged'])
