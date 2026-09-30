"""Package the validated native rail pack and verify its archived contents."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from pack_settings import REVISION
from wap7_audio import SOUND_SET_REF,STOCK_SOUND_SET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--copy-to', type=Path)
    audio = parser.add_mutually_exclusive_group()
    audio.add_argument('--private', action='store_true', help='Keep a local audio customization out of the tracked release archive')
    audio.add_argument('--stock-audio', action='store_true', help='Omit private audio and use the base electric sound set in the public archive')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / 'game_build/gj94_indian_rail_pack'
    revision = json.loads((source / 'mod.json').read_text())['revision']
    assert revision == REVISION
    has_private_audio = (source / 'content/vehicle/train/wap7/sound/wap7_horn.wav').is_file()
    if has_private_audio and not (args.private or args.stock_audio):
        parser.error('The build contains a private horn; use --private locally or --stock-audio for a public release.')
    files = sorted(p for p in source.rglob('*') if p.is_file())
    private_files = {'content/vehicle/train/wap7/sound/wap7_horn.wav', 'content/vehicle/train/wap7/sound/wap7.snd.lua'}
    if args.stock_audio:
        files = [p for p in files if p.relative_to(source).as_posix() not in private_files]
    target = root / ('game_build/packages/Indian-Rail-Prototype-Pack-TF3-Private.zip' if args.private else 'dist/Indian-Rail-Prototype-Pack-TF3.zip')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix('.zip.tmp')
    digests = {}
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            name = path.relative_to(source.parent).as_posix()
            data = path.read_bytes()
            if args.stock_audio and path.suffix == '.mdl':
                data = data.replace(SOUND_SET_REF.encode(), STOCK_SOUND_SET.encode())
            archive.writestr(name, data)
            digests[name] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(temporary) as archive:
        assert set(archive.namelist()) == set(digests)
        for name, digest in digests.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
        if not args.private:
            assert not any(name.endswith('/sound/wap7_horn.wav') for name in archive.namelist())
            assert not any(SOUND_SET_REF.encode() in archive.read(name) for name in archive.namelist() if name.endswith('.mdl'))
    temporary.replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = target.parent / 'SHA256SUMS.txt'
    lines = manifest.read_text().splitlines() if manifest.exists() else []
    lines = [line for line in lines if not line.endswith('  ' + target.name)]
    lines.append(digest + '  ' + target.name)
    manifest.write_text('\n'.join(lines) + '\n')
    if args.copy_to:
        destination = args.copy_to / target.name
        shutil.copy2(target, destination)
        assert hashlib.sha256(destination.read_bytes()).hexdigest() == digest
    print(f'Revision {revision}: {len(files)} files packaged and individually verified; {target.stat().st_size:,} bytes')
    print(f'SHA256 {digest}')


if __name__ == '__main__':
    main()
