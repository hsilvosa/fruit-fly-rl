"""Bounded validation-only replay diagnostics; never optimize or access final outcomes."""
import json,time
from pathlib import Path
import numpy as np
from fly_rl.training.generalization import sha256
from fly_rl.training.suites import load_suite
from fly_rl.simulation.world import RADIUS,DT,segment_box


def contact_geometry(start,velocity,room,obstacles):
    attempted=np.asarray(start)+np.asarray(velocity)*DT
    axes=np.flatnonzero((attempted<RADIUS)|(attempted>np.asarray(room)-RADIUS)).tolist()
    hits=[i for i,(low,high) in enumerate(obstacles) if segment_box(np.asarray(start),attempted,np.asarray(low)-RADIUS,np.asarray(high)+RADIUS)]
    return {'attempted_position':attempted.tolist(),'wall_axes':axes,'obstacle_indices':hits,
            'kind':'wall_and_obstacle' if axes and hits else 'wall' if axes else 'obstacle' if hits else 'none'}


def clearance(position,room,obstacles):
    """Signed distance to room boundaries or radius-inflated collision boxes."""
    p=np.asarray(position);distance=float(np.min(np.minimum(p-RADIUS,np.asarray(room)-RADIUS-p)))
    for low,high in obstacles:
        low=np.asarray(low)-RADIUS;high=np.asarray(high)+RADIUS
        outside=np.maximum(np.maximum(low-p,p-high),0)
        value=float(np.linalg.norm(outside)) if outside.any() else -float(np.min(np.minimum(p-low,high-p)))
        distance=min(distance,value)
    return distance


def validation_cases(experiment,count,case_kind="failure"):
    if case_kind not in ['failure','collision','timeout']:raise ValueError('Invalid validation case kind')
    if type(count) is not int or not 1<=count<=4:raise ValueError('Trace 1 to 4 validation failures')
    folder=Path(experiment);state=json.loads((folder/'experiment.json').read_text(encoding='utf-8'))
    if state.get('status')!='completed' or 'final_summary' in state or 'selected_summary' in state or state.get('split')=='test':raise ValueError('Use a completed individual validation experiment')
    frozen=json.loads((folder/'selection.json').read_text(encoding='utf-8'))
    if frozen.get('selection_split','validation')!='validation' or frozen.get('validation',{}).get('split')=='test':raise ValueError('Validation selection required')
    for path,expected in [(frozen['checkpoint'],frozen['checkpoint_sha256']),(str(Path(frozen['checkpoint']).with_suffix('.json')),frozen['metadata_sha256']),(frozen['suite'],frozen['suite_sha256'])]:
        if sha256(path)!=expected:raise ValueError('Frozen validation integrity mismatch')
    suite=load_suite(frozen['suite']);rows=frozen['validation']['episodes']
    if sorted(r['seed'] for r in rows)!=sorted(suite['splits']['validation']['seeds']):raise ValueError('Validation seed provenance mismatch')
    if set(suite['splits']['validation']['seeds']) & set(suite['splits']['test']['seeds']):raise ValueError('Validation/test overlap')
    # Alternate collision and timeout examples; choose deterministically without consulting test outcomes.
    buckets=[[r for r in sorted(rows,key=lambda r:r['seed']) if not r['success'] and r.get(kind)] for kind in (['collision','timeout'] if case_kind=='failure' else [case_kind])]
    chosen=[]
    while len(chosen)<count and any(buckets):
        for bucket in buckets:
            if bucket and len(chosen)<count:chosen.append(bucket.pop(0))
    if not chosen:raise ValueError('No retained validation failures')
    return frozen,chosen


