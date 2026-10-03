"""Show validation across adaptation seeds and one independent final outcome."""
import json
from pathlib import Path
import numpy as np


def plot_generalization(experiment, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=Path(experiment)
    state=json.loads((folder/'status.json').read_text())
    if state['status']!='completed': raise ValueError('Experiment must finish before plotting final results')
    final=json.loads((folder/'selected/final-test.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(15,4.8),layout='constrained')
    for seed in state['training_seeds']:
        run=json.loads((folder/f'seed-{seed}/experiment.json').read_text())
        values=[run['baseline_validation']]+[r['validation'] for r in run['results']]
        steps=[0]+list(np.cumsum([r['training']['added_transitions'] for r in run['results']]))
        axes[0].plot(steps,[v['success_rate']*100 for v in values],marker='o',label=f'Adaptation seed {seed}')
    axes[0].set(title='Shared validation pool; selection only',xlabel='Added transitions per seed',ylabel='Goals reached (%)',ylim=(0,100))
    axes[0].legend();axes[0].grid(alpha=.2)
    scores=[final['selected_summary'],final['untrained_summary']]
    rates=np.array([v['success_rate'] for v in scores])*100
    bounds=np.array([v['success_wilson_95'] for v in scores])*100
    errors=np.maximum(np.vstack([rates-bounds[:,0],bounds[:,1]-rates]),0)
    axes[1].bar(['Frozen selected','Untrained'],rates,yerr=errors,capsize=5)
    axes[1].axhline(80,linestyle='--',color='gray',label='80% target')
    axes[1].set(title='Fresh final test; Wilson 95% interval',ylabel='Goals reached (%)',ylim=(0,100));axes[1].legend()
    for i,row in enumerate(scores): axes[1].text(i,min(rates[i]+8,95),f"{row['successes']}/{row['episodes']}",ha='center')
    rows=[r for r in final['selected']['episodes'] if r['success'] and r.get('path_over_feasible_reference') is not None]
    if rows:
        axes[2].boxplot([[r['path_over_feasible_reference'] for r in rows]],tick_labels=['Successful selected flights'])
    else:
        axes[2].text(.5,.5,'No successful flights with a reference',transform=axes[2].transAxes,ha='center')
    axes[2].set(title='Route quality alongside success',ylabel='Flown length / feasible reference length')
    fig.suptitle('Full MaleCNS / coordinated dense flight / approximate geometric references, not global optima')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(output,dpi=150);plt.close(fig)
    return {'plot':str(output.resolve()),'training_invoked':False,'evaluation_invoked':False,
            'selected_summary':scores[0],'successful_reference_count':len(rows)}
