"""Attach the approved local horn without putting its recording in Git."""
import os
import shutil
import wave
from pathlib import Path
from pack_settings import REVISION,CACHE_VERSION


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
    backup = root / f'game_build/wap7_horn_before_v{REVISION:02d}'
    backup.mkdir(exist_ok=True)
    for path in [mod / 'mod.json', model]:
        target = backup / path.name
        if not target.exists():
            shutil.copy2(path, target)
    updated = original.replace(previous, custom, 1).replace(stock, custom, 1)
    import re
    updated = re.sub(r'__version="_v\d+"', '__version="' + CACHE_VERSION + '"', updated)
    model.write_text(updated)
    # All locomotives use the same approved sound set, stored only once.
    for key in ('wag9','wag12b_a','wag12b_b'):
        other = mod / f'content/vehicle/train/{key}/{key}.mdl'
        if not other.is_file():
            continue
        target = backup / other.name
        if not target.exists():
            shutil.copy2(other, target)
        text = other.read_text().replace(stock, custom, 1)
        text = re.sub(r'__version="_v\d+"', '__version="' + CACHE_VERSION + '"', text)
        other.write_text(text)
    metadata = json.loads((mod / 'mod.json').read_text())
    metadata['revision'] = REVISION
    (mod / 'mod.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Local sound set attached to available locomotives with approved horn and base electric tracks; pack revision {REVISION}')
