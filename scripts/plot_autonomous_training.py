"""Plot existing PPO episode logs without loading models or running evaluation."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def read_episodes(path):
    text=Path(path).read_text(encoding='utf-8')
    lines=text.splitlines()
    episodes=[]
    for index,line in enumerate(lines):
        try:episodes.append(json.loads(line))
        except json.JSONDecodeError:
            # A writer may still be appending the final line. Earlier errors
            # must be surfaced rather than silently removing evidence.
            if index==len(lines)-1 and not text.endswith('\n'):break
            raise
    return episodes


def plot(run, output):
    run=Path(run);output=Path(output)
    episodes=read_episodes(run/'episodes.jsonl')
    if not episodes:raise ValueError('No completed episodes to plot')
    scenes=list(dict.fromkeys(e['scene'] for e in episodes))
    fig,axes=plt.subplots(len(scenes),2,figsize=(12,3*len(scenes)),squeeze=False)
    for row,scene in enumerate(scenes):
        values=[e for e in episodes if e['scene']==scene]
        x=np.array([e['transitions'] for e in values])/1000
        rewards=np.array([e['reward'] for e in values])
        axes[row,0].scatter(x,rewards,s=12,alpha=.55,color='#27678c')
        axes[row,0].set_ylabel(scene+'\nEpisode return')
        axes[row,1].step(x,np.cumsum([e['success'] for e in values]),where='post',label='Goals',color='#21855b')
        axes[row,1].step(x,np.cumsum([e['collision'] for e in values]),where='post',label='Collisions',color='#ba543a')
        axes[row,1].step(x,np.cumsum([e['timeout'] for e in values]),where='post',label='Timeouts',color='#7764a1')
        axes[row,1].set_ylabel('Completed episodes (cumulative)')
        for ax in axes[row]:
            ax.grid(alpha=.2);ax.set_xlabel('Training transitions (thousands)')
        axes[row,1].legend(loc='upper left')
    fig.suptitle('Autonomous PPO training logs: '+run.name+'\nDifferent situations within a scene have different difficulty; these are training outcomes, not validation.',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.965))
    output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(output,dpi=140);plt.close(fig)
    return dict(episodes=len(episodes),goals=sum(e['success'] for e in episodes),
                collisions=sum(e['collision'] for e in episodes),timeouts=sum(e['timeout'] for e in episodes),
                last_episode_transition=max(e['transitions'] for e in episodes),output=str(output))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();print(json.dumps(plot(args.run,args.output),indent=2))
