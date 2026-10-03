"""Deterministic clearance-aware visibility roadmap; evaluation use only."""
import itertools
import time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from fly_rl.simulation.world import RADIUS, segment_box

PLANNER_VERSION = 'visibility-corners-v2'


def path_clear(points, room, obstacles, clearance=0.02):
    points = np.asarray(points, dtype=float)
    radius = RADIUS + clearance
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        return False
    if (points < radius).any() or (points > np.asarray(room) - radius).any():
        return False
    boxes=np.asarray(obstacles,dtype=float).reshape(-1,2,3)
    if not np.isfinite(boxes).all(): return False
    return not any(segment_box(a, b, low-radius, high+radius)
                   for a, b in zip(points, points[1:]) for low, high in boxes) and not any(
                   ((points>=low-radius)&(points<=high+radius)).all(axis=1).any() for low,high in boxes)


def _visible(starts, ends, boxes, radius):
    """Vectorized exact segment/AABB test, including blocked diagonal edges."""
    if not len(boxes):
        return np.ones(len(starts), dtype=bool)
    delta = (ends-starts)[:, None, :]
    low = boxes[None, :, 0, :] - radius - starts[:, None, :]
    high = boxes[None, :, 1, :] + radius - starts[:, None, :]
    parallel = np.abs(delta) < 1e-12
    a = np.divide(low, delta, out=np.zeros_like(low), where=~parallel)
    b = np.divide(high, delta, out=np.zeros_like(high), where=~parallel)
    near = np.where(parallel, -np.inf, np.minimum(a, b)).max(axis=2)
    far = np.where(parallel, np.inf, np.maximum(a, b)).min(axis=2)
    outside = (parallel & ((low > 0) | (high < 0))).any(axis=2)
    hit = (np.maximum(near, 0) <= np.minimum(far, 1)) & ~outside
    return ~hit.any(axis=1)


def reference_path(room, obstacles, start, target, clearance=0.02, fallback=None):
    """Shortest path on sampled corners, with separately labeled certified fallback.

    This geometric reference has no inertia/turning constraints and is not a
    global continuous-space optimum. It must never enter policy observations.
    """
    started = time.perf_counter()
    if not np.isfinite(clearance) or clearance < 0:
        raise ValueError('Clearance must be finite and nonnegative')
    room = np.asarray(room, dtype=float)
    boxes = np.asarray(obstacles, dtype=float).reshape(-1, 2, 3)
    start, target = np.asarray(start, dtype=float), np.asarray(target, dtype=float)
    radius = RADIUS + clearance
    if room.shape!=(3,) or start.shape!=(3,) or target.shape!=(3,) or not np.isfinite(room).all() or not np.isfinite(boxes).all() or (boxes[:,0]>boxes[:,1]).any():
        raise ValueError('Invalid reference geometry')
    result = {'version': PLANNER_VERSION, 'clearance': clearance, 'body_radius': RADIUS,
              'global_optimum_claim': False, 'dynamic_feasibility_claim': False}
    if not path_clear([start, start], room, boxes, clearance) or not path_clear([target, target], room, boxes, clearance):
        return dict(result, status='invalid_endpoint', points=None, length=None, elapsed_seconds=time.perf_counter()-started)
    if path_clear([start, target], room, boxes, clearance):
        points = np.array([start, target]); status = 'direct'
    else:
        corners = [np.where(sign, high+radius+1e-4, low-radius-1e-4)
                   for low, high in boxes for sign in itertools.product([False, True], repeat=3)]
        candidates = np.asarray(corners)
        valid = ((candidates >= radius) & (candidates <= room-radius)).all(axis=1)
        valid &= _visible(candidates, candidates, boxes, radius)
        nodes = np.vstack([start, target, candidates[valid]])
        weights = np.zeros((len(nodes), len(nodes)))
        left, right = np.triu_indices(len(nodes), 1)
        for offset in range(0, len(left), 256):
            i, j = left[offset:offset+256], right[offset:offset+256]
            visible = _visible(nodes[i], nodes[j], boxes, radius)
            lengths = np.linalg.norm(nodes[i]-nodes[j], axis=1)
            weights[i[visible], j[visible]] = lengths[visible]
            weights[j[visible], i[visible]] = lengths[visible]
        distances, previous = dijkstra(csr_matrix(weights), directed=False, indices=0, return_predecessors=True)
        if np.isfinite(distances[1]):
            indices = [1]
            while indices[-1] != 0:
                indices.append(int(previous[indices[-1]]))
            points = nodes[indices[::-1]]; status = 'roadmap'
        elif fallback is not None and len(fallback)>=2 and np.allclose(fallback[0],start,rtol=0,atol=1e-9) and np.allclose(fallback[-1],target,rtol=0,atol=1e-9) and path_clear(fallback, room, boxes, clearance):
            points = np.asarray(fallback); status = 'certified_fallback'
        else:
            return dict(result, status='no_sampled_route', points=None, length=None,
                        elapsed_seconds=time.perf_counter()-started)
    assert path_clear(points, room, boxes, clearance)
    return dict(result, status=status, points=points.tolist(),
                length=float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()),
                elapsed_seconds=time.perf_counter()-started)
