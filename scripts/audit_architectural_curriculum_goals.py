"""Audit training-goal sampling availability; no brain, policy or evaluation."""
import argparse
import json
from pathlib import Path
import numpy as np
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.architectural_training_goals import sample_training_goal


def audit(output):
    output=Path(output)
    if output.exists():raise ValueError('Never overwrite an existing availability audit')
    rows=[]
    for scene,builder in BUILDERS.items():
        for situation in range(len(builder().situations)-1):
            world=ArchitecturalWorld(scene,situation,seed=42);world.reset(seed=42)
            original=world.target.copy()
            for distance in (1.,2.,4.,8.):
                for seed in (310001,310002,310003):
                    row=dict(scene=scene,situation=situation,distance=distance,seed=seed)
                    try:
                        goal=sample_training_goal(world,distance,np.random.default_rng(seed))
                        row.update(available=True,training_goal=goal.tolist())
                    except ValueError as exc:
                        row.update(available=False,error=str(exc))
                    assert np.array_equal(world.target,original)
                    rows.append(row)
    result=dict(kind='CPU geometry sampling audit',training=False,
                full_connectome_used=False,policy_evaluation=False,
                original_tasks_unchanged=True,attempts_per_sample=256,rows=rows,
                limitation='Availability on these seeds is not universal feasibility or navigation evidence.')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    result=audit(parser.parse_args().output)
    for distance in (1.,2.,4.,8.):
        rows=[r for r in result['rows'] if r['distance']==distance]
        print(distance,'m:',sum(r['available'] for r in rows),'/',len(rows),'available samples')
