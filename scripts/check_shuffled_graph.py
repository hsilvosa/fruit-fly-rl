"""Diagnostic of the edge-shuffled reservoir against the real one, with random sensor input (no policy, no training).
Prints graph statistics and the statistics of the 256 pooled features after 100 steps, so that a dead or saturated control is
detected before any training. Usage: check_shuffled_graph.py"""
import os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
import numpy as np
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.connectome.shuffled import ShuffledBrain
from fly_rl.training.learning import checkpoint_sensor_version

sv = checkpoint_sensor_version('runs/training/reference-transfer-7/mix3e4/stage-2.zip')
real_matrix = sparse.load_npz('data/processed/brain.npz').tocsr()
t = time.time()
shuffled = ShuffledBrain(1, 'data', 8, 'cuda', sensor_version=sv)
print('shuffle built in', round(time.time() - t), 's; edges real', real_matrix.nnz, 'shuffled', shuffled.audit['edges'], flush=True)
real = Brain('data', 8, 'cuda', sensor_version=sv)
rng = np.random.default_rng(0)
x = rng.uniform(0.0, 1.0, (100, 8, real.sensor_count)).astype(np.float32)
for name, brain in (('real', real), ('shuffled', shuffled)):
    brain.reset()
    for step in range(100):
        f = brain.step(x[step])
    state = brain.state.abs().cpu().numpy()
    print(name, 'features mean abs', round(float(np.abs(f).mean()), 4), 'std across features', round(float(f.std(axis=1).mean()), 4),
          'std across batch', round(float(f.std(axis=0).mean()), 4), '| state mean abs', round(float(state.mean()), 4),
          'fraction near saturation (>0.95)', round(float((state > 0.95).mean()), 4), flush=True)
print('fingerprints', real.fingerprint[-60:], '|', shuffled.fingerprint[:60])
