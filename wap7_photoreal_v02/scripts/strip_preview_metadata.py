"""Remove PNG text/EXIF metadata without decoding or recompressing image data.

Run after rendering: python scripts/strip_preview_metadata.py
Original IDAT chunks are retained byte-for-byte. Pillow independently verifies
that decoded pixels are unchanged. Per-render JSON records preserve the original
rendered-file hash alongside the published file hash.
"""
import hashlib
import json
import struct
import zlib
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'qa/preview_metadata_cleanup.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def chunks(data):
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'Not a PNG'
    pos = 8
    rows = []
    while pos < len(data):
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        end = pos + size + 12
        block = data[pos:end]
        assert end <= len(data), 'Truncated PNG'
        assert zlib.crc32(block[4:-4]) & 0xffffffff == struct.unpack('>I', block[-4:])[0], 'Bad PNG CRC'
        rows.append((kind, block, block[8:-4]))
        pos = end
        if kind == b'IEND':
            break
    assert pos == len(data), 'Trailing PNG data'
    return rows


def pixel_stamp(path):
    with Image.open(path) as image:
        image.load()
        return {'width': image.width, 'height': image.height, 'mode': image.mode,
                'decoded_pixels_sha256': sha(image.tobytes())}


records = json.loads(REPORT.read_text())['images'] if REPORT.is_file() else []
by_path = {row['path']: row for row in records}
for path in sorted((ROOT / 'previews').rglob('*.png')):
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    original_chunks = chunks(raw)
    removed = [kind.decode() for kind, _, _ in original_chunks
               if kind in {b'tEXt', b'zTXt', b'iTXt', b'eXIf'}]
    if not removed:
        continue
    before_pixels = pixel_stamp(path)
    clean = raw[:8] + b''.join(block for kind, block, _ in original_chunks
                              if kind not in {b'tEXt', b'zTXt', b'iTXt', b'eXIf'})
    original_idat = b''.join(data for kind, _, data in original_chunks if kind == b'IDAT')
    clean_idat = b''.join(data for kind, _, data in chunks(clean) if kind == b'IDAT')
    assert original_idat == clean_idat, 'Image data changed'
    path.write_bytes(clean)
    after_pixels = pixel_stamp(path)
    assert before_pixels == after_pixels, 'Decoded pixels changed'
    by_path[relative] = {'path': relative, 'raw_render_sha256': sha(raw),
                         'published_image_sha256': sha(clean), 'removed_chunk_types': sorted(set(removed)),
                         'original_idat_sha256': sha(original_idat),
                         'published_idat_sha256': sha(clean_idat),
                         'idat_bytes_unchanged': True, 'decoded_pixels_unchanged': True,
                         **after_pixels}
    print('LOSSLESS_METADATA_CLEANUP', relative, sha(clean), flush=True)

# Preserve the renderer's original hash, then identify the published PNG.
for record in by_path.values():
    raw_hash = record['raw_render_sha256']
    for path in list((ROOT / 'qa').rglob('*.json')) + list((ROOT / 'previews').rglob('*.json')):
        if path == REPORT:
            continue
        value = json.loads(path.read_text())
        if not isinstance(value, dict):
            continue
        changed = False
        for key in ('image_sha256', 'output_png_sha256', 'png_sha256'):
            if value.get(key) == raw_hash:
                value['render_output_image_sha256'] = raw_hash
                value[key] = record['published_image_sha256']
                value['publication_metadata_cleanup'] = {
                    'report': 'qa/preview_metadata_cleanup.json', 'path': record['path'],
                    'idat_bytes_unchanged': True, 'decoded_pixels_unchanged': True}
                changed = True
                if 'png_bytes' in value:
                    value['render_output_png_bytes'] = value['png_bytes']
                    value['png_bytes'] = (ROOT / record['path']).stat().st_size
                if 'image_bytes' in value:
                    value['render_output_image_bytes'] = value['image_bytes']
                    value['image_bytes'] = (ROOT / record['path']).stat().st_size
        if changed:
            path.write_text(json.dumps(value, indent=2) + '\n')

# Render records keep paths relative to the distributed package, not to a
# particular computer. Only paths naming a real file in this package qualify.
def portable_paths(value):
    if isinstance(value, dict):
        return {key: portable_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_paths(item) for item in value]
    if isinstance(value, str) and value.startswith('/'):
        marker = '/' + ROOT.name + '/'
        if marker in value:
            relative = value.split(marker, 1)[1]
            if (ROOT / relative).is_file():
                return relative
    return value

for path in list((ROOT / 'qa').rglob('*.json')) + list((ROOT / 'previews').rglob('*.json')):
    if path == REPORT:
        continue
    before = json.loads(path.read_text())
    after = portable_paths(before)
    if before != after:
        path.write_text(json.dumps(after, indent=2) + '\n')

REPORT.write_text(json.dumps({'method': 'Remove PNG text and EXIF chunks; retain exact original compressed IDAT chunks',
                              'images': sorted(by_path.values(), key=lambda row: row['path'])}, indent=2) + '\n')
