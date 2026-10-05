"""Promote the strongest measured obstacle-room checkpoint, preserving sources."""
from fly_rl.atomic_io import replace_file
import json
import shutil
from pathlib import Path

def select_policy(iteration_path,output):
    source=Path(iteration_path);state=json.loads(source.read_text())
    results=state.get('results',[])
    if not results: raise ValueError('No evaluated checkpoints are available')
    best=max(results,key=lambda r:(r['obstacles']['success_rate'],
        -r['obstacles']['collision_rate'],-r['obstacles']['mean_distance_end']))
    if best['obstacles']['success_rate']<=0: raise ValueError('No checkpoint has reached a target')
    checkpoint=Path(best['checkpoint']).resolve();output=Path(output).resolve()
    if checkpoint==output: raise ValueError('Promotion must preserve the source checkpoint')
    metadata=json.loads(checkpoint.with_suffix('.json').read_text())
    metadata['selection']={'iteration':str(source.resolve()),'checkpoint':str(checkpoint),
        'development_evaluation':best['obstacles'],'criterion':'success, then collisions, then remaining distance'}
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=output.with_suffix('.zip.tmp');shutil.copy2(checkpoint,tmp);replace_file(tmp, output)
    tmp=output.with_suffix('.json.tmp');tmp.write_text(json.dumps(metadata,indent=2));replace_file(tmp, output.with_suffix('.json'))
    return {'output':str(output),'source':str(checkpoint),'success_rate':best['obstacles']['success_rate'],
            'selection_uses_development_rooms':True,'training_invoked':False}
