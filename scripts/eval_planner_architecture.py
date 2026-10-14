"""Planner reference on the architectural scenes (level C), evaluation only. Runs the explicit planner (planner-1.4-exp.3, with the full
connectome in the loop for its neural observations) on the 21 situations with the same initial headings as the learned-policy evaluation:
heading h of every situation uses seed 900000 + h, whose start pose, goal and yaw are identical in ArchitecturalWorld and in
ArchitecturalSceneWorld (checked on all 168 cases). The planner never chooses a learned policy's actions; it is a reference.
Usage: eval_planner_architecture.py <output.json> <first heading> <last heading> [seed, default 900000]   (headings 0 to 7)"""
import hashlib, json, os, sys, time
from pathlib import Path
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
import numpy as np

out, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 900000
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_env import ArchitecturalBrainEnv
from fly_rl.navigation.architectural_portal_recovery import PortalEscapeArchitecturalPolicy

sources = hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path('fly_rl/navigation').glob('*.py')))).hexdigest()
cases = [(name, index, situation.name) for name, builder in BUILDERS.items() for index, situation in enumerate(builder().situations)]
if os.environ.get('PROBE_CASES'):  # cost probe: only the first n situations of each heading
    cases = cases[:int(os.environ['PROBE_CASES'])]
env = ArchitecturalBrainEnv(cases[0][0], device='cuda', seed=seed)
assert env.brain.n == 167184 and env.brain.audit['edges'] == 25583622
rows, began = [], time.monotonic()
for heading in range(first, last + 1):
    for scene, index, name in cases:
        features = env.select_situation(scene, index, seed + heading)
        world = env.worlds[0]
        policy = PortalEscapeArchitecturalPolicy(world.room)
        row = dict(scene=scene, situation=index, name=name, heading=heading, seed=seed + heading, episode_limit=world.episode_limit,
                   steps=0, success=False, collision=False, timeout=False, distance_end=float(world.distance))
        for step in range(world.episode_limit):
            action, _ = policy.predict(features)
            features, rewards, dones, infos = env.step(action)
            info = infos[0]
            row.update(steps=step + 1, distance_end=float(info['distance']))
            if dones[0]:
                row.update(success=bool(info['success']), collision=bool(info['collision']), timeout=bool(info['truncated']))
                break
        rows.append(row)
        total = {k: sum(r[k] for r in rows) for k in ('success', 'collision', 'timeout')}
        json.dump(dict(controller='planner-1.4-exp.3', navigation_sources_sha256=sources, seed=seed, headings=[first, last],
                       episodes=len(rows), total=total, elapsed_seconds=round(time.monotonic() - began), cases=rows), open(out, 'w'), indent=1)
        print(scene, index, 'heading', heading, 'success' if row['success'] else 'collision' if row['collision'] else 'timeout' if row['timeout'] else 'incomplete', row['steps'], flush=True)
env.close()
print('TOTAL', total, 'seconds', round(time.monotonic() - began), flush=True)
