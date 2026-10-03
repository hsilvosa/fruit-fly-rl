import numpy as np
from fly_rl.simulation.planner import reference_path, path_clear, _visible
from fly_rl.simulation.world import segment_box, RADIUS, FlightWorld


def test_reference_direct_and_detour_are_swept_clear():
    room = [10, 10, 10]; start = [1, 5, 5]; goal = [9, 5, 5]
    direct = reference_path(room, [], start, goal)
    assert direct['status'] == 'direct' and direct['length'] == 8
    boxes = [(np.array([4, 3, 3]), np.array([6, 7, 7]))]
    route = reference_path(room, boxes, start, goal)
    assert route['status'] == 'roadmap' and route['length'] > 8
    assert path_clear(route['points'], room, boxes)
    assert np.array_equal(route['points'][0], start) and np.array_equal(route['points'][-1], goal)
    assert route == dict(route) and not route['global_optimum_claim']
    again = reference_path(room, boxes, start, goal)
    assert route['points'] == again['points'] and route['length'] == again['length']


def test_blocked_room_and_invalid_endpoints_are_not_feasible():
    boxes = [(np.array([4, 0, 0]), np.array([6, 10, 10]))]
    assert reference_path([10]*3, boxes, [1, 5, 5], [9, 5, 5])['length'] is None
    assert reference_path([10]*3, [], [.1, 1, 1], [9, 5, 5])['status'] == 'invalid_endpoint'
    assert not path_clear([[1, 5, 5], [9, 5, 5]], [10]*3, boxes)


def test_vectorized_visibility_matches_exact_collision_rule():
    rng = np.random.default_rng(4)
    starts = rng.uniform(0, 10, (200, 3)); ends = rng.uniform(0, 10, (200, 3))
    ends[:20, 0] = starts[:20, 0]
    boxes = np.array([[[4, 3, 2], [6, 7, 8]], [[1, 1, 1], [2, 2, 2]]], dtype=float)
    radius = RADIUS+.02
    expected = [not any(segment_box(a, b, low-radius, high+radius) for low, high in boxes)
                for a, b in zip(starts, ends)]
    assert np.array_equal(_visible(starts, ends, boxes, radius), expected)


def test_dense_reference_remains_within_bounds_and_body_clearance():
    for seed in [30000, 40000]:
        world = FlightWorld(seed, 'dense')
        route = reference_path(world.room, world.obstacles, world.position, world.target,
                               fallback=world.reference_route)
        assert route['length'] is not None
        assert path_clear(route['points'], world.room, world.obstacles)
        assert route['length'] >= world.distance-1e-6
