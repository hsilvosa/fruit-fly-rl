"""Bounded-memory flight records with unique runs and atomic chunk writes."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import uuid
import sys
import subprocess
from importlib.metadata import version,PackageNotFoundError
import numpy as np
from fly_rl.simulation.sensors import SENSOR_NAMES,SENSOR_VERSION,DIRECTIONS,RAY_RANGE

def serializable(value):
    if isinstance(value,np.ndarray): return value.tolist()
    if isinstance(value,np.generic): return value.item()
    raise TypeError(type(value).__name__)

def software_info():
    packages={}
    for name in ['fly-rl','numpy','torch','gymnasium','stable-baselines3','panda3d']:
        try: packages[name]=version(name)
        except PackageNotFoundError: packages[name]=None
    root=Path(__file__).resolve().parents[2]
    prefix=['git','-c',f'safe.directory={root.as_posix()}','-C',str(root)]
    revision=None;dirty=None
    try:
        result=subprocess.run(prefix+['rev-parse','HEAD'],capture_output=True,text=True,timeout=5)
        if result.returncode==0: revision=result.stdout.strip()
        result=subprocess.run(prefix+['status','--porcelain'],capture_output=True,text=True,timeout=5)
        if result.returncode==0: dirty=bool(result.stdout.strip())
    except (OSError,subprocess.TimeoutExpired): pass
    return {'python':sys.version.split()[0],'packages':packages,'source_revision':revision,'working_tree_dirty':dirty}

class FlightRecorder:
    def __init__(self,root,metadata,chunk_size=128):
        self.path=Path(root)/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+uuid.uuid4().hex[:8])
        self.path.mkdir(parents=True)
        self.chunk_size=chunk_size;self.buffer=[];self.closed=False
        self.manifest={'schema_version':2,'started_utc':datetime.now(timezone.utc).isoformat(),
            'status':'running','transition_count':0,'event_count':0,'chunks':[],
            'sensor_version':metadata.get('sensor_version',SENSOR_VERSION),'sensor_names':SENSOR_NAMES,
            'local_ray_directions':DIRECTIONS.tolist(),'ray_range':RAY_RANGE,
            'metadata':metadata,'brain_snapshots':[],'software':software_info(),
            'configuration':{'chunk_size':chunk_size,'dt':metadata.get('dt',.05),
                'sensor_version':metadata.get('sensor_version',SENSOR_VERSION),'ray_range':RAY_RANGE,
                'sensor_values':len(SENSOR_NAMES),'reservoir':metadata.get('reservoir_spec')}}
        self.events=(self.path/'events.jsonl').open('a',encoding='utf8')
        self._save_manifest()

    def _save_manifest(self):
        tmp=self.path/'manifest.tmp'
        tmp.write_text(json.dumps(self.manifest,indent=2,default=serializable),encoding='utf8')
        tmp.replace(self.path/'manifest.json')

    def event(self,kind,step,payload):
        self.events.write(json.dumps({'event':kind,'step':step,'payload':payload},default=serializable)+'\n')
        self.events.flush();self.manifest['event_count']+=1

    def transition(self,step,room_id,sensors,features,action,before,info,reward):
        after=info['transition_state']
        self.buffer.append({'step':np.int64(step),'room_id':np.int64(room_id),
            'sensors':np.asarray(sensors,dtype=np.float32).copy(),'next_sensors':info['next_sensors'].copy(),
            'brain_features':np.asarray(features,dtype=np.float32).copy(),
            'next_brain_features':info['next_brain_features'].copy(),
            'action':np.asarray(action,dtype=np.float32).copy(),'applied_action':np.clip(action,-1,1).astype(np.float32),
            'position':before['position'],'next_position':after['position'],
            'velocity':before['velocity'],'next_velocity':after['velocity'],
            'yaw':np.float32(before['yaw']),'next_yaw':np.float32(after['yaw']),
            'bank':np.float32(before.get('bank',0)),'next_bank':np.float32(after.get('bank',0)),
            'pitch':np.float32(before.get('pitch',0)),'next_pitch':np.float32(after.get('pitch',0)),
            'reward':np.float32(reward),'terminated':np.bool_(info['terminated']),
            'truncated':np.bool_(info['truncated']),'collision':np.bool_(info['collision']),
            'success':np.bool_(info['success'])})
        if len(self.buffer)>=self.chunk_size: self.flush()

    def flush(self):
        if not self.buffer: return
        number=len(self.manifest['chunks'])
        name=f'transitions-{number:06d}.npz';tmp=self.path/(name+'.tmp')
        arrays={key:np.stack([row[key] for row in self.buffer]) for key in self.buffer[0]}
        with tmp.open('wb') as f: np.savez_compressed(f,**arrays)
        target=self.path/name;tmp.replace(target)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        self.manifest['chunks'].append({'file':name,'rows':len(self.buffer),'sha256':digest})
        self.manifest['transition_count']+=len(self.buffer);self.buffer.clear();self._save_manifest()

    def brain_snapshot(self,step,state):
        name=f'brain-{step:09d}.npz';tmp=self.path/(name+'.tmp')
        with tmp.open('wb') as f: np.savez_compressed(f,activity=np.asarray(state,dtype=np.float32),step=step)
        tmp.replace(self.path/name);self.manifest['brain_snapshots'].append(name)

    def close(self,summary=None):
        if self.closed: return
        self.flush();self.events.close()
        self.manifest.update(status='failed' if summary and summary.get('status')=='failed' else 'closed',
            ended_utc=datetime.now(timezone.utc).isoformat(),summary=summary or {})
        self._save_manifest()
        self.closed=True

    def update_summary(self,summary):
        self.manifest['summary']=summary
        self._save_manifest()
