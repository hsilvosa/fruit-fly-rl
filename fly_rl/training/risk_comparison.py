"""Bounded matched fresh v3 risk/control experiment; explicit invocation only."""
from fly_rl.atomic_io import replace_file
import json,shutil,time
from pathlib import Path
from fly_rl.training.risk_shaping import VERSION,PROTOCOL
from fly_rl.training.fresh_sensor_comparison import prepare_fresh_comparison,validate_budget,code_hashes,initialize_pair
from fly_rl.training.generalization import sha256,final_test
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed
from fly_rl.training.dense_training import train_dense
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.simulation.sensors import SENSOR_V3




def prepare_risk_comparison(suite,output,steps_per_seed=None,batch=8,rounds=2,seeds=(42,73),data='data'):
    # Reuse audited preparation; no model construction or learning.
    plan=prepare_fresh_comparison(suite,output,steps_per_seed,batch,rounds,seeds,data)
    plan.update(kind='fresh-v3-risk-comparison',reward_shaping=PROTOCOL,sensor_version=SENSOR_V3,
        selection='validation success, fewer collisions, lower ending distance; baseline wins exact arm tie',
        initialization='fresh v3 checkpoint per seed; identical initial checkpoint and empty optimizer state for baseline and risk')
    Path(output).write_text(json.dumps(plan,indent=2),encoding='utf-8');return plan


