"""Upgrade an existing native pack without rebuilding geometry or icons."""
import hashlib
import json
import re
from pathlib import Path

from check_tf3_balance import table
from freight_locomotives import write_formation
from pack_settings import CACHE_VERSION, REVISION
from release_metadata import write_release_metadata
from tf3_lua import lua, write_lua
from vande_bharat import write_formations
from vehicle_performance import UPGRADED_KEYS, description, settings

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'game_build/gj94_indian_rail_pack'
BASELINE = ROOT / 'game_build/performance_upgrade_baseline.json'


def once(text, pattern, replacement):
    result, count = re.subn(pattern, lambda _: replacement, text)
    assert count == 1, (pattern, count)
    return result


def main():
    manifest = json.loads((MOD / 'mod.json').read_text())
    assert manifest['modId'] == MOD.name
    planned = {}
    for key in UPGRADED_KEYS:
        path = MOD / f'content/vehicle/train/{key}/{key}.mdl'
        text = path.read_text(encoding='utf8')
        spec = settings(key)
        land = table(text, 'landVehicle')
        updated = once(land, r'\btopSpeed=[-+\d.eE]+', 'topSpeed=' + lua(spec['speed'] / 3.6))
        engines = [dict(power=spec['power'], tractiveEffort=spec['effort'], type='ELECTRIC')] if spec['power'] else []
        original_engines = table(updated, 'engines')
        assert updated.count('engines=' + original_engines) == 1
        updated = updated.replace('engines=' + original_engines, 'engines=' + lua(engines), 1)
        text = text.replace(land, updated, 1)
        if 'comfort' in spec:
            text = once(text, r'\bcomfortFactor=[-+\d.eE]+', 'comfortFactor=' + lua(spec['comfort']))
        text = once(text, r'\bdescription="(?:[^"\\]|\\.)*"', 'description=' + lua(description(key)))
        text = once(text, r'\b__version="[^"]+"', '__version=' + lua(CACHE_VERSION))
        planned[path] = text

    # Keep the original metadata and complete resource hashes for independent
    # validation. Reapplying this revision must not overwrite its baseline.
    if not BASELINE.exists() or json.loads(BASELINE.read_text())['target_revision'] != REVISION:
        originals = {p.relative_to(MOD).as_posix(): p.read_text(encoding='utf8') for p in planned}
        originals.update({p.relative_to(MOD).as_posix(): p.read_text(encoding='utf8') for p in MOD.rglob('*.mu.lua')})
        hashes = {p.relative_to(MOD).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in MOD.rglob('*') if p.is_file()}
        BASELINE.write_text(json.dumps(dict(target_revision=REVISION, previous_revision=manifest['revision'],
            models_and_formations=originals, files=hashes), indent=2) + '\n', encoding='utf8')
    for path, text in planned.items():
        path.write_text(text, encoding='utf8')
    write_formation(ROOT, write_lua)
    write_formations(ROOT, write_lua)
    write_release_metadata(MOD)
    print(f'Updated {len(planned)} model metadata tables and three formation descriptions; resource revision {REVISION}.')


if __name__ == '__main__':
    main()
