"""Plot archived validation traces without running a policy."""
import json
from pathlib import Path
import numpy as np


def plot_validation_trace(source,output):
    report=json.loads(Path(source).read_text(encoding='utf-8'))
    if report.get('split')!='validation' or report.get('test_evaluated'):raise ValueError('Validation traces only')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from fly_rl.training.generalization import sha256
    from fly_rl.simulation.world import DT
    fig=plt.figure(figsize=(14,5*len(report['cases'])),layout='constrained')
    for i,case in enumerate(report['cases']):
        if sha256(case['trace'])!=case['sha256']:raise ValueError('Trace checksum mismatch')
        with np.load(case['trace'],allow_pickle=False) as trace:
            ax=fig.add_subplot(len(report['cases']),3,i*3+1,projection='3d');positions=np.vstack([trace['position_before'][0],trace['position_after']]);target=trace['target'];room=trace['room']
            ax.plot(*positions.T,color='#2876a6');ax.scatter(*positions[0],color='green',label='start');ax.scatter(*positions[-1],color='red',label='end');ax.scatter(*target,color='gold',marker='*',s=80,label='target')
            for low,high in trace['obstacles']:
                x,y,z=low;a,b,c=high
                vertices=[(x,y,z),(a,y,z),(a,b,z),(x,b,z),(x,y,c),(a,y,c),(a,b,c),(x,b,c)]
                faces=[[vertices[j] for j in face] for face in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
                ax.add_collection3d(Poly3DCollection(faces,alpha=.08,facecolor='gray',edgecolor='gray',linewidth=.3))
            contact=case.get('outcome',{}).get('contact') if case.get('outcome') else None
            outcome=case.get('outcome') or {};label=contact['kind'] if contact else 'timeout' if outcome.get('truncated') else 'success' if outcome.get('success') else case['status']
            ax.set(xlim=(0,room[0]),ylim=(0,room[1]),zlim=(0,room[2]),xlabel='X',ylabel='Y',zlabel='Altitude',title=f"Seed {case['seed']}: {label}");ax.set_box_aspect(room);ax.legend(fontsize=8)
            t=np.arange(1,len(trace['action'])+1)*DT
            ax=fig.add_subplot(len(report['cases']),3,i*3+2);ax.plot(t,trace['target_distance_after'],label='target distance');ax.plot(t,trace['position_after'][:,2],label='altitude');ax.plot(t,trace['clearance_after'],label='collision clearance');ax.axhline(0,color='gray',linewidth=.5);ax.set(xlabel='Simulated seconds',ylabel='Simulation units',title='Geometry through flight');ax.legend(fontsize=8)
            ax=fig.add_subplot(len(report['cases']),3,i*3+3);ax.plot(t,np.linalg.norm(trace['velocity_after'],axis=1),label='speed');ax.axhline(.1,color='gray',linestyle='--',label='idle threshold');ax.plot(t,trace['yaw_rate_after'],label='yaw rate');ax.set(xlabel='Simulated seconds',ylabel='Speed / yaw rate',title='Motion through flight');ax.legend(fontsize=8)
    fig.suptitle('Validation failure replays; selected cases, not a new success-rate estimate')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(output,dpi=140);plt.close(fig)
    return {'plot':str(output.resolve()),'cases':len(report['cases']),'training_invoked':False,'evaluation_invoked':False}
