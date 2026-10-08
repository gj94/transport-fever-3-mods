"""Export the frozen packed scene without modifying it or invalidating render hashes."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
src=P/'ERS_full_station_v02.blend'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
source_hash=digest(src)
bpy.ops.wm.open_mainfile(filepath=str(src))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
out=P/'exports'/'ERS_full_station_v02.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
result={'source_blend':src.name,'source_blend_sha256':source_hash,'source_file_unchanged':source_hash==digest(src),'export':str(out.relative_to(P)),'export_bytes':out.stat().st_size,'export_sha256':digest(out),'blender':bpy.app.version_string}
(P/'exports'/'export_manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
# Deliberately do not save the scene after export: its proof-bound hash stays stable.
