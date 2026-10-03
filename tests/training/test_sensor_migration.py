import json
import pytest
from fly_rl.training.sensor_migration import migrate_sensors
from fly_rl.training.learning import checkpoint_sensor_version
from fly_rl.simulation.sensors import SENSOR_VERSION,SENSOR_V3


def test_explicit_migration_preserves_weights_and_source_and_checks_contract(tmp_path):
    source=tmp_path/'old.zip';source.write_bytes(b'policy-and-optimizer')
    meta={'fingerprint':'graph:reservoir-v2-'+SENSOR_VERSION+'-256-seed42-leak0.5-scale0.9','timesteps':100}
    source.with_suffix('.json').write_text(json.dumps(meta))
    output=tmp_path/'new.zip';provenance=migrate_sensors(source,output)
    assert source.read_bytes()==output.read_bytes()
    assert json.loads(source.with_suffix('.json').read_text())==meta
    assert checkpoint_sensor_version(output)==SENSOR_V3
    assert provenance['from']==SENSOR_VERSION
    with pytest.raises(FileExistsError):migrate_sensors(source,output)
    wrong=json.loads(output.with_suffix('.json').read_text());wrong['sensor_version']=SENSOR_VERSION
    output.with_suffix('.json').write_text(json.dumps(wrong))
    with pytest.raises(ValueError,match='metadata/fingerprint'):checkpoint_sensor_version(output)


def test_recording_keeps_v3_sensor_provenance(tmp_path):
    from fly_rl.recordings.recording import FlightRecorder
    recorder=FlightRecorder(tmp_path,{'sensor_version':SENSOR_V3})
    assert recorder.manifest['sensor_version']==SENSOR_V3
    assert recorder.manifest['configuration']['sensor_version']==SENSOR_V3
    recorder.events.close()
