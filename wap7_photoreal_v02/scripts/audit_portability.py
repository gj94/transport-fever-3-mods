"""Read-only Blender dependency audit from an independently copied package.

Usage: blender -b -t 1 --python audit_portability.py -- PACKAGE REPORT.json
The package must be a fresh filesystem copy of the reviewed delivery folder.
The source is opened without saving. This does not claim game validation.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
root = Path(args[0]).resolve()
report_path = Path(args[1]).resolve()
master = root / 'WAP7_detail_v02.blend'
original = hashlib.sha256(master.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(master), load_ui=False)
problems = []
dependencies = []


def check_path(kind, name, filepath, packed=False):
    if packed:
        return
    if not filepath or filepath == '<builtin>':
        return
    if not filepath.startswith('//'):
        problems.append(f'{kind} {name}: external path is not relative')
    path = Path(bpy.path.abspath(filepath)).resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        problems.append(f'{kind} {name}: external dependency escapes copied package')
        return
    if not path.is_file():
        problems.append(f'{kind} {name}: missing {relative}')
        return
    data = path.read_bytes()
    dependencies.append({'kind': kind, 'name': name, 'path': relative,
                         'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})


images = []
for image in bpy.data.images:
    if image.source != 'FILE':
        continue
    packed = bool(image.packed_file)
    check_path('image', image.name, image.filepath, packed)
    if not packed:
        image.reload()
    # Accessing the data size forces Blender's image loader to resolve the copy.
    width, height = image.size[:]
    if not width or not height:
        problems.append('image ' + image.name + ': failed to load pixels')
    images.append({'name': image.name, 'packed': packed, 'width': width, 'height': height,
                   'relative_path': image.filepath if image.filepath.startswith('//') else None})
for font in bpy.data.fonts:
    check_path('font', font.name, font.filepath, bool(font.packed_file))
for library in bpy.data.libraries:
    check_path('library', library.name, library.filepath, bool(library.packed_file))
for clip in bpy.data.movieclips:
    check_path('movieclip', clip.name, clip.filepath)
for sound in bpy.data.sounds:
    check_path('sound', sound.name, sound.filepath, bool(sound.packed_file))

after = hashlib.sha256(master.read_bytes()).hexdigest()
if original != after:
    problems.append('Read-only audit changed source bytes')
scene = bpy.context.scene
report = {'blender_version': bpy.app.version_string,
          'master': master.name, 'master_sha256': original,
          'opened_from_fresh_copy': True, 'source_unchanged': original == after,
          'external_dependencies': dependencies, 'images': images,
          'objects': len(bpy.data.objects), 'meshes': len(bpy.data.meshes),
          'unit_system': scene.unit_settings.system,
          'unit_scale_length': scene.unit_settings.scale_length,
          'linked_libraries': len(bpy.data.libraries), 'problems': problems,
          'pass': not problems,
          'scope': 'Read-only source portability and dependency loading. No rendering, conversion or TF3 runtime test.'}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'pass': report['pass'], 'images': len(images),
                  'dependencies': len(dependencies), 'objects': report['objects'],
                  'problems': problems}), flush=True)
assert report['pass'], 'Portability audit failed'
