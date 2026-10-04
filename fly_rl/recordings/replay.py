"""Replay numerical records directly; no connectome or model is evaluated."""
import bisect
from types import SimpleNamespace
import numpy as np
import torch
from fly_rl.recordings.archive import Archive,room_fingerprint
from fly_rl.simulation.world import FlightWorld

class ReplayEnv:
    def __init__(self,path):
        self.archive=Archive(path);self.inspection=self.archive.inspect()
        if self.inspection['errors']: raise ValueError('Archive failed integrity checks: '+str(self.inspection['errors']))
        self.chunks=self.inspection['valid_chunks']
        self.ends=np.cumsum([c['rows'] for c in self.chunks]).tolist()
        self.total=self.ends[-1] if self.ends else 0
        if not self.total: raise ValueError('No saved transitions to replay')
        self.worlds=[FlightWorld(0,sensor_version=self.archive.manifest.get("sensor_version"))];self.cursor=0;self.finished=False;self.cache_index=None;self.cache=None
        audit=self.archive.manifest.get('metadata',{}).get('dataset',{})
        self.brain=SimpleNamespace(n=audit.get('annotated_neurons',0),audit={'edges':audit.get('edges',0)},
            state=torch.zeros((256,1)))
        self.current_room_id=None;self.steps=0
        self.episode_starts=[]
        previous_room=None;offset=0
        for chunk in self.chunks:
            a=self.archive.load_chunk(chunk['file'])
            for j,rid in enumerate(a['room_id']):
                if int(rid)!=previous_room: self.episode_starts.append(offset+j);previous_room=int(rid)
            offset+=len(a['step'])
        self.reset()

    def row(self,index=None):
        index=self.cursor if index is None else index
        if not 0<=index<self.total: raise IndexError('Replay frame out of range')
        ci=bisect.bisect_right(self.ends,index)
        if ci!=self.cache_index:
            self.cache=self.archive.load_chunk(self.chunks[ci]['file']);self.cache_index=ci
        local=index-(self.ends[ci-1] if ci else 0)
        return {k:v[local] for k,v in self.cache.items()}

    def apply(self,row,after=False):
        rid=int(row['room_id']);layout=self.archive.rooms[rid];world=self.worlds[0]
        world.room=np.asarray(layout.get('size',[12.,12.,6.]),dtype=float)
        from fly_rl.simulation.map_profiles import resolve_profile
        world.map_profile=resolve_profile(layout['initial_state'].get('map_profile'))
        world.episode_limit=layout['initial_state'].get('episode_limit',600)
        world.mode=layout['initial_state'].get('mode','obstacles')
        world.dynamics=layout['initial_state'].get('dynamics','legacy')
        world.obstacles=[(np.asarray(b[0]),np.asarray(b[1])) for b in layout['initial_state']['obstacles']]
        world.target=np.asarray(layout['initial_state']['target'],dtype=float)
        prefix='next_' if after else ''
        world.position=row[prefix+'position'].copy();world.velocity=row[prefix+'velocity'].copy()
        world.yaw=float(row[prefix+'yaw']);world.last_action=row['applied_action'].copy()
        world.bank=float(row.get(prefix+'bank',0));world.pitch=float(row.get(prefix+'pitch',0))
        world.distance=float(np.linalg.norm(world.target-world.position))
        world.ticks=int(row['step']);self.current_room_id=rid
        features=row['next_brain_features' if after else 'brain_features'].copy()
        self.sensor_state=row['next_sensors' if after else 'sensors'].copy()
        self.brain.state=torch.from_numpy(features[:,None])
        return features[None,:]

    def seed(self,seed): pass
    def reset(self): return self.seek(0)
    def seek(self,index):
        self.cursor=int(np.clip(index,0,self.total-1));self.finished=False
        return self.apply(self.row())
    def next_episode(self):
        next_start=next((x for x in self.episode_starts if x>self.cursor),0)
        return self.seek(next_start)
    def step(self,ignored_action):
        row=self.row();features=self.apply(row,after=True)
        self.steps=int(row['step']);self.cursor+=1;self.finished=self.cursor>=self.total
        info={k:bool(row[k]) for k in ['collision','success','terminated','truncated']}
        info.update(distance=self.worlds[0].distance,recorded_step=self.steps,
            recorded_action=row['applied_action'].tolist(),nearest_obstacle=float(np.min(row['next_sensors'][:128]))*8.)
        return features,np.asarray([row['reward']],dtype=np.float32),np.asarray([info['terminated'] or info['truncated']]),[info]
    def close(self): pass

class RecordedPolicy:
    def __init__(self,env): self.env=env
    def predict(self,features,deterministic=True): return self.env.row()['action'][None,:],None

def matching_trajectory(archive_path,layout):
    archive=Archive(archive_path);inspection=archive.inspect()
    if inspection['errors']: raise ValueError('Comparison archive failed integrity checks')
    room_ids={rid for rid,payload in archive.rooms.items() if room_fingerprint(payload)==layout}
    points=[]
    # Show a single matching episode, never join separate flights into one line.
    selected=None
    for chunk in inspection['valid_chunks']:
        arrays=archive.load_chunk(chunk['file'])
        for i,rid in enumerate(arrays['room_id']):
            rid=int(rid)
            if selected is None and rid in room_ids: selected=rid
            if rid==selected:
                if not points: points.append(arrays['position'][i].copy())
                points.append(arrays['next_position'][i].copy())
    return points
