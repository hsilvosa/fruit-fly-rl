"""Original architectural drafts; CPU geometry only, separate from flight benchmarks."""
import json
from pathlib import Path

import numpy as np

from fly_rl.simulation.architectural_layouts import BUILDERS
from fly_rl.simulation.architectural_parts import SCENE_VERSION, ArchitecturalScene, Opening, Situation, Solid
from fly_rl.simulation.world import RADIUS, segment_box

__all__ = ['BUILDERS', 'SCENE_VERSION', 'ArchitecturalScene', 'MATERIALS', 'Opening', 'Situation', 'Solid',
           'export_scene', 'route_clearance', 'validate']

KINDS = ('interior', 'outdoor', 'mixed')

# Diffuse colors shared by the OBJ materials, the gallery and the interactive preview.
MATERIALS = {
    'wall': (.80, .80, .77), 'glass': (.55, .76, .84), 'wood': (.64, .45, .28), 'furniture': (.36, .50, .56),
    'fabric': (.42, .47, .62), 'stone': (.70, .66, .60), 'ceramic': (.92, .92, .90), 'metal': (.38, .41, .45),
    'screen': (.12, .13, .15), 'lamp': (.98, .86, .52), 'concrete': (.66, .66, .64), 'building': (.74, .71, .66),
    'vehicle': (.72, .30, .24), 'bus': (.86, .62, .16), 'rubber': (.15, .15, .16), 'vegetation': (.33, .55, .30),
    'bark': (.42, .31, .22), 'signal': (.18, .20, .18), 'canvas': (.86, .40, .30), 'water': (.36, .62, .80),
    'rack': (.24, .42, .70), 'cargo': (.80, .64, .40), 'art': (.85, .30, .35), 'ground': (.86, .86, .83),
}


def _point_box_distance(points, low, high):
    gap = np.maximum(np.maximum(low - points, points - high), 0.)
    return np.linalg.norm(gap, axis=1)


def route_clearance(scene, route, step=.02):
    """Smallest sampled distance from the body centre to any solid or scene bound along a route."""
    route = np.asarray(route, dtype=float)
    pieces = []
    for a, b in zip(route, route[1:]):
        n = max(2, int(np.ceil(np.linalg.norm(b - a) / step)) + 1)
        pieces.append(a + np.linspace(0., 1., n)[:, None] * (b - a))
    points = np.concatenate(pieces)
    size = np.asarray(scene.size, dtype=float)
    best = np.minimum(points, size - points).min()
    for solid in scene.solids:
        best = min(best, _point_box_distance(points, np.asarray(solid.low), np.asarray(solid.high)).min())
    return float(best)


def validate(scene, clearance=.2):
    """Check geometry and a feasible polyline, not controller arrival or generalization."""
    size = np.asarray(scene.size, dtype=float)
    if size.shape != (3,) or not np.isfinite(size).all() or (size <= 0).any():
        raise ValueError('Invalid scene dimensions')
    if scene.kind not in KINDS:
        raise ValueError(f'Unknown scene kind: {scene.kind}')
    names = set()
    for solid in scene.solids:
        low, high = np.asarray(solid.low), np.asarray(solid.high)
        if solid.name in names or not np.isfinite([low, high]).all() or (low >= high).any():
            raise ValueError(f'Invalid or duplicate solid: {solid.name}')
        if (low < 0).any() or (high > size).any():
            raise ValueError(f'Solid outside scene: {solid.name}')
        if solid.material not in MATERIALS:
            raise ValueError(f'Unknown material: {solid.name} / {solid.material}')
        names.add(solid.name)
    margin = RADIUS + clearance
    if not np.isfinite(clearance) or clearance < 0:
        raise ValueError('Invalid clearance')
    situations = []
    situation_names = set()
    for situation in scene.situations:
        route = np.asarray(situation.route, dtype=float)
        if situation.name in situation_names or route.ndim != 2 or route.shape[1] != 3 or len(route) < 2:
            raise ValueError('Invalid or duplicate situation')
        situation_names.add(situation.name)
        if not np.isfinite(route).all() or (route < margin).any() or (route > size - margin).any():
            raise ValueError(f'Route outside flight bounds: {situation.name}')
        for a, b in zip(route, route[1:]):
            for solid in scene.solids:
                if segment_box(a, b, np.asarray(solid.low) - margin, np.asarray(solid.high) + margin):
                    raise ValueError(f'Blocked route: {situation.name} / {solid.name}')
        situations.append({'name': situation.name, 'tags': list(situation.tags),
                           'route_length_m': round(float(np.linalg.norm(np.diff(route, axis=0), axis=1).sum()), 4),
                           'climb_m': round(float(np.ptp(route[:, 2])), 4),
                           'min_sampled_clearance_m': round(route_clearance(scene, route), 3)})
    materials = {}
    for solid in scene.solids:
        materials[solid.material] = materials.get(solid.material, 0) + 1
    return {'passed': True, 'name': scene.name, 'kind': scene.kind, 'geometry_sha256': scene.fingerprint(),
            'collision_boxes': len(scene.solids), 'materials': dict(sorted(materials.items())),
            'body_radius_m': RADIUS, 'extra_clearance_m': clearance, 'situations': situations,
            'claim': 'Static geometric feasibility only; not a dynamically executable flight certificate'}


def export_scene(scene, output):
    """Write a portable OBJ/MTL pair and authoritative collision/scenario JSON."""
    report = validate(scene)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    payload = scene.to_dict()
    payload['validation'] = report
    (output / f'{scene.name}.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8', newline='\n')
    used = sorted({s.material for s in scene.solids} | {'ground'})
    mtl = ''
    for name in used:
        r, g, b = MATERIALS[name]
        mtl += f'newmtl {name}\nKd {r} {g} {b}\n'
        if name == 'glass':
            mtl += 'd 0.35\n'
        mtl += '\n'
    (output / f'{scene.name}.mtl').write_text(mtl.rstrip() + '\n', encoding='utf-8', newline='\n')
    lines = [f'# {SCENE_VERSION}; original synthetic architecture, meters, Z up', f'mtllib {scene.name}.mtl']
    index = 1
    faces = ((3, 7, 5, 1), (6, 8, 4, 2), (5, 6, 2, 1), (4, 8, 7, 3), (2, 4, 3, 1), (7, 8, 6, 5))
    for solid in scene.solids:
        lines += [f'o {solid.name}', f'usemtl {solid.material}']
        lines += [f'v {x:g} {y:g} {z:g}' for x in (solid.low[0], solid.high[0])
                  for y in (solid.low[1], solid.high[1]) for z in (solid.low[2], solid.high[2])]
        lines += ['f ' + ' '.join(str(index + v - 1) for v in face) for face in faces]
        index += 8
    x, y, _ = scene.size
    lines += ['o ground-visual-only', 'usemtl ground', 'v 0 0 0', f'v {x:g} 0 0',
              f'v {x:g} {y:g} 0', f'v 0 {y:g} 0', f'f {index} {index+1} {index+2} {index+3}']
    (output / f'{scene.name}.obj').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    return report
