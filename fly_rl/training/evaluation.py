"""Bounded held-out episode measurements; evaluation never optimizes weights."""
import numpy as np
from fly_rl.training.learning import BrainEnv,load_model,make_policy

def evaluate(data,device,checkpoint,episodes=16,mode='obstacles',seed=10000,goal_probe=False,dynamics='legacy',allow_transfer=False,route_metrics=False,sensor_version=None,map_profile=None):
    if not 1<=episodes<=64: raise ValueError('Evaluation supports 1 to 64 episodes')
    from fly_rl.training.learning import checkpoint_sensor_version,checkpoint_history
    sensor_version=sensor_version or checkpoint_sensor_version(checkpoint)
    env=BrainEnv(data,episodes,device,seed=seed,mode=mode,dynamics=dynamics,sensor_version=sensor_version,map_profile=map_profile,**checkpoint_history(checkpoint))
    try:
        model=load_model(checkpoint,env.brain,env,allow_transfer) if checkpoint else make_policy(env)
        env.seed(seed);features=env.reset()
        if goal_probe:
            # Counterfactual same geometry, opposite endpoints, randomized heading.
            for i,w in enumerate(env.worlds):
                w.position,w.target=w.target.copy(),w.position.copy();w.yaw=float(np.random.default_rng(seed+i).uniform(-np.pi,np.pi))
                w.distance=float(np.linalg.norm(w.target-w.position))
            env.brain.reset();features=env.brain.step(np.asarray([w.observe() for w in env.worlds]))
        import time
        started=time.perf_counter()
        references=[]
        if route_metrics:
            from fly_rl.simulation.planner import reference_path
            references=[reference_path(w.room,w.obstacles,w.position,w.target,fallback=w.reference_route or None) for w in env.worlds]
        active=np.ones(episodes,dtype=bool);rows=[]
        path=np.zeros(episodes);idle=np.zeros(episodes);length=np.zeros(episodes,dtype=int)
        initial=np.array([w.distance for w in env.worlds])
        from fly_rl.simulation.map_profiles import difficulty_metrics
        metrics=[difficulty_metrics(w) for w in env.worlds] if env.map_profile else None
        limits=[w.episode_limit for w in env.worlds]
        for _ in range(max(limits)):
            before=np.array([w.position.copy() for w in env.worlds])
            actions=model.predict(features,deterministic=True)[0]
            features,rewards,dones,infos=env.step(actions)
            for i in np.flatnonzero(active):
                state=infos[i]['transition_state'];length[i]+=1
                path[i]+=np.linalg.norm(state['position']-before[i])
                idle[i]+=np.linalg.norm(state['velocity'])<.1
                if dones[i]:
                    rows.append({'seed':seed+int(i),'success':bool(infos[i]['success']),
                        'collision':bool(infos[i]['collision']),'timeout':bool(infos[i]['truncated']),
                        'steps':int(length[i]),'distance_start':float(initial[i]),
                        'distance_end':float(infos[i]['distance']),'path_length':float(path[i]),
                        'idle_fraction':float(idle[i]/length[i])})
                    if route_metrics:
                        rows[-1]['route_reference']=references[i]
                        rows[-1]['path_over_feasible_reference']=float(path[i]/references[i]['length']) if infos[i]['success'] and references[i]['length'] else None
                    rows[-1]['arrival_seconds']=float(length[i]*.05) if infos[i]['success'] else None
                    if metrics:rows[-1]['map_difficulty']=metrics[i]
                    active[i]=False
            if not active.any(): break
        if len(rows)!=episodes: raise RuntimeError('Evaluation did not finish all episodes')
        return {'checkpoint':str(checkpoint) if checkpoint else None,'mode':mode,'goal_probe':goal_probe,'dynamics':dynamics,
            'episodes':rows,'success_rate':float(np.mean([r['success'] for r in rows])),
            'collision_rate':float(np.mean([r['collision'] for r in rows])),
            'timeout_rate':float(np.mean([r['timeout'] for r in rows])),
            'mean_idle_fraction':float(np.mean([r['idle_fraction'] for r in rows])),
            'mean_distance_end':float(np.mean([r['distance_end'] for r in rows])),
            'training_invoked':False,'sensor_version':sensor_version,'seed_start':seed,'route_metrics':route_metrics,
            'map_profile':env.map_profile.to_dict() if env.map_profile else None,'elapsed_seconds':time.perf_counter()-started}
    finally: env.close()
