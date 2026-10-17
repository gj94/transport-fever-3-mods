"""Validate the actual upgraded Lua resources, preservation and stock costs."""
import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'lua-validation-deps'))
from lupa.lua54 import LuaRuntime, lua_type
from check_tf3_balance import model_stats, unit_stats
from tf3_resource_paths import resolve_model_ref
from vehicle_performance import apply_performance

MOD = ROOT / 'game_build/gj94_indian_rail_pack'
GAME = Path('D:/SteamLibrary/steamapps/common/Transport Fever 3')


def plain(value):
    if isinstance(value, list):
        return {i: plain(v) for i, v in enumerate(value, 1)}
    return {k: plain(v) for k, v in value.items()} if lua_type(value) == 'table' or isinstance(value, dict) else value


def scrub(model, vb):
    model = copy.deepcopy(model)
    metadata = model['metadata']
    for key in ('topSpeed', 'engines'):
        metadata['landVehicle'].pop(key)
    if vb:
        metadata['transportVehicle'].pop('comfortFactor')
    metadata['description'].pop('description')
    metadata['versioning'].pop('__version')
    return model


def force(stats, speed):
    # Ideal available tractive force, kN: the lower of starting effort and P/v.
    # This does not model TF3's drag, curves, gradients, adhesion or track limits.
    return min(stats['tractive_effort_kn'], stats['power_kw'] / (speed / 3.6)) if speed else stats['tractive_effort_kn']


