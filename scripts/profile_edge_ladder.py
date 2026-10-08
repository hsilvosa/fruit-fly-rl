"""Find where a frozen policy's capability ends on easier map profiles (evaluation only).
Usage: profile_edge_ladder.py <checkpoint.zip> <seed> <episodes> <output.json> <profile>..."""
import json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.training.evaluation import evaluate
ck, seed, n, out, profiles = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5:]
rows = []
for p in profiles:
    t = time.time(); r = evaluate('data', 'cuda', ck, episodes=n, mode='dense', seed=seed, dynamics='coordinated',
                                  map_profile=p, allow_transfer=True)
    e = r['episodes']
    rows.append({'profile': p, 'seed_start': seed, 'episodes': n, 'successes': sum(x['success'] for x in e),
                 'collisions': sum(x['collision'] for x in e), 'timeouts': sum(x['timeout'] for x in e),
                 'mean_distance_start': sum(x['distance_start'] for x in e) / n, 'mean_distance_end': r['mean_distance_end'],
                 'seconds': round(time.time() - t)})
    print(rows[-1], flush=True); json.dump(rows, open(out, 'w'), indent=1)
