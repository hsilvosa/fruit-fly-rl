import copy
import numpy as np
from fly_rl.navigation.architectural import ArchitecturalController
from fly_rl.navigation.architectural_diagnostics import recovery_snapshot


def test_same_cell_deadlock_is_visible_without_mutation():
    controller = ArchitecturalController((16., 12., 2.8))
    controller.position = np.array([.125, .125, 1.125])
    controller.stall_ticks = 200
    controller.debug = dict(target_delta_global=[.01, .01, .01], requested_speed=0., actual_speed=0., found=False)
    before = copy.deepcopy(controller.debug)
    occupancy = controller.evidence.copy()
    result = recovery_snapshot(controller)
    assert result['reference_same_cell']
    assert result['recovery_reason'] == 'reference-in-current-cell'
    assert result['route_found'] is False
    assert controller.debug == before
    assert controller.stall_ticks == 200
    assert np.array_equal(controller.evidence, occupancy)


def test_distinct_reference_and_threshold_are_distinguished():
    controller = ArchitecturalController((16., 12., 2.8))
    controller.position = np.array([.125, .125, 1.125])
    controller.debug = dict(target_delta_global=[1., 0., 0.], requested_speed=0., actual_speed=0.)
    controller.stall_ticks = 24
    assert recovery_snapshot(controller)['recovery_reason'] == 'waiting-for-stall-threshold'
    controller.stall_ticks = 25
    assert recovery_snapshot(controller)['recovery_reason'] == 'eligible-for-reference-veto'
    controller.debug['actual_speed'] = 1.
    assert recovery_snapshot(controller)['recovery_reason'] == 'not-stalled'
