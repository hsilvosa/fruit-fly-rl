"""Original architectural layouts for revision 0.2: interiors, multi-level spaces and streets."""
from fly_rl.simulation.architectural_parts import ArchitecturalScene, Builder, Opening, Situation, windows


def _scene(name, kind, size, b, situations, description):
    return ArchitecturalScene(name, kind, tuple(float(v) for v in size), tuple(b.solids), tuple(situations), description)


def office():
    size = (30., 20., 3.4)
    b = Builder()
    glazing = windows(.2, 29.8, 3., 2.4, .9, 2.6)
    b.shell('shell', size, south=glazing, north=windows(10., 29.8, 3., 2.4, .9, 2.6))
    # Glass meeting rooms in the north-west, separated by a solid wall.
    b.wall_x('meeting-front', .2, 10., 13., size[2], .1, (Opening(2.6, 1., 0, 2.2), Opening(7.6, 1., 0, 2.2)), 'glass')
    b.wall_y('meeting-divider', 13.1, 19.8, 5., size[2], .12)
    b.wall_y('meeting-side', 13.1, 19.8, 10., size[2], .1, (), 'glass')
    for room, x in (('a', 1.4), ('b', 6.4)):
        b.table(f'meeting-{room}-table', x, 16.2, 2.4, 1.1)
        b.chairs_around(f'meeting-{room}-chair', x, 16.2, 2.4, 1.1, 2, ends=True)
        b.pendant(f'meeting-{room}-lamp', x + 1.2, 16.75, size[2], .9, .6)
        b.box(f'meeting-{room}-screen', (x - .2, 19.72, 1.), (x + 2.6, 19.8, 2.4), 'screen')
    # Reception and waiting area.
    b.box('reception-desk', (6., 8.5, 0), (9.5, 9.2, 1.1), 'wood')
    b.box('reception-desk-return', (8.8, 6.8, 0), (9.5, 8.5, 1.1), 'wood')
    b.sofa('waiting-sofa-0', 5.5, 1., 2.2, .9, 's')
    b.sofa('waiting-sofa-1', 5.5, 3.6, 2.2, .9, 'n')
    b.table('waiting-table', 6., 2.2, 1.2, .9, .42)
    for i, (x, y) in enumerate(((.5, .5), (9.2, .5), (.5, 12.2))):
        b.plant(f'reception-plant-{i}', x, y)
    # Structural columns.
    for i, (x, y) in enumerate(((10., 6.5), (16., 6.5), (22., 6.5), (16., 13.5), (22., 13.5))):
        b.column(f'column-{i}', x, y, .5, size[2])
    # Open-plan desk clusters: four desks, cross-shaped privacy screens and one chair per desk.
    for row, y in enumerate((2., 9.2, 15.6)):
        for col, x in enumerate((11.2, 17.6)):
            name = f'cluster-{row}-{col}'
            for k, (dx, dy) in enumerate(((0, 0), (1.6, 0), (0, .8), (1.6, .8))):
                b.table(f'{name}-desk-{k}', x + dx, y + dy, 1.6, .8)
                b.box(f'{name}-monitor-{k}', (x + dx + .55, y + dy + (.55 if dy == 0 else .2), .75),
                      (x + dx + 1.05, y + dy + (.6 if dy == 0 else .25), 1.1), 'screen')
                b.chair(f'{name}-chair-{k}', x + dx + .58, y - .55 if dy == 0 else y + 1.7, 's' if dy == 0 else 'n')
            b.box(f'{name}-screen-long', (x, y + .78, .75), (x + 3.2, y + .82, 1.2), 'fabric')
            b.box(f'{name}-screen-cross', (x + 1.58, y, .75), (x + 1.62, y + 1.6, 1.2), 'fabric')
            b.pendant(f'{name}-lamp', x + 1.6, y + .8, size[2], .8, .5)
    b.box('storage-north', (10.5, 19.2, 0), (13.5, 19.8, 1.1), 'furniture')
    # Private offices in the north-east.
    b.wall_x('office-front', 22., 29.8, 11.2, size[2], .2, (Opening(23.4, 1., 0, 2.2), Opening(28., 1., 0, 2.2)))
    b.wall_y('office-west', 11.4, 19.8, 22., size[2])
    b.wall_y('office-divider', 11.4, 19.8, 25.9, size[2])
    for name, x in (('office-a', 22.8), ('office-b', 26.8)):
        b.table(f'{name}-desk', x, 17.8, 2., .8)
        b.chair(f'{name}-chair', x + .78, 17.2, 's')
    b.shelf('office-a-shelf', 25.45, 13., .45, 2.5, 2.)
    b.plant('office-b-plant', 29.1, 12.)
    # Kitchen and break area in the south-east.
    b.box('kitchen-divider', (22., .2, 0), (22.6, 5., 1.1), 'furniture')
    b.box('kitchen-counter', (29.15, .8, 0), (29.8, 6.5, .92), 'stone')
    b.box('kitchen-upper', (29.45, .8, 1.5), (29.8, 6.5, 2.2), 'furniture')
    b.box('fridge', (29., 6.6, 0), (29.8, 7.4, 2.), 'metal')
    b.box('kitchen-island', (25., 2.8, 0), (27.4, 3.8, .95), 'stone')
    b.pendant('kitchen-island-lamp', 26.2, 3.3, size[2], 1., .45)
    b.table('break-table', 24., 5.8, 1.8, .9)
    b.chairs_around('break-chair', 24., 5.8, 1.8, .9, 2)
    routes = (
        Situation('reception-to-meeting-room', ((2.6, 3., 1.4), (2.6, 14.4, 1.4)),
                  'Leave reception and enter a glass meeting room through a 1 m door.', ('doorway', 'glass')),
        Situation('open-plan-to-private-office', ((8.5, 5.25, 1.5), (23.4, 5.25, 1.5), (23.4, 14.5, 1.5)),
                  'Cross the open-plan floor between desk clusters and columns, then turn into a private office.',
                  ('columns', 'clutter', 'doorway')),
        Situation('over-the-desks', ((12., 7.7, .8), (12., 7.7, 1.8), (12., 12.4, 1.8), (12., 12.4, 1.)),
                  'Climb over a desk cluster and its privacy screens, below the hanging lamps, then descend.',
                  ('altitude-change', 'overhang', 'clutter')),
    )
    return _scene('office-floor', 'interior', size, b, routes,
                  'Open-plan office with glass meeting rooms, reception, desk clusters, private offices and a kitchen.')


