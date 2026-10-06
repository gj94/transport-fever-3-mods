"""Read-only authoring/delivery comparison of shader state and exact dependencies.

Usage: blender -b -t 1 --python compare_delivery_materials.py -- AUTHORING.blend COPIED_PACKAGE REPORT.json
Only the copied delivery is required to have exclusively package-local paths.
Both source files are left untouched. The resulting report contains no machine paths.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def simple(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bpy.types.ID):
        return {'id_type': value.bl_rna.identifier, 'name': value.name}
    try:
        return [simple(item) for item in value]
    except TypeError:
        return {'rna_type': value.bl_rna.identifier} if hasattr(value, 'bl_rna') else str(type(value))


def properties(value):
    result = {}
    for prop in value.bl_rna.properties:
        name = prop.identifier
        if name in {'rna_type', 'id_data', 'name', 'location', 'width', 'height',
                    'dimensions', 'select', 'show_options', 'show_preview', 'show_texture',
                    'hide', 'use_custom_color', 'label', 'users', 'tag', 'session_uid',
                    'is_evaluated', 'is_runtime_data', 'use_fake_user', 'use_extra_user'}:
            continue
        if name == 'color' and isinstance(value, bpy.types.Node):
            continue
        if prop.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            try:
                result[name] = simple(getattr(value, name))
            except (AttributeError, TypeError, ValueError):
                pass
    return result


def node_tree(tree, visiting=None):
    if tree is None:
        return None
    visiting = set() if visiting is None else set(visiting)
    if tree.name in visiting:
        return {'recursive_node_group': tree.name}
    visiting.add(tree.name)
    nodes = []
    for node in sorted(tree.nodes, key=lambda n: n.name):
        row = {'name': node.name, 'type': node.bl_idname, 'properties': properties(node),
               'inputs': [{'identifier': socket.identifier, 'name': socket.name,
                           'type': socket.bl_idname,
                           'value': simple(socket.default_value) if hasattr(socket, 'default_value') else None}
                          for socket in node.inputs],
               'outputs': [{'identifier': socket.identifier, 'name': socket.name,
                            'value': simple(socket.default_value) if hasattr(socket, 'default_value') else None}
                           for socket in node.outputs]}
        for key in ('image', 'object', 'texture'):
            if hasattr(node, key):
                item = getattr(node, key)
                row[key] = simple(item)
        for key in ('image_user', 'texture_mapping', 'color_mapping'):
            if hasattr(node, key):
                row[key] = properties(getattr(node, key))
        if hasattr(node, 'color_ramp'):
            ramp = node.color_ramp
            row['color_ramp'] = {'properties': properties(ramp),
                                 'elements': [{'position': e.position, 'color': list(e.color)} for e in ramp.elements]}
        if hasattr(node, 'mapping'):
            mapping = node.mapping
            row['mapping'] = {'properties': properties(mapping),
                               'curves': [[{'location': list(point.location), 'handle_type': point.handle_type}
                                           for point in curve.points] for curve in getattr(mapping, 'curves', [])]}
        if hasattr(node, 'node_tree') and node.node_tree:
            row['group'] = node_tree(node.node_tree, visiting)
        nodes.append(row)
    links = sorted((link.from_node.name, link.from_socket.identifier,
                    link.to_node.name, link.to_socket.identifier) for link in tree.links)
    return {'nodes': nodes, 'links': links}


def file_bytes(block):
    if block.packed_file:
        return bytes(block.packed_file.data)
    path = Path(bpy.path.abspath(block.filepath))
    if not path.is_file():
        raise RuntimeError('Missing source dependency: ' + block.name)
    return path.read_bytes()


def snapshot():
    materials = {material.name: {'properties': properties(material),
                                 'node_tree': node_tree(material.node_tree) if material.use_nodes else None}
                 for material in bpy.data.materials}
    worlds = {world.name: {'properties': properties(world),
                          'node_tree': node_tree(world.node_tree) if world.use_nodes else None}
              for world in bpy.data.worlds}
    images = {}
    for image in bpy.data.images:
        if image.source != 'FILE':
            continue
        data = file_bytes(image)
        images[image.name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                              'color_space': image.colorspace_settings.name,
                              'color_space_is_data': image.colorspace_settings.is_data,
                              'alpha_mode': image.alpha_mode, 'source': image.source,
                              'size': list(image.size), 'channels': image.channels,
                              'use_view_as_render': image.use_view_as_render}
    fonts = {}
    for font in bpy.data.fonts:
        if font.filepath in {'', '<builtin>'}:
            fonts[font.name] = {'builtin': True}
        else:
            data = file_bytes(font)
            fonts[font.name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    text = {}
    assignments = {}
    for obj in bpy.data.objects:
        if obj.hide_render:
            continue
        assignments[obj.name] = [slot.material.name if slot.material else None for slot in obj.material_slots]
        if obj.type == 'FONT':
            curve = obj.data
            text[obj.name] = {'properties': properties(curve),
                              'fonts': {key: getattr(curve, key).name if getattr(curve, key) else None
                                        for key in ('font', 'font_bold', 'font_italic', 'font_bold_italic')},
                              'body_format': [properties(item) for item in curve.body_format]}
    return {'materials': materials, 'worlds': worlds, 'images': images,
            'fonts': fonts, 'live_text': text, 'visible_material_assignments': assignments}


args = sys.argv[sys.argv.index('--') + 1:]
authoring = Path(args[0]).resolve()
delivery_root = Path(args[1]).resolve()
delivery = delivery_root / 'WAP7_detail_v02.blend'
report_path = Path(args[2]).resolve()
source_hash = hashlib.sha256(authoring.read_bytes()).hexdigest()
delivery_hash = hashlib.sha256(delivery.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(authoring), load_ui=False)
before = snapshot()
bpy.ops.wm.open_mainfile(filepath=str(delivery), load_ui=False)
after = snapshot()
differences = []
counts = {}
fingerprints = {}
for category, current in after.items():
    counts[category] = len(current)
    for name, value in current.items():
        if name not in before[category]:
            differences.append({'category': category, 'name': name, 'reason': 'new delivery datablock'})
        elif before[category][name] != value:
            differences.append({'category': category, 'name': name, 'reason': 'state changed'})
    fingerprints[category] = {'authoring_used_sha256': digest({name: before[category].get(name) for name in current}),
                               'delivery_sha256': digest(current)}
# Final authoring text objects must survive, because live type affects real glyphs.
for name in set(before['live_text']) - set(after['live_text']):
    differences.append({'category': 'live_text', 'name': name, 'reason': 'visible text was removed'})
for name in set(before['visible_material_assignments']) - set(after['visible_material_assignments']):
    differences.append({'category': 'visible_material_assignments', 'name': name, 'reason': 'visible object was removed'})
unchanged = source_hash == hashlib.sha256(authoring.read_bytes()).hexdigest() and delivery_hash == hashlib.sha256(delivery.read_bytes()).hexdigest()
report = {'authoring_master_sha256': source_hash, 'delivery_master_sha256': delivery_hash,
          'blender_version': bpy.app.version_string, 'compared_counts': counts,
          'category_fingerprints': fingerprints,
          'image_settings': after['images'], 'font_bytes': after['fonts'],
          'differences': differences, 'source_files_unchanged': unchanged,
          'pass': not differences and unchanged,
          'scope': 'Exact shader-node state, assignments, image bytes/color spaces/alpha and live-font bytes/layout comparison. Storage paths may change to package-relative dependencies. No TF3 runtime test.'}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'pass': report['pass'], 'compared_counts': counts, 'differences': differences}), flush=True)
assert report['pass'], 'Delivery material/font comparison failed'
