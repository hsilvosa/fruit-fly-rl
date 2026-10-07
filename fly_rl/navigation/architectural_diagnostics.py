"""Read-only recovery evidence for architectural development checks."""
import numpy as np


def recovery_snapshot(controller):
    """Describe recovery eligibility without changing controller state or occupancy."""
    debug = controller.debug
    current = controller.cells(controller.position)
    delta = debug.get('target_delta_global')
    reference = None if delta is None else controller.cells(controller.position + np.asarray(delta))
    stalled = (delta is not None and debug.get('requested_speed', 1.) < .02
               and debug.get('actual_speed', 1.) < .05)
    same_cell = reference is not None and np.array_equal(reference, current)
    valid = reference is not None and controller.valid(reference)
    if not stalled:
        reason = 'not-stalled'
    elif controller.stall_ticks < 25:
        reason = 'waiting-for-stall-threshold'
    elif not valid:
        reason = 'reference-outside-grid'
    elif same_cell:
        reason = 'reference-in-current-cell'
    else:
        reason = 'eligible-for-reference-veto'
    return dict(current_cell=np.asarray(current).tolist(),
                reference_cell=None if reference is None else np.asarray(reference).tolist(),
                reference_same_cell=bool(same_cell), reference_valid=bool(valid),
                recovery_reason=reason, route_found=debug.get('found'),
                braking_clearance=debug.get('ahead'),
                momentum_braking_clearance=debug.get('momentum_ahead'))
