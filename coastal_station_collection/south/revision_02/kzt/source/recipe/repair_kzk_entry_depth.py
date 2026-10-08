"""Expose the photographed doorway louvers with a recessed dark backing, in a new source revision."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(__file__).resolve().parents[1];R=B/'revision_02/kzk';src=B/'kzk/KZK_station_v01.blend';h0=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;Q=json.loads((R/'QA_BUILD.json').read_text());b=Q['building'];sg=b['side'];front=b['front_y'];bx=b['center'][0];bounds=[]
o=S.objects['KZK triple louvered vent'];bounds.extend(o.matrix_world@Vector(v) for v in o.bound_box)
for v in o.data.vertices:v.co.y+=sg*.20
o.data.update()
o=S.objects['KZK horizontal concrete rain shade'];bounds.extend(o.matrix_world@Vector(v) for v in o.bound_box)
for v in o.data.vertices:
 local=(v.co.y-front)/sg;v.co.y=front+sg*(.84+(local-.5)*1.44/.88)
o.data.update()
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
for x in [-.8,0,.8]:
 vs=[(bx+x+xx*.755/2,front+sg*.22+yy*.035/2,.95+2.57+zz*.40/2) for xx,yy,zz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];me=bpy.data.meshes.new('KZK recessed louver backing');me.from_pydata(vs,[],F);me.materials.append(bpy.data.materials['dark']);ob=bpy.data.objects.new('KZK recessed louver backing',me);S.collection.objects.link(ob);bounds.extend(Vector(v) for v in vs)
bpy.context.view_layer.update()
for name in ['KZK triple louvered vent','KZK horizontal concrete rain shade']:bounds.extend(S.objects[name].matrix_world@Vector(v) for v in S.objects[name].bound_box)
Q['entry_depth_repair']={'louver_outward_shift_m':.20,'three_dark_backings':True,'rainshade_projection_m':1.56,'reason':'Photographed horizontal slats were visually lost against the cream lintel; explicit recessed dark backing and exposed slats follow the August2023 source. Broad shade projection is estimated.'};Q['objects']=len(S.objects);Q['meshes']=len([o for o in S.objects if o.type=='MESH']);Q['vertices']=sum(len(o.data.vertices) for o in S.objects if o.type=='MESH');(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));dest=R/'KZK_station_v01.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);h1=hashlib.sha256(dest.read_bytes()).hexdigest();(R/'QA_ENTRY_REPAIR.json').write_text(json.dumps({'station':'KZK','input_source_sha256':h0,'output_source_sha256':h1,**Q['entry_depth_repair'],'scope':'Only entry louver backing/depth and concrete rainshade; rooms, paths, tracks and platforms unchanged'},indent=2))
lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)));corners=[Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]];prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());redo=[];ret=[]
for name,r in prov['views'].items():
 cam=S.objects.get(r.get('camera',''));loc=cam.location.copy();rot=cam.rotation_euler.copy();lens=cam.data.lens;ov=r.get('camera_override')
 if ov:cam.location=ov['location'];cam.rotation_euler=(Vector(ov['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=ov['lens_mm']
 pp=[world_to_camera_view(S,cam,p) for p in corners];out=max(v.z for v in pp)<=0 or max(v.x for v in pp)<0 or min(v.x for v in pp)>1 or max(v.y for v in pp)<0 or min(v.y for v in pp)>1;cam.location=loc;cam.rotation_euler=rot;cam.data.lens=lens
 if out:r.update(unchanged_view_verified=True,current_source_scene_sha256=h1,inheritance_basis='Only approach-side entry louvers and shade changed, outside recorded camera frustum');ret.append(name)
 else:redo.append(name[:2])
prov['current_source_scene_sha256']=h1;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(R/'REPAIR_LINEAGE.json').write_text(json.dumps({'station':'KZK','input_source_sha256':h0,'output_source_sha256':h1,'changed_bounds':[list(lo),list(hi)],'retained_views':ret,'rerender_prefixes':sorted(set(redo))},indent=2))
