"""Light audit (no training, no policy, no GPU): does the reward + discount make route-following look worse than hovering?
For passages maps: follow the certified reference route at constant speed and compute the discounted return from the start,
under the real reward (2 * progress in Euclidean distance - 0.02 per step, +20 on arrival), gamma 0.995. Compare with hovering."""
import json, os, sys
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.simulation.world import FlightWorld, DT
from fly_rl.simulation.map_profiles import resolve_profile

GAMMA = 0.995
rows = []
for name in ('passages', 'passages-wide', 'none'):
    for seed in range(870000, 870016):
        w = FlightWorld(seed, 'dense', None, 'coordinated', None, None if name == 'none' else resolve_profile(name))
        w.reset(seed=seed)
        route = np.vstack([w.position] + [np.asarray(p) for p in w.reference_route]) if len(w.reference_route) else np.vstack([w.position, w.target])
        if np.linalg.norm(route[-1] - w.target) > 0.5:
            route = np.vstack([route, w.target])
        seg = np.linalg.norm(np.diff(route, axis=0), axis=1)
        length = float(seg.sum())
        straight = float(np.linalg.norm(w.target - route[0]))
        # progress profile of Euclidean distance along the route
        cum = np.concatenate([[0], np.cumsum(seg)])
        out = {'profile': name, 'seed': seed, 'route_m': length, 'straight_m': straight, 'limit': w.episode_limit}
        for speed in (1.0, 2.0, 3.0):
            steps = int(np.ceil(length / (speed * DT)))
            s = np.minimum(np.arange(steps + 1) * speed * DT, length)
            pts = np.stack([np.interp(s, cum, route[:, k]) for k in range(3)], axis=1)
            d = np.linalg.norm(pts - w.target, axis=1)
            r = 2 * (d[:-1] - d[1:]) - 0.02
            reached = d[-1] < 0.45
            r[-1] += 20. if reached else 0.
            disc = GAMMA ** np.arange(len(r))
            out[f'v{speed:g}'] = {'steps': steps, 'fits_limit': steps <= w.episode_limit, 'return': float((r * disc).sum()),
                                  'arrival_weight': float(GAMMA ** steps), 'arrival_bonus_discounted': float(20 * GAMMA ** steps),
                                  'min_prefix': float(np.minimum.accumulate((r * disc).cumsum())[-1])}
        hover = -0.02 * (1 - GAMMA ** w.episode_limit) / (1 - GAMMA)  # discounted hover cost, timeout penalty bootstrapped away
        out['hover_return'] = float(hover)
        out['hover_with_timeout_penalty'] = float(hover - 5 * GAMMA ** w.episode_limit)
        rows.append(out)
for name in ('passages', 'passages-wide', 'none'):
    sub = [r for r in rows if r['profile'] == name]
    print(f"== {name}  n={len(sub)}  route {np.mean([r['route_m'] for r in sub]):.1f} m (straight {np.mean([r['straight_m'] for r in sub]):.1f} m), limit {sub[0]['limit']} ticks")
    for v in ('v1', 'v2', 'v3'):
        print(f"  speed {v}: steps {np.mean([r[v]['steps'] for r in sub]):.0f}, fits limit {np.mean([r[v]['fits_limit'] for r in sub]):.0%}, "
              f"discounted return {np.mean([r[v]['return'] for r in sub]):.2f}, arrival weight {np.mean([r[v]['arrival_weight'] for r in sub]):.4f}, "
              f"discounted +20 bonus {np.mean([r[v]['arrival_bonus_discounted'] for r in sub]):.3f}")
    print(f"  hover return {np.mean([r['hover_return'] for r in sub]):.2f}, with timeout penalty {np.mean([r['hover_with_timeout_penalty'] for r in sub]):.2f}")
json.dump(rows, open('private/reference-recovery-1-evidence/reward-audit.json', 'w'), indent=1)
