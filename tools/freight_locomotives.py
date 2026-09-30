"""Native settings and height-sampled motion for the WAG source masters."""
import math

# kW, kN, kg, km/h. WAG12B values are per section, not complete-pair values.
# Power/weight/effort basis: NWR WTT 2025 p166 and RDSO Handout p7.
# Speed/year are the user's explicit gameplay overrides (30 September 2026).
SPECS = {
    'wag9': dict(name='Indian Railways WAG-9', length=20.562, weight=123000,
                 speed=120, year=1995, bogie_distance=6.0, power=4500, effort=460,
                 panto_low=4.255, panto_high=5.917),
    'wag12b_a': dict(name='WAG-12B section A', length=19.2, weight=90000,
                     speed=120, year=2017, bogie_distance=5.1, power=4500, effort=353,
                     panto_low=4.245, panto_high=7.52),
    'wag12b_b': dict(name='WAG-12B section B', length=19.2, weight=90000,
                     speed=120, year=2017, bogie_distance=5.1, power=4500, effort=353,
                     panto_low=4.245, panto_high=7.52),
}


def sample_tracks(bpy, key, clean):
    """Resample angular live drivers into TF3's linear contact-height frames."""
    from mathutils import Vector
    spec = SPECS[key]
    dual = key == 'wag9'
    tracks = {}
    for end in ('FRONT', 'REAR') if dual else ('',):
        prefix = 'PANTO_' + end if dual else 'PANTO'
        ctrl = bpy.data.objects[prefix + '_CTRL']
        pivots = [bpy.data.objects[prefix + '_' + part] for part in
                  ('LOWER_PIVOT', 'ELBOW_PIVOT', 'HEAD_LEVEL_PIVOT')]
        ctrl['extension'] = 0.0
        ctrl.update_tag()
        bpy.context.view_layer.update()
        rest = {ob: ob.matrix_local.copy() for ob in pivots}
        values = {ob: [] for ob in pivots}
        base, arms, strip = (4.149, 2.53, .044) if dual else (4.168, 4.4, .032)
        low, high = spec['panto_low'], spec['panto_high']
        a0, a1 = (math.asin((height - base) / arms) for height in (low, high))
        for i in range(101):
            height = low + (high - low) * i / 100
            ctrl['extension'] = max(0.0, min(1.0, (math.asin((height-base)/arms)-a0)/(a1-a0)))
            ctrl.update_tag()
            bpy.context.view_layer.update()
            head = pivots[-1].matrix_world
            assert abs(head.translation.z + strip - height) < 2e-5, (key, end, height)
            assert (head.to_3x3().col[2] - Vector((0, 0, 1))).length < 1e-5
            for ob in pivots:
                delta = rest[ob].inverted() @ ob.matrix_local
                values[ob].append([float(delta[r][c]) for c in range(4) for r in range(4)])
        ctrl['extension'] = 0.0
        ctrl.update_tag()
        bpy.context.view_layer.update()
        state = 'pantograph_' + end.lower() if dual else 'pantograph'
        for ob in pivots:
            tracks[clean(ob.name)] = {state: {'times': list(range(0, 1001, 10)), 'transfs': values[ob]}}
        print('FREIGHT_PANTOGRAPH', key, end, '101 level-head samples', low, high)
    return tracks


def write_formation(rootdir, write_lua):
    folder = rootdir / 'game_build/gj94_indian_rail_pack/content/vehicle/train/wag12b'
    folder.mkdir(parents=True, exist_ok=True)
    write_lua(folder / 'wag12b.mu.lua', {
        'vehicles': [
            {'name': 'gj94_indian_rail_pack::/vehicle/train/wag12b_a/wag12b_a.mdl', 'forward': True},
            {'name': 'gj94_indian_rail_pack::/vehicle/train/wag12b_b/wag12b_b.mdl', 'forward': False},
        ],
        'name': 'Indian Railways WAG-12B (twin section)',
        'desc': 'Twin-section electric freight locomotive. 9,000 kW, 706 kN, 180 t, 120 km/h. Requires electrified track; add freight wagons.',
        'filterTags': ['default'],
    })
