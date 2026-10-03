import numpy as np
from fly_rl.simulation.world import FlightWorld,RADIUS,ROOM,segment_box

def test_progress_beats_standing_and_timeout_is_failure():
    still=FlightWorld(10,mode='near');moving=FlightWorld(10,mode='near')
    wait=still.step(np.zeros(4))[1]
    progress=moving.step([1,0,0,0])[1]
    assert wait<0 and progress>wait
    still.ticks=599
    _,reward,ended,truncated,_=still.step(np.zeros(4))
    assert truncated and not ended and reward<=-5

def test_curriculum_near_targets_are_clear_and_reproducible():
    for seed in range(30):
        world=FlightWorld(seed,mode='near');other=FlightWorld(seed,mode='near')
        assert np.array_equal(world.target,other.target) and not world.obstacles
        assert (world.target>RADIUS).all() and (world.target<ROOM-RADIUS).all()
        assert 1.5<=world.distance<=3.3
        assert not any(segment_box(world.position,world.target,l-RADIUS,h+RADIUS) for l,h in world.obstacles)