def apartment():
    size = (16., 12., 2.8)
    b = Builder()
    b.shell('shell', size, south=windows(.2, 15.8, 2.6, 1.6, .9, 2.3), north=windows(.2, 15.8, 3.2, 1.2, 1., 2.2))
    b.wall_x('hall-south', .2, 15.8, 7., size[2], .15, (Opening(4.5, 1.6, 0, 2.2), Opening(12.5, .9)))
    b.wall_y('living-study', .2, 7., 9., size[2], .15)
    b.wall_x('hall-north', .2, 15.8, 8.4, size[2], .15, (Opening(3., .9), Opening(7., .9), Opening(11., .9)))
    b.wall_y('bedroom-bath', 8.55, 11.8, 5.5, size[2], .15)
    b.wall_y('bath-bedroom', 8.55, 11.8, 8.6, size[2], .15)
    # Kitchen along the west wall, island and dining table.
    b.box('counter', (.2, 2.8, 0), (.85, 6., .9), 'stone')
    b.box('upper-cabinets', (.2, 2.8, 1.5), (.55, 6., 2.2), 'furniture')
    b.box('fridge', (.2, 6.05, 0), (.9, 6.85, 2.), 'metal')
    b.box('island', (2.4, 4.2, 0), (4.2, 5.1, .95), 'stone')
    b.pendant('island-lamp-0', 2.9, 4.65, size[2], .8, .35)
    b.pendant('island-lamp-1', 3.7, 4.65, size[2], .8, .35)
    b.table('dining-table', 5.6, 4.4, 1.8, .9)
    b.chairs_around('dining-chair', 5.6, 4.4, 1.8, .9, 2)
    b.pendant('dining-lamp', 6.5, 4.85, size[2], .9, .5)
    # Living area facing a television on the study wall.
    b.sofa('sofa', 5.4, .9, .9, 2.2, 'w')
    b.table('coffee-table', 6.7, 1.4, .8, 1.2, .42)
    b.box('tv-unit', (8.45, 1., 0), (8.95, 3., .5), 'furniture')
    b.box('tv', (8.88, 1.2, .9), (8.95, 2.8, 1.7), 'screen')
    b.box('floor-lamp-pole', (5.05, .45, 0), (5.1, .5, 1.5), 'metal')
    b.box('floor-lamp-shade', (4.9, .3, 1.5), (5.25, .65, 1.75), 'lamp')
    b.plant('living-plant', .4, .4)
    # Study.
    b.table('study-desk', 13.8, 1., 1.8, .8)
    b.chair('study-chair', 14.5, 1.9, 'n')
    b.shelf('study-books', 9.15, 1., .35, 4., 2.2, 5)
    b.sofa('reading-chair', 10.2, 4.6, 1., 1., 'w')
    b.plant('study-plant', 15.2, 6.2)
    # Bedroom one.
    b.bed('bed-1', 1.2, 9.7, 1.6, 2.1, 'n')
    b.box('nightstand-1', (.6, 11.3, 0), (1.1, 11.8, .55), 'wood')
    b.box('wardrobe-1', (4.85, 9.6, 0), (5.45, 11.8, 2.2), 'wood')
    # Bathroom.
    b.box('bathtub', (5.65, 11.05, 0), (7.35, 11.8, .55), 'ceramic')
    b.box('shower-screen', (6.8, 11.05, .55), (6.84, 11.8, 1.9), 'glass')
    b.box('toilet-bowl', (5.7, 8.85, 0), (6.1, 9.45, .42), 'ceramic')
    b.box('toilet-tank', (5.65, 8.55, 0), (6.15, 8.8, .8), 'ceramic')
    b.box('vanity', (8.05, 9.2, 0), (8.6, 10.2, .85), 'furniture')
    b.box('mirror', (8.56, 9.25, 1.1), (8.6, 10.15, 1.9), 'glass')
    # Bedroom two with a ceiling fan.
    b.bed('bed-2', 11.5, 9.7, 1.8, 2.1, 'n')
    b.box('nightstand-2', (13.4, 11.3, 0), (13.9, 11.8, .55), 'wood')
    b.box('wardrobe-2', (8.75, 11.2, 0), (10.6, 11.8, 2.2), 'wood')
    b.box('fan-rod', (12.35, 10.7, 2.35), (12.45, 10.8, 2.8), 'metal')
    b.box('fan-blades-x', (11.8, 10.69, 2.3), (13., 10.81, 2.35), 'wood')
    b.box('fan-blades-y', (12.34, 10.15, 2.3), (12.46, 11.35, 2.35), 'wood')
    routes = (
        Situation('sofa-to-bedroom', ((4.65, 2.2, 1.4), (4.65, 7.78, 1.4), (11., 7.78, 1.4), (11., 10., 1.4)),
                  'Pass between kitchen island and dining table, through the living-room arch, along a 1.25 m hall and into a bedroom.',
                  ('doorway', 'narrow-hall', 'clutter')),
        Situation('study-to-bathroom', ((12.5, 3., 1.3), (12.5, 7.78, 1.3), (7., 7.78, 1.3), (7., 9.6, 1.3)),
                  'Leave the study through a 0.9 m door and enter the bathroom through another.', ('doorway', 'narrow-hall')),
        Situation('kitchen-low-to-high', ((1.6, 3.4, .6), (3.3, 3.4, 1.5), (3.3, 6.2, 1.5)),
                  'Start low beside the counter, climb and cross the island beneath two hanging lamps.',
                  ('altitude-change', 'overhang')),
    )
    return _scene('apartment', 'interior', size, b, routes,
                  'Two-bedroom apartment: open kitchen and living room, study, bathroom and a 1.25 m hallway.')