def freeze_risk_winner(groups,output,budgets):
    records=[]
    for arm,folder in sorted(groups,key=lambda pair:pair[0]):
        folder=Path(folder);state=json.loads((folder/'experiment.json').read_text(encoding='utf-8'));frozen=json.loads((folder/'selection.json').read_text(encoding='utf-8'))
        if state['status']!='completed' or state.get('final_test_evaluated'):raise ValueError('Completed validation-only groups required')
        if sorted((r['training_seed'],r['added_transitions']) for r in state['seed_experiments'])!=sorted(budgets.items()):raise ValueError('Matched declared seed budgets required')
        for path,h in [(frozen['checkpoint'],frozen['checkpoint_sha256']),(str(Path(frozen['checkpoint']).with_suffix('.json')),frozen['metadata_sha256']),(frozen['suite'],frozen['suite_sha256'])]:
            if sha256(path)!=h:raise ValueError('Frozen integrity mismatch')
        require_unconsumed(load_suite(frozen['suite']))
        if frozen['evaluation_configuration']['sensor_version']!=SENSOR_V3:raise ValueError('Both arms must use v3')
        records.append((arm,state,frozen))
    if len(records)!=2 or {r[0] for r in records}!={'baseline','risk'}:raise ValueError('Exactly one baseline and risk group required')
    if len({(r[2]['suite_sha256'],r[2]['dynamics'],json.dumps(r[2]['evaluation_configuration'],sort_keys=True)) for r in records})!=1:raise ValueError('Matched standard evaluation required')
    def rank(record):
        v=record[2]['validation'];return v['success_rate'],-v['collision_rate'],-v['mean_distance_end']
    arm,state,frozen=max(records,key=rank);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    shutil.copy2(frozen['checkpoint'],output/'selected-policy.zip');shutil.copy2(Path(frozen['checkpoint']).with_suffix('.json'),output/'selected-policy.json');shutil.copy2(frozen['suite'],output/'suite.json')
    frozen=dict(frozen,checkpoint=str((output/'selected-policy.zip').resolve()),suite=str((output/'suite.json').resolve()),selected_arm=arm)
    comparisons=[{'arm':r[0],'validation':r[2]['validation'],'seed_experiments':r[1]['seed_experiments']} for r in records]
    frozen['risk_comparison']=comparisons
    (output/'selection.json').write_text(json.dumps(frozen,indent=2),encoding='utf-8')
    result={'status':'completed','kind':'validation-selected-risk-comparison','selected_arm':arm,'selected_experiment':state['selected_experiment'],'validation':frozen['validation'],'risk_comparison':comparisons,'final_test_evaluated':False,'training':{'added_transitions':2*sum(budgets.values())}}
    (output/'experiment.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result


def run_risk_comparison(configuration,output,device='cuda'):
    plan=json.loads(Path(configuration).read_text(encoding='utf-8'));total=validate_budget(plan['steps_per_seed'],plan['batch'],plan['rounds'],plan['seeds'])
    if total is None or plan['status']!='configured':raise ValueError('Agree a declared budget before running the draft')
    if plan['kind']!='fresh-v3-risk-comparison' or plan['version']!=1 or plan['reward_shaping']!=PROTOCOL or plan['sensor_version']!=SENSOR_V3 or plan['dynamics']!='coordinated' or not plan['route_metrics'] or total!=plan['total_training_transitions']:raise ValueError('Unsupported or inconsistent risk protocol')
    if code_hashes()!=plan['source_hashes']:raise ValueError('Source changed; prepare a new configuration')
    if sha256(plan['suite'])!=plan['suite_sha256']:raise ValueError('Frozen suite mismatch')
    suite=load_suite(plan['suite']);require_unconsumed(suite)
    audit=json.loads((Path(plan['data'])/'processed/audit.json').read_text(encoding='utf-8'))
    if audit['fingerprint']!=plan['data_fingerprint']:raise ValueError('Dataset fingerprint mismatch')
    base=Path(output);base.mkdir(parents=True,exist_ok=False);started=time.time()
    aliases={str(p.resolve()):sha256(p) for p in Path('runs').glob('*policy.*') if p.suffix in ['.zip','.json']}
    state={'status':'running','kind':plan['kind'],'configuration_sha256':sha256(configuration),'budget_added_transitions':total,'initializations':[],'results':[],'test_evaluated':False,'alias_hashes_before':aliases}
    shutil.copy2(configuration,base/'configuration.json')
    def save():
        tmp=base/'status.tmp';tmp.write_text(json.dumps(state,indent=2),encoding='utf-8');replace_file(tmp, base/'status.json')
    save()
    try:
        root=Path(__file__).resolve().parents[2]
        for name in plan['source_hashes']:
            target=base/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
        for seed in plan['seeds']:
            state['stage']=f'initialize-{seed}';save();proof=initialize_pair(plan['data'],device,suite,seed,base/f'initial-{seed}')
            if proof['data_fingerprint']!=plan['data_fingerprint']:raise ValueError('Graph does not match plan')
            state['initializations'].append(proof);save()
        groups=[]
        for arm,profile in [('baseline',None),('risk',VERSION)]:
            members=[]
            for seed in plan['seeds']:
                state['stage']=f'{arm}-seed-{seed}';save();folder=base/f'{arm}-seed-{seed}'
                result=train_dense(plan['data'],device,plan['suite'],folder,base/f'initial-{seed}/v3.zip',plan['steps_per_seed'],plan['batch'],'coordinated',plan['rounds'],seed,False,True,reward_shaping=profile)
                if result['training']['added_transitions']!=plan['steps_per_seed']:raise ValueError('Declared training budget mismatch')
                state['results'].append({'arm':arm,'seed':seed,'added_transitions':result['training']['added_transitions'],'validation':result['validation']});members.append(folder);save()
            group=base/f'{arm}-selected';select_experiment(members,group);groups.append((arm,group))
        state['stage']='validation-only-selection';save();winner=freeze_risk_winner(groups,base/'selected',{seed:plan['steps_per_seed'] for seed in plan['seeds']})
        state['selected_arm']=winner['selected_arm'];state['stage']='frozen-final-test';save();final=final_test(plan['data'],device,base/'selected')
        unchanged=all(sha256(path)==h for path,h in aliases.items())
        if not unchanged:raise RuntimeError('Original launcher alias changed')
        state.update(status='completed',stage='done',test_evaluated=True,final_summary=final['selected_summary'],untrained_summary=final['untrained_summary'],aliases_unchanged=unchanged)
    except BaseException as exc:state.update(status='failed',error=repr(exc));raise
    finally:state['elapsed_seconds']=time.time()-started;save()
    return state
