"""Plot development progress and a completed frozen-policy test without learning."""
import json
from pathlib import Path
import numpy as np

def plot_dense(experiment,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=Path(experiment);state=json.loads((folder/'experiment.json').read_text())
    final=json.loads((folder/'final-test.json').read_text())
    if state['status']!='completed' or final['status']!='completed': raise ValueError('A completed experiment and final test are required')
    rounds=[state['baseline_validation']]+[r['validation'] for r in state['results']]
    steps=[0];total=0
    for row in state['results']: total+=row['training']['added_transitions'];steps.append(total)
    plt.style.use('dark_background')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    axes[0].plot(steps,[r['success_rate']*100 for r in rounds],'o-',color='#5ee0af',label='Success')
    axes[0].plot(steps,[r['collision_rate']*100 for r in rounds],'o-',color='#fa907d',label='Collision')
    axes[0].set(title='Development: 32 validation rooms',xlabel='Added training transitions',ylabel='Episodes (%)',ylim=(0,100))
    axes[0].legend();axes[0].grid(alpha=.15)
    scores=[final['selected_summary'],final['untrained_summary']]
    values=np.array([s['success_rate'] for s in scores])*100
    lower=np.array([s['success_wilson_95'][0] for s in scores])*100
    upper=np.array([s['success_wilson_95'][1] for s in scores])*100
    errors=np.maximum(np.vstack([values-lower,upper-values]),0)
    axes[1].bar(['Frozen selected policy','Untrained policy'],values,yerr=errors,capsize=6,
                error_kw={'ecolor':'#eeeeee','elinewidth':1.5},color=['#5ee0af','#7c99bc'])
    axes[1].set(title='Final test: 64 held-out rooms',ylabel='Success (%) / Wilson 95% interval',ylim=(0,100))
    for i,s in enumerate(scores): axes[1].text(i,min(values[i]+12,96),f"{s['successes']}/{s['episodes']}",ha='center')
    fig.suptitle('MaleCNS v1.0 / dense rooms / coordinated flight')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=160);plt.close(fig)
    return {'plot':str(output.resolve()),'training_invoked':False,'test_used_for_selection':False}
