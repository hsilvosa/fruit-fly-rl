"""Predeclared equal-budget v2/v3 warm-start comparison; final selection is validation only."""
import json,shutil,time
from pathlib import Path
from datetime import datetime,timezone
from fly_rl.training.generalization import sha256,final_test
from fly_rl.training.dense_training import train_dense
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.training.sensor_migration import migrate_sensors
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed
from fly_rl.training.learning import checkpoint_sensor_version
from fly_rl.simulation.sensors import SENSOR_VERSION,SENSOR_V3


def freeze_sensor_winner(groups,output,expected_budgets=None):
    expected_budgets=expected_budgets or {42:65536,73:65536}
    records=[]
    for group in map(Path,groups):
        state=json.loads((group/'experiment.json').read_text())
        frozen=json.loads((group/'selection.json').read_text())
        if state['status']!='completed' or state['final_test_evaluated']:raise ValueError('Validation-only completed groups required')
        for p,h in [(frozen['checkpoint'],frozen['checkpoint_sha256']),(str(Path(frozen['checkpoint']).with_suffix('.json')),frozen['metadata_sha256']),(frozen['suite'],frozen['suite_sha256'])]:
            if sha256(p)!=h:raise ValueError('Frozen integrity mismatch')
        require_unconsumed(load_suite(frozen['suite']))
        configuration=dict(frozen['evaluation_configuration']);sensor=configuration.pop('sensor_version')
        members=state['seed_experiments']
        signature=sorted((m['training_seed'],m['added_transitions']) for m in members)
        if signature!=sorted(expected_budgets.items()):raise ValueError('Predeclared equal seed budgets required')
        records.append((state,frozen,group,configuration,sensor))
    if len(records)!=2 or {r[4] for r in records}!={SENSOR_VERSION,SENSOR_V3}:raise ValueError('Exactly one v2 and one v3 group required')
    if len({(r[1]['suite_sha256'],r[1]['dynamics'],json.dumps(r[3],sort_keys=True)) for r in records})!=1:raise ValueError('Matched suite, dynamics and evaluation configuration required')
    def rank(r):
        v=r[1]['validation'];return (v['success_rate'],-v['collision_rate'],-v['mean_distance_end'])
    best=max(records,key=rank)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    shutil.copy2(best[1]['checkpoint'],output/'selected-policy.zip')
    shutil.copy2(Path(best[1]['checkpoint']).with_suffix('.json'),output/'selected-policy.json')
    shutil.copy2(best[1]['suite'],output/'suite.json')
    frozen=dict(best[1],checkpoint=str((output/'selected-policy.zip').resolve()),suite=str((output/'suite.json').resolve()),frozen_utc=datetime.now(timezone.utc).isoformat())
    frozen['sensor_comparison']=[{'sensor_version':r[4],'validation':r[1]['validation'],'seed_experiments':r[0]['seed_experiments']} for r in records]
    (output/'selection.json').write_text(json.dumps(frozen,indent=2))
    state={'status':'completed','kind':'validation-selected-sensor-comparison','final_test_evaluated':False,'validation':frozen['validation'],'selected_sensor_version':best[4],'selected_experiment':best[0]['selected_experiment'],'sensor_comparison':frozen['sensor_comparison'],'training':{'added_transitions':2*sum(expected_budgets.values())}}
    (output/'experiment.json').write_text(json.dumps(state,indent=2));return state


def run_comparison(data,device,suite,baseline,output):
    if checkpoint_sensor_version(baseline)!=SENSOR_VERSION:raise ValueError('Shared baseline must use v2')
    require_unconsumed(load_suite(suite))
    base=Path(output);base.mkdir(parents=True,exist_ok=False)
    started=time.time();original=sha256(baseline);original_meta=sha256(Path(baseline).with_suffix('.json'))
    state={'status':'running','budget_added_transitions':262144,'steps_per_seed':65536,'rounds_per_seed':2,'batch':8,'training_seeds':[42,73],'suite':str(Path(suite).resolve()),'baseline':str(Path(baseline).resolve()),'baseline_sha256':original,'baseline_metadata_sha256':original_meta,'results':[],'test_evaluated':False}
    def save():
        tmp=base/'status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(base/'status.json')
    save()
    try:
        snapshots=[];repository=Path(__file__).resolve().parents[2]
        for p in sorted((repository/'fly_rl').rglob('*.py')):
            destination=base/'source'/p.relative_to(repository);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,destination)
            snapshots.append({'path':str(p.relative_to(repository)),'sha256':sha256(p)})
        (base/'source/manifest.json').write_text(json.dumps(snapshots,indent=2))
        migrated=base/'v3-baseline.zip';migrate_sensors(baseline,migrated)
        groups=[]
        for label,checkpoint in [('v2',baseline),('v3',migrated)]:
            runs=[]
            for seed in [42,73]:
                state['stage']=f'{label}-seed-{seed}';save()
                folder=base/f'{label}-seed-{seed}'
                result=train_dense(data,device,suite,folder,checkpoint,65536,8,'coordinated',2,seed,False,True)
                state['results'].append({'interface':label,'seed':seed,'baseline_validation':result['baseline_validation'],'validation':result['validation'],'added_transitions':result['training']['added_transitions']});save();runs.append(folder)
            group=base/f'{label}-selected';select_experiment(runs,group);groups.append(group)
        state['stage']='validation-only-interface-selection';save()
        winner=freeze_sensor_winner(groups,base/'selected');state['selected_sensor_version']=winner['selected_sensor_version'];state['selected_experiment']=winner['selected_experiment'];state['stage']='frozen-final-test';save()
        result=final_test(data,device,base/'selected');state['test_evaluated']=True;state['final_summary']=result['selected_summary'];state['untrained_summary']=result['untrained_summary']
        assert sha256(baseline)==original and sha256(Path(baseline).with_suffix('.json'))==original_meta
        state.update(status='completed',stage='done',baseline_unchanged=True)
    except BaseException as exc:
        state.update(status='failed',error=repr(exc));raise
    finally:state['elapsed_seconds']=time.time()-started;save()
    return state
