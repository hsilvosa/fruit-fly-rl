"""Original architectural drafts; CPU geometry only, separate from flight benchmarks."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np

from fly_rl.simulation.world import RADIUS, segment_box

SCENE_VERSION = 'architecture-0.1'


@dataclass(frozen=True)
class Solid:
    name: str
    low: tuple
    high: tuple
    material: str


@dataclass(frozen=True)
class Situation:
    name: str
    route: tuple
    description: str


@dataclass(frozen=True)
class ArchitecturalScene:
    name: str
    size: tuple
    solids: tuple
    situations: tuple
    description: str

    def to_dict(self):
        return {'schema': SCENE_VERSION, 'units': 'meters', 'origin': 'southwest ground corner',
                'axes': 'x east, y north, z up', 'license': 'MIT',
                'provenance': 'Original project design; not a reconstruction of a real location',
                **asdict(self)}

    def fingerprint(self):
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload.encode()).hexdigest()


def _solid(name, low, high, material='wall'):
    return Solid(name, tuple(low), tuple(high), material)


def _door_wall(name, x0, x1, y, height, door_x, width=1.2, door_height=2.3):
    """A wall with an actual gap and lintel, rather than a painted doorway."""
    left, right = door_x - width / 2, door_x + width / 2
    return [_solid(name + '-left', (x0, y, 0), (left, y + .2, height)),
            _solid(name + '-right', (right, y, 0), (x1, y + .2, height)),
            _solid(name + '-lintel', (left, y, door_height), (right, y + .2, height))]


def _interior_shell(size):
    x, y, z = size
    return [_solid('south-wall', (0, 0, 0), (x, .2, z)),
            _solid('north-wall', (0, y - .2, 0), (x, y, z)),
            _solid('west-wall', (0, .2, 0), (.2, y - .2, z)),
            _solid('east-wall', (x - .2, .2, 0), (x, y - .2, z))]


def office():
    size = (24., 18., 3.6)
    solids = _interior_shell(size)
    for row, y in enumerate((7.8, 10.)):
        for column in range(3):
            x = column * 8.
            solids += _door_wall(f'office-{row}-{column}-door', x + .2, x + 7.8, y, size[2], x + 4)
    for x in (7.8, 15.8):
        for a, b in ((.2, 7.8), (10.2, 17.8)):
            solids.append(_solid(f'partition-{x}-{a}', (x, a, 0), (x + .2, b, size[2])))
    for column in range(3):
        x = column * 8.
        for y in (2., 14.):
            solids.append(_solid(f'desk-{column}-{y}', (x + 1., y, 0), (x + 3., y + .9, .78), 'wood'))
            solids.append(_solid(f'cabinet-{column}-{y}', (x + 5.8, y, 0), (x + 7.3, y + .5, 2.), 'furniture'))
    routes = (
        Situation('room-to-room', ((4., 3., 1.5), (4., 9., 1.5), (20., 9., 1.5), (20., 15., 1.5)),
                  'Leave a furnished office, follow the corridor and enter a different room.'),
        Situation('corridor-to-office', ((1., 9., 1.5), (12., 9., 1.5), (12., 13., 1.5)),
                  'Find a doorway along the corridor and enter the middle north office.'),
    )
    return ArchitecturalScene('office-floor', size, tuple(solids), routes,
                              'Six furnished offices connected by a 2.2 m corridor and 1.2 m doors.')


def apartment():
    size = (18., 14., 3.2)
    solids = _interior_shell(size)
    for row, y in enumerate((5.8, 8.)):
        for column in range(3):
            x = column * 6.
            solids += _door_wall(f'apartment-{row}-{column}-door', x + .2, x + 5.8, y, size[2], x + 3., .9, 2.1)
    for x in (5.8, 11.8):
        for a, b in ((.2, 5.8), (8.2, 13.8)):
            solids.append(_solid(f'partition-{x}-{a}', (x, a, 0), (x + .2, b, size[2])))
    for column in range(3):
        x = column * 6.
        solids += [_solid(f'bed-{column}', (x + .6, .8, 0), (x + 2.3, 3., .65), 'furniture'),
                   _solid(f'wardrobe-{column}', (x + 4.4, .5, 0), (x + 5.5, 2., 2.3), 'wood'),
                   _solid(f'table-{column}', (x + .8, 10.5, 0), (x + 2.4, 12., .9), 'wood'),
                   _solid(f'sofa-{column}', (x + 4.2, 10., 0), (x + 5.5, 13., 1.), 'furniture')]
    routes = (
        Situation('bedroom-to-living-room', ((3., 3., 1.3), (3., 7., 1.3), (15., 7., 1.3), (15., 11., 1.3)),
                  'Cross two narrow residential doorways and a hallway.'),
        Situation('low-to-high', ((9., 3., .6), (9., 7., 1.3), (9., 10., 1.8)),
                  'Change altitude while moving between furnished rooms.'),
    )
    return ArchitecturalScene('apartment', size, tuple(solids), routes,
                              'A residential interior with six rooms, 0.9 m doors and low furniture.')


def street():
    size = (60., 40., 12.)
    solids = []
    # An east-west street with a north-south intersection at x=30.
    for side, y0, y1 in (('south', 0., 12.), ('north', 28., 40.)):
        for index, (a, b, h) in enumerate(((0., 12., 7.), (13., 25., 10.), (35., 46., 8.), (47., 60., 11.))):
            solids.append(_solid(f'{side}-building-{index}', (a, y0, 0), (b, y1, h), 'building'))
    for index, x in enumerate((5., 16., 40., 51.)):
        solids.append(_solid(f'parked-car-{index}', (x, 14., 0), (x + 4.3, 15.8, 1.5), 'vehicle'))
        solids.append(_solid(f'planter-{index}', (x, 25., 0), (x + 1.2, 26.2, .65), 'wood'))
        solids.append(_solid(f'hedge-{index}', (x + .15, 25.15, .65), (x + 1.05, 26.05, 2.), 'vegetation'))
    for index, x in enumerate((10., 22., 38., 49.)):
        solids.append(_solid(f'light-pole-{index}', (x, 26.8, 0), (x + .2, 27., 5.), 'metal'))
    solids.append(_solid('delivery-van', (37., 22., 0), (42., 24., 2.6), 'vehicle'))
    routes = (
        Situation('street-traverse', ((2., 20., 1.5), (30., 20., 1.5), (58., 20., 1.5)),
                  'Traverse a street with parked vehicles and a crossing.'),
        Situation('intersection-turn', ((2., 20., 1.5), (30., 20., 1.5), (30., 37., 1.5)),
                  'Turn at the intersection into the perpendicular street.'),
        Situation('vehicle-clearance', ((37., 20., 1.5), (39., 20., 3.2), (39., 25., 3.2)),
                  'Climb above a parked delivery van; no moving traffic is simulated.'),
    )
    return ArchitecturalScene('street-block', size, tuple(solids), routes,
                              'A static street intersection, eight buildings, parked vehicles and street furniture.')


BUILDERS = {'office-floor': office, 'apartment': apartment, 'street-block': street}


def validate(scene, clearance=.2):
    """Check geometry and a feasible polyline, not controller arrival or generalization."""
    size = np.asarray(scene.size, dtype=float)
    if size.shape != (3,) or not np.isfinite(size).all() or (size <= 0).any():
        raise ValueError('Invalid scene dimensions')
    names = set()
    for solid in scene.solids:
        low, high = np.asarray(solid.low), np.asarray(solid.high)
        if solid.name in names or not np.isfinite([low, high]).all() or (low >= high).any():
            raise ValueError(f'Invalid or duplicate solid: {solid.name}')
        if (low < 0).any() or (high > size).any():
            raise ValueError(f'Solid outside scene: {solid.name}')
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
        situations.append({'name': situation.name, 'route_length_m': float(np.linalg.norm(np.diff(route, axis=0), axis=1).sum())})
    return {'passed': True, 'geometry_sha256': scene.fingerprint(), 'collision_boxes': len(scene.solids),
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
    colors = {'wall': (.72, .75, .78), 'wood': (.61, .40, .24), 'furniture': (.32, .52, .62),
              'building': (.67, .70, .74), 'vehicle': (.75, .34, .25), 'vegetation': (.29, .51, .30),
              'metal': (.28, .31, .35), 'ground': (.82, .83, .80)}
    mtl = ''.join(f'newmtl {name}\nKd {r} {g} {b}\n\n' for name, (r, g, b) in colors.items())
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
