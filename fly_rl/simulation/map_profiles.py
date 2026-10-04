"""Versioned procedural geometry; the certified route never enters observations."""
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import numpy as np

PROFILE_VERSION = 'rooms-v4-profiled-passages'
METRICS_VERSION = 'geometry-v1-grid32-linf'


@dataclass(frozen=True)
class MapProfile:
    name: str
    room_size: tuple
    obstacle_count: int
    wall_count: int = 0
    aperture_width: float = 4.
    aperture_height: float = 4.
    route_clearance: float = .25
    minimum_separation: float = 14.
    branch_count: int = 0
    version: str = PROFILE_VERSION

    def __post_init__(self):
        object.__setattr__(self, 'room_size', tuple(self.room_size))
        if self.version != PROFILE_VERSION or not isinstance(self.name, str) or not self.name:
            raise ValueError('Invalid map profile name/version')
        if len(self.room_size) != 3 or not np.isfinite(self.room_size).all() or any(v < 10 or v > 96 for v in self.room_size):
            raise ValueError('Room dimensions must be finite and between 10 and 96')
        if type(self.obstacle_count) is not int or not 0 <= self.obstacle_count <= 256:
            raise ValueError('Obstacle count must be between 0 and 256')
        if type(self.wall_count) is not int or not 0 <= self.wall_count <= 10 or self.obstacle_count < 4*self.wall_count:
            raise ValueError('Each partition needs four boxes; use at most ten partitions')
        if type(self.branch_count) is not int or not 0 <= self.branch_count <= max(0, self.wall_count-1) or self.obstacle_count < 4*(self.wall_count+self.branch_count):
            raise ValueError('Dead-end branches require interior partition cells and four boxes each')
        if self.branch_count and (self.room_size[0]-8)/(self.wall_count+1)-.7 <= self.aperture_width+2*(.16+self.route_clearance):
            raise ValueError('Branch openings need enough partition-cell width')
        values = [self.aperture_width, self.aperture_height, self.route_clearance, self.minimum_separation]
        if not np.isfinite(values).all() or not .05 <= self.route_clearance <= .35:
            raise ValueError('Invalid aperture or clearance')
        if not .5 <= self.aperture_width <= self.room_size[1]*.4 or not .5 <= self.aperture_height <= self.room_size[2]*.4:
            raise ValueError('Apertures must fit the alternating partition positions')
        if min(self.aperture_width, self.aperture_height) <= 2*(.16+self.route_clearance):
            raise ValueError('Aperture cannot fit the certified body clearance')
        if not 1 <= self.minimum_separation <= self.room_size[0]-4:
            raise ValueError('Invalid minimum endpoint separation')
        if self.wall_count and (self.room_size[0]-8)/(self.wall_count+1) < 2.:
            raise ValueError('Partitions need enough longitudinal spacing')

    def to_dict(self):
        result = asdict(self)
        result['room_size'] = list(self.room_size)
        # Zero preserves already-frozen profile dictionaries and suites.
        if not self.branch_count:result.pop('branch_count')
        return result


PROFILES = {
    'gate-near': MapProfile('gate-near', (12, 12, 10), 4, 1, 4.5, 4., minimum_separation=5.),
    'gate-long': MapProfile('gate-long', (24, 12, 10), 4, 1, 4.5, 4., minimum_separation=14.),
    'gate-two': MapProfile('gate-two', (24, 12, 10), 8, 2, 4.5, 4., minimum_separation=14.),
    'passages-wide': MapProfile('passages-wide', (32, 32, 12), 12, 3, 8., 4.8),
    'large-wide': MapProfile('large-wide', (48, 48, 16), 20, 5, 8., 6., .22, 24.),
    'large-narrow': MapProfile('large-narrow', (48, 48, 16), 20, 5, 3.2, 3.2, .22, 24.),
    'open': MapProfile('open', (32, 32, 12), 24),
    'passages': MapProfile('passages', (32, 32, 12), 64, 3, 4., 4.),
    'large': MapProfile('large', (48, 48, 16), 112, 5, 3.2, 3.2, .22, 24.),
    'maze': MapProfile('maze', (64, 64, 20), 192, 8, 2.4, 2.8, .18, 36., branch_count=4),
}


def resolve_profile(value):
    """None/dense-v3 preserves the original generator, including its RNG stream."""
    if value is None or (isinstance(value, str) and value == 'dense-v3'):
        return None
    if isinstance(value, MapProfile):
        return value
    if isinstance(value, dict):
        return MapProfile(**value)
    if isinstance(value, str) and value in PROFILES:
        return PROFILES[value]
    if isinstance(value, (str, Path)) and Path(value).is_file():
        return MapProfile(**json.loads(Path(value).read_text(encoding='utf-8')))
    raise ValueError('Unknown map profile; use dense-v3, open, passages, large, maze, or a profile JSON file')


