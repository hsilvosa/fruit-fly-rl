import json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.simulation.world import FlightWorld
from fly_rl.connectome.brain import Brain,FEATURES

def test_coordinated_flight_reduces_sideways_motion_and_resets_turn():
    old=FlightWorld(0,dynamics='legacy');new=FlightWorld(0,dynamics='coordinated')
    old.obstacles=[];new.obstacles=[]
    old.position=new.position=np.array([6.,6.,3.])
    for _ in range(10):
        old.step([0,1,0,0]);new.step([0,1,0,0])
    assert np.linalg.norm(new.velocity)<np.linalg.norm(old.velocity)*.25
    assert new.yaw_rate>0 and new.yaw!=0 and np.isfinite(new.bank)
    new.reset();assert new.yaw_rate==0 and new.bank==0 and new.pitch==0

def test_dynamics_mismatch_is_rejected_before_checkpoint_loading(tmp_path):
    from fly_rl.training.learning import BrainEnv,load_model
    brain=Brain(matrix=sparse.eye(8,format='csr',dtype=np.float32),device='cpu')
    env=BrainEnv(brain=brain,dynamics='coordinated')
    path=tmp_path/'policy.zip';path.with_suffix('.json').write_text(json.dumps({'fingerprint':brain.fingerprint}))
    with pytest.raises(ValueError,match='dynamics mismatch'): load_model(path,brain,env)

def test_neural_ids_and_local_sensitivity_match_finite_difference(tmp_path):
    import torch
    from fly_rl.visualization.neural_view import NeuralInspector
    from fly_rl.training.learning import BrainEnv,make_policy
    brain=Brain(matrix=sparse.eye(12,format='csr',dtype=np.float32)*.9,device='cpu')
    env=BrainEnv(brain=brain,device='cpu');features=env.reset();policy=make_policy(env,True)
    folder=tmp_path/'processed';folder.mkdir();ids=np.arange(100,112)
    np.save(folder/'neuron_ids.npy',ids)
    inspector=NeuralInspector(brain,tmp_path)
    result=inspector.sample(policy,features,np.array([.1,0,0,0]),1)
    assert result['phase']=='before_action' and not result['causal_claim']
    assert all(r['neuron_id'] in ids for r in result['activity'])
    row=result['local_sensitivity'][0];index=int(row['neuron_id']-100)
    epsilon=.001;direction=np.zeros((1,FEATURES),np.float32)
    direction[0,inspector.bucket[index]]=inspector.sign[index]*epsilon
    def mean(x):
        with torch.no_grad(): return policy.policy.get_distribution(torch.tensor(x)).distribution.mean[0,0].clamp(-1,1).item()
    finite=(mean(features+direction)-mean(features-direction))/(2*epsilon)
    assert np.isclose(row['value'],finite,rtol=.05,atol=1e-5)
    inspector.reset();assert inspector.previous is None


@pytest.mark.parametrize('readout', ['grouped', 'contrast'])
def test_history_sensitivity_uses_actual_reader_finite_difference(tmp_path, readout):
    import torch
    from types import SimpleNamespace
    from fly_rl.connectome.readout import InputGroupedBrain
    from fly_rl.connectome.innovation import ContrastActivityBrain
    from fly_rl.simulation.sensors import SENSOR_V6
    from fly_rl.visualization.neural_view import NeuralInspector
    torch.set_num_threads(2)
    # Algebra unit graph only. Viewer and flight verification use all neurons.
    n=400 if readout=='grouped' else 30000
    cls=InputGroupedBrain if readout=='grouped' else ContrastActivityBrain
    brain=cls(matrix=sparse.eye(n, format='csr', dtype=np.float32)*.2,
              device='cpu', sensor_version=SENSOR_V6)
    sensors=np.full((1,3869),.3,np.float32)
    brain.step(sensors);previous=brain.state.clone();current_features=brain.step(sensors)
    features=np.zeros((1,9,3869),np.float32);features[:,-1]=current_features
    folder=tmp_path/'processed';folder.mkdir();np.save(folder/'neuron_ids.npy',np.arange(n)+100000)

    class LinearActor(torch.nn.Module):
        def __init__(self):
            super().__init__()
            weights=torch.zeros(3869);weights[[256,269,1600,3100]]=.1
            self.weights=torch.nn.Parameter(weights)
        def get_distribution(self,x):
            scalar=x[:,-1]@self.weights
            mean=torch.stack([scalar,scalar*0,scalar*0,scalar*0],1)
            return SimpleNamespace(distribution=SimpleNamespace(mean=mean))
    actor=LinearActor();model=SimpleNamespace(policy=actor)
    inspector=NeuralInspector(brain,tmp_path);result=inspector.sample(model,features,[1,0,0,0],1)
    index=int(result['local_sensitivity'][0]['neuron_id'])-100000
    analytic=result['local_sensitivity'][0]['value'];saved=brain.state.clone();epsilon=.01
    def perturbed(sign):
        if readout=='grouped':
            brain.state=saved.clone();brain.state[index,0]+=sign*epsilon
            values=brain.read_activity()
        else:
            drive=torch.atanh((2*saved-previous).clamp(-1+1e-6,1-1e-6))
            drive[index,0]+=sign*epsilon
            states=.5*previous+.5*torch.tanh(drive)
            values=brain.reconstruct_activity(previous,states)
        x=features.copy();x[:,-1]=values
        with torch.no_grad():return actor.get_distribution(torch.tensor(x)).distribution.mean[0,0].item()
    finite=(perturbed(1)-perturbed(-1))/(2*epsilon)
    assert np.isclose(analytic,finite,rtol=.03,atol=2e-6)
    assert result['sensitivity_basis']==('recurrent_neuron_state' if readout=='grouped' else 'reconstructed_neuronal_drive')
    assert np.isfinite(inspector.sensitivity).all()
