"""Execute coach metadata; compare all seated roots with the upstream handoffs.

Also run the installed game's automatic price rules on each coach. This verifies
resource/metadata integration; boarding, sorting and curves need a game test.
"""
import json
import math
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'lua-validation-deps'))
from lupa.lua54 import LuaRuntime
from coach_families import SPECS
from check_tf3_balance import model_stats

GAME = Path('D:/SteamLibrary/steamapps/common/Transport Fever 3')
MOD = ROOT / 'game_build/gj94_indian_rail_pack'
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('math.pow=function(a,b) return a^b end; math.round=function(a) return math.floor(a+.5) end; _=function(s) return s end')
scripts = {}
for package in ('scripts','base'):
    with zipfile.ZipFile(GAME / f'base/content/{package}.zip') as archive:
        scripts.update({n: archive.read(n).decode() for n in archive.namelist() if n.endswith('.lua')})
cache = {}
def require(name):
    assert name.startswith(('::/','/')), name
    if name not in cache:
        cache[name] = lua.execute(scripts[name.removeprefix('::').lstrip('/')])
    return cache[name]
lua.globals().require = require
util = require('::/base/model_metadata_util.lua')

# Explicit contract values also guard against accidental changes to the scaling.
expected = {'icf': [10, 26, 36, 60, 40, 40, 60], 'lhb': [14, 32, 44, 62, 48, 48, 62]}
assert len(SPECS)==14 and 'icf_sl' not in SPECS
for family in ('icf','lhb'):
    values={s['kind']:s['game_capacity'] for s in SPECS.values() if s['family']==family}
    assert values['1A']<values['2A']<values['3A'] and values['2A']<values['SL']
report = {}
for key, spec in SPECS.items():
    path = MOD / 'content/vehicle/train' / key / (key + '.mdl')
    lua.execute(path.read_text())
    model = lua.globals().data()
    metadata = model['metadata']
    assert spec['game_capacity'] == expected[spec['family']][('1A','2A','3A','2S','CC','SL','GS').index(spec['kind'])]
    if spec['family'] == 'icf':
        refs = json.loads((ROOT / f"icf_family_v01/{spec['kind']}/pax_markers.json").read_text())
        markers = {r['name'].lower(): [r['local_matrix_rows'][i][j] for j in range(4) for i in range(4)] for r in refs}
    else:
        refs = json.loads((ROOT / f"lhb_family_v01/models/LHB_{spec['kind']}_markers.json").read_text())['PAX_character_roots']
        markers = {}
        for ref in refs:
            x,y,z = ref['position_parent_m']; c,s = math.cos(ref['yaw_radians']),math.sin(ref['yaw_radians'])
            markers[ref['name'].lower()] = [c,s,0,0,-s,c,0,0,0,0,1,0,x,y,z,1]
    seats = metadata['seatProvider']['seats']
    assert len(seats) == spec['physical'] == len(markers), key
    # The exporter sorts source names. Compare actual full transforms, not counts alone.
    for i, name in enumerate(sorted(markers), 1):
        seat = seats[i]; actual = [seat['transf'][j] for j in range(1,17)]
        assert seat['animation'] == 'sitting' and not seat['crew'], (key,name)
        assert max(abs(a-b) for a,b in zip(actual,markers[name])) < 1e-6, (key,name)
        assert seat['group'] == ('interior' if spec['family']=='icf' else 'body_pivot')
    tv = metadata['transportVehicle']
    assert len(tv['filterTags'])==1 and tv['filterTags'][1]=='default' and not tv['multipleUnitOnly']
    assert len(tv['entrances']) == (6 if key=='lhb_gs' else 4), key
    assert len(metadata['railVehicle']['config']['axles'])==4, key
    assert len(model['lods'])==4 and metadata['availability']['yearTo']==0
    assert metadata['availability']['yearFrom']==spec['year']
    assert tv['compartments'][1]['loadConfigs'][1]['cargoEntry']['capacity']==spec['capacity']
    assert tv['priceFactor']==.5 and tv['maintenanceFactor']==1
    assert metadata['cost']['price']==-1 and metadata['maintenance']['runningCosts']==-1
    stats = model_stats(path.read_text())
    util['addCostMetadata'](str(path), model)
    assert metadata['cost']['price']==stats['base_purchase'], key
    assert metadata['maintenance']['runningCosts']==stats['base_annual_upkeep'], key
    report[key] = dict(game_capacity=spec['game_capacity'],physical_seats=len(seats),year=spec['year'],
                       speed_kmh=spec['speed'],base_purchase=stats['base_purchase'],
                       base_annual_upkeep=stats['base_annual_upkeep'],seated_root_transforms_verified=True)
    print(key, json.dumps(report[key]))
(ROOT / 'game_build/coach_family_validation.json').write_text(json.dumps(report,indent=2)+'\n')
