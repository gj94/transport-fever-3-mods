"""Read-only geometry/portability checks, saves qa_validation.json."""
import bpy,json,math,struct
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_2017_station.blend'))
s=bpy.context.scene
issues=[]
images=[i for i in bpy.data.images if i.source=='FILE']
for i in images:
 if not i.packed_file:issues.append('External image dependency: '+i.name)
nonfinite=[];empty=[]
for o in s.objects:
 if o.type=='MESH':
  if not o.data.vertices:empty.append(o.name)
  if any(not math.isfinite(v) for vert in o.data.vertices for v in vert.co):nonfinite.append(o.name)
railheads=[o for o in s.objects if o.name.startswith('Rail head')]
ys=sorted(o.location.y for o in railheads)
gauges=[round(ys[1]-ys[0]-.065,6),round(ys[3]-ys[2]-.065,6)]
# Original cube geometry has signed volume > 0 when outward-facing.
import bmesh
negative=[]
for o in s.objects:
 if o.type=='MESH' and len(o.data.vertices)==8 and len(o.data.polygons)==6:
  bm=bmesh.new();bm.from_mesh(o.data);vol=bm.calc_volume(signed=True);bm.free()
  if vol<=0:negative.append(o.name)
with open(P/'exports'/'ERS_2017_station.glb','rb') as f:
 magic,ver,size=struct.unpack('<4sII',f.read(12));clen,ctyp=struct.unpack('<II',f.read(8));gltf=json.loads(f.read(clen))
q={'saved_blend_reopened':True,'units_metric':s.unit_settings.system=='METRIC','unit_scale':s.unit_settings.scale_length,'source_file_image_count':len(images),'all_file_images_packed':all(i.packed_file for i in images),'empty_meshes':empty,'nonfinite_geometry':nonfinite,'inward_box_meshes':negative,'measured_inner_rail_head_gauges_m':gauges,'glb_magic':magic.decode(),'glb_version':ver,'glb_size_matches':size==(P/'exports'/'ERS_2017_station.glb').stat().st_size,'glb_meshes':len(gltf.get('meshes',[])),'glb_images':len(gltf.get('images',[])),'glb_external_uris':[v['uri'] for v in gltf.get('images',[]) if 'uri' in v]+[v['uri'] for v in gltf.get('buffers',[]) if 'uri' in v],'issues':issues,'visual_review':'See QA.md; automated checks do not replace render inspection'}
(P/'qa_validation.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
assert not (issues or empty or nonfinite or negative)
assert all(abs(g-1.675)<1e-5 for g in gauges), 'Rail gauge outside 0.01 mm tolerance'
assert q['glb_size_matches'] and not q['glb_external_uris']