def main():
    baseline = json.loads((ROOT / 'game_build/performance_upgrade_baseline.json').read_text())
    actual = {p.relative_to(MOD).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in MOD.rglob('*') if p.is_file()}
    assert actual.keys() == baseline['files'].keys(), 'Resource additions/removals are outside this metadata upgrade'
    changed = sorted(name for name in actual if actual[name] != baseline['files'][name])
    expected_models = {'wap7', 'wag12b_a', 'wag12b_b', 'vb_dtc', 'vb_mc', 'vb_mc2',
                       'vb_tc_cc', 'vb_tc_ec', 'vb_ndtc_ec', 'vb_ndtc_ec2'}
    expected_files = {f'content/vehicle/train/{key}/{key}.mdl' for key in expected_models}
    expected_files |= {'mod.json', '_metadata/modinfo.json', 'content/vehicle/train/wag12b/wag12b.mu.lua',
        'content/vehicle/train/vande_bharat/vande_bharat_8.mu.lua', 'content/vehicle/train/vande_bharat/vande_bharat_16.mu.lua'}
    assert set(changed) == expected_files, changed
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('math.pow=function(a,b) return a^b end; math.round=function(a) return math.floor(a+.5) end; _=function(s) return s end')
    scripts = {}
    for package in ('scripts', 'base'):
        with zipfile.ZipFile(GAME / f'base/content/{package}.zip') as archive:
            scripts.update({name: archive.read(name).decode() for name in archive.namelist() if name.endswith('.lua')})
    cache = {}
    def require(name):
        assert name.startswith(('::/', '/')), name
        if name not in cache:
            cache[name] = lua.execute(scripts[name.removeprefix('::').lstrip('/')])
        return cache[name]
    lua.globals().require = require
    util = require('::/base/model_metadata_util.lua')
    def load(text):
        lua.execute(text)
        return lua.globals().data()
    before = {}
    after = {}
    for key in sorted(expected_models):
        name = f'content/vehicle/train/{key}/{key}.mdl'
        path = MOD / name
        old_text = baseline['models_and_formations'][name]
        new_text = path.read_text()
        old = plain(load(old_text))
        model = load(new_text)
        new = plain(model)
        assert scrub(old, key.startswith('vb_')) == scrub(new, key.startswith('vb_')), key
        export_metadata = copy.deepcopy(old['metadata'])
        apply_performance(export_metadata, key)
        # Native Lua serialization stores floats to nine significant digits and
        # reads array tables back with one-based numeric keys.
        export_metadata['landVehicle']['topSpeed'] = float(format(export_metadata['landVehicle']['topSpeed'], '.9g'))
        export_metadata['versioning'] = new['metadata']['versioning']
        assert plain(export_metadata) == new['metadata'], ('full-export/update settings disagree', key)
        stats = model_stats(new_text)
        if key == 'wap7':
            expected = (200, 9000, 600)
        elif key.startswith('wag12b_'):
            expected = (200, 8000, 500)
        else:
            powered = key in {'vb_mc', 'vb_mc2'}
            expected = (320, 4000 if powered else 0, 220 if powered else 0)
            assert stats['comfort'] == (1.0 if 'ec' in key else .95), key
        assert (stats['speed_kmh'], stats['power_kw'], stats['tractive_effort_kn']) == expected, (key, stats)
        metadata = model['metadata']
        assert metadata['cost']['price'] == -1 and metadata['maintenance']['runningCosts'] == -1
        assert metadata['transportVehicle']['priceFactor'] == .5
        assert metadata['transportVehicle']['maintenanceFactor'] == 1
        util['addCostMetadata'](str(path), model)
        assert metadata['cost']['price'] == stats['base_purchase'], key
        assert metadata['maintenance']['runningCosts'] == stats['base_annual_upkeep'], key
        before[key] = model_stats(old_text)
        after[key] = stats
    formations = {}
    for name in sorted(expected_files):
        if not name.endswith('.mu.lua'):
            continue
        path = MOD / name
        old = plain(load(baseline['models_and_formations'][name]))
        new = plain(load(path.read_text()))
        old.pop('desc')
        new.pop('desc')
        assert old == new, name
        refs = [new['vehicles'][i]['name'] for i in range(1, len(new['vehicles']) + 1)]
        keys = [resolve_model_ref(MOD, path, ref).stem for ref in refs]
        old_stats = unit_stats(path.stem, [before[key] for key in keys])
        stats = unit_stats(path.stem, [after[key] for key in keys])
        assert stats['capacity'] == old_stats['capacity'] and stats['weight_t'] == old_stats['weight_t']
        if 'wag12b' in name:
            assert stats['speed_kmh'] == 200 and stats['power_kw'] == 16000 and stats['tractive_effort_kn'] == 1000
        else:
            factor = 2 if '_16.' in name else 1
            assert stats['speed_kmh'] == 320 and stats['power_kw'] == 16000 * factor and stats['tractive_effort_kn'] == 880 * factor
        assert stats['base_purchase'] > old_stats['base_purchase'], name
        for speed in (0, 40, 100, old_stats['speed_kmh']):
            assert force(stats, speed) > force(old_stats, speed), (name, speed)
        stats['available_force_kn'] = {str(v): round(force(stats, v), 3) for v in (0, 100, stats['speed_kmh'])}
        formations[path.stem] = stats
    for speed in (0, 40, 100, 180):
        assert force(after['wap7'], speed) > force(before['wap7'], speed), ('wap7', speed)
    report = dict(changed_files=changed, unchanged_resource_files=len(actual)-len(changed),
        models=after, formations=formations, stock_lua_costs_match=True,
        geometry_seating_capacities_years_fares_and_horn_preserved=True,
        force_basis='Ideal available tractive force min(effort, power/speed); not a runtime acceleration or route-speed prediction.')
    (ROOT / 'game_build/vehicle_performance_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(expected_models)} upgraded models, three complete formations, exact stock Lua costs; {len(changed)} metadata/description resources changed.')
    print(f'PASS: {report["unchanged_resource_files"]} other files unchanged; model geometry, seats, capacities, dates, fares, weights, animations and horn preserved.')
    for name, stats in formations.items():
        print(name, json.dumps(stats))
    print('wap7', json.dumps(after['wap7']))


if __name__ == '__main__':
    main()
