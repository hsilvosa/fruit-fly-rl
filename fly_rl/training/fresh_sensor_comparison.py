"""Fresh paired policy experiment. Preparation and initialization never learn."""
import json,shutil,time
from pathlib import Path
from fly_rl.training.generalization import sha256,final_test
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed
from fly_rl.training.learning import BrainEnv,make_policy,save_model
from fly_rl.training.sensor_migration import migrate_sensors
from fly_rl.training.dense_training import train_dense
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.training.sensor_comparison import freeze_sensor_winner


def code_hashes():
    root=Path(__file__).resolve().parents[2]
    return {str(p.relative_to(root).as_posix()):sha256(p) for p in sorted((root/'fly_rl').rglob('*.py'))}


def validate_budget(steps,batch,rounds,seeds):
    if type(batch) is not int or not 1<=batch<=16:raise ValueError('Batch must be 1 to 16')
    if type(rounds) is not int or not 1<=rounds<=8:raise ValueError('Rounds must be 1 to 8')
    if len(seeds)<2 or len(seeds)>4 or len(set(seeds))!=len(seeds) or any(type(s) is not int or not 0<=s<2**32 for s in seeds):raise ValueError('Use 2 to 4 distinct valid initialization seeds')
    if steps is None:return None
    if type(steps) is not int or not 0<steps<=1048576 or steps%(rounds*512*batch):raise ValueError('Steps must be positive bounded complete rollouts per round')
    return 2*len(seeds)*steps


def prepare_fresh_comparison(suite,output,steps_per_seed=None,batch=8,rounds=2,seeds=(42,73),data='data'):
    total=validate_budget(steps_per_seed,batch,rounds,list(seeds))
    audited=load_suite(suite);require_unconsumed(audited)
    if audited['mode']!='dense':raise ValueError('Fresh sensor comparison uses dense rooms')
    audit=json.loads((Path(data)/'processed/audit.json').read_text(encoding="utf-8"))
    plan={'version':1,'kind':'fresh-paired-sensor-comparison','status':'draft-budget-required' if total is None else 'configured',
        'suite':str(Path(suite).resolve()),'suite_sha256':sha256(suite),'data':str(Path(data).resolve()),'data_fingerprint':audit['fingerprint'],
        'steps_per_seed':steps_per_seed,'batch':batch,'rounds':rounds,'seeds':list(seeds),'total_training_transitions':total,
        'dynamics':'coordinated','route_metrics':True,'source_hashes':code_hashes(),
        'selection':'validation success, fewer collisions, lower end distance; stable v2 tie',
        'final_test':'one frozen validation winner and same-interface untrained control; no test-driven selection',
        'initialization':'fresh policy per seed, identical v2/v3 archive bytes; zero timesteps, zero updates, empty optimizer state'}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as handle:json.dump(plan,handle,indent=2)
    return plan


def initialize_pair(data,device,suite,seed,output):
    env=BrainEnv(data,1,device,seed=seed,mode='dense',layout_seeds=suite['splits']['train']['seeds'],dynamics='coordinated',map_profile=suite.get('map_profile'))
    try:
        model=make_policy(env,seed=seed)
        if model.num_timesteps!=0 or model._n_updates!=0 or model.policy.optimizer.state:raise ValueError('Initialization must be fresh and unoptimized')
        output=Path(output);output.mkdir(parents=True,exist_ok=False)
        v2=output/'v2.zip';save_model(model,v2,env.brain);migrate_sensors(v2,output/'v3.zip')
        proof={'seed':seed,'initial_timesteps':0,'optimizer_updates':0,'optimizer_state_entries':0,
            'v2':str(v2.resolve()),'v3':str((output/'v3.zip').resolve()),'paired_weights_sha256':sha256(v2),
            'full_neurons':env.brain.n,'data_fingerprint':env.brain.audit['fingerprint'],'training_invoked':False}
        if sha256(v2)!=sha256(output/'v3.zip'):raise ValueError('Paired initialization bytes differ')
        (output/'initialization.json').write_text(json.dumps(proof,indent=2),encoding="utf-8");return proof
    finally:env.close()


def run_fresh_comparison(configuration,output,device='cuda'):
    plan=json.loads(Path(configuration).read_text(encoding='utf-8'))
    total=validate_budget(plan['steps_per_seed'],plan['batch'],plan['rounds'],plan['seeds'])
    if total is None or plan['status']!='configured':raise ValueError('Choose and agree the explicit training budget before running this draft')
    if total!=plan['total_training_transitions'] or plan['kind']!='fresh-paired-sensor-comparison' or plan['version']!=1:raise ValueError('Configuration budget or kind mismatch')
    if plan['dynamics']!='coordinated' or plan['route_metrics'] is not True:raise ValueError('Unsupported comparison configuration')
    if code_hashes()!=plan['source_hashes']:raise ValueError('Source changed; prepare a new configuration')
    if sha256(plan['suite'])!=plan['suite_sha256']:raise ValueError('Frozen suite mismatch')
    suite=load_suite(plan['suite']);require_unconsumed(suite)
    audit=json.loads((Path(plan['data'])/'processed/audit.json').read_text(encoding="utf-8"))
    if audit['fingerprint']!=plan['data_fingerprint']:raise ValueError('Dataset fingerprint mismatch')
    base=Path(output);base.mkdir(parents=True,exist_ok=False);started=time.time()
    state={'status':'running','kind':plan['kind'],'configuration_sha256':sha256(configuration),'budget_added_transitions':total,'results':[],'initializations':[],'test_evaluated':False}
    shutil.copy2(configuration,base/'configuration.json')
    def save():
        tmp=base/'status.tmp';tmp.write_text(json.dumps(state,indent=2),encoding="utf-8");tmp.replace(base/'status.json')
    save()
    try:
        root=Path(__file__).resolve().parents[2]
        for name in plan['source_hashes']:
            target=base/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
        for seed in plan['seeds']:
            state['stage']=f'initialize-{seed}';save()
            proof=initialize_pair(plan['data'],device,suite,seed,base/f'initial-{seed}')
            if proof['data_fingerprint']!=plan['data_fingerprint']:raise ValueError('Actual graph does not match plan')
            state['initializations'].append(proof);save()
        groups=[]
        for label in ['v2','v3']:
            members=[]
            for seed in plan['seeds']:
                state['stage']=f'{label}-seed-{seed}';save();folder=base/f'{label}-seed-{seed}'
                run=train_dense(plan['data'],device,plan['suite'],folder,base/f'initial-{seed}'/f'{label}.zip',plan['steps_per_seed'],plan['batch'],'coordinated',plan['rounds'],seed,False,True)
                if run['training']['added_transitions']!=plan['steps_per_seed']:raise ValueError('Training exceeded declared seed budget')
                state['results'].append({'interface':label,'seed':seed,'validation':run['validation'],'added_transitions':run['training']['added_transitions']});members.append(folder);save()
            group=base/f'{label}-selected';select_experiment(members,group);groups.append(group)
        state['stage']='validation-only-selection';save()
        winner=freeze_sensor_winner(groups,base/'selected',{seed:plan['steps_per_seed'] for seed in plan['seeds']})
        state['selected_sensor_version']=winner['selected_sensor_version'];state['stage']='frozen-final-test';save()
        final=final_test(plan['data'],device,base/'selected');state.update(test_evaluated=True,final_summary=final['selected_summary'],untrained_summary=final['untrained_summary'],status='completed',stage='done')
    except BaseException as exc:state.update(status='failed',error=repr(exc));raise
    finally:state['elapsed_seconds']=time.time()-started;save()
    return state