def segments_hit_boxes(route, boxes, margin=0.):
    """Vectorized closed slab intersection for every route segment and box."""
    route = np.asarray(route, dtype=float)
    if not len(boxes):
        return False
    boxes = np.asarray(boxes, dtype=float)
    starts = route[:-1, None, :]
    delta = np.diff(route, axis=0)[:, None, :]
    low = boxes[None, :, 0, :] - margin - starts
    high = boxes[None, :, 1, :] + margin - starts
    parallel = np.abs(delta) < 1e-12
    a = np.divide(low, delta, out=np.zeros_like(low), where=~parallel)
    b = np.divide(high, delta, out=np.zeros_like(high), where=~parallel)
    near = np.where(parallel, -np.inf, np.minimum(a, b)).max(axis=2)
    far = np.where(parallel, np.inf, np.maximum(a, b)).min(axis=2)
    outside = (parallel & ((low > 0) | (high < 0))).any(axis=2)
    return bool(((np.maximum(near, 0) <= np.minimum(far, 1)) & ~outside).any())


def generate_layout(world, profile):
    from fly_rl.simulation.world import RADIUS, DT
    rng, room = world.rng, world.room
    margin = RADIUS + profile.route_clearance
    world.branch_routes=[]
    world.branch_openings=[]
    if profile.wall_count:
        world.position = np.array([2., rng.uniform(.35, .65)*room[1], rng.uniform(.35, .65)*room[2]])
        world.target = np.array([room[0]-2., rng.uniform(.35, .65)*room[1], rng.uniform(.35, .65)*room[2]])
        route, boxes = [world.position.copy()], []
        # Alternate openings in both horizontal position and altitude.
        phase = int(rng.integers(2))
        partitions=np.linspace(4., room[0]-4., profile.wall_count+2)[1:-1]
        for i, x in enumerate(partitions):
            side = (i+phase) % 2
            y = room[1]*((.3 if side == 0 else .7)+rng.uniform(-.025, .025))
            z = room[2]*((.3 if side == 0 else .7)+rng.uniform(-.015, .015))
            yl, yh = y-profile.aperture_width/2, y+profile.aperture_width/2
            zl, zh = z-profile.aperture_height/2, z+profile.aperture_height/2
            boxes.extend([
                (np.array([x-.35, 0., 0.]), np.array([x+.35, yl, room[2]])),
                (np.array([x-.35, yh, 0.]), np.array([x+.35, room[1], room[2]])),
                (np.array([x-.35, yl, 0.]), np.array([x+.35, yh, zl])),
                (np.array([x-.35, yl, zh]), np.array([x+.35, yh, room[2]])),
            ])
            route.extend([np.array([x-.9, y, z]), np.array([x+.9, y, z])])
        route.append(world.target.copy())
        # Reversing endpoints keeps both longitudinal flight directions in the task.
        if rng.random() < .5:
            route.reverse()
            world.position, world.target = route[0].copy(), route[-1].copy()
        world.branch_openings=[]
        # Each selected interior chamber gains a side wing with one doorway.
        # Neighboring partitions and the outer room wall close its other sides.
        cells=np.linspace(0,profile.wall_count-2,profile.branch_count,dtype=int) if profile.branch_count else []
        for j, cell in enumerate(cells):
            xl,xh=partitions[cell]+.35,partitions[cell+1]-.35
            x=(xl+xh)/2; side=(j+phase)%2
            y=room[1]*(.2 if side==0 else .8)
            z=room[2]*(.3 if side==0 else .7)
            al,ah=x-profile.aperture_width/2,x+profile.aperture_width/2
            zl,zh=z-profile.aperture_height/2,z+profile.aperture_height/2
            branch=[
                (np.array([xl,y-.35,0.]),np.array([al,y+.35,room[2]])),
                (np.array([ah,y-.35,0.]),np.array([xh,y+.35,room[2]])),
                (np.array([al,y-.35,0.]),np.array([ah,y+.35,zl])),
                (np.array([al,y-.35,zh]),np.array([ah,y+.35,room[2]])),
            ]
            boxes.extend(branch)
            world.branch_openings.append({'center':[float(x),float(y),float(z)],
                'side':int(side),'cell':int(cell),'box_indices':list(range(len(boxes)-4,len(boxes)))})
            main=next(a+(b-a)*((x-a[0])/(b[0]-a[0])) for a,b in zip(route,route[1:])
                      if abs(b[0]-a[0])>1e-12 and min(a[0],b[0])<=x<=max(a[0],b[0]))
            direction=-1 if side==0 else 1
            world.branch_routes.append([main,np.array([x,y-direction,z]),np.array([x,y+direction,z]),
                                        np.array([x,1. if side==0 else room[1]-1.,z])])
    else:
        world.position = rng.uniform([2., 2., 1.5], room-[2., 2., 1.5])
        for _ in range(1000):
            world.target = rng.uniform([2., 2., 1.5], room-[2., 2., 1.5])
            if np.linalg.norm(world.target-world.position) >= profile.minimum_separation:
                break
        else:
            raise RuntimeError('Could not place profile endpoints')
        y, z = rng.uniform(2., room[1]-2.), rng.uniform(1.5, room[2]-1.5)
        route = [world.position.copy(), np.array([world.position[0], y, z]),
                 np.array([world.target[0], y, z]), world.target.copy()]
        boxes = []
    if segments_hit_boxes(route, boxes, margin):
        raise RuntimeError('Partition route violates the declared clearance')
    if any(segments_hit_boxes(branch,boxes,margin) for branch in world.branch_routes):
        raise RuntimeError('Dead-end entry route violates the declared clearance')
    for _ in range(10000):
        if len(boxes) == profile.obstacle_count:
            break
        half = rng.uniform([.35, .35, .5], [1.8, 1.8, min(3.5, room[2]/4)])
        center = rng.uniform(half+.3, room-half-.3)
        candidate = (center-half, center+half)
        if any(segments_hit_boxes(path,[candidate],margin) for path in [route]+world.branch_routes):
            continue
        # Preserve solid barriers and make summed box volume an exact union volume.
        if any(np.all(candidate[0] < high) and np.all(candidate[1] > low) for low, high in boxes):
            continue
        boxes.append(candidate)
    if len(boxes) != profile.obstacle_count:
        raise RuntimeError('Could not fill profile without blocking its certified route')
    world.obstacles, world.reference_route = boxes, route
    length = float(np.linalg.norm(np.diff(route, axis=0), axis=1).sum())
    # Generous, explicit geometric allowance; not a dynamic feasibility proof.
    world.episode_limit = int(np.ceil(max(60., 2*length/1.5+15.)/DT))