def street():
    size = (70., 50., 18.)
    b = Builder(size)
    # Roads: east-west y 20-30, north-south x 31-39; sidewalks 3 m wide.
    b.building('sw-corner', 0., 3., 13., 17., 12., (9., 1.5), 2)
    b.building('sw-tower', 13.5, 4., 28., 17., 15., None, 1)
    b.building('se-low', 42., 2., 55., 17., 10.)
    b.building('se-tower', 55.5, 0., 70., 17., 16., (12., 2.), 2)
    b.building('nw-corner', 0., 33., 14., 48., 14., (10., 1.5), 1)
    b.building('nw-low', 14.5, 33., 28., 50., 9.)
    # North-east block with a 4 m pedestrian passage to a back lane.
    b.box('ne-west-mass', (42., 33., 0), (54., 47., 13.), 'building')
    b.box('ne-east-mass', (58., 33., 0), (70., 47., 13.), 'building')
    b.box('ne-passage-roof', (54., 33., 4.5), (58., 47., 13.), 'building')
    b.box('ne-parapet', (42., 33., 13.), (70., 33.25, 13.9), 'stone')
    # Skybridge between the two southern blocks, over the north-south road.
    b.box('skybridge-deck', (28., 8., 6.5), (42., 10.5, 6.8), 'concrete')
    b.box('skybridge-south-glass', (28., 8., 6.8), (42., 8.05, 9.2), 'glass')
    b.box('skybridge-north-glass', (28., 10.45, 6.8), (42., 10.5, 9.2), 'glass')
    b.box('skybridge-roof', (28., 8., 9.2), (42., 10.5, 9.45), 'concrete')
    # Facade details: shop awnings and balconies.
    b.awning('awning-sw-0', 1., 12., 17., 'n')
    b.awning('awning-sw-1', 14.5, 27., 17., 'n')
    b.balconies('balcony-se-low', 42., 55., 17., 'n', 2, z_first=3.6)
    b.balconies('balcony-se-tower', 55.5, 70., 17., 'n', 3, z_first=3.6)
    # North sidewalk trees, south sidewalk lamps and bus stop.
    for i, x in enumerate((4., 11., 18., 25., 45., 50., 66.)):
        b.tree(f'tree-{i}', x, 31.6, 2.8, 2.8)
    for i, x in enumerate((8., 16., 24., 46., 54., 62.)):
        b.lamp_post(f'lamp-s-{i}', x, 19.6, 6., 1.4, 'n')
    for i, x in enumerate((8., 21., 47., 62.)):
        b.lamp_post(f'lamp-n-{i}', x, 30.4, 6., 1.4, 's')
    b.box('shelter-roof', (44., 17.2, 2.5), (48.5, 19., 2.65), 'glass')
    b.box('shelter-back', (44., 17.2, 0), (48.5, 17.3, 2.5), 'glass')
    b.box('shelter-side', (44., 17.3, 0), (44.1, 19., 2.5), 'glass')
    b.box('shelter-post', (48.4, 18.9, 0), (48.5, 19., 2.5), 'metal')
    b.bench('shelter-bench', 45., 17.4)
    b.bench('corner-bench', 20., 17.4)
    b.bollards('bollards-sw', 28.4, 17.6, 28.4, 19.6, 4)
    b.bollards('bollards-ne', 41.6, 30.4, 41.6, 32.6, 4)
    b.box('kiosk', (28.4, 35., 0), (30.4, 37., 2.6), 'wood')
    b.box('kiosk-roof', (28.2, 34.8, 2.6), (30.6, 37.2, 2.8), 'metal')
    # Traffic signals with mast arms over the carriageway.
    b.traffic_light('signal-sw', 30.6, 19.6, 4., 'e')
    b.traffic_light('signal-ne', 39.4, 30.4, 4., 'w')
    # Overhead tram wire along the east-west road.
    b.box('tram-wire', (0, 24.98, 6.), (70., 25.02, 6.03), 'metal')
    # Parked vehicles.
    for i, x in enumerate((3., 9., 15., 21.5)):
        b.car(f'car-s-{i}', x, 20.2)
    for i, x in enumerate((5., 12., 50., 58., 64.5)):
        b.car(f'car-n-{i}', x, 28.)
    b.box('bus-body', (44., 20.3, .35), (56., 22.8, 3.1), 'bus')
    b.box('bus-windows', (44.4, 20.25, 1.4), (55.6, 22.85, 2.5), 'glass')
    b.box('bus-chassis', (44.6, 20.5, 0), (55.4, 22.6, .35), 'rubber')
    b.van('delivery-van', 36.8, 36., along_x=False)
    routes = (
        Situation('street-traverse', ((2., 25.8, 2.), (68., 25.8, 2.)),
                  'Fly the length of the street between parked cars, a bus and lamp heads.', ('long-range',)),
        Situation('intersection-turn', ((2., 25.8, 2.), (35., 25.8, 2.), (35., 48.5, 2.)),
                  'Turn north at the intersection under a signal mast arm and pass a delivery van.', ('turn', 'overhang')),
        Situation('under-the-skybridge', ((35., 1.5, 3.), (35., 24.5, 3.), (8., 24.5, 3.)),
                  'Follow the north-south road under a glass skybridge, then turn west along the street.',
                  ('overhang', 'turn', 'long-range')),
        Situation('through-the-passage', ((20., 26., 2.5), (56., 26., 2.5), (56., 48.5, 2.5)),
                  'Leave the street through a 4 m covered passage into the back lane.', ('passage', 'turn')),
        Situation('over-the-bus', ((42.8, 21.5, 1.5), (42.8, 21.5, 4.), (57.5, 21.5, 4.), (57.5, 21.5, 1.5)),
                  'Climb over a parked bus beneath lamp heads and the tram wire, then descend.',
                  ('altitude-change', 'overhang')),
    )
    return _scene('street-block', 'outdoor', size, b, routes,
                  'Crossroads with set-back buildings, a covered passage, skybridge, bus stop, trees, signals and parked vehicles.')


