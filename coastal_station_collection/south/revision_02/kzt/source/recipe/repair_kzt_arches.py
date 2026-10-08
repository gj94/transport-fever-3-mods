"""Expose the already modelled shallow arch profiles above the lattice, preserving the frozen candidate."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(__file__).resolve().parents[1];src=B/'kzt/KZT_station_v01.blend';R=B/'revision_02/kzt';bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;h0=hashlib.sha256(src.read_bytes()).hexdigest();Q=json.loads((R/'QA_BUILD.json').read_text());sg=Q['building']['side'];bounds=[];changed=[]
for o in S.objects:
 if o.name.startswith('KZT turquoise arched parapet'):
  bounds.extend(o.matrix_world@Vector(v) for v in o.bound_box);o.location.y+=sg*.16;changed.append(o.name)
assert len(changed)==6,changed
bpy.context.view_layer.update()
for n in changed:bounds.extend(S.objects[n].matrix_world@Vector(v) for v in S.objects[n].bound_box)
Q['arch_face_repair']={'moved_objects':changed,'forward_shift_m':.16,'reason':'Existing curved spandrels were hidden behind the rectangular lattice/backing planes; move their faces forward to expose the photographed shallow arches.'};(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));dest=R/'KZT_station_v01.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);h1=hashlib.sha256(dest.read_bytes()).hexdigest();(R/'QA_ARCH_REPAIR.json').write_text(json.dumps({'station':'KZT','input_source_sha256':h0,'output_source_sha256':h1,**Q['arch_face_repair'],'scope':'Only six existing facade spandrels moved in depth; lattice, room geometry, tracks/platforms and facilities unchanged'},indent=2))
lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)));corners=[Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]];prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());redo=[];ret=[]
for name,r in prov['views'].items():
 cam=S.objects.get(r.get('camera',''));oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldlens=cam.data.lens;ov=r.get('camera_override')
 if ov:cam.location=ov['location'];cam.rotation_euler=(Vector(ov['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=ov['lens_mm']
 pp=[world_to_camera_view(S,cam,p) for p in corners];out=max(v.z for v in pp)<=0 or max(v.x for v in pp)<0 or min(v.x for v in pp)>1 or max(v.y for v in pp)<0 or min(v.y for v in pp)>1;cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.lens=oldlens
 if out:r.update(unchanged_view_verified=True,current_source_scene_sha256=h1,inheritance_basis='Only facade spandrels shifted0.16m, wholly outside this recorded camera frustum');ret.append(name)
 else:redo.append(name[:2])
prov['current_source_scene_sha256']=h1;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(R/'REPAIR_LINEAGE.json').write_text(json.dumps({'station':'KZT','input_source_sha256':h0,'output_source_sha256':h1,'changed_bounds':[list(lo),list(hi)],'retained_views':ret,'rerender_prefixes':sorted(set(redo))},indent=2))
