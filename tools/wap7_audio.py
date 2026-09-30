"""Attach the approved local horn without putting its recording in Git."""
import os
import shutil
import wave
from pathlib import Path


HORN_REF = 'sound/wap7_horn.wav'
STOCK_SOUND_SET = '::/vehicle/train/shared/sound/train_electric_modern.snd'
SOUND_SET_REF = 'gj94_indian_rail_pack::/vehicle/train/wap7/sound/wap7.snd'


def attach_local_horn(root, folder, sound_config):
    source = Path(os.environ.get('TF3_WAP7_HORN', root.parent / 'WAP7-Horn-Preview.wav'))
    if not source.is_file():
        if 'TF3_WAP7_HORN' in os.environ:
            raise FileNotFoundError(source)
        return False
    with wave.open(str(source)) as audio:
        assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) == (1, 2, 48000)
        assert audio.getnframes() == 96000, 'Prepare a two-second horn clip'
    target = folder / HORN_REF
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    shutil.copy2(root / 'tools/wap7.snd.lua', folder / 'sound/wap7.snd.lua')
    sound_config['soundSet']['name'] = SOUND_SET_REF
    sound_config.get('effects', {}).pop('horn', None)
    return True


if __name__ == '__main__':
    import json
    root = Path(__file__).resolve().parents[1]
    mod = root / 'game_build/gj94_indian_rail_pack'
    folder = mod / 'content/vehicle/train/wap7'
    model = folder / 'wap7.mdl'
    original = model.read_text()
    stock = 'soundConfig={soundSet={name="' + STOCK_SOUND_SET + '"}}'
    previous = 'soundConfig={soundSet={name="' + STOCK_SOUND_SET + '"},effects={horn={"' + HORN_REF + '"}}}'
    custom = 'soundConfig={soundSet={name="' + SOUND_SET_REF + '"}}'
    assert sum(original.count(ref) for ref in (stock, previous, custom)) == 1
    if not attach_local_horn(root, folder, {'soundSet': {'name': STOCK_SOUND_SET}}):
        raise FileNotFoundError('Set TF3_WAP7_HORN or provide WAP7-Horn-Preview.wav beside the repository')
    backup = root / 'game_build/wap7_horn_before_v10'
    backup.mkdir(exist_ok=True)
    for path in [mod / 'mod.json', model]:
        target = backup / path.name
        if not target.exists():
            shutil.copy2(path, target)
    updated = original.replace(previous, custom, 1).replace(stock, custom, 1)
    for version in ('_v07', '_v08', '_v09'):
        updated = updated.replace('__version="' + version + '"', '__version="_v10"')
    model.write_text(updated)
    metadata = json.loads((mod / 'mod.json').read_text())
    metadata['revision'] = 10
    (mod / 'mod.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('WAP7 local sound set attached with approved horn and base electric tracks; pack revision 10')
