import json
import numpy as np
import pytest
from fly_rl.simulation.world import FlightWorld
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.recordings.archive import Archive,recover,compare
from fly_rl.recordings.replay import ReplayEnv,matching_trajectory

def make_archive(root,seed=10,steps=5):
    w=FlightWorld(seed);recorder=FlightRecorder(root,{'dt':.05,'dataset':{'annotated_neurons':8,'edges':8}},chunk_size=3)
    recorder.event('room',0,{'room_id':0,'seed':seed,'size':[12.,12.,6.],'initial_state':w.snapshot()})
    before_states=[];after_states=[]
    for i in range(steps):
        before=w.snapshot();sensors=w.observe();action=np.array([.5,.1,0.,.1],dtype=np.float32)
        next_sensors,reward,terminated,truncated,info=w.step(action)
        info.update(next_sensors=next_sensors,next_brain_features=np.full(256,i+1,dtype=np.float32))
        recorder.transition(i+1,0,sensors,np.full(256,i,dtype=np.float32),action,before,info,reward)
        before_states.append(before['position']);after_states.append(w.position.copy())
    recorder.close();return recorder.path,before_states,after_states

def test_inspect_and_replay_are_exact_and_read_only(tmp_path):
    path,before,after=make_archive(tmp_path)
    original=(path/'manifest.json').read_bytes()
    report=Archive(path).inspect()
    assert report['integrity_ok'] and report['valid_transitions']==5 and len(report['valid_chunks'])==2
    env=ReplayEnv(path)
    assert np.array_equal(env.worlds[0].position,before[0])
    for position in after:
        env.step(None);assert np.array_equal(env.worlds[0].position,position)
    assert env.finished
    env.reset();assert env.cursor==0
    env.seek(4);assert np.array_equal(env.worlds[0].position,before[4])
    assert (path/'manifest.json').read_bytes()==original
    assert len(matching_trajectory(path,report['episodes'][0]['layout']))==6

def test_checksum_corruption_cannot_be_silently_recovered(tmp_path):
    path,_,_=make_archive(tmp_path)
    chunk=path/'transitions-000000.npz'
    with np.load(chunk,allow_pickle=False) as data: arrays={k:data[k] for k in data.files}
    arrays['reward'][0]+=1
    with chunk.open('wb') as f: np.savez_compressed(f,**arrays)
    report=Archive(path).inspect();assert not report['integrity_ok']
    with pytest.raises(ValueError): ReplayEnv(path)
    recover(path,apply=True)
    assert not Archive(path).inspect()['integrity_ok']
    assert list(path.glob('manifest.before-recovery-*.json'))

def test_recovery_dry_run_then_indexes_unlisted_complete_chunk(tmp_path):
    path,_,_=make_archive(tmp_path)
    manifest=json.loads((path/'manifest.json').read_text())
    manifest['chunks']=manifest['chunks'][:1];manifest['transition_count']=3;manifest['status']='running'
    (path/'manifest.json').write_text(json.dumps(manifest))
    original=(path/'manifest.json').read_bytes()
    report=recover(path);assert not report['applied'] and report['inspection']['valid_transitions']==5
    assert original==(path/'manifest.json').read_bytes()
    recover(path,True)
    manifest=json.loads((path/'manifest.json').read_text())
    assert manifest['transition_count']==5 and manifest['status']=='interrupted'

def test_compare_matches_actual_geometry_not_seeds(tmp_path):
    a,_,_=make_archive(tmp_path,10);b,_,_=make_archive(tmp_path,10);c,_,_=make_archive(tmp_path,11)
    assert compare(a,b)['shared_layouts']==1
    assert compare(a,c)['shared_layouts']==0

def test_partial_event_is_reported_and_software_is_recorded(tmp_path):
    path,_,_=make_archive(tmp_path)
    manifest=json.loads((path/'manifest.json').read_text())
    assert manifest['software']['python'] and 'numpy' in manifest['software']['packages']
    with (path/'events.jsonl').open('a') as f: f.write('{incomplete')
    assert Archive(path).inspect()['errors']