def trace_validation(data,device,experiment,output,count=2,max_steps=1200,case_kind="failure"):
    if type(max_steps) is not int or not 1<=max_steps<=1200:raise ValueError('Trace budget must be 1 to 1200 decisions')
    frozen,cases=validation_cases(experiment,count,case_kind)
    from fly_rl.training.learning import BrainEnv,load_model,checkpoint_sensor_version
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    checkpoint=frozen['checkpoint'];original=sha256(checkpoint);metadata_hash=sha256(Path(checkpoint).with_suffix('.json'))
    suite=load_suite(frozen['suite'])
    env=BrainEnv(data,len(cases),device,seed=cases[0]['seed'],mode=frozen['mode'],dynamics=frozen['dynamics'],sensor_version=checkpoint_sensor_version(checkpoint),map_profile=suite.get('map_profile'))
    started=time.perf_counter()
    try:
        model=load_model(checkpoint,env.brain,env);initial_steps=model.num_timesteps;initial_updates=model._n_updates
        # Individual reset seeds need not be contiguous. Keep the real full graph and independent batch states.
        for w,row in zip(env.worlds,cases):w.reset(seed=row['seed'])
        env.brain.reset();features=env.brain.step(np.asarray([w.observe() for w in env.worlds]))
        layouts=[w.snapshot() for w in env.worlds];active=np.ones(len(cases),dtype=bool);records=[[] for _ in cases];outcomes=[None for _ in cases]
        output.mkdir(parents=True,exist_ok=False)
        for tick in range(max_steps):
            before=[w.snapshot() for w in env.worlds];sensors=np.asarray([w.observe() for w in env.worlds]);prior=features.copy()
            actions=model.predict(features,deterministic=True)[0];features,rewards,dones,infos=env.step(actions)
            for i in np.flatnonzero(active):
                after=infos[i]['transition_state'];layout=layouts[i]
                records[i].append({'velocity_before':before[i]['velocity'],'yaw_before':before[i]['yaw'],'position_before':before[i]['position'],'position_after':after['position'],'velocity_after':after['velocity'],
                    'features_before':prior[i],'sensors_before':sensors[i],'action':actions[i],'reward':rewards[i],
                    'yaw_after':after['yaw'],'yaw_rate_after':after['yaw_rate'],'bank_after':after['bank'],'pitch_after':after['pitch'],
                    'target_distance_after':infos[i]['distance'],'clearance_after':clearance(after['position'],layout['room_size'],layout['obstacles'])})
                if dones[i]:
                    outcomes[i]={key:bool(infos[i][key]) for key in ['success','collision','truncated']}
                    outcomes[i]['contact']=contact_geometry(before[i]['position'],after['velocity'],layout['room_size'],layout['obstacles']) if infos[i]['collision'] else None
                    active[i]=False
            if not active.any():break
        summaries=[]
        for i,(row,layout,trace) in enumerate(zip(cases,layouts,records)):
            arrays={key:np.asarray([step[key] for step in trace]) for key in trace[0]};arrays.update(room=layout['room_size'],obstacles=layout['obstacles'],target=layout['target'])
            path=output/f"seed-{row['seed']}.npz";np.savez_compressed(path,**arrays)
            outcome=outcomes[i];matched=outcome is not None and (outcome['success'],outcome['collision'],outcome['truncated'])==(row['success'],row['collision'],row['timeout'])
            summaries.append({'seed':row['seed'],'decisions':len(trace),'status':'completed' if outcome else 'budget-truncated',
                'outcome':outcome,'retained_outcome':{k:row[k] for k in ['success','collision','timeout','steps','distance_end']},
                'outcome_matches_retained':matched,'ending_distance_difference':float(arrays['target_distance_after'][-1]-row['distance_end']),
                'trace':str(path.resolve()),'sha256':sha256(path),'min_altitude':float(arrays['position_after'][:,2].min()),
                'max_altitude':float(arrays['position_after'][:,2].max()),'idle_fraction':float(np.mean(np.linalg.norm(arrays['velocity_after'],axis=1)<.1))})
        if model.num_timesteps!=initial_steps or model._n_updates!=initial_updates:raise RuntimeError('Diagnostic must not optimize')
        if sha256(checkpoint)!=original or sha256(Path(checkpoint).with_suffix('.json'))!=metadata_hash:raise RuntimeError('Checkpoint changed')
        result={'status':'completed','split':'validation','trace_version':2,'case_kind':case_kind,'experiment':str(Path(experiment).resolve()),'checkpoint_sha256':original,'metadata_sha256':metadata_hash,
            'suite_sha256':frozen['suite_sha256'],'sensor_version':env.brain.sensor_version,'full_neurons':env.brain.n,
            'map_profile':suite.get('map_profile'),
            'cases':summaries,'batch_decisions':tick+1,'environment_transitions':(tick+1)*len(cases),'recorded_transitions':sum(len(t) for t in records),
            'maximum_environment_transitions':max_steps*len(cases),'training_invoked':False,'optimizer_updates_added':0,'test_evaluated':False,
            'phase':'features and sensors before action; state after action before automatic reset',
            'clearance_definition':'Signed Euclidean distance to radius-inflated axis-aligned collision boxes; room-boundary margin. Diagnostic only, not a policy input.',
            'limits':'Selected failure examples, not success-rate evidence. Contacts reconstructed from the actual swept attempted move. Outcome agreement does not imply bitwise trajectory identity. Inactive batch slots may advance unrecorded reset episodes.',
            'elapsed_seconds':time.perf_counter()-started}
        (output/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result
    finally:env.close()
