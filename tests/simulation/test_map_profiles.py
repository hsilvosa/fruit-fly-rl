import json
import numpy as np
import pytest
from fly_rl.simulation.world import FlightWorld, RADIUS, ray_box, segment_box
from fly_rl.simulation.map_profiles import PROFILES, MapProfile, resolve_profile, difficulty_metrics, segments_hit_boxes
from fly_rl.simulation.planner import path_clear
from fly_rl.training.suites import layout_hash, prepare_suite, load_suite


@pytest.mark.parametrize('profile', list(PROFILES))
def test_profiles_are_deterministic_bounded_and_geometrically_feasible(profile):
    p = PROFILES[profile]
    for seed in range(8):
        w = FlightWorld(seed, 'dense', map_profile=profile)
        same = FlightWorld(seed, 'dense', map_profile=p.to_dict())
        assert layout_hash(w) == layout_hash(same)
        assert len(w.obstacles) == p.obstacle_count and np.array_equal(w.room, p.room_size)
        assert path_clear(w.reference_route, w.room, w.obstacles, p.route_clearance)
        assert w.distance >= p.minimum_separation
        for low, high in w.obstacles:
            assert (low >= 0).all() and (high <= w.room).all() and (low < high).all()
        assert w.observation_space.contains(w.observe())
        metrics = difficulty_metrics(w)
        assert metrics['certified_body_clearance_linf_lower_bound'] >= p.route_clearance-1e-5
        assert metrics['episode_seconds'] >= 2*metrics['certified_route_length']/1.5+15.-1e-8
        if p.name in ['passages', 'large', 'maze']:
            assert metrics['direct_path_blocked'] and metrics['certified_route_turns_over_15deg'] >= 2*p.wall_count
        # The certificate and descriptors are not additional controller observations.
        before = w.observe()
        w.reference_route = [[0, 0, 0], w.room]
        assert np.array_equal(before, w.observe())


def test_legacy_profile_preserves_pinned_geometry_and_timeout():
    for seed in range(16):
        a, b = FlightWorld(seed, 'dense'), FlightWorld(seed, 'dense', map_profile='dense-v3')
        assert layout_hash(a) == layout_hash(b) and a.episode_limit == b.episode_limit == 1200
    assert resolve_profile(None) is None


def test_custom_profiles_roundtrip_and_reject_impossible_apertures(tmp_path):
    config = PROFILES['large'].to_dict()
    config.update(name='custom', obstacle_count=96, aperture_width=3.8)
    path = tmp_path/'profile.json'
    path.write_text(json.dumps(config))
    assert resolve_profile(str(path)) == MapProfile(**config)
    with pytest.raises(ValueError, match='clearance'):
        MapProfile('too-narrow', (32, 32, 12), 24, 2, .5, .5)
    with pytest.raises(ValueError, match='Obstacle'):
        MapProfile('unbounded', (32, 32, 12), 999)
    with pytest.raises(ValueError, match='dense'):
        FlightWorld(map_profile='large')


def test_profile_rays_match_scalar_boxes_and_gaps_are_real():
    w = FlightWorld(5, 'dense', map_profile='large')
    directions, distances = w.rays()
    for d, actual in zip(directions, distances):
        walls = [((w.room[k] if d[k] > 0 else 0)-w.position[k])/d[k] for k in range(3) if abs(d[k]) > 1e-9]
        expected = min([8.]+[v for v in walls if v >= 0]+[ray_box(w.position, d, low, high) for low, high in w.obstacles])
        assert actual == pytest.approx(expected)
    left, right, below, above = w.obstacles[:4]
    x = left[0][0]
    y = (left[1][1]+right[0][1])/2
    z = (below[1][2]+above[0][2])/2
    assert not segments_hit_boxes([[x-1, y, z], [x+2, y, z]], w.obstacles[:4], RADIUS+.1)
    assert segments_hit_boxes([[x-1, 1, z], [x+2, 1, z]], w.obstacles[:4], RADIUS)
    # Exercise swept collision against an actual partition, not just the certificate helper.
    w.position = np.array([x-RADIUS-.02, 1., z])
    w.yaw = 0.; w.velocity = np.array([3., 0., 0.]); w.distance = float(np.linalg.norm(w.target-w.position))
    _, _, done, _, info = w.step([0, 0, 0, 0])
    assert done and info['collision'] and not info['success']


def test_grid_union_does_not_double_count_overlaps():
    w = FlightWorld(0, 'dense', map_profile='open')
    w.obstacles = [(np.array([0., 0., 0.]), w.room/2)]*2
    w.reference_route = [np.array([20., 20., 8.]), np.array([28., 28., 8.])]
    metrics = difficulty_metrics(w)
    assert metrics['occupancy_grid_fraction'] == pytest.approx(.125)
    assert metrics['box_volume_fraction_sum'] == pytest.approx(.25)


def test_profiled_suite_freezes_all_training_variants_and_detects_tampering(tmp_path):
    path = tmp_path/'suite.json'
    prepare_suite(path, 100, 200, 300, 2, 2, 2, map_profile='large', training_profiles=['open', 'passages', 'large'])
    suite = load_suite(path)
    assert suite['schema_version'] == 3 and len(suite['training_variants']) == 2
    assert all(p['seeds'] == [start, start+1] for p, start in zip(suite['splits'].values(), [100, 200, 300]))
    with pytest.raises(ValueError, match='reuse'):
        prepare_suite(tmp_path/'reused.json', 100, 500, 600, 2, 2, 2, [path], map_profile='maze')
    suite['training_variants'][0]['geometry_sha256'][0] = '0'*64
    path.write_text(json.dumps(suite))
    with pytest.raises(ValueError, match='variant fingerprint'):
        load_suite(path)


def test_profile_configuration_mutation_invalidates_suite(tmp_path):
    path = tmp_path/'suite.json'
    prepare_suite(path, 100, 200, 300, 1, 1, 1, map_profile='large')
    suite = load_suite(path)
    suite['map_profile']['aperture_width'] = 3.6
    path.write_text(json.dumps(suite))
    with pytest.raises(ValueError, match='fingerprint'):
        load_suite(path)


def test_maze_has_side_branches_with_a_real_entry_and_closed_outer_boundary():
    w=FlightWorld(10,'dense',map_profile='maze')
    assert w.map_profile.branch_count==len(w.branch_openings)==4
    assert difficulty_metrics(w)['dead_end_branches']==4
    assert len(w.branch_routes)==4 and all(path_clear(route,w.room,w.obstacles,w.map_profile.route_clearance) for route in w.branch_routes)
    for opening in w.branch_openings:
        x,y,z=opening['center'];side=opening['side']
        boxes=[w.obstacles[i] for i in opening['box_indices']]
        # Door joins the ordinary chamber to a wing bounded by both adjacent partitions.
        assert not segments_hit_boxes([[x,y-1,z],[x,y+1,z]],boxes,RADIUS+.05)
        low_x=boxes[0][0][0]
        assert segments_hit_boxes([[low_x+.2,y-1,z],[low_x+.2,y+1,z]],boxes,RADIUS)
        endpoints=[box for box in w.obstacles[:4*w.map_profile.wall_count] if box[0][0] <= low_x <= box[1][0]]
        assert endpoints
    # Older serialized maze configurations still reconstruct their branch-free geometry.
    old=PROFILES['maze'].to_dict();old.pop('branch_count')
    assert resolve_profile(old).branch_count==0