def atrium():
    size = (30., 24., 14.)
    b = Builder()
    b.wall_x('facade-south', 0, 30., 0, size[2], .2, (), 'glass')
    b.wall_x('wall-north', 0, 30., 23.8, size[2])
    b.wall_y('wall-west', .2, 23.8, 0, size[2], .2, windows(2., 22., 4., 2.4, 1., 3.4) )
    b.wall_y('wall-east', .2, 23.8, 29.8, size[2])
    void = (10., 7., 20., 17.)
    for level, z in ((1, 4.5), (2, 9.)):
        lo = z - .3
        b.box(f'slab-{level}-south', (.2, .2, lo), (29.8, 7., z), 'concrete')
        b.box(f'slab-{level}-north', (.2, 17., lo), (29.8, 23.8, z), 'concrete')
        b.box(f'slab-{level}-west', (.2, 7., lo), (10., 17., z), 'concrete')
        if level == 1:
            b.box('slab-1-east', (20., 7., lo), (29.8, 17., z), 'concrete')
        else:  # Opening for the east stair.
            b.box('slab-2-east-a', (20., 7., lo), (24., 17., z), 'concrete')
            b.box('slab-2-east-b', (26., 7., lo), (29.8, 17., z), 'concrete')
            b.box('slab-2-east-c', (24., 7., lo), (26., 8., z), 'concrete')
            b.box('slab-2-east-d', (24., 15.5, lo), (26., 17., z), 'concrete')
        b.railing(f'rail-{level}-west', 10., 7., 10., 17., z)
        b.railing(f'rail-{level}-east', 20., 7., 20., 17., z)
        if level == 1:  # Gap where the grand stair lands.
            b.railing('rail-1-south', 10., 7., 20., 7., z)
            b.railing('rail-1-north-a', 10., 17., 11., 17., z)
            b.railing('rail-1-north-b', 13., 17., 20., 17., z)
        else:  # Gaps where the bridge meets each gallery.
            for side, y in (('south', 7.), ('north', 17.)):
                b.railing(f'rail-2-{side}-a', 10., y, 14., y, z)
                b.railing(f'rail-2-{side}-b', 16., y, 20., y, z)
    # Bridge across the void at level 2.
    b.box('bridge-deck', (14., 7., 8.7), (16., 17., 9.), 'concrete')
    b.railing('bridge-rail-west', 14., 7., 14., 17., 9.)
    b.railing('bridge-rail-east', 16., 7., 16., 17., 9.)
    # Grand stair from the ground to level 1 inside the void; east stair from level 1 to 2.
    b.stairs('grand-stair', 11., 8.5, 2., .3, .18, 25, 'n')
    b.box('grand-stair-landing', (11., 16., 0), (13., 17., 4.5), 'concrete')
    b.stairs('east-stair', 24., 8., 2., .3, .18, 25, 'n', 4.5)
    for i, (x, y) in enumerate(((10., 7.), (20., 7.), (10., 17.), (20., 17.), (5., 3.5), (25., 3.5), (5., 20.5), (25., 20.5))):
        b.column(f'column-{i}', x, y, .6, size[2])
    # Hanging sculpture in the void.
    for i, (x, y, z) in enumerate(((12., 10., 11.2), (17.8, 9.8, 10.4), (17.8, 14.2, 11.6))):
        b.box(f'mobile-{i}-cord', (x - .01, y - .01, z + .6), (x + .01, y + .01, size[2]), 'metal')
        b.box(f'mobile-{i}-form', (x - .5, y - .5, z), (x + .5, y + .5, z + .6), 'art')
    # Ground floor: reception, café, a planted tree.
    b.box('reception-desk', (12., 3., 0), (18., 4., 1.1), 'wood')
    for i, (x, y) in enumerate(((2.5, 9.5), (5.5, 9.5), (2.5, 13.), (5.5, 13.))):
        b.table(f'cafe-table-{i}', x, y, .9, .9)
        b.chair(f'cafe-chair-{i}-0', x + .22, y - .55, 's')
        b.chair(f'cafe-chair-{i}-1', x + .22, y + 1., 'n')
    b.box('cafe-counter', (.2, 17.5, 0), (4.5, 18.3, 1.05), 'wood')
    b.box('planter', (17., 11.2, 0), (19., 13.2, .5), 'stone')
    b.tree('atrium-tree', 18., 12.2, 2.8, 3.2, 3.6)
    # Upper galleries: lounges and work tables.
    for level, z in ((1, 4.5), (2, 9.)):
        b.table(f'gallery-{level}-table-a', 3., 19., 2.4, 1., z0=z)
        b.table(f'gallery-{level}-table-b', 22., 19., 2.4, 1., z0=z)
        b.box(f'gallery-{level}-bench', (3., 2., z), (8., 2.5, z + .45), 'wood')
        b.box(f'gallery-{level}-planter', (22., 2., z), (27., 2.6, z + .9), 'vegetation')
    b.shelf('library-1', .2, 9., .4, 6., 2.4, 5, z0=4.5)
    routes = (
        Situation('lobby-to-first-gallery', ((15., 5.5, 1.5), (15., 9.5, 1.5), (15., 9.5, 6.2), (15., 4.5, 6.2)),
                  'Enter the void, climb 4.7 m and cross the glass balustrade onto the first-floor gallery.',
                  ('multi-level', 'altitude-change', 'glass')),
        Situation('void-climb-to-top-gallery', ((18.6, 5., 1.), (18.6, 15.6, 1.), (18.6, 15.6, 10.6), (18.6, 20., 10.6)),
                  'Pass beneath a tree canopy, climb past a hanging sculpture and land on the top gallery.',
                  ('multi-level', 'altitude-change', 'overhang')),
        Situation('bridge-crossing', ((15., 3.5, 10.), (15., 20.5, 10.)),
                  'Cross the void on the second-floor bridge between two glass railings.', ('multi-level', 'narrow-passage')),
    )
    return _scene('atrium', 'interior', size, b, routes,
                  'Three-storey atrium with galleries, a grand stair, a bridge across the void and a hanging sculpture.')


