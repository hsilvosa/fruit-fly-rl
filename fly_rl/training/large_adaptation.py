"""Bounded warm-start adaptation; the large target and final pool are fixed."""
from fly_rl.atomic_io import replace_file
import json
import shutil
import time
from pathlib import Path
from fly_rl.training.generalization import sha256,final_test
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed
from fly_rl.training.fresh_sensor_comparison import code_hashes
from fly_rl.training.mastery_curriculum import VERSION,PROTOCOL,practice_partition,validate_mastery_profiles
from fly_rl.training.dense_training import train_dense
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.simulation.map_profiles import resolve_profile
from fly_rl.simulation.sensors import SENSOR_V3


def run_large_adaptation(configuration,output,device='cuda'):
    config=Path(configuration);plan=json.loads(config.read_text())
    continuous=plan['kind']=='large-warm-continuous-v4'
    expected_steps,expected_rounds,expected_total=(212992,26,425984) if continuous else (262144,32,524288)
    if (plan['kind'] not in ['large-warm-mastery-v3','large-warm-continuous-v4'] or plan['total_added_transitions']!=expected_total
            or plan['steps_per_seed']!=expected_steps or plan['rounds']!=expected_rounds or plan['batch']!=8
            or plan['seeds']!=[42,73] or plan['validation_interval']!=4
            or plan['validation_minimum']!=.85 or plan['final_success_target']!=.8
            or plan['curriculum']!=PROTOCOL):
        raise ValueError('Unsupported or changed bounded large adaptation protocol')
    if continuous and (plan.get('continuous_episodes') is not True or plan.get('previous_interrupted_transitions')!=98304):
        raise ValueError('Continuous correction must preserve the cumulative 524288-transition budget')
    if code_hashes()!=plan['source_hashes']:raise ValueError('Frozen adaptation sources changed')
    suite=load_suite(plan['suite']);require_unconsumed(suite)
    if suite['map_profile']!=resolve_profile('large').to_dict():raise ValueError('Target must be the original large profile')
    validate_mastery_profiles(suite['training_profiles']);training,practice=practice_partition(suite)
    if suite['training_profiles'][-1]!=suite['map_profile']:raise ValueError('Last stage must be the large target')
    for file,digest in [(plan['suite'],plan['suite_sha256']),(plan['baseline'],plan['baseline_sha256']),
                         (str(Path(plan['baseline']).with_suffix('.json')),plan['baseline_metadata_sha256'])]:
        if sha256(file)!=digest:raise ValueError('Frozen input hash mismatch')
    metadata=json.loads(Path(plan['baseline']).with_suffix('.json').read_text())
    if metadata['sensor_version']!=SENSOR_V3 or metadata['timesteps']<=0:raise ValueError('A trained v3 warm start is required')
    root=Path(output);root.mkdir(parents=True,exist_ok=False)
    aliases={str(p.resolve()):sha256(p) for p in Path('runs').glob('*policy.*') if p.suffix in ['.zip','.json']}
    state={'status':'running','kind':plan['kind'],'stage':'freeze-inputs','configuration_sha256':sha256(config),
           'budget_added_transitions':expected_total,'results':[],'test_evaluated':False,'alias_hashes_before':aliases,
           'continuous_episodes':continuous,'previous_interrupted_transitions':98304 if continuous else 0,
           'optimization_layouts':training,'practice_layouts':practice,'validation_minimum':.85,'final_success_target':.8}
    started=time.monotonic()
    def save():
        temp=root/'status.tmp';temp.write_text(json.dumps(state,indent=2),encoding='utf8');replace_file(temp, root/'status.json')
    save()
    try:
        shutil.copy2(config,root/'configuration.json')
        project=Path(__file__).resolve().parents[2]
        for name in plan['source_hashes']:
            dest=root/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(project/name,dest)
        baseline=root/'initial-policy.zip'
        shutil.copy2(plan['baseline'],baseline);shutil.copy2(Path(plan['baseline']).with_suffix('.json'),baseline.with_suffix('.json'))
        members=[]
        for seed in plan['seeds']:
            state['stage']=f'mastery-seed-{seed}';save()
            member=root/f'mastery-seed-{seed}'
            result=train_dense(plan['data'],device,plan['suite'],member,baseline,expected_steps,8,'coordinated',expected_rounds,seed,
                               False,True,curriculum=VERSION,mastery=True,allow_transfer=True,validation_interval=4,
                               **({'continuous_episodes':True} if continuous else {}))
            if result['training']['added_transitions']!=expected_steps:raise ValueError('Adaptation exceeded declared steps')
            state['results'].append({'seed':seed,'added_transitions':expected_steps,'validation':result['validation'],
                                     'final_curriculum':result['results'][-1]['training']['curriculum']})
            members.append(member);save()
        state['stage']='validation-selection';save()
        winner=select_experiment(members,root/'selected',distance_precision=6)
        state['validation']=winner['validation']
        if winner['validation']['success_rate']<.85:
            state.update(status='completed',stage='validation-target-not-met',goal_achieved=False)
        else:
            state['stage']='one-frozen-final-test';save()
            assessed=final_test(plan['data'],device,root/'selected')
            state.update(status='completed',stage='done',test_evaluated=True,
                         final_summary=assessed['selected_summary'],untrained_summary=assessed['untrained_summary'],
                         goal_achieved=assessed['selected_summary']['success_rate']>=.8)
    except BaseException as e:
        state.update(status='failed',error=repr(e));raise
    finally:
        state['alias_hashes_after']={name:sha256(name) if Path(name).exists() else None for name in aliases}
        state['aliases_unchanged']=state['alias_hashes_after']==aliases
        state['warm_start_unchanged']=sha256(plan['baseline'])==plan['baseline_sha256'] and sha256(Path(plan['baseline']).with_suffix('.json'))==plan['baseline_metadata_sha256']
        state['elapsed_seconds']=time.monotonic()-started;save()
        if not state['aliases_unchanged'] or not state['warm_start_unchanged']:raise RuntimeError('Original policy integrity changed')
    return state
