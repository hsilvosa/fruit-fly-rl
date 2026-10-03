"""Plot retained validation outcomes; never run a policy or read final-test outcomes."""
import json,math
from pathlib import Path
from collections import Counter
from fly_rl.training.suites import load_suite
from fly_rl.training.diagnostics import outcome_label


def collect_validation(experiments):
    result=[];suite_ids=set()
    for folder in map(Path,experiments):
        state=json.loads((folder/'experiment.json').read_text(encoding='utf-8'))
        if state.get('split')=='test' or 'selected_summary' in state or 'final_summary' in state:
            raise ValueError('Use individual validation experiments, not final-test outcomes')
        suite=load_suite(folder/'suite.json');suite_ids.add(json.dumps(suite['splits']['validation'],sort_keys=True))
        measured=state['validation']
        if measured.get('split')=='test':raise ValueError('Test measurements are forbidden')
        rows=measured['episodes'];seeds=[r['seed'] for r in rows]
        if sorted(seeds)!=sorted(suite['splits']['validation']['seeds']):raise ValueError('Validation seed provenance mismatch')
        for row in rows:
            if not all(math.isfinite(row[key]) for key in ['distance_end','idle_fraction']):raise ValueError('Nonfinite validation measurements')
            if row['distance_end']<0 or not 0<=row['idle_fraction']<=1:raise ValueError('Invalid validation measurement range')
        categories=Counter(outcome_label(r) for r in rows)
        timeouts=[r for r in rows if r.get('timeout')]
        result.append({'experiment':str(folder.resolve()),'sensor_version':measured.get('sensor_version','unknown'),
            'training_seed':state.get('training_seed'),'episodes':len(rows),'categories':dict(categories),
            'timeouts_near_goal':sum(r['distance_end']<2 for r in timeouts),
            'timeouts_frequent_stopping':sum(r['idle_fraction']>=.25 for r in timeouts),
            'timeouts_near_goal_and_stopping':sum(r['distance_end']<2 and r['idle_fraction']>=.25 for r in timeouts),
            'rows':rows})
    if not result:raise ValueError('Provide at least one validation experiment')
    if len(suite_ids)!=1:raise ValueError('Compare experiments on the same validation layouts')
    return {'scope':'selected checkpoints on shared validation rooms; outcomes repeat across controllers',
        'experiments':result,'unique_validation_rooms':len(result[0]['rows']),
        'thresholds':{'near_goal_distance':2.,'frequent_stopping_fraction':.25,'idle_speed_in_evaluator':.1},
        'training_invoked':False,'evaluation_invoked':False,
        'limits':'Endpoint distance and whole-flight idle fraction are heuristics. No collision position or altitude history was retained; their causes cannot be reconstructed. Near-goal and stopping flags can overlap.'}


def plot_validation_failures(experiments,output):
    report=collect_validation(experiments)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,3,figsize=(16,5),layout='constrained')
    labels=[('v3' if '-v3-' in e['sensor_version'] else 'v2')+f" seed {e['training_seed']}" for e in report['experiments']]
    categories=['success','collision_location_unknown','timeout_with_frequent_stopping','timeout_near_goal','timeout_without_arrival']
    bottom=np.zeros(len(labels));colors=['#57945d','#c44c4c','#e9a34b','#9471b2','#6388ab']
    for category,color in zip(categories,colors):
        values=np.array([e['categories'].get(category,0) for e in report['experiments']])
        axes[0].bar(labels,values,bottom=bottom,label=category.replace('_',' '),color=color);bottom+=values
    axes[0].set(title='Selected validation outcomes',ylabel='Recorded flights');axes[0].legend(fontsize=8);axes[0].tick_params(axis='x',rotation=25)
    for e,label in zip(report['experiments'],labels):
        rows=[r for r in e['rows'] if not r['success']]
        axes[1].scatter([r['distance_end'] for r in rows],[r['idle_fraction'] for r in rows],label=label,alpha=.75)
    axes[1].axvline(2,color='gray',linestyle='--');axes[1].axhline(.25,color='gray',linestyle='--')
    axes[1].set(title='Failures: retained scalar measurements',xlabel='Ending target distance (units)',ylabel='Whole-flight idle fraction',ylim=(-.02,1.02));axes[1].legend(fontsize=8)
    x=np.arange(len(labels));axes[2].bar(x-.18,[e['timeouts_near_goal'] for e in report['experiments']],width=.36,label='Timeout < 2 units')
    axes[2].bar(x+.18,[e['timeouts_frequent_stopping'] for e in report['experiments']],width=.36,label='Timeout idle >= 25%')
    axes[2].set(xticks=x,xticklabels=labels,title='Nonexclusive timeout flags',ylabel='Recorded flights');axes[2].tick_params(axis='x',rotation=25);axes[2].legend(fontsize=8)
    fig.suptitle('Shared validation rooms only; heuristics do not establish failure causes')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(output,dpi=150);plt.close(fig)
    report['plot']=str(output.resolve());output.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
