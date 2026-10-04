"""One bounded dense-room experiment; the final-test split stays unused."""
import json
import shutil
from pathlib import Path
from datetime import datetime,timezone
from fly_rl.training.suites import load_suite
from fly_rl.training.learning import train
from fly_rl.simulation.sensors import SENSOR_VERSION
from fly_rl.training.evaluation import evaluate
from fly_rl.recordings.recording import software_info
from fly_rl.training.generalization import sha256

def train_dense(data,device,suite_path,output,baseline,steps=131072,batch=16,dynamics='legacy',rounds=1,training_seed=42,promote=True,route_metrics=False,curriculum=None,reward_shaping=None,mastery=False,allow_transfer=False,validation_interval=1,continuous_episodes=False,gamma=.995,timeout_as_terminal=False,target_envs=0):
    if batch<1 or type(training_seed) is not int or not 0<=training_seed<2**32: raise ValueError('Invalid batch or training seed')
    if rounds<1 or steps<1 or steps%rounds: raise ValueError('Positive rounds must divide the transition budget')
    if steps//rounds%(512*batch): raise ValueError('Each round must contain whole PPO rollouts (512 * batch)')
    if type(validation_interval) is not int or validation_interval<1:raise ValueError('Positive validation interval required')
    if target_envs and (curriculum!='geometry-v2-practice-mastery' or not continuous_episodes):
        raise ValueError('Dedicated target exposure requires continuous mastery')
    if type(target_envs) is not int or not 0 <= target_envs < batch:raise ValueError('Invalid target environment count')
    suite=load_suite(suite_path)
    if suite.get('map_profile') and promote:raise ValueError('Profiled experiments preserve original aliases; use --no-promote')
    from fly_rl.training.test_access import require_unconsumed
    require_unconsumed(suite)
    from fly_rl.training.mastery_curriculum import VERSION as MASTERY_VERSION,practice_partition,MasterySchedule
    training_layouts=suite['splits']['train']['seeds']
    practice_seeds=None
    if mastery or curriculum==MASTERY_VERSION:
        training_layouts,practice_seeds=practice_partition(suite)
    folder=Path(output)
    folder.mkdir(parents=True,exist_ok=False)
    state={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),
        'suite':str(Path(suite_path).resolve()),'steps':steps,'batch':batch,'software':software_info(),
        'baseline':str(baseline),'training_seed':training_seed,'curriculum':curriculum,'reward_shaping':reward_shaping,'route_metrics':route_metrics,'promote_requested':promote,'dynamics':dynamics,'rounds':rounds,'results':[],
        'discount_gamma':gamma,'timeout_as_terminal':timeout_as_terminal,'target_envs':target_envs,
        'final_test_evaluated':False,'stage':'baseline-validation'}
    shutil.copy2(suite_path,folder/'suite.json')
    def save():
        tmp=folder/'experiment.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(folder/'experiment.json')
    def validation(checkpoint):
        seeds=suite['splits']['validation']['seeds']
        if seeds!=list(range(seeds[0],seeds[0]+len(seeds))): raise ValueError('Noncontiguous validation suite')
        return evaluate(data,device,checkpoint,len(seeds),suite['mode'],seeds[0],dynamics=dynamics,route_metrics=route_metrics,map_profile=suite.get('map_profile'),**({'allow_transfer':True} if allow_transfer else {}))
    save()
    from fly_rl.training.learning import TrainingSession
    session=TrainingSession() if continuous_episodes else None
    state['continuous_episodes']=continuous_episodes
    try:
        def rank(result):
            distance=round(result['mean_distance_end'],6) if mastery or curriculum==MASTERY_VERSION else result['mean_distance_end']
            return (result['success_rate'],-result['collision_rate'],-distance)
        best=state['baseline_validation']=validation(baseline);best_path=Path(baseline);resume=baseline;save()
        if mastery or curriculum==MASTERY_VERSION:best=None
        gate_state=None
        for index in range(1,rounds+1):
            state.update(stage='training',current_round=index);save()
            checkpoint=folder/f'round-{index}'/'policy.zip'
            extra={'practice_seeds':practice_seeds,'curriculum_state':gate_state} if curriculum==MASTERY_VERSION else {}
            if allow_transfer:extra['allow_transfer']=True
            if session is not None:extra['session']=session
            if gamma!=.995:extra['gamma']=gamma
            if timeout_as_terminal:extra['timeout_as_terminal']=True
            if target_envs:extra['target_envs']=target_envs
            result=train(data,device,steps//rounds,batch,checkpoint,resume=resume,
                mode=suite['mode'],layout_seeds=training_layouts,dynamics=dynamics,training_seed=training_seed,curriculum=curriculum,curriculum_offset=(index-1)*(steps//rounds),curriculum_total=steps,reward_shaping=reward_shaping,map_profile=suite.get('map_profile'),curriculum_profiles=suite.get('training_profiles'),**extra)
            if curriculum==MASTERY_VERSION:
                state.update(stage='training-practice');save()
                snap=result['curriculum']
                gate=session.env.curriculum if session is not None else MasterySchedule(steps,suite['training_profiles'],practice_seeds,snap['transitions'],snap,target_envs)
                profile=gate.profiles[gate.stage].to_dict()
                probes=[evaluate(data,device,checkpoint,8,suite['mode'],practice_seeds[i*8],
                    dynamics=dynamics,allow_transfer=True,map_profile=profile) for i in range(2)]
                gate.record_practice(probes)
                gate_state=result['curriculum']=gate.snapshot()
                result['practice_inference']=probes
                metadata=json.loads(checkpoint.with_suffix('.json').read_text())
                metadata['training_curriculum']=gate_state
                checkpoint.with_suffix('.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
            measured=None
            if index%validation_interval==0 or index==rounds:
                state.update(stage='round-validation');save()
                measured=validation(checkpoint)
            state['results'].append({'round':index,'checkpoint':str(checkpoint.resolve()),'training':result,'validation':measured})
            if measured is not None and (best is None or rank(measured)>rank(best)): best=measured;best_path=checkpoint
            resume=checkpoint;save()
        selected=folder/'selected-policy.zip'
        shutil.copy2(best_path,selected);shutil.copy2(best_path.with_suffix('.json'),selected.with_suffix('.json'))
        state['validation']=best
        state['training']={'added_transitions':sum(r['training']['added_transitions'] for r in state['results'])}
        state['validation_improved']=rank(best)>rank(state['baseline_validation'])
        state['navigation_demonstrated']=best['success_rate']>0
        state['selection_outcome']='successful_candidate' if state['navigation_demonstrated'] else 'no_successful_candidate'
        state['promoted']=state['navigation_demonstrated'] and state['validation_improved'] and promote
        state['selected_policy']=str(selected.resolve())
        from fly_rl.training import evaluation as evaluator_module
        from fly_rl.simulation import planner as planner_module
        frozen={'version':1,'checkpoint':str(selected.resolve()),'checkpoint_sha256':sha256(selected),
            'metadata_sha256':sha256(selected.with_suffix('.json')),'suite':str((folder/'suite.json').resolve()),
            'suite_sha256':sha256(folder/'suite.json'),'dynamics':dynamics,'mode':suite['mode'],
            'selection_split':'validation','evaluation_configuration':{'sensor_version':best.get('sensor_version',SENSOR_VERSION),'route_metrics':route_metrics,'planner_version':planner_module.PLANNER_VERSION,'clearance':.02,'evaluator_sha256':sha256(evaluator_module.__file__),'planner_sha256':sha256(planner_module.__file__)},'source':str(best_path.resolve()),'validation':best,
            'frozen_utc':datetime.now(timezone.utc).isoformat(),'software':state['software']}
        if suite.get('map_profile'):
            frozen['evaluation_configuration']['map_profile']=suite['map_profile']
            frozen['evaluation_configuration']['world_sha256']=sha256(__import__('fly_rl.simulation.world',fromlist=['']).__file__)
            frozen['evaluation_configuration']['map_profiles_sha256']=sha256(__import__('fly_rl.simulation.map_profiles',fromlist=['']).__file__)
        with (folder/'selection.json').open('x',encoding='utf8') as handle: json.dump(frozen,handle,indent=2)
        if state['promoted'] and promote:
            destination=Path('runs/dense-flight-policy.zip' if dynamics=='coordinated' else 'runs/dense-policy.zip')
            destination.parent.mkdir(parents=True,exist_ok=True)
            metadata=json.loads(selected.with_suffix('.json').read_text())
            metadata['selection']={'suite':str(Path(suite_path).resolve()),'split':'validation',
                'evaluation':state['validation'],'source':str(best_path.resolve()),'final_test_evaluated':False}
            tmp=destination.with_suffix('.zip.tmp');shutil.copy2(selected,tmp);tmp.replace(destination)
            tmp=destination.with_suffix('.json.tmp');tmp.write_text(json.dumps(metadata,indent=2));tmp.replace(destination.with_suffix('.json'))
            state['promoted_checkpoint']=str(destination.resolve())
        state['status']='completed';state['stage']='done'
    except BaseException as exc:
        state['status']='failed';state['error']=repr(exc);raise
    finally:
        if session is not None:session.close()
        state['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return state
