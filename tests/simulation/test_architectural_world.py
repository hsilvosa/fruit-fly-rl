import numpy as np
import pytest
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.world import RADIUS
from fly_rl.navigation.architectural import ArchitecturalController, ArchitecturalPlannerPolicy

SITUATIONS=[(name,index) for name,builder in BUILDERS.items() for index in range(len(builder().situations))]

@pytest.mark.parametrize('name,index',SITUATIONS)
def test_original_situation_observation_decoding_and_independent_reset(name,index):
    world=ArchitecturalWorld(name,index,42)
    values,info=world.reset(seed=42)
    assert values.shape==(3869,) and np.isfinite(values).all()
    controller=ArchitecturalController(world.room)
    goal=controller.update(values)
    expected=(world.target-world.position)@world.rotation()
    expected[2]+=world.position[2]
    assert np.allclose(goal,expected,atol=1e-4)
    assert np.isclose(controller.position[2],world.position[2])
    assert controller.valid(controller.cells(goal))
    assert not world.reference_route and 'reference_route' not in world.snapshot()
    assert info['scene_sha256']==world.scene.fingerprint()
    assert world.mode=='architecture'
    other=ArchitecturalWorld(name,index,42)
    world.velocity.fill(1);world.ticks=99;world.last_action.fill(1)
    reset,_=world.reset(seed=42)
    assert np.array_equal(reset,values)
    assert world.ticks==0 and not world.velocity.any() and not world.last_action.any()
    world.obstacles[0][0][0]+=1
    assert not np.array_equal(world.obstacles[0][0],other.obstacles[0][0])


def test_thin_solid_glass_blocks_ray_and_swept_body():
    world=ArchitecturalWorld('office-floor',seed=42)
    world.reset(seed=42)
    for solid in world.scene.solids:
        if solid.material!='glass':continue
        low,high=np.array(solid.low),np.array(solid.high)
        for axis in range(3):
            start=(low+high)/2;start[axis]=low[axis]-RADIUS-.02
            if (start>RADIUS).all() and (start<world.room-RADIUS).all():break
        else:continue
        break
    else:raise AssertionError('No interior glass fixture')
    world.obstacles=[(low,high)];world.position=start
    direction=np.eye(3)[axis]
    _,ranges=world.cast_rays(direction[None],24.)
    assert np.isclose(ranges[0],RADIUS+.02)
    world.velocity=direction*3;world.yaw=0;world.yaw_rate=0
    _,_,terminated,_,info=world.step(np.zeros(4),observe=False)
    assert terminated and info['collision'] and not info['success']


@pytest.mark.parametrize('name',list(BUILDERS))
def test_room_ceiling_remains_physical_without_visual_ceiling_mesh(name):
    world=ArchitecturalWorld(name,seed=42);world.reset(seed=42)
    world.obstacles=[];world.position=world.room/2;world.position[2]=world.room[2]-RADIUS-.02
    world.velocity=np.array([0.,0.,3.])
    _,_,terminated,_,info=world.step(np.zeros(4),observe=False)
    assert terminated and info['collision']


@pytest.mark.parametrize('index',[True,1.2,-1,1000])
def test_invalid_situation_rejected(index):
    with pytest.raises(ValueError):ArchitecturalWorld('office-floor',index)


def test_policy_reset_and_input_contract():
    policy=ArchitecturalPlannerPolicy((30.,20.,3.4))
    policy.controller.evidence.fill(4)
    policy.reset()
    assert not policy.controller.evidence.any()
    assert policy.specification['controller_version']=='planner-1.4-exp.1'
    assert not policy.specification['learned'] and not policy.specification['reference_route_input']
    for values in [np.zeros((1,9,3869)),np.full((1,9,5669),np.nan)]:
        with pytest.raises(ValueError):policy.predict(values)