def difficulty_metrics(world):
    """Geometry descriptors, not a learned difficulty score or an optimal route."""
    from fly_rl.simulation.world import RADIUS, DT
    room, route = world.room, np.asarray(world.reference_route or [world.position, world.target])
    delta = np.diff(route, axis=0)
    lengths = np.linalg.norm(delta, axis=1)
    direct = float(np.linalg.norm(world.target-world.position))
    boxes = np.asarray(world.obstacles)
    grid_shape = (32, 32, 16)
    centers = [(np.arange(n)+.5)*size/n for n, size in zip(grid_shape, room)]
    occupied = np.zeros(grid_shape, dtype=bool)
    for low, high in world.obstacles:
        slices = tuple(slice(np.searchsorted(c, l), np.searchsorted(c, h, side='right'))
                       for c, l, h in zip(centers, low, high))
        occupied[slices] = True
    low = 0.
    high = float(np.minimum(route, room-route).min())
    for _ in range(20):
        mid = (low+high)/2
        if segments_hit_boxes(route, boxes, mid):
            high = mid
        else:
            low = mid
    unit = delta/np.maximum(lengths[:, None], 1e-12)
    angles = np.arccos(np.clip((unit[:-1]*unit[1:]).sum(axis=1), -1, 1))
    profile = world.map_profile
    result = {
        'version': METRICS_VERSION, 'profile': profile.name if profile else 'dense-v3',
        'room_size': room.tolist(), 'obstacle_count': len(world.obstacles),
        'occupancy_grid_fraction': float(occupied.mean()), 'occupancy_grid_shape': list(grid_shape),
        'box_volume_fraction_sum': float(np.prod(boxes[:, 1]-boxes[:, 0], axis=1).sum()/np.prod(room)) if len(boxes) else 0.,
        'endpoint_distance': direct, 'certified_route_length': float(lengths.sum()),
        'certified_route_over_direct': float(lengths.sum()/max(direct, 1e-12)),
        'certified_route_turns_over_15deg': int((angles > np.deg2rad(15)).sum()),
        'certified_route_vertical_travel': float(np.abs(delta[:, 2]).sum()),
        'certified_body_clearance_linf_lower_bound': float(max(0., low-RADIUS)),
        'direct_path_blocked': segments_hit_boxes([world.position, world.target], boxes, RADIUS),
        'aperture_size': [profile.aperture_width, profile.aperture_height] if profile and profile.wall_count else None,
        'episode_limit': world.episode_limit, 'episode_seconds': world.episode_limit*DT,
        'route_is_optimal': False, 'dynamic_feasibility_proven': False,
    }
    if profile and profile.branch_count:result['dead_end_branches']=profile.branch_count
    return result
