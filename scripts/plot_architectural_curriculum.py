"""Plot recorded lesson rounds and original-goal validation; no evaluation."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(run, output):
    status=json.loads((Path(run)/'status.json').read_text())
    rounds=status['mastery']['rounds']
    if status['status']!='completed' or not rounds:
        raise ValueError('Require completed evidence with mastery rounds')
    fig, axes=plt.subplots(1,2,figsize=(12,4.5))
    values=[sum(r['goals'].values())/(len(r['goals'])*r['episodes_per_task'])*100 for r in rounds]
    labels=[f"{i+1}\n{r['stage']+1} m" for i,r in enumerate(rounds)]
    colors=['#21855b' if r['passed'] else '#a56135' for r in rounds]
    axes[0].bar(labels,values,color=colors)
    for i,value in enumerate(values):axes[0].text(i,value+2,f'{value:.1f}%',ha='center',fontsize=9)
    axes[0].set_ylim(0,112);axes[0].set_ylabel('Lesson successes (%)')
    axes[0].set_xlabel('Completed round / lesson distance')
    axes[0].set_title('Adaptive training practice')
    axes[0].text(.02,.97,'Green: every task passed; brown: at least one failed',transform=axes[0].transAxes,va='top',fontsize=8)
    names=['Goals','Collisions','Timeouts']
    keys=['success','collision','timeout']
    before=[sum(r[k] for r in status['validation_before']) for k in keys]
    after=[sum(r[k] for r in status['validation_after']) for k in keys]
    x=list(range(3))
    axes[1].bar([i-.18 for i in x],before,width=.36,label='Before',color='#8797a6')
    axes[1].bar([i+.18 for i in x],after,width=.36,label='After',color='#27678c')
    axes[1].set_xticks(x,names);axes[1].set_ylim(0,7)
    axes[1].set_ylabel('Original-goal validation episodes')
    axes[1].set_title('Six development situations');axes[1].legend()
    for ax in axes:ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Nearby lesson mastery did not transfer to complete routes')
    fig.text(.5,.01,'Training practice and reused development validation are separate; neither is an independent final test.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.94))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=160);plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();plot(args.run,args.output)
