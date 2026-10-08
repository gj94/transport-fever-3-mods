"""Memory-bounded editable glTF parts; shared world metre coordinates.
Run one Blender process at a time. No rendering during exports.
"""
import bpy,json,sys,gc,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exchange';O.mkdir(exist_ok=True)
S=bpy.context.scene
for c in bpy.data.collections:c.hide_render=False;c.hide_viewport=False
for o in S.objects:o.hide_set(False)
groups=[('01_heritage',['01_','02_']),('02_interiors',['03_','04_','05_','06_','18_','80_']),('03_platform_bodies',['12_']),('04_shelters_and_furniture',['13_']),('05_bridges',['14_']),('06_signals_ohe',['15_']),('07_yard_utilities',['11_','11B','16_','16B','20_']),('08_running_rails',['10B']),('09_surrounds',['17_']),('10_signage',['19_']),('11_paving_and_forecourt',['21_'])]
items=[]
for name,prefixes in groups:
 objs=set(o for c in bpy.data.collections if any(c.name.startswith(p) for p in prefixes) for o in c.objects if o.type in ('MESH','FONT','CURVE'))
 items.append((name,objs))
track=bpy.data.collections.get('10_TRACK_NETWORK_MAPPED_PROFILES');routes=sorted({o.get('route_id','') for o in track.objects})
for i in range(0,len(routes),5):
 ids=routes[i:i+5];objs={o for o in track.objects if o.get('route_id','') in ids};items.append(('tracks_%02d'%(i//5+1),objs))
manifest=[]
converted={}
dg=bpy.context.evaluated_depsgraph_get()
for old in [o for o in S.objects if o.type in ('FONT','CURVE')]:
 try:
  me=bpy.data.meshes.new_from_object(old.evaluated_get(dg));ob=bpy.data.objects.new(old.name+'_exchange_mesh',me);S.collection.objects.link(ob);ob.matrix_world=old.matrix_world;converted[old]=ob
 except Exception as e:print('CONVERT_WARNING',old.name,str(e),flush=True)
for name,objs in items:
 if not objs:continue
 objs={converted.get(o,o) for o in objs}
 path=O/(name+'.glb')
 for o in S.objects:o.select_set(False)
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=next(iter(objs))
 print('EXPORT',name,len(objs),flush=True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_yup=True,export_extras=True)
 manifest.append({'file':path.name,'objects':len(objs),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2));gc.collect()
(O/'README.txt').write_text('TVC v02 modular glTF exchange. Import all GLBs together at identity transforms; coordinates are metres in one shared station-local frame, exported glTF Y-up. No trains. Source .blend is authoritative. Procedural material noise/bump may not transfer; base colours and geometry do. Globe map data attribution: © OpenStreetMap contributors, ODbL1.0 https://www.openstreetmap.org/copyright . No new licence for authored geometry. See parent README.md for evidence limits.')
print('EXPORT_COMPLETE',len(manifest),flush=True)
