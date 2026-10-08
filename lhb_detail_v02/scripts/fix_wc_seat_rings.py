"""Localized post-build repair: replace disconnected WC seat rods only.
Run after build (and after the 1A legend correction); unchanged objects/materials
are fingerprinted before/after. Original build modules are intentionally retained.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def boxcoords(o):return [o.matrix_world@Vector(c) for c in o.bound_box]
def fingerprint():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  if o.name.startswith('WC_seat_ring'):continue
  r=[o.name,o.type,o.parent.name if o.parent else None,[list(v) for v in o.matrix_world],sorted(c.name for c in o.users_collection),o.hide_render,o.hide_viewport]
  if o.type in ('MESH','FONT','CURVE'):
   ev=o.evaluated_get(dg);me=ev.to_mesh();r += [[[list(v.co) for v in me.vertices],[[list(p.vertices),p.material_index,p.use_smooth] for p in me.polygons],[m.name if m else None for m in me.materials]]];ev.to_mesh_clear()
  r += [{key:str(o[key]) for key in o.keys()}];out[o.name]=digest(r)
 return out
def mats():
 out=[]
 for m in bpy.data.materials:
  ns=[]
  if m.use_nodes:
   for n in m.node_tree.nodes:
    sockets=[]
    for s in n.inputs:
     if hasattr(s,'default_value'):
      v=s.default_value
      try:v=list(v)
      except TypeError:pass
      sockets.append([s.name,v])
    ns.append([n.name,n.bl_idname,sockets])
   links=sorted([l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in m.node_tree.links)
  else:links=[]
  out.append([m.name,list(m.diffuse_color),m.use_nodes,ns,links])
 return digest(out)
reports=[]
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 source=P/'models'/f'LHB_{k}.blend';before_sha=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);bpy.context.view_layer.update()
 old=[o for o in bpy.data.objects if o.name.startswith('WC_seat_ring')];assert len(old)==(24 if k=='1A' else 48),(k,len(old))
 baseline=fingerprint();materials=mats();groups={}
 for o in old:
  cs=boxcoords(o);c=sum(cs,Vector())/8;groups.setdefault((c.x>0,c.y>0),[]).append(o)
 changes=[]
 for sign,objects in groups.items():
  assert len(objects)==24
  pts=[p for o in objects for p in boxcoords(o)];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  parent=objects[0].parent;col=objects[0].users_collection[0];mat=objects[0].data.materials[0]
  verts=[];N=33;M=24
  for cx,cy,start in [(.26-.135,.185-.135,0),(-.26+.135,.185-.135,90),(-.26+.135,-.185+.135,180),(.26-.135,-.185+.135,270)]:
   for j in range(N):
    a=math.radians(start+90*j/(N-1));u=cx+.135*math.cos(a);v=cy+.135*math.sin(a)
    for t in range(M):
     b=t*math.tau/M;verts.append((u+.029*math.cos(b)*math.cos(a),v+.029*math.cos(b)*math.sin(a),.029*math.sin(b)))
  mn=[min(v[i] for v in verts) for i in range(3)];mx=[max(v[i] for v in verts) for i in range(3)]
  verts=[tuple(lo[i]+(v[i]-mn[i])/(mx[i]-mn[i])*(hi[i]-lo[i]) for i in range(3)) for v in verts];L=4*N
  faces=[(i*M+j,((i+1)%L)*M+j,((i+1)%L)*M+(j+1)%M,i*M+(j+1)%M) for i in range(L) for j in range(M)]
  me=bpy.data.meshes.new('WC_seat_continuous_mesh');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert abs(vol)>1e-6
  if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(me);bm.free()
  for p in me.polygons:p.use_smooth=True
  ob=bpy.data.objects.new('WC_seat_ring_continuous_'+('positive' if sign[0] else 'negative'),me);col.objects.link(ob);ob.parent=parent;me.materials.append(mat)
  removed=[o.name for o in objects]
  for o in objects:bpy.data.objects.remove(o,do_unlink=True)
  bpy.context.view_layer.update();cs=boxcoords(ob);newlo=[min(p[i] for p in cs) for i in range(3)];newhi=[max(p[i] for p in cs) for i in range(3)];assert max(abs(a-b) for a,b in zip(lo+hi,newlo+newhi))<2e-6
  changes.append({'removed_objects':removed,'replacement':ob.name,'bounds_before':[lo,hi],'bounds_after':[newlo,newhi],'vertices':len(me.vertices),'faces':len(me.polygons),'manifold':True,'material':mat.name,'parent':parent.name})
 assert fingerprint()==baseline and mats()==materials
 root=bpy.data.objects[f'LHB_{k}_ROOT_metres'];patch={'script':'scripts/fix_wc_seat_rings.py','sha256':sha(Path(__file__)),'scope':'Only WC_seat_ring disconnected rods replaced by continuous manifold rings; all other evaluated geometry, hierarchy, custom properties and all material node inputs/links unchanged'};root['wc_seat_ring_patch']=json.dumps(patch,sort_keys=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 glass=bpy.data.materials['GLASS_source_transmission_FBX_alpha'];bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=0;bs.inputs['Alpha'].default_value=.22;glass.diffuse_color=(*glass.diffuse_color[:3],.22)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.fbx(filepath=str(source.with_suffix('.fbx')),use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
 for suffix in ['manifest','markers']:
  p=P/'models'/f'LHB_{k}_{suffix}.json';d=json.loads(p.read_text());d['wc_seat_ring_patch']=patch;p.write_text(json.dumps(d,indent=2))
 reports.append({'variant':k,'status':'pass','source_sha256_before':before_sha,'source_sha256_after':sha(source),'fbx_sha256_after':sha(source.with_suffix('.fbx')),'unaffected_object_fingerprints':baseline,'materials_before_after':materials,'changes':changes,'patch':patch})
 (P/'qa/wc_seat_ring_patch.json').write_text(json.dumps({'status':'pass' if len(reports)==7 else 'in_progress','classes':reports},indent=2));print('WC_PATCH_PASS',k,flush=True)
