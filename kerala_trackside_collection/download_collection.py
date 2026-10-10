#!/usr/bin/env python3
"""Download/reconstruct selected Kerala Trackside packs with SHA-256 verification.
Uses only Python 3's standard library. No credentials or package installation needed.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import urllib.request

BASE_URL = 'https://raw.githubusercontent.com/gj94/transport-fever-3-mods/main/kerala_trackside_collection/'
ROOT = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def valid(path, entry):
    return path.is_file() and path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256']


def safe_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError('Unsafe manifest path: ' + value)
    return path


def fetch_part(entry, offline):
    relative = safe_path(entry['path'])
    target = ROOT.joinpath(*relative.parts)
    if valid(target, entry):
        return target
    if offline:
        raise RuntimeError('Missing or invalid local part: ' + str(relative))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.download')
    url = BASE_URL + relative.as_posix()
    request = urllib.request.Request(url, headers={'User-Agent': 'KeralaTracksideDownloader/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=180) as response, temporary.open('wb') as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
        if not valid(temporary, entry):
            raise RuntimeError('Downloaded part failed size/SHA-256 check: ' + str(relative))
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target


def restore(archive, output_dir, offline):
    name = archive['file_name']
    if PurePosixPath(name).name != name or '\\' in name:
        raise ValueError('Invalid archive filename')
    destination = output_dir / name
    if valid(destination, archive):
        print('Already verified:', name)
        return
    if destination.exists():
        raise RuntimeError('Output already exists with different contents; move it aside first: ' + str(destination))
    parts = [fetch_part(entry, offline) for entry in archive['files']]
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.restoring')
    try:
        with temporary.open('wb') as output:
            for part in parts:
                with part.open('rb') as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b''):
                        output.write(chunk)
        if not valid(temporary, archive):
            raise RuntimeError('Restored archive failed size/SHA-256 check: ' + name)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    print('Verified:', name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--list', action='store_true', help='List the 24 independent archive packs')
    mode.add_argument('--all', action='store_true', help='Restore all 24 archive packs')
    mode.add_argument('--native', action='store_true', help='Restore the 5 packed Blender asset libraries')
    mode.add_argument('--archive', action='append', metavar='NAME', help='Exact archive filename (repeat for more than one)')
    parser.add_argument('--offline', action='store_true', help='Use only local files from a clone, repository ZIP or manual download')
    parser.add_argument('--output', type=Path, default=ROOT / 'restored_archives', help='Destination for complete verified ZIPs')
    args = parser.parse_args(argv)
    manifest_path = ROOT / 'ARCHIVES.json'
    if not manifest_path.is_file():
        parser.error('Save ARCHIVES.json beside this script first.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    archives = manifest['archives']
    if args.list:
        for archive in archives:
            print(f"{archive['file_name']}  ({archive['bytes'] / 1024 / 1024:.1f} MiB; {archive['delivery_role']})")
        return 0
    if args.native:
        selected = [a for a in archives if a['delivery_role'] == 'native_library']
    elif args.archive:
        names = set(args.archive)
        unknown = names - {a['file_name'] for a in archives}
        if unknown:
            parser.error('Unknown archive(s): ' + ', '.join(sorted(unknown)))
        selected = [a for a in archives if a['file_name'] in names]
    else:
        selected = archives
    print(f"Restoring {len(selected)} archive(s), {sum(a['bytes'] for a in selected) / 1024 / 1024:.1f} MiB total.")
    for archive in selected:
        restore(archive, args.output, args.offline)
    print('Done. Complete ZIPs:', args.output.resolve())
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print('Error:', error, file=sys.stderr)
        sys.exit(1)
