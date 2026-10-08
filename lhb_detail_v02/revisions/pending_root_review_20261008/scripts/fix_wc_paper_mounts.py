"""Localized post-build repair: mount WC paper holders on actual corridor-wall faces.
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
  if o.name.startswith(('WC_paper_holder','WC_tissue_roll')):continue
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
 source=P/'models'/f'LHB_{k}.blend';oldsha=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);bpy.context.view_layer.update();baseline=fingerprint();materials=mats();changes=[]
 holders=[o for o in bpy.data.objects if o.name.startswith('WC_paper_holder')];assert len(holders)==(3 if k=='1A' else 4)
 for holder in holders:
  points=boxcoords(holder);center=sum(points,Vector())/8;sign=1 if center.y>0 else -1
  walls=[o for o in bpy.data.objects if o.name.startswith('WC_corridor_wall') and o.location.x*center.x>0 and o.location.y*center.y>0];assert len(walls)==1
  wall=walls[0];face=max(p.y*sign for p in boxcoords(wall));rear=min(p.y*sign for p in points);delta=(face-rear)*sign
  rolls=[o for o in bpy.data.objects if o.name.startswith('WC_tissue_roll') and (sum(boxcoords(o),Vector())/8-center).length<.15];assert len(rolls)==1
  roll=rolls[0];before=[list(holder.location),list(roll.location)];holder.location.y+=delta;roll.location.y+=delta;bpy.context.view_layer.update()
  roll_rear=min(p.y*sign for p in boxcoords(roll));extra=max(0,face+.001-roll_rear);roll.location.y+=extra*sign;bpy.context.view_layer.update()
  contact=min(p.y*sign for p in boxcoords(holder));assert abs(contact-face)<2e-6
  assert min(p.y*sign for p in boxcoords(roll))>=face-2e-6
  changes.append({'holder':holder.name,'roll':roll.name,'wall':wall.name,'wall_inner_face_abs_y':face,'holder_rear_face_abs_y':contact,'locations_before':before,'locations_after':[list(holder.location),list(roll.location)],'holder_delta_y':delta,'roll_extra_wall_clearance_shift':extra*sign})
 assert fingerprint()==baseline and mats()==materials
 root=bpy.data.objects[f'LHB_{k}_ROOT_metres'];patch={'script':'scripts/fix_wc_paper_mounts.py','sha256':sha(Path(__file__)),'scope':'Only paper-holder and matching tissue-roll Y translations to actual corridor-wall inner face; all other evaluated geometry, hierarchy, custom properties and material node values/links unchanged'};root['wc_paper_mount_patch']=json.dumps(patch,sort_keys=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 glass=bpy.data.materials['GLASS_source_transmission_FBX_alpha'];bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=0;bs.inputs['Alpha'].default_value=.22;glass.diffuse_color=(*glass.diffuse_color[:3],.22)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.fbx(filepath=str(source.with_suffix('.fbx')),use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
 for suffix in ['manifest','markers']:
  p=P/'models'/f'LHB_{k}_{suffix}.json';d=json.loads(p.read_text());d['wc_paper_mount_patch']=patch;p.write_text(json.dumps(d,indent=2))
 reports.append({'variant':k,'status':'pass','source_sha256_before':oldsha,'source_sha256_after':sha(source),'fbx_sha256_after':sha(source.with_suffix('.fbx')),'unaffected_object_fingerprints':baseline,'materials_before_after':materials,'changes':changes,'patch':patch})
 (P/'qa/wc_paper_mount_patch.json').write_text(json.dumps({'status':'pass' if len(reports)==7 else 'in_progress','classes':reports},indent=2));print('WC_MOUNT_PASS',k,flush=True)
