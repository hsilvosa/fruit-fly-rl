import numpy as np
import pytest
from fly_rl.simulation.world import FlightWorld
from fly_rl.training.guided_learning import RouteTeacher,fit_actor,actor_mean
from fly_rl.training.learning import BrainEnv,make_policy
from fly_rl.connectome.brain import Brain
from scipy import sparse


@pytest.mark.parametrize('seed',[370000,370001,370002,370003])
def test_coordinated_teacher_traverses_the_original_large_map(seed):
    w=FlightWorld(seed,mode='dense',dynamics='coordinated',map_profile='large')
    teacher=RouteTeacher(w)
    for _ in range(w.episode_limit):
        _,_,terminated,truncated,info=w.step(teacher.action(w))
        if terminated or truncated:break
    assert info['success'] and not info['collision'] and not info['truncated']
    assert len(w.obstacles)==112 and w.map_profile.name=='large'


def test_initial_turn_does_not_climb_off_the_certified_path():
    w=FlightWorld(370003,mode='dense',dynamics='coordinated',map_profile='large');teacher=RouteTeacher(w)
    target=teacher.route[0];w.yaw=np.arctan2(target[1]-w.position[1],target[0]-w.position[0])+np.pi
    action=teacher.action(w)
    assert abs(action[0])<1e-6 and abs(action[2])<1e-6 and abs(action[3])>.9


def test_actor_fit_changes_learned_policy_using_only_brain_features():
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=1,device='cpu')
    env=BrainEnv(brain=brain,batch=1,device='cpu');model=make_policy(env,smoke=True)
    rng=np.random.default_rng(42);x=rng.normal(size=(64,256)).astype(np.float32);y=np.tile([.2,0.,-.1,.4],(64,1)).astype(np.float32)
    before=model.predict(x,deterministic=True)[0]
    result=fit_actor(model,x,y,64,80,rng,batch_size=32)
    after=model.predict(x,deterministic=True)[0]
    assert result['finite_losses'] and result['last_loss']<result['first_loss']
    assert ((after-y)**2).mean()<((before-y)**2).mean()
    assert not hasattr(model.policy,'teacher') and env.observation_space.shape==(256,)


def test_guided_collection_preserves_only_brain_feature_observations_and_counts_steps():
    from fly_rl.training.guided_learning import collect_guided
    from fly_rl.simulation.sensors import SENSOR_V3
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=2,device='cpu',sensor_version=SENSOR_V3)
    env=BrainEnv(brain=brain,batch=2,device='cpu',mode='dense',dynamics='coordinated',sensor_version=SENSOR_V3,map_profile='large',layout_seeds=[370000,370001],history_frames=2)
    model=make_policy(env);x=np.zeros((32,3,256),dtype=np.float32);y=np.zeros((32,4),dtype=np.float32)
    rewards=np.zeros(32,dtype=np.float32);terminals=np.zeros(32,dtype=bool)
    features,teachers,result=collect_guided(env,model,x,y,0,32,np.random.default_rng(42),1.,rewards=rewards,terminals=terminals)
    assert model.num_timesteps==32 and result['teacher_actions']==32 and result['student_actions']==0
    assert np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(rewards).all()
    assert features.shape==(2,3,256) and x.shape[-1]==256 and env.worlds[0].observe().shape==(269,)
    np.testing.assert_array_equal(model._last_obs,features)


def test_guided_critic_targets_stop_at_episode_boundaries_without_actor_changes():
    from fly_rl.training.guided_learning import fit_critic
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=2,device='cpu');env=BrainEnv(brain=brain,batch=2,device='cpu')
    model=make_policy(env);model.gamma=.5;x=np.zeros((4,256),dtype=np.float32)
    before=model.predict(x,deterministic=True)[0].copy()
    result=fit_critic(model,x,np.ones(4),np.array([False,True,True,False]),4,2,10,np.random.default_rng(42),batch_size=4)
    assert result['target_mean']==pytest.approx(1.125) and result['finite_losses']
    np.testing.assert_array_equal(before,model.predict(x,deterministic=True)[0])


