"""Box-based architectural parts; every part is a set of named axis-aligned collision solids."""
from dataclasses import asdict, dataclass
import hashlib
import json

SCENE_VERSION = 'architecture-0.2'


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
    tags: tuple = ()


@dataclass(frozen=True)
class ArchitecturalScene:
    name: str
    kind: str
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


@dataclass(frozen=True)
class Opening:
    """A gap in a wall from `bottom` to `top`; `fill` closes it with a pane (e.g. glass)."""
    center: float
    width: float
    bottom: float = 0.
    top: float = 2.1
    fill: str = None


def windows(start, stop, spacing, width, bottom=.9, top=2.5, fill='glass'):
    count = int((stop - start) // spacing)
    offset = start + (stop - start - count * spacing) / 2 + spacing / 2
    return [Opening(offset + i * spacing, width, bottom, top, fill) for i in range(count)]


class Builder:
    """Collects solids, rounds coordinates and rejects duplicate names."""

    def __init__(self, size=None):
        self.solids = []
        self._names = set()
        self.size = size

    def clipped(self, name, low, high, material):
        """Add a box trimmed to the scene bounds (for trim that would overhang the map edge)."""
        low = [max(0., v) for v in low]
        high = [min(s, v) for s, v in zip(self.size, high)] if self.size else high
        self.box(name, low, high, material)

    def box(self, name, low, high, material='wall'):
        if name in self._names:
            raise ValueError(f'Duplicate solid name: {name}')
        self._names.add(name)
        self.solids.append(Solid(name, tuple(round(float(v), 4) for v in low),
                                 tuple(round(float(v), 4) for v in high), material))

    # Walls ---------------------------------------------------------------------------------
    def _wall(self, name, a0, a1, c, height, thickness, openings, material, z0, along_x):
        def put(suffix, s0, s1, z_low, z_high, mat, inset=0.):
            if s1 - s0 < 1e-6 or z_high - z_low < 1e-6:
                return
            lo, hi = c + inset, c + thickness - inset
            if along_x:
                self.box(f'{name}-{suffix}', (s0, lo, z_low), (s1, hi, z_high), mat)
            else:
                self.box(f'{name}-{suffix}', (lo, s0, z_low), (hi, s1, z_high), mat)

        cursor, top = a0, z0 + height
        for i, op in enumerate(sorted(openings, key=lambda o: o.center)):
            left, right = op.center - op.width / 2, op.center + op.width / 2
            if left < cursor - 1e-6 or right > a1 + 1e-6:
                raise ValueError(f'Opening {i} does not fit wall {name}')
            put(f'pier-{i}', cursor, left, z0, top, material)
            put(f'sill-{i}', left, right, z0, z0 + op.bottom, material)
            put(f'lintel-{i}', left, right, z0 + op.top, top, material)
            if op.fill:
                pane = max(0., (thickness - .04) / 2)
                put(f'pane-{i}', left, right, z0 + op.bottom, z0 + op.top, op.fill, pane)
            cursor = right
        put('end', cursor, a1, z0, top, material)

    def wall_x(self, name, x0, x1, y, height, thickness=.2, openings=(), material='wall', z0=0.):
        """Wall running east-west; `y` is its south face."""
        self._wall(name, x0, x1, y, height, thickness, openings, material, z0, True)

    def wall_y(self, name, y0, y1, x, height, thickness=.2, openings=(), material='wall', z0=0.):
        """Wall running north-south; `x` is its west face."""
        self._wall(name, y0, y1, x, height, thickness, openings, material, z0, False)

    def shell(self, name, size, t=.2, south=(), north=(), west=(), east=()):
        x, y, z = size
        self.wall_x(f'{name}-south', 0, x, 0, z, t, south)
        self.wall_x(f'{name}-north', 0, x, y - t, z, t, north)
        self.wall_y(f'{name}-west', t, y - t, 0, z, t, west)
        self.wall_y(f'{name}-east', t, y - t, x - t, z, t, east)

    # Furniture -----------------------------------------------------------------------------
    def table(self, name, x, y, w, d, h=.75, material='wood', leg=.06, top=.04, z0=0.):
        self.box(f'{name}-top', (x, y, z0 + h - top), (x + w, y + d, z0 + h), material)
        for i, (lx, ly) in enumerate(((x, y), (x + w - leg, y), (x, y + d - leg), (x + w - leg, y + d - leg))):
            self.box(f'{name}-leg-{i}', (lx, ly, z0), (lx + leg, ly + leg, z0 + h - top), 'metal')

    def chair(self, name, x, y, back, s=.45, z0=0.):
        """Seat block with a backrest on side `back` ('n', 's', 'e' or 'w')."""
        self.box(f'{name}-seat', (x, y, z0), (x + s, y + s, z0 + .46), 'fabric')
        b = .07
        span = {'n': ((x, y + s - b), (x + s, y + s)), 's': ((x, y), (x + s, y + b)),
                'e': ((x + s - b, y), (x + s, y + s)), 'w': ((x, y), (x + b, y + s))}[back]
        self.box(f'{name}-back', (*span[0], z0 + .46), (*span[1], z0 + .9), 'fabric')

    def chairs_around(self, name, x, y, w, d, per_side=2, ends=False):
        """Chairs along the long (x) sides of a table at (x, y, w, d)."""
        n = 0
        for k in range(per_side):
            cx = x + w * (k + .5) / per_side - .225
            self.chair(f'{name}-{n}', cx, y - .55, 's'); n += 1
            self.chair(f'{name}-{n}', cx, y + d + .1, 'n'); n += 1
        if ends:
            cy = y + d / 2 - .225
            self.chair(f'{name}-{n}', x - .55, cy, 'w'); n += 1
            self.chair(f'{name}-{n}', x + w + .1, cy, 'e')

    def sofa(self, name, x, y, w, d, back, h=.85, material='fabric'):
        self.box(f'{name}-seat', (x, y, 0), (x + w, y + d, .42), material)
        a = .22
        if back in 'ns':
            by = (y + d - a, y + d) if back == 'n' else (y, y + a)
            self.box(f'{name}-back', (x, by[0], .42), (x + w, by[1], h), material)
            self.box(f'{name}-arm-0', (x, y, .42), (x + a, y + d, .62), material)
            self.box(f'{name}-arm-1', (x + w - a, y, .42), (x + w, y + d, .62), material)
        else:
            bx = (x + w - a, x + w) if back == 'e' else (x, x + a)
            self.box(f'{name}-back', (bx[0], y, .42), (bx[1], y + d, h), material)
            self.box(f'{name}-arm-0', (x, y, .42), (x + w, y + a, .62), material)
            self.box(f'{name}-arm-1', (x, y + d - a, .42), (x + w, y + d, .62), material)

    def bed(self, name, x, y, w, d, head):
        self.box(f'{name}-base', (x, y, 0), (x + w, y + d, .3), 'wood')
        self.box(f'{name}-mattress', (x + .03, y + .03, .3), (x + w - .03, y + d - .03, .55), 'fabric')
        span = {'n': ((x, y + d - .08), (x + w, y + d)), 's': ((x, y), (x + w, y + .08)),
                'e': ((x + w - .08, y), (x + w, y + d)), 'w': ((x, y), (x + .08, y + d))}[head]
        self.box(f'{name}-headboard', (*span[0], 0), (*span[1], 1.1), 'wood')

    def shelf(self, name, x, y, w, d, h, levels=4, material='wood', z0=0.):
        t = .03
        along_x = w >= d
        if along_x:
            self.box(f'{name}-side-0', (x, y, z0), (x + t, y + d, z0 + h), material)
            self.box(f'{name}-side-1', (x + w - t, y, z0), (x + w, y + d, z0 + h), material)
        else:
            self.box(f'{name}-side-0', (x, y, z0), (x + w, y + t, z0 + h), material)
            self.box(f'{name}-side-1', (x, y + d - t, z0), (x + w, y + d, z0 + h), material)
        for i in range(levels + 1):
            z = z0 + min(h - t, i * h / levels)
            self.box(f'{name}-board-{i}', (x, y, z), (x + w, y + d, z + t), material)

    def pendant(self, name, x, y, ceiling, drop=.9, size=.4, material='metal'):
        """A lamp hanging from the ceiling: thin cord and a shade at the bottom."""
        self.box(f'{name}-cord', (x - .01, y - .01, ceiling - drop + .25), (x + .01, y + .01, ceiling), material)
        self.box(f'{name}-shade', (x - size / 2, y - size / 2, ceiling - drop), (x + size / 2, y + size / 2, ceiling - drop + .25), 'lamp')

    def plant(self, name, x, y, pot=.45, h=1.5):
        self.box(f'{name}-pot', (x, y, 0), (x + pot, y + pot, .45), 'stone')
        g = pot * .25
        self.box(f'{name}-leaves', (x - g, y - g, .45), (x + pot + g, y + pot + g, h), 'vegetation')

    def column(self, name, cx, cy, size, height, z0=0., material='concrete'):
        h = size / 2
        self.box(name, (cx - h, cy - h, z0), (cx + h, cy + h, z0 + height), material)

    def stairs(self, name, x, y, width, run, rise, steps, direction, z0=0., material='concrete'):
        """Solid stair flight; `direction` is the climbing direction ('n', 's', 'e' or 'w')."""
        for i in range(steps):
            z1 = z0 + (i + 1) * rise
            a, b = i * run, (i + 1) * run
            if direction == 'n':
                lo, hi = (x, y + a), (x + width, y + b)
            elif direction == 's':
                lo, hi = (x, y - b), (x + width, y - a)
            elif direction == 'e':
                lo, hi = (x + a, y), (x + b, y + width)
            else:
                lo, hi = (x - b, y), (x - a, y + width)
            self.box(f'{name}-step-{i:02d}', (*lo, z0), (*hi, z1), material)

    def railing(self, name, x0, y0, x1, y1, z, h=1.1, material='glass', t=.05):
        """Balustrade between two points along one axis."""
        if abs(y1 - y0) < 1e-9:
            self.box(name, (min(x0, x1), y0 - t / 2, z), (max(x0, x1), y0 + t / 2, z + h), material)
        else:
            self.box(name, (x0 - t / 2, min(y0, y1), z), (x0 + t / 2, max(y0, y1), z + h), material)

    # Outdoor -------------------------------------------------------------------------------
    def tree(self, name, x, y, trunk_h=2.8, crown=3.2, crown_h=3.6):
        t = .35
        self.box(f'{name}-trunk', (x - t / 2, y - t / 2, 0), (x + t / 2, y + t / 2, trunk_h), 'bark')
        c, s = crown / 2, crown * .32
        self.box(f'{name}-crown', (x - c, y - c, trunk_h), (x + c, y + c, trunk_h + crown_h * .7), 'vegetation')
        self.box(f'{name}-crown-top', (x - s, y - s, trunk_h + crown_h * .7), (x + s, y + s, trunk_h + crown_h), 'vegetation')

    def car(self, name, x, y, along_x=True, length=4.4, width=1.8, material='vehicle'):
        L, W = (length, width) if along_x else (width, length)
        self.box(f'{name}-body', (x, y, .3), (x + L, y + W, .95), material)
        if along_x:
            self.box(f'{name}-cabin', (x + length * .25, y + .1, .95), (x + length * .78, y + W - .1, 1.45), 'glass')
        else:
            self.box(f'{name}-cabin', (x + .1, y + length * .25, .95), (x + W - .1, y + length * .78, 1.45), 'glass')
        r = .32
        corners = ((x + .5, y), (x + L - .5 - r * 2, y), (x + .5, y + W - .22), (x + L - .5 - r * 2, y + W - .22)) if along_x \
            else ((x, y + .5), (x, y + L - .5 - r * 2), (x + W - .22, y + .5), (x + W - .22, y + L - .5 - r * 2))
        for i, (wx, wy) in enumerate(corners):
            hi = (wx + r * 2, wy + .22) if along_x else (wx + .22, wy + r * 2)
            self.box(f'{name}-wheel-{i}', (wx, wy, 0), (*hi, .62), 'rubber')

    def van(self, name, x, y, along_x=True, length=5.6, width=2.1, height=2.7):
        L, W = (length, width) if along_x else (width, length)
        self.box(f'{name}-cargo', (x, y, .35), (x + L * (.72 if along_x else 1), y + W * (1 if along_x else .72), height), 'vehicle')
        if along_x:
            self.box(f'{name}-cab', (x + L * .72, y, .35), (x + L, y + W, height * .78), 'vehicle')
        else:
            self.box(f'{name}-cab', (x, y + W * .72, .35), (x + L, y + W, height * .78), 'vehicle')
        self.box(f'{name}-chassis', (x + .3 if along_x else x, y if along_x else y + .3, 0),
                 (x + L - .3 if along_x else x + L, y + W if along_x else y + W - .3, .35), 'rubber')

    def lamp_post(self, name, x, y, h=6., arm=1.4, direction='n'):
        self.box(f'{name}-pole', (x - .08, y - .08, 0), (x + .08, y + .08, h), 'metal')
        dx, dy = {'n': (0, 1), 's': (0, -1), 'e': (1, 0), 'w': (-1, 0)}[direction]
        ex, ey = x + dx * arm, y + dy * arm
        self.box(f'{name}-arm', (min(x, ex) - .05, min(y, ey) - .05, h - .12), (max(x, ex) + .05, max(y, ey) + .05, h), 'metal')
        self.box(f'{name}-head', (ex - .25, ey - .25, h - .35), (ex + .25, ey + .25, h - .12), 'lamp')

    def traffic_light(self, name, x, y, arm, direction):
        """Pole with a mast arm reaching over the road and signal heads hanging from it."""
        h = 5.8
        self.box(f'{name}-pole', (x - .12, y - .12, 0), (x + .12, y + .12, h), 'metal')
        dx, dy = {'n': (0, 1), 's': (0, -1), 'e': (1, 0), 'w': (-1, 0)}[direction]
        ex, ey = x + dx * arm, y + dy * arm
        self.box(f'{name}-arm', (min(x, ex) - .07, min(y, ey) - .07, h - .2), (max(x, ex) + .07, max(y, ey) + .07, h), 'metal')
        for i, f in enumerate((.55, 1.)):
            sx, sy = x + dx * arm * f, y + dy * arm * f
            self.box(f'{name}-signal-{i}', (sx - .18, sy - .18, h - 1.25), (sx + .18, sy + .18, h - .2), 'signal')
        self.box(f'{name}-pedestrian', (x - .15, y - .15, 2.3), (x + .15, y + .15, 2.9), 'signal')

    def bench(self, name, x, y, along_x=True, length=1.8):
        L, W = (length, .5) if along_x else (.5, length)
        self.box(f'{name}-seat', (x, y, .4), (x + L, y + W, .46), 'wood')
        for i, f in enumerate((.1, .9)):
            if along_x:
                self.box(f'{name}-leg-{i}', (x + L * f - .04, y, 0), (x + L * f + .04, y + W, .4), 'metal')
            else:
                self.box(f'{name}-leg-{i}', (x, y + L * f - .04, 0), (x + W, y + L * f + .04, .4), 'metal')

    def bollards(self, name, x0, y0, x1, y1, count):
        for i in range(count):
            f = i / max(1, count - 1)
            x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            self.box(f'{name}-{i}', (x - .1, y - .1, 0), (x + .1, y + .1, .9), 'metal')

    def umbrella(self, name, x, y, size=2.4, h=2.5):
        self.box(f'{name}-pole', (x - .03, y - .03, 0), (x + .03, y + .03, h), 'metal')
        s = size / 2
        self.box(f'{name}-canopy', (x - s, y - s, h - .25), (x + s, y + s, h), 'canvas')
        self.box(f'{name}-base', (x - .25, y - .25, 0), (x + .25, y + .25, .12), 'stone')

    def building(self, name, x0, y0, x1, y1, height, setback=None, roof_units=0, material='building'):
        """Solid building mass, optional set-back upper storey and rooftop plant."""
        if setback:
            base, inset = setback
            self.box(f'{name}-base', (x0, y0, 0), (x1, y1, base), material)
            self.clipped(f'{name}-cornice', (x0 - .2, y0 - .2, base), (x1 + .2, y1 + .2, base + .3), 'stone')
            self.box(f'{name}-upper', (x0 + inset, y0 + inset, base + .3), (x1 - inset, y1 - inset, height), material)
            roof, rx0, ry0, rx1, ry1 = height, x0 + inset, y0 + inset, x1 - inset, y1 - inset
        else:
            self.box(f'{name}-mass', (x0, y0, 0), (x1, y1, height), material)
            roof, rx0, ry0, rx1, ry1 = height, x0, y0, x1, y1
        p, top = .25, roof + .9
        self.box(f'{name}-parapet-s', (rx0, ry0, roof), (rx1, ry0 + p, top), 'stone')
        self.box(f'{name}-parapet-n', (rx0, ry1 - p, roof), (rx1, ry1, top), 'stone')
        self.box(f'{name}-parapet-w', (rx0, ry0 + p, roof), (rx0 + p, ry1 - p, top), 'stone')
        self.box(f'{name}-parapet-e', (rx1 - p, ry0 + p, roof), (rx1, ry1 - p, top), 'stone')
        for i in range(roof_units):
            ux = rx0 + (rx1 - rx0) * (i + 1) / (roof_units + 1)
            uy = (ry0 + ry1) / 2
            self.box(f'{name}-roof-unit-{i}', (ux - .8, uy - .6, roof), (ux + .8, uy + .6, roof + 1.4), 'metal')

    def balconies(self, name, x0, x1, face_y, facing, floors, spacing=4., depth=1.2, width=2.6, z_first=3.6, floor_h=3.):
        """Slabs with glass railings projecting from an east-west facade."""
        sign = 1 if facing == 'n' else -1
        n = 0
        count = int((x1 - x0) // spacing)
        offset = x0 + (x1 - x0 - count * spacing) / 2 + spacing / 2
        for f in range(floors):
            z = z_first + f * floor_h
            for k in range(count):
                cx = offset + k * spacing
                ya, yb = sorted((face_y, face_y + sign * depth))
                self.box(f'{name}-{n}-slab', (cx - width / 2, ya, z), (cx + width / 2, yb, z + .18), 'concrete')
                rail = yb - .05 if sign > 0 else ya
                self.box(f'{name}-{n}-rail', (cx - width / 2, rail, z + .18), (cx + width / 2, rail + .05, z + 1.1), 'glass')
                n += 1

    def awning(self, name, x0, x1, face_y, facing, depth=1.6, z=2.9, material='canvas'):
        ya, yb = sorted((face_y, face_y + (depth if facing == 'n' else -depth)))
        self.box(name, (x0, ya, z), (x1, yb, z + .25), material)
