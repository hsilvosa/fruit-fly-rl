"""Analyze saved validation collision traces; no policy execution or training."""
import json
from pathlib import Path
import numpy as np
from fly_rl.training.generalization import sha256
from fly_rl.simulation.world import RADIUS,DT,ray_box
from fly_rl.simulation.sensors import DIRECTIONS,RAY_RANGE


def ray_risk(sensors,horizon=.75):
    """Heuristic risk from observed rays only; not a certified collision predictor."""
    if not np.isfinite(horizon) or horizon<=0:raise ValueError('Positive finite risk horizon required')
    values=np.asarray(sensors,dtype=float)
    if values.ndim<1 or values.shape[-1]!=269 or not np.isfinite(values).all():raise ValueError('Finite 269-value sensors required')
    distances=values[..., :128]*RAY_RANGE;closing=values[...,128:256]*3.
    visible=(distances<RAY_RANGE-1e-5)&(closing>.1)
    ttc=np.divide(np.maximum(distances-RADIUS,0),closing,out=np.full_like(distances,np.inf),where=visible)
    return np.maximum(0,1-ttc/horizon).max(axis=-1)


def motion_ttc(position,velocity,room,obstacles):
    speed=float(np.linalg.norm(velocity))
    if speed<1e-6:return None
    direction=np.asarray(velocity)/speed;p=np.asarray(position);room=np.asarray(room)
    distance=min(((room[i]-RADIUS if direction[i]>0 else RADIUS)-p[i])/direction[i] for i in range(3) if abs(direction[i])>1e-12)
    for low,high in obstacles:distance=min(distance,ray_box(p,direction,np.asarray(low)-RADIUS,np.asarray(high)+RADIUS))
    return float(max(0,distance)/speed)


def object_visibility(position,yaw,sensors,obstacles,indices):
    c=np.cos(yaw);s=np.sin(yaw);rotation=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
    directions=DIRECTIONS@rotation.T;observed=np.asarray(sensors[:128])*RAY_RANGE
    visible=0
    for d,r in zip(directions,observed):
        if any((lambda hit:hit<RAY_RANGE and abs(hit-r)<2e-4)(ray_box(position,d,*obstacles[index])) for index in indices):visible+=1
    return visible


def diagnose_collisions(source,output):
    source=Path(source);report=json.loads(source.read_text(encoding='utf-8'))
    if report.get('split')!='validation' or report.get('test_evaluated') or report.get('trace_version',1)<2:raise ValueError('Version 2 validation traces required')
    results=[]
    for case in report['cases']:
        if not case.get('outcome',{}).get('collision'):continue
        if sha256(case['trace'])!=case['sha256']:raise ValueError('Trace integrity mismatch')
        with np.load(case['trace'],allow_pickle=False) as t:
            risk=ray_risk(t['sensors_before']);speeds=np.linalg.norm(t['velocity_before'],axis=1)
            contacts=case['outcome']['contact'];indices=contacts['obstacle_indices'];window=min(20,len(risk));start=len(risk)-window
            visibility=[object_visibility(t['position_before'][i],t['yaw_before'][i],t['sensors_before'][i],t['obstacles'],indices) for i in range(start,len(risk))] if indices else []
            ttcs=[motion_ttc(t['position_before'][i],t['velocity_before'][i],t['room'],t['obstacles']) for i in range(start,len(risk))]
            results.append({'seed':case['seed'],'contact':contacts,'retained_outcome_matches':case['outcome_matches_retained'],'decisions':case['decisions'],
                'preimpact_window_decisions':window,'preimpact_window_seconds':window*DT,
                'speed_at_last_decision':float(speeds[-1]),'mean_preimpact_speed':float(speeds[-window:].mean()),
                'min_preimpact_observed_range':float(t['sensors_before'][-window:,:128].min()*RAY_RANGE),
                'positive_thrust_fraction':float(np.mean(t['action'][-window:,0]>0)),'mean_forward_action':float(t['action'][-window:,0].mean()),
                'mean_absolute_turn_action':float(np.abs(t['action'][-window:,3]).mean()),
                'risk_active_decisions':int(np.count_nonzero(risk[-window:]>0)),'mean_preimpact_ray_risk':float(risk[-window:].mean()),
                'colliding_object_visible_decisions':sum(v>0 for v in visibility),'visible_ray_counts':visibility,
                'constant_velocity_ttc_seconds':ttcs,'ray_risk_history':risk.tolist(),
                'trace':case['trace'],'trace_sha256':case['sha256']})
    if not results:raise ValueError('No collision cases')
    result={'split':'validation','source':str(source.resolve()),'source_sha256':sha256(source),'checkpoint_sha256':report['checkpoint_sha256'],
        'cases':results,'training_invoked':False,'evaluation_invoked':False,'test_evaluated':False,
        'limits':'Selected validation cases. Geometric ray visibility does not prove neural recognition. Constant-velocity TTC ignores future steering. Ray risk uses visible distances and projected approach speed, subtracting a scalar body radius; it is approximate, not swept-box clearance.'}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2),encoding='utf-8');return result
