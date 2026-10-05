"""Inspect and conservatively index saved flights without loading a policy."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import shutil
import numpy as np

REQUIRED=['step','room_id','sensors','next_sensors','brain_features','next_brain_features',
          'action','applied_action','position','next_position','velocity','next_velocity',
          'yaw','next_yaw','reward','terminated','truncated','collision','success']

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def room_fingerprint(payload):
    state=payload['initial_state']
    return hashlib.sha256(json.dumps({'size':payload.get('size',[12,12,6]),
        'target':state['target'],'obstacles':state['obstacles']},sort_keys=True).encode()).hexdigest()

class Archive:
    def __init__(self,path):
        self.path=Path(path).resolve()
        self.manifest=json.loads((self.path/'manifest.json').read_text())
        self.events=[];self.event_errors=[];self.rooms={}
        for line_number,line in enumerate((self.path/'events.jsonl').read_text().splitlines(),1):
            try:
                event=json.loads(line)
                if event['event']=='room':
                    payload=event['payload'];room_fingerprint(payload)
                    self.rooms[int(payload['room_id'])]=payload
                self.events.append(event)
            except (ValueError,KeyError,TypeError) as exc:
                self.event_errors.append(f'events.jsonl line {line_number}: {exc}')

    def load_chunk(self,name):
        if Path(name).name!=name: raise ValueError('Archive filenames must be local basenames')
        with np.load(self.path/name,allow_pickle=False) as source:
            arrays={key:source[key] for key in source.files}
        missing=set(REQUIRED)-set(arrays)
        if missing: raise ValueError('Missing fields: '+str(sorted(missing)))
        rows=len(arrays['step']);sensor_count=len(self.manifest['sensor_names'])
        for key in REQUIRED:
            if len(arrays[key])!=rows or not np.isfinite(arrays[key]).all():
                raise ValueError('Invalid rows or nonfinite values: '+key)
        for key in ['position','next_position','velocity','next_velocity']:
            if arrays[key].shape!=(rows,3): raise ValueError('Invalid vector: '+key)
        for key in ['action','applied_action']:
            if arrays[key].shape!=(rows,4): raise ValueError('Invalid action: '+key)
        for key in ['sensors','next_sensors']:
            if arrays[key].shape!=(rows,sensor_count): raise ValueError('Sensor schema mismatch')
        for key in ['brain_features','next_brain_features']:
            if arrays[key].shape!=(rows,self.manifest.get('metadata',{}).get('brain_feature_count',256)): raise ValueError('Feature schema mismatch')
        if arrays['step'].shape!=(rows,) or not np.issubdtype(arrays['step'].dtype,np.integer):
            raise ValueError('Steps must be integer scalars')
        return arrays

    def inspect(self):
        errors=list(self.event_errors);warnings=[];valid=[];episodes={};previous=0;total=0
        controller=self.manifest.get('metadata',{}).get('controller',{})
        if controller.get('kind')=='explicit_geometry_planner':
            try:
                archived=json.loads((self.path/'controller.json').read_text(encoding='utf-8'))
                if archived!=controller: raise ValueError('Controller specification differs from manifest')
                if digest(self.path/'controller.py')!=controller['source_sha256']:
                    raise ValueError('Primary controller checksum mismatch')
                for source in controller.get('sources',[]):
                    name=source['archive_file']
                    if Path(name).name!=name: raise ValueError('Invalid controller source filename')
                    if digest(self.path/name)!=source['sha256']:
                        raise ValueError(f'Controller dependency checksum mismatch: {name}')
            except (OSError,ValueError,KeyError,TypeError) as exc:
                errors.append(f'Controller sources: {exc}')
        indexed={c['file']:c for c in self.manifest['chunks']}
        candidates=sorted(set(indexed)|{p.name for p in self.path.glob('transitions-*.npz')})
        dt=float(self.manifest.get('metadata',{}).get('dt',.05))
        for name in candidates:
            try:
                if Path(name).name!=name: raise ValueError('Invalid archive filename')
                if name in self.manifest.get('invalid_files',{}):
                    raise ValueError('Excluded by recovery; original integrity failure remains unresolved')
                checksum=digest(self.path/name)
                if name in indexed and checksum!=indexed[name]['sha256']:
                    raise ValueError('Checksum mismatch')
                arrays=self.load_chunk(name);rows=len(arrays['step'])
                if name in indexed and rows!=indexed[name]['rows']: raise ValueError('Row count mismatch')
                if rows and (arrays['step'][0]<=previous or np.any(np.diff(arrays['step'])!=1)):
                    raise ValueError('Overlapping, unordered, or discontinuous steps')
                if rows and arrays['step'][0]!=previous+1:
                    warnings.append(f'{name}: gap before step {int(arrays["step"][0])}')
                for i in range(rows):
                    rid=int(arrays['room_id'][i])
                    if rid not in self.rooms: raise ValueError(f'No room layout for room {rid}')
                # Only accumulate a chunk after validating all of its references.
                for i in range(rows):
                    rid=int(arrays['room_id'][i])
                    e=episodes.setdefault(rid,{'room_id':rid,'layout':room_fingerprint(self.rooms[rid]),
                        'steps':0,'reward':0.,'path_length':0.,'collision':False,'success':False,'truncated':False,'complete':False})
                    e['steps']+=1;e['reward']+=float(arrays['reward'][i])
                    e['path_length']+=float(np.linalg.norm(arrays['next_position'][i]-arrays['position'][i]))
                    for key in ['collision','success','truncated']: e[key] |= bool(arrays[key][i])
                    e['complete'] |= bool(arrays['terminated'][i] or arrays['truncated'][i])
                valid.append({'file':name,'rows':rows,'sha256':checksum})
                total+=rows
                if rows: previous=int(arrays['step'][-1])
                if name not in indexed: warnings.append(name+': complete file absent from manifest')
            except (OSError,ValueError,KeyError,EOFError) as exc: errors.append(f'{name}: {exc}')
        snapshots=[]
        expected=self.manifest.get('metadata',{}).get('dataset',{}).get('annotated_neurons')
        for path in sorted(self.path.glob('brain-*.npz')):
            try:
                with np.load(path,allow_pickle=False) as a:
                    if a['activity'].ndim!=1 or not np.isfinite(a['activity']).all(): raise ValueError('Invalid activity')
                    if expected is not None and len(a['activity'])!=expected: raise ValueError('Neuron count mismatch')
                    snapshots.append({'file':path.name,'step':int(a['step']),'neurons':len(a['activity'])})
            except (OSError,ValueError,KeyError,EOFError) as exc: errors.append(f'{path.name}: {exc}')
        if total!=self.manifest['transition_count']: warnings.append('Manifest transition count differs from valid files')
        if len(self.events)!=self.manifest.get('event_count'): warnings.append('Manifest event count differs from readable events')
        if self.manifest['status'] in ['running','interrupted']: warnings.append('Session did not finish normally; an unwritten tail may be missing')
        for e in episodes.values(): e['duration_seconds']=e['steps']*dt
        return {'run':str(self.path),'status':self.manifest['status'],'valid_transitions':total,
            'last_saved_step':previous,'valid_events':len(self.events),'valid_chunks':valid,
            'valid_snapshots':snapshots,'episodes':list(episodes.values()),
            'completed_episodes':sum(e['complete'] for e in episodes.values()),
            'collisions':sum(e['collision'] for e in episodes.values()),
            'successes':sum(e['success'] for e in episodes.values()),
            'total_reward':sum(e['reward'] for e in episodes.values()),
            'errors':errors,'warnings':warnings,'integrity_ok':not errors}

def recover(path,apply=False):
    archive=Archive(path);report=archive.inspect()
    result={'inspection':report,'applied':False,'recoverable_chunks':len(report['valid_chunks']),
            'unwritten_tail_recoverable':False,'note':'Recovery indexes valid files. It never recreates missing decisions or deletes files.'}
    if apply:
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        backup=archive.path/f'manifest.before-recovery-{stamp}.json'
        shutil.copy2(archive.path/'manifest.json',backup)
        manifest=archive.manifest
        original_index={c['file']:c for c in manifest['chunks']}
        valid_names={c['file'] for c in report['valid_chunks']}
        candidate_names=set(original_index)|{p.name for p in archive.path.glob('transitions-*.npz')}
        manifest['invalid_files']={name:original_index.get(name,{}) for name in candidate_names-valid_names}
        manifest.update(chunks=report['valid_chunks'],transition_count=report['valid_transitions'],
            event_count=report['valid_events'],brain_snapshots=[s['file'] for s in report['valid_snapshots']])
        if manifest['status']=='running' or report['errors'] or report['warnings']: manifest['status']='interrupted'
        manifest['recovery']={'time_utc':datetime.now(timezone.utc).isoformat(),'backup':backup.name,
                              'errors':report['errors'],'warnings':report['warnings'],'unwritten_tail_recoverable':False}
        tmp=archive.path/'manifest.recovery.tmp';tmp.write_text(json.dumps(manifest,indent=2),encoding='utf8')
        tmp.replace(archive.path/'manifest.json');result['applied']=True;result['backup']=str(backup)
    return result

def compare(left,right):
    a=Archive(left).inspect();b=Archive(right).inspect()
    if a['errors'] or b['errors']: raise ValueError('Cannot compare corrupt archives; inspect them first')
    shared=sorted({e['layout'] for e in a['episodes']} & {e['layout'] for e in b['episodes']})
    return {'left':str(Path(left)),'right':str(Path(right)),'shared_layouts':len(shared),
        'comparisons':[{'layout':layout,'left':[e for e in a['episodes'] if e['layout']==layout],
                       'right':[e for e in b['episodes'] if e['layout']==layout]} for layout in shared],
        'note':'Only identical obstacle and target layouts are compared. No learned improvement is inferred.'}
