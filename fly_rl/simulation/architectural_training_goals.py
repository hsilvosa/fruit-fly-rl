"""Training-only nearby goal sampling; never a policy action planner."""
import numpy as np
from fly_rl.simulation.world import RADIUS, segment_box


def sample_training_goal(world, distance, rng, attempts=256, margin=.1):
    """Return a body-clear short goal or report no valid sample.

    Geometry is privileged task-generation information only. This function
    does not change the world, choose actions or consume a reference route.
    """
    if not np.isfinite(distance) or not .5 < distance <= 12:
        raise ValueError('Training distance must be in (0.5, 12] meters')
    if type(attempts) is not int or attempts < 1:
        raise ValueError('Invalid sampling budget')
    if not np.isfinite(margin) or margin < 0:
        raise ValueError('Invalid physical clearance margin')
    radius=RADIUS+margin
    start=np.asarray(world.position,dtype=float)
    for _ in range(attempts):
        direction=rng.normal(size=3)
        length=np.linalg.norm(direction)
        if length < 1e-8:continue
        goal=start+direction/length*distance
        if (goal < radius).any() or (goal > world.room-radius).any():continue
        if any(segment_box(start,goal,low-radius,high+radius) for low,high in world.obstacles):continue
        return goal
    raise ValueError('No clear training goal found within sampling budget')
