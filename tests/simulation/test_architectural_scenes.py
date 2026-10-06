"""Asset geometry checks; no brain or learned policy is instantiated."""
from dataclasses import replace
import json

import numpy as np
import pytest

from fly_rl.simulation.architectural_scenes import BUILDERS, Situation, Solid, export_scene, validate
from fly_rl.simulation.world import ray_box
from fly_rl.visualization.architecture_preview import write_preview


@pytest.mark.parametrize('name', BUILDERS)
def test_drafts_have_clear_reference_routes_and_stable_hashes(name):
    scene = BUILDERS[name]()
    assert validate(scene)['passed']
    assert scene.fingerprint() == BUILDERS[name]().fingerprint()
    assert len(scene.situations) >= 2


def test_door_has_real_opening_and_solid_lintel():
    scene = BUILDERS['apartment']()
    origin = np.array([3., 5., 1.3])
    direction = np.array([0., 1., 0.])
    distances = [ray_box(origin, direction, np.array(b.low), np.array(b.high)) for b in scene.solids]
    assert min(distances) > 2.5  # First doorway at y=5.8 is open.
    origin[2] = 2.4
    assert min(ray_box(origin, direction, np.array(b.low), np.array(b.high)) for b in scene.solids) == pytest.approx(.8)


def test_blocked_route_is_rejected():
    scene = BUILDERS['office-floor']()
    obstruction = Solid('block-route', (3., 5., 0.), (5., 6., 3.), 'wall')
    with pytest.raises(ValueError, match='Blocked route'):
        validate(replace(scene, solids=scene.solids + (obstruction,)))


def test_invalid_bounds_and_routes_are_rejected():
    scene = BUILDERS['office-floor']()
    with pytest.raises(ValueError, match='outside scene'):
        validate(replace(scene, solids=scene.solids + (Solid('bad', (-1., 0., 0.), (1., 1., 1.), 'wall'),)))
    with pytest.raises(ValueError, match='flight bounds'):
        validate(replace(scene, situations=(Situation('bad', ((0., 0., 0.), (1., 1., 1.)), ''),)))


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


def test_preview_is_self_contained_and_labels_reference(tmp_path):
    path = tmp_path / 'index.html'
    write_preview([BUILDERS['office-floor']()], path)
    text = path.read_text()
    assert '__SCENES__' not in text
    assert 'not a flown route' in text
    assert '<script src=' not in text
    assert 'getContext(\'2d\')' in text
