"""Export measured training curves and evaluation results without training."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

def plot_training(iteration,output,independent=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    iteration=Path(iteration).resolve();state=json.loads(iteration.read_text())
    rows=[];sources=[]
    for number,result in enumerate(state['results'],1):
        folder=Path(result['checkpoint']).resolve().parent
        for source in sorted(folder.glob('tensorboard/**/events.out*')):
            accumulator=EventAccumulator(str(source),size_guidance={'scalars':0}).Reload()
            sources.append({'file':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
            for tag in accumulator.Tags()['scalars']:
                for item in accumulator.Scalars(tag):
                    if not np.isfinite(item.value): raise ValueError('Nonfinite metric: '+tag)
                    rows.append({'round':number,'mode':result['training']['room_mode'],
                        'tag':tag,'step':item.step,'value':item.value,'wall_time':item.wall_time,'source':str(source)})
    if not rows: raise ValueError('No TensorBoard scalars found')
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    csv_path=output.with_suffix('.csv')
    with csv_path.open('w',newline='',encoding='utf8') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    colors=['#2563eb','#d97706','#059669']
    labels={'near':'Cercanos, sin obstáculos','empty':'Lejanos, sin obstáculos','obstacles':'Con obstáculos'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f8fafc',
        'axes.facecolor':'white','axes.labelcolor':'#334155','text.color':'#0f172a'})
    fig,axes=plt.subplots(2,2,figsize=(13.5,9))
    def curve(ax,tag,multiplier=1):
        for i,result in enumerate(state['results'],1):
            values=sorted([r for r in rows if r['round']==i and r['tag']==tag],key=lambda r:r['step'])
            if values:
                ax.plot([r['step'] for r in values],[r['value']*multiplier for r in values],
                    color=colors[(i-1)%len(colors)],marker='o',markersize=4,lw=2,
                    label=labels[result['training']['room_mode']])
        for result in state['results'][:-1]:
            ax.axvline(result['training']['transitions'],color='#94a3b8',ls=':',lw=1)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x/1000:.0f}k'))
        ax.set_xlabel('Transiciones acumuladas del modelo nuevo')
        ax.grid(axis='y',alpha=.15)
    curve(axes[0,0],'rollout/ep_rew_mean')
    axes[0,0].set_title('Recompensa durante el entrenamiento',loc='left',pad=12)
    axes[0,0].set_ylabel('Recompensa media por episodio')
    axes[0,0].legend(fontsize=8,frameon=False,loc='lower right')
    curve(axes[1,0],'rollout/ep_len_mean',.05)
    axes[1,0].set_title('Duración media de los episodios',loc='left',pad=12)
    axes[1,0].set_ylabel('Segundos simulados')
    axes[1,0].axhline(30,color='#64748b',ls='--',lw=1)
    curve(axes[1,1],'train/value_loss')
    axes[1,1].set_yscale('log')
    axes[1,1].set_title('Error del estimador de recompensa futura',loc='left',pad=12)
    axes[1,1].set_ylabel('Pérdida del crítico (escala logarítmica)')
    evaluations=[r['obstacles'] for r in state['results']]
    names=[f'Ronda {i+1}\n{r["training"]["transitions"]:,} pasos'.replace(',','.') for i,r in enumerate(state['results'])]
    if independent:
        check=json.loads(Path(independent).read_text())
        evaluations.append(check);names.append('Otras semillas\nModelo final')
    ax=axes[0,1];positions=np.arange(len(evaluations))
    bars=ax.bar(positions,[e['success_rate']*100 for e in evaluations],width=.58,
        color=[colors[i%3] for i in range(len(evaluations))])
    for bar,e in zip(bars,evaluations):
        successes=sum(r['success'] for r in e['episodes']);count=len(e['episodes'])
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+3,
            f'{successes}/{count} · {e["success_rate"]*100:g}%',ha='center',fontsize=10)
    ax.set_xticks(positions,names,fontsize=9);ax.set_ylim(0,116)
    ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('Llegadas al objetivo (%)')
    ax.set_title('Evaluación en habitaciones con obstáculos',loc='left',pad=12);ax.grid(axis='y',alpha=.15)
    fig.suptitle('Cómo aprendió a llegar al objetivo',x=.06,y=.98,ha='left',fontsize=23,fontweight='bold')
    total=f'{state["results"][-1]["training"]["transitions"]:,}'.replace(',','.')
    fig.text(.06,.935,f'MaleCNS completo · PPO · {total} transiciones · métricas guardadas, sin nuevo entrenamiento',fontsize=11,color='#475569')
    fig.subplots_adjust(top=.86,bottom=.20,left=.075,right=.965,hspace=.43,wspace=.29)
    fig.text(.06,.045,'Las curvas de entrenamiento usan medias móviles de episodios. La dificultad cambia entre rondas.\n'
        'El éxito se midió al final de cada ronda; no se registró una tasa de éxito continua.\n'
        'Las otras semillas generan habitaciones nuevas del mismo generador; no prueban todos los tipos de entorno.',
        fontsize=9,color='#475569',linespacing=1.6)
    fig.savefig(output,dpi=160);fig.savefig(output.with_suffix('.svg'));plt.close(fig)
    report={'plot':str(output),'svg':str(output.with_suffix('.svg')),'csv':str(csv_path),
        'scalar_rows':len(rows),'source_files':sources,'iteration':str(iteration),
        'independent_evaluation':str(independent) if independent else None,'training_invoked':False}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return report
