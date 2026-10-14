"""Evaluate one cell of a checkpoint trained with a given brain, in its own process.
Usage: eval_cell_brain.py <real|shuffled> <checkpoint> <profile|none> <seed> <episodes> <out.json> <det|sampled>
The shuffled brain is injected into the evaluation environment; no frozen source is modified."""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
arm, ck, prof, seed, n, out, mode = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7]
assert arm in ('real', 'shuffled') and mode in ('det', 'sampled')
import fly_rl.training.evaluation as ev
from fly_rl.training.learning import checkpoint_sensor_version
if arm == 'shuffled':
    from fly_rl.connectome.shuffled import ShuffledBrain
    original = ev.BrainEnv
    sv = checkpoint_sensor_version(ck)

    def with_shuffled_brain(data, batch, device, **kwargs):
        return original(data, batch, device, brain=ShuffledBrain(1, data, batch, device, sensor_version=sv), **kwargs)
    ev.BrainEnv = with_shuffled_brain
r = ev.evaluate('data', 'cuda', ck, episodes=n, mode='dense', seed=seed, dynamics='coordinated',
                map_profile=None if prof == 'none' else prof, allow_transfer=True, deterministic=(mode == 'det'))
e = r['episodes']
json.dump({'successes': sum(bool(x['success']) for x in e), 'collisions': sum(bool(x['collision']) for x in e),
           'timeouts': sum(bool(x['timeout']) for x in e), 'episodes': n, 'mode': mode, 'arm': arm,
           'success_seeds': [x['seed'] for x in e if x['success']]}, open(out, 'w'))
