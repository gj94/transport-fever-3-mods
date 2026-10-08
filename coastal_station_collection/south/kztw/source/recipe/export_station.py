import os
"""Portable geometry-equivalent glTF, authoring blend remains the authoritative source."""
from pathlib import Path
import bpy,sys,json,hashlib
BASE=Path(__file__).resolve().parents[1];code=sys.argv[sys.argv.index('--')+1].upper();R=Path(os.environ.get('SOUTH_STATION_OUTPUT_DIR',str(BASE/code.lower())));src=R/f'{code}_station_v01.blend';bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;sha=hashlib.sha256(src.read_bytes()).hexdigest();out=R/'exchange';out.mkdir(exist_ok=True);dg=bpy.context.evaluated_depsgraph_get();converted=[]
for o in list(S.objects):
 if o.type in ('FONT','CURVE'):
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));n=bpy.data.objects.new(o.name+'_portable',me);S.collection.objects.link(n);n.matrix_world=o.matrix_world;converted.append(o)
for o in converted:bpy.data.objects.remove(o,do_unlink=True)
for o in S.objects:o.select_set(o.type=='MESH')
meshes=[o for o in S.objects if o.type=='MESH'];bpy.context.view_layer.objects.active=meshes[0];glb=out/f'{code}_station_v01.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_yup=True,export_extras=True)
report=dict(station=code,file=glb.name,source_blend_sha256=sha,sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),bytes=glb.stat().st_size,exported_mesh_objects=len(meshes),exported_mesh_vertices=sum(len(o.data.vertices) for o in meshes),coordinate_units='metres',gltf_axis='Y-up; import at identity transforms',material_limit='Procedural noise and bump are not baked; portable materials use base colors, roughness and metallic settings. Geometry and shaped labels preserved.',status='Export written; independent glTF structural verification follows')
(out/'MANIFEST.json').write_text(json.dumps(report,indent=2));print('EXPORTED',code,glb.stat().st_size,flush=True)