def test_recovery_labels_advance_after_a_passage_even_if_student_missed_a_waypoint():
    w=FlightWorld(370004,mode='dense',dynamics='coordinated',map_profile='large');teacher=RouteTeacher(w,recover=True)
    w.position=teacher.route[1].copy();teacher.action(w)
    assert teacher.index>=2


def test_unapproved_guided_draft_never_allocates_brain_or_starts_learning(tmp_path):
    import json
    from fly_rl.training.guided_learning import run_guided
    path=tmp_path/'draft.json';path.write_text(json.dumps({'status':'draft-budget-required'}))
    with pytest.raises(ValueError,match='explicit budget approval'):run_guided(path,'cpu')


def test_critic_returns_do_not_cross_a_manual_reset_between_dagger_rounds():
    from fly_rl.training.guided_learning import fit_critic
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=2,device='cpu')
    env=BrainEnv(brain=brain,batch=2,device='cpu');model=make_policy(env);model.gamma=.5
    x=np.zeros((6,256),dtype=np.float32)
    rewards=np.array([1,1,1,1,10,10],dtype=np.float32)
    terminated=np.zeros(6,dtype=bool);cuts=np.array([False,False,True,True,False,False])
    result=fit_critic(model,x,rewards,terminated,6,2,1,np.random.default_rng(42),batch_size=2,data_boundaries=cuts)
    assert result['target_mean']==pytest.approx(25/6) and result['data_boundary_rows']==2
    assert not terminated.any()  # Data cuts never fabricate a physical failure.


def test_student_only_collection_applies_student_actions_and_resets_teacher_independently():
    from types import SimpleNamespace
    from fly_rl.training.guided_learning import collect_guided
    def world(target):
        return SimpleNamespace(reference_route=[np.zeros(3),np.array(target,dtype=float)],
            position=np.zeros(3),velocity=np.zeros(3),yaw=0.,rotation=lambda:np.eye(3),seed_value=42)
    class Env:
        num_envs=2
        def __init__(self):self.worlds=[world([1,0,0]),world([1,0,0])];self.applied=[]
        def reset(self):return np.zeros((2,256),dtype=np.float32)
        def step(self,actions):
            self.applied.append(actions.copy())
            done=np.array([len(self.applied)==1,False])
            if done[0]:self.worlds[0]=world([0,1,0])
            return np.ones((2,256),dtype=np.float32),np.ones(2),done,[
                {'success':False,'collision':bool(done[0]),'truncated':False},
                {'success':False,'collision':False,'truncated':False}]
    env=Env();action=np.array([.25,0.,.2,.1],dtype=np.float32)
    seen=[]
    def predict(features,deterministic):
        seen.append(features.copy());return np.tile(action,(2,1)),None
    model=SimpleNamespace(num_timesteps=0,predict=predict)
    observations=np.zeros((4,256),dtype=np.float32);targets=np.zeros((4,4),dtype=np.float32)
    trace={'executed_actions':np.zeros((4,4)),'position':np.zeros((4,3)),
           'velocity':np.zeros((4,3)),'yaw':np.zeros(4),'layout_seed':np.zeros(4),
           'teacher_used':np.zeros(4,dtype=bool)}
    _,_,result=collect_guided(env,model,observations,targets,0,4,np.random.default_rng(42),0.,trace=trace)
    for applied in env.applied:np.testing.assert_array_equal(applied,np.tile(action,(2,1)))
    np.testing.assert_array_equal(trace['executed_actions'],np.tile(action,(4,1)))
    assert not trace['teacher_used'].any() and result['teacher_actions']==0 and result['student_actions']==4
    assert result['episode_outcomes']['collision']==1 and model.num_timesteps==4
    assert targets[2,3]==pytest.approx(1.) and targets[3,3]==pytest.approx(0.)
    np.testing.assert_array_equal(observations[:2],seen[0]);np.testing.assert_array_equal(observations[2:],seen[1])
