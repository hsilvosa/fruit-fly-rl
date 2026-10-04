"""Explicit warm-start copy between known sensor contracts; weights are untouched."""
import json,shutil
from pathlib import Path
from fly_rl.simulation.sensors import SENSOR_VERSION,SENSOR_V3,SENSOR_V4,SENSOR_V5
from fly_rl.training.learning import checkpoint_sensor_version
from fly_rl.training.generalization import sha256

def migrate_sensors(source,output,target=SENSOR_V3):
    source,output=Path(source),Path(output)
    original=checkpoint_sensor_version(source)
    if (original,target) not in [(SENSOR_VERSION,SENSOR_V3),(SENSOR_V3,SENSOR_V4),(SENSOR_V3,SENSOR_V5)]:
        raise ValueError('Migration requires v2 to v3, or v3 to v4/v5')
    metadata=json.loads(source.with_suffix('.json').read_text())
    if output.exists() or output.with_suffix('.json').exists(): raise FileExistsError('Output already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    metadata['sensor_version']=target
    metadata['fingerprint']=metadata['fingerprint'].replace(original,target)
    metadata['sensor_migration']={'source':str(source.resolve()),'weights_sha256':sha256(source),
        'source_metadata_sha256':sha256(source.with_suffix('.json')),'from':original,'to':target,
        'note':'Explicit semantic transfer. Same policy and optimizer bytes; new observations require evaluation.'}
    shutil.copy2(source,output)
    output.with_suffix('.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    assert sha256(source)==sha256(output)
    return metadata['sensor_migration']