def warehouse():
    size = (40., 26., 10.)
    b = Builder()
    docks = [Opening(x, 3.5, 0, 4.2, 'metal') for x in (8., 16., 24.)]
    b.wall_x('wall-south', 0, 40., 0, size[2], .2, docks)
    b.wall_x('wall-north', 0, 40., 25.8, size[2], .2, windows(1., 39., 4., 3., 7., 8.5))
    b.wall_y('wall-west', .2, 25.8, 0, size[2])
    b.wall_y('wall-east', .2, 25.8, 39.8, size[2])
    for i, x in enumerate((5., 11., 17., 23., 29., 35.)):
        b.box(f'truss-{i}', (x - .15, .2, 8.6), (x + .15, 25.8, 9.), 'metal')
        for j, y in enumerate((6.5, 19.5)):
            b.pendant(f'high-bay-{i}-{j}', x, y, 8.6, 1., .5)
    b.box('purlin', (.2, 12.9, 9.), (39.8, 13.1, 9.2), 'metal')
    # Five pallet-rack rows: uprights every 3 m, beams at four levels and partly filled bays.
    levels = (0., 1.5, 3., 4.5, 6.)
    for row, y in enumerate((3., 7.2, 11.4, 15.6, 19.8)):
        name = f'rack-{row}'
        for i in range(9):
            x = 3. + 3. * i
            b.box(f'{name}-upright-{i}-s', (x, y, 0), (x + .1, y + .1, 7.), 'rack')
            b.box(f'{name}-upright-{i}-n', (x, y + 1., 0), (x + .1, y + 1.1, 7.), 'rack')
        for k, z in enumerate(levels[1:]):
            b.box(f'{name}-beam-{k}-s', (3., y, z), (27.1, y + .1, z + .12), 'rack')
            b.box(f'{name}-beam-{k}-n', (3., y + 1., z), (27.1, y + 1.1, z + .12), 'rack')
        for bay in range(8):
            for k, z in enumerate(levels):
                if (row * 7 + bay * 3 + k * 5) % 4 == 0:
                    continue
                base = z + (.12 if k else 0)
                b.box(f'{name}-pallet-{bay}-{k}', (3.25 + 3. * bay, y + .05, base), (5.85 + 3. * bay, y + 1.05, base + 1.1), 'cargo')
    # Mezzanine with an office, columns, railing and stair.
    b.box('mezzanine-deck', (30., 14., 3.4), (39.8, 25.8, 3.7), 'metal')
    for i, (x, y) in enumerate(((30.4, 14.4), (34.8, 14.4), (30.4, 20.), (34.8, 20.))):
        b.column(f'mezzanine-column-{i}', x, y, .3, 3.4, material='metal')
    b.railing('mezzanine-rail-south', 30., 14., 39.8, 14., 3.7, 1.1, 'metal')
    b.railing('mezzanine-rail-west-a', 30., 14., 30., 22., 3.7, 1.1, 'metal')
    b.railing('mezzanine-rail-west-b', 30., 23.2, 30., 25.8, 3.7, 1.1, 'metal')
    b.stairs('mezzanine-stair', 30., 22., 1.2, .2, 3.7 / 18, 18, 'w')
    b.box('mezzanine-office', (34., 20., 3.7), (39.8, 25.8, 6.5), 'wall')
    b.box('mezzanine-office-window', (33.98, 21., 4.6), (34., 25., 5.8), 'glass')
    # Floor equipment.
    b.box('forklift-body', (31., 6., 0), (33.4, 7.2, 1.4), 'vehicle')
    b.box('forklift-mast', (30.7, 6.1, 0), (31., 7.1, 3.), 'metal')
    b.box('forklift-guard', (31.3, 6., 2.), (32.6, 7.2, 2.1), 'metal')
    b.box('forklift-post', (32.5, 6., 1.4), (32.6, 7.2, 2.), 'metal')
    for i, x in enumerate((12., 20.)):
        b.box(f'staging-pallet-{i}', (x, .6, 0), (x + 1.2, 1.6, 1.), 'cargo')
    b.box('conveyor', (4., 23., 0), (26., 23.8, .9), 'metal')
    routes = (
        Situation('aisle-run', ((1.5, 9.85, 2.), (29., 9.85, 2.)),
                  'Fly the full length of a 3.1 m aisle between 7 m pallet racks.', ('narrow-aisle', 'long-range')),
        Situation('aisle-switch', ((1.5, 5.65, 1.5), (28.4, 5.65, 1.5), (28.4, 18.25, 1.5), (3., 18.25, 1.5)),
                  'Leave one aisle at the rack ends and return down another.', ('narrow-aisle', 'turn')),
        Situation('over-the-racks', ((14., 1.5, 1.5), (14., 1.5, 7.8), (14., 24.5, 7.8), (14., 24.5, 1.5)),
                  'Climb above the racks, fly between roof trusses and hanging lights, then descend.',
                  ('altitude-change', 'overhang')),
        Situation('under-mezzanine-and-up', ((33., 8., 1.5), (33., 18., 1.5), (28.6, 18., 1.5), (28.6, 18., 5.3), (32.5, 18., 5.3)),
                  'Fly beneath the mezzanine deck between its columns, then climb over the railing onto it.',
                  ('multi-level', 'overhang', 'columns')),
    )
    return _scene('warehouse', 'interior', size, b, routes,
                  'High-bay warehouse with pallet racks, roof trusses, loading docks, a forklift and an office mezzanine.')


