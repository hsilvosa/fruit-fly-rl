"""Asset geometry checks; no brain or learned policy is instantiated."""
from dataclasses import replace
import json

import numpy as np
import pytest

from fly_rl.simulation.architectural_parts import Builder, Opening
from fly_rl.simulation.architectural_scenes import BUILDERS, Situation, Solid, export_scene, route_clearance, validate
from fly_rl.simulation.world import RADIUS, ray_box
from fly_rl.visualization.architecture_preview import write_preview


def _first_hit(scene, origin, direction):
    origin, direction = np.asarray(origin, float), np.asarray(direction, float)
    return min(ray_box(origin, direction, np.array(b.low), np.array(b.high)) for b in scene.solids)


@pytest.mark.parametrize('name', BUILDERS)
def test_drafts_have_clear_reference_routes_and_stable_hashes(name):
    scene = BUILDERS[name]()
    report = validate(scene)
    assert report['passed']
    assert scene.fingerprint() == BUILDERS[name]().fingerprint()
    assert len(scene.situations) >= 3
    assert all(s.tags for s in scene.situations)
    for item in report['situations']:
        assert item['min_sampled_clearance_m'] >= RADIUS + .2 - 1e-6


def test_collection_covers_interior_outdoor_and_mixed_scenes():
    kinds = {BUILDERS[name]().kind for name in BUILDERS}
    assert kinds == {'interior', 'outdoor', 'mixed'}
    assert len(BUILDERS) >= 6


def test_door_has_real_opening_and_solid_lintel():
    scene = BUILDERS['apartment']()
    # Bedroom-two door in the hall wall at y=8.4, centred on x=11 and 2.1 m high.
    assert _first_hit(scene, (11., 7.78, 1.3), (0., 1., 0.)) > 1.5
    assert _first_hit(scene, (11., 7.78, 2.4), (0., 1., 0.)) == pytest.approx(.62)


def test_glass_panes_and_walls_block_rays():
    scene = BUILDERS['office-floor']()
    # The meeting-room glass front at y=13 blocks a ray beside its doorway.
    assert _first_hit(scene, (4.5, 12., 1.4), (0., 1., 0.)) == pytest.approx(1.)
    names = {b.name: b.material for b in scene.solids}
    assert names['shell-south-pane-0'] == 'glass'


def test_atrium_routes_change_level_and_bridge_spans_void():
    scene = BUILDERS['atrium']()
    report = validate(scene)
    climbs = {s['name']: s['climb_m'] for s in report['situations']}
    assert climbs['void-climb-to-top-gallery'] > 9
    # Directly below the bridge deck there is open void down to the ground.
    assert _first_hit(scene, (15., 12., 8.6), (0., 0., -1.)) > 8.


def test_wall_openings_must_fit():
    b = Builder()
    with pytest.raises(ValueError, match='does not fit'):
        b.wall_x('w', 0., 2., 0., 3., openings=(Opening(1.9, 1.),))
    with pytest.raises(ValueError, match='Duplicate'):
        b.box('a', (0, 0, 0), (1, 1, 1)); b.box('a', (0, 0, 0), (1, 1, 1))


def test_blocked_route_is_rejected():
    scene = BUILDERS['office-floor']()
    obstruction = Solid('block-route', (2., 5., 0.), (3., 6., 3.), 'wall')
    with pytest.raises(ValueError, match='Blocked route'):
        validate(replace(scene, solids=scene.solids + (obstruction,)))


def test_invalid_bounds_routes_and_materials_are_rejected():
    scene = BUILDERS['office-floor']()
    with pytest.raises(ValueError, match='outside scene'):
        validate(replace(scene, solids=scene.solids + (Solid('bad', (-1., 0., 0.), (1., 1., 1.), 'wall'),)))
    with pytest.raises(ValueError, match='flight bounds'):
        validate(replace(scene, situations=(Situation('bad', ((0., 0., 0.), (1., 1., 1.)), ''),)))
    with pytest.raises(ValueError, match='Unknown material'):
        validate(replace(scene, solids=scene.solids + (Solid('odd', (1., 1., 0.), (2., 2., 1.), 'unobtainium'),)))


def test_route_clearance_matches_nearest_surface():
    scene = BUILDERS['warehouse']()
    # The aisle between racks at y 8.3 and 11.4 is centred at 9.85, 1.55 m from each; the floor is 2 m below.
    assert route_clearance(scene, ((5., 9.85, 2.), (20., 9.85, 2.))) == pytest.approx(1.55, abs=1e-6)


def test_export_preserves_geometry_and_valid_obj_indices(tmp_path):
    scene = BUILDERS['street-block']()
    export_scene(scene, tmp_path)
    payload = json.loads((tmp_path / 'street-block.json').read_text())
    assert payload['validation']['geometry_sha256'] == scene.fingerprint()
    lines = (tmp_path / 'street-block.obj').read_text().splitlines()
    vertices = sum(line.startswith('v ') for line in lines)
    faces = [tuple(map(int, line[2:].split())) for line in lines if line.startswith('f ')]
    assert vertices == len(scene.solids) * 8 + 4
    assert len(faces) == len(scene.solids) * 6 + 1
    assert all(1 <= i <= vertices for face in faces for i in face)
    points = np.array([list(map(float, line[2:].split())) for line in lines if line.startswith('v ')])
    for index, solid in enumerate(scene.solids):
        center = (np.asarray(solid.low) + np.asarray(solid.high)) / 2
        for face in faces[index * 6:index * 6 + 6]:
            p = points[np.array(face) - 1]
            normal = np.cross(p[1] - p[0], p[2] - p[0])
            assert normal @ (p.mean(axis=0) - center) > 0  # Outward winding for mesh importers.
    for solid in scene.solids:
        assert f'o {solid.name}' in lines
    mtl = (tmp_path / 'street-block.mtl').read_text()
    assert all(f'newmtl {m}' in mtl for m in {s.material for s in scene.solids})


def test_preview_is_self_contained_and_labels_reference(tmp_path):
    path = tmp_path / 'index.html'
    write_preview([BUILDERS['office-floor'](), BUILDERS['atrium']()], path)
    text = path.read_text(encoding='utf-8')
    assert '__SCENES__' not in text and '__COLORS__' not in text
    assert 'not a flown route' in text
    assert '<script src=' not in text
    assert 'getContext(\'2d\')' in text
    assert 'min_sampled_clearance_m' in text
