"""A bounded curriculum with saved results and success-based stage promotion."""
from fly_rl.atomic_io import replace_file
from pathlib import Path
import json
from datetime import datetime,timezone
from fly_rl.training.learning import train
from fly_rl.training.evaluation import evaluate
from fly_rl.recordings.recording import software_info
from fly_rl.simulation.world import REWARD_VERSION

def iterate(data,device,output,baseline,steps=65536,rounds=3,batch=16,dynamics='legacy'):
    if rounds<1 or rounds>3: raise ValueError('Use one to three bounded rounds')
    folder=Path(output)
    folder.mkdir(parents=True,exist_ok=False)
    state={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),
        'reward_version':REWARD_VERSION,'steps_per_round':steps,'rounds':rounds,'batch':batch,
        'software':software_info(),'baseline_checkpoint':baseline,'results':[],'dynamics':dynamics}
    def save():
        tmp=folder/'iteration.tmp';tmp.write_text(json.dumps(state,indent=2));replace_file(tmp, folder/'iteration.json')
    save()
    try:
        state['baseline']=evaluate(data,device,baseline,mode='obstacles',dynamics=dynamics,allow_transfer=dynamics!='legacy');save()
        mode='near';checkpoint=None
        for i in range(rounds):
            state['current_round']=i+1;state['current_mode']=mode;save()
            destination=folder/f'round-{i+1}'/'policy.zip'
            result=train(data,device,steps,batch,destination,resume=checkpoint,mode=mode,dynamics=dynamics)
            check=evaluate(data,device,destination,mode=mode,dynamics=dynamics)
            obstacle_check=check if mode=='obstacles' else evaluate(data,device,destination,mode='obstacles',dynamics=dynamics)
            state['results'].append({'training':result,'evaluation':check,'obstacles':obstacle_check,
                                     'checkpoint':str(destination)})
            checkpoint=str(destination)
            # Do not advance just because survival or training reward improved.
            if check['success_rate']>=.6:
                mode={'near':'empty','empty':'obstacles','obstacles':'obstacles'}[mode]
            save();print(json.dumps(state['results'][-1]),flush=True)
        if any(r['obstacles']['success_rate']>0 for r in state['results']):
            from fly_rl.training.selection import select_policy
            save();state['selected_policy']=select_policy(folder/'iteration.json',folder/'selected-policy.zip')
        state['status']='completed'
    except BaseException as exc:
        state['status']='failed';state['error']=repr(exc);raise
    finally: state['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return state