def courtyard():
    size = (40., 34., 12.)
    b = Builder()
    # Perimeter buildings; the southern one has a 4 m gate passage.
    b.box('south-west-mass', (0, 0, 0), (18., 8., 10.), 'building')
    b.box('south-east-mass', (22., 0, 0), (40., 8., 10.), 'building')
    b.box('gate-roof', (18., 0, 4.2), (22., 8., 10.), 'building')
    b.box('west-wing', (0, 8., 0), (8., 34., 10.), 'building')
    b.box('east-wing', (32., 8., 0), (40., 34., 10.), 'building')
    for name, low, high in (('parapet-south', (0, 7.75, 10.), (40., 8., 10.8)),
                            ('parapet-west', (7.75, 8., 10.), (8., 34., 10.8)),
                            ('parapet-east', (32., 8., 10.), (32.25, 34., 10.8))):
        b.box(name, low, high, 'stone')
    # North building: enterable glass-fronted lobby beneath upper floors.
    b.wall_x('lobby-facade', 8., 32., 26., 4., .2, (Opening(20., 2.2, 0, 2.8),), 'glass')
    b.box('lobby-back-wall', (8., 33.8, 0), (32., 34., 4.), 'wall')
    b.box('north-upper', (8., 26., 4.), (32., 34., 10.), 'building')
    b.box('lobby-canopy', (17., 24.6, 3.), (23., 26., 3.25), 'metal')
    b.box('reception-desk', (18., 31.5, 0), (22., 32.3, 1.1), 'wood')
    b.column('lobby-column-0', 14., 30., .5, 4.)
    b.column('lobby-column-1', 26., 30., .5, 4.)
    b.sofa('lobby-sofa', 10., 29., 2.2, .9, 's')
    b.box('lift-core', (27., 31., 0), (30., 33.8, 4.), 'concrete')
    b.plant('lobby-plant', 31., 26.8)
    # Arcade along the west wing.
    b.box('arcade-roof', (8., 8., 3.6), (11., 26., 4.), 'stone')
    for i, y in enumerate((10., 14., 18., 22.)):
        b.column(f'arcade-column-{i}', 10.6, y, .4, 3.6, material='stone')
    # Fountain.
    b.box('fountain-wall-s', (17., 14., 0), (23., 14.3, .6), 'stone')
    b.box('fountain-wall-n', (17., 19.7, 0), (23., 20., .6), 'stone')
    b.box('fountain-wall-w', (17., 14.3, 0), (17.3, 19.7, .6), 'stone')
    b.box('fountain-wall-e', (22.7, 14.3, 0), (23., 19.7, .6), 'stone')
    b.box('fountain-water', (17.3, 14.3, 0), (22.7, 19.7, .35), 'water')
    b.box('fountain-column', (19.6, 16.6, .35), (20.4, 17.4, 2.2), 'stone')
    b.box('fountain-bowl', (19., 16., 2.2), (21., 18., 2.45), 'stone')
    for i, (x, y) in enumerate(((14., 12.), (26., 12.), (14., 22.), (26., 22.))):
        b.tree(f'tree-{i}', x, y)
    b.bench('bench-s', 18.1, 12.8)
    b.bench('bench-n', 18.1, 20.7)
    # Café under umbrellas on the east side.
    for i, y in enumerate((11., 15., 19.)):
        b.umbrella(f'umbrella-{i}', 28., y)
        b.table(f'cafe-table-{i}', 27.6, y - .4, .8, .8)
        b.chair(f'cafe-chair-{i}-w', 26.95, y - .22, 'w')
        b.chair(f'cafe-chair-{i}-e', 28.6, y - .22, 'e')
    for i in range(5):
        x = 23.2 + .6 * i
        b.box(f'bike-rack-{i}', (x, 8.6, 0), (x + .05, 9.2, .85), 'metal')
    b.lamp_post('lamp-0', 12.5, 17., 4., .6, 'e')
    b.lamp_post('lamp-1', 24.5, 17., 4., .6, 'w')
    routes = (
        Situation('gate-over-fountain', ((20., 1., 2.), (20., 12.6, 2.), (20., 12.6, 3.2), (20., 24., 3.2)),
                  'Enter through the gate passage, climb and cross over the fountain bowl.',
                  ('passage', 'altitude-change')),
        Situation('arcade-walk', ((9.2, 9., 1.6), (9.2, 24.2, 1.6), (16.5, 24.2, 1.6)),
                  'Fly the length of the covered arcade between wall and columns, then exit under the trees.',
                  ('columns', 'overhang', 'narrow-passage')),
        Situation('courtyard-to-lobby', ((30.5, 9.5, 1.5), (30.5, 24.5, 1.5), (20., 24.5, 1.5), (20., 29.5, 1.5)),
                  'Pass the café, cross the courtyard and enter the lobby through its glass doorway.',
                  ('indoor-outdoor', 'doorway', 'glass')),
    )
    return _scene('courtyard', 'mixed', size, b, routes,
                  'Enclosed courtyard with a gate passage, arcade, fountain, café umbrellas and an enterable lobby.')


BUILDERS = {'office-floor': office, 'apartment': apartment, 'street-block': street,
            'atrium': atrium, 'warehouse': warehouse, 'courtyard': courtyard}
