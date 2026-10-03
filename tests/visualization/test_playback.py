import pytest
from fly_rl.visualization.playback import simulation_speed
from fly_rl.simulation.world import DT

def test_shift_advances_ten_times_as_many_fixed_physics_steps():
    normal=DT*simulation_speed(1.,False)
    accelerated=DT*simulation_speed(1.,True)
    assert round(normal/DT)==1 and round(accelerated/DT)==10
    assert simulation_speed(2.,True)==20.
    for invalid in [0.,-1.,float('nan'),float('inf')]:
        with pytest.raises(ValueError): simulation_speed(invalid)
