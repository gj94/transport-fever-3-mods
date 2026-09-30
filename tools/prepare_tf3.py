"""Create consolidated, textured TF3 FBX inputs without changing source masters."""
import bpy, math, json, re, sys
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from native_tf3 import native_export
from model_sources import selected_models,asset_objects
from vande_bharat import sample_tracks,write_formations
from native_tf3 import write_lua
from pantograph_rig import configure_tf3_pantographs,MIN_HEIGHT,MAX_HEIGHT
from freight_locomotives import SPECS as FREIGHT_SPECS, sample_tracks as freight_tracks, write_formation
OUT=ROOT/'game_build'/'imports'
def clean(s): return re.sub(r'[^a-z0-9_]','_',s.lower())
reports=[]
for key,source in selected_models(sys.argv):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/source))
 root,objects=asset_objects(bpy)
 # Sample the author's live rig at evenly spaced contact heights. TF3's
 # animation frame is a height fraction, whereas Blender extension is an angle.
 pantograph_tracks={}
 if key=='wap7':
  configure_tf3_pantographs(bpy)
  for end in ('FRONT','REAR'):
   ctrl=bpy.data.objects['PANTO_'+end+'_CTRL']
   pivots=[bpy.data.objects['PANTO_'+end+'_'+part] for part in ('LOWER_PIVOT','ELBOW_PIVOT','HEAD_LEVEL_PIVOT')]
   rest={o:o.matrix_local.copy() for o in pivots}
   tracks={o:[] for o in pivots}
   for i in range(101):
    height=MIN_HEIGHT+(MAX_HEIGHT-MIN_HEIGHT)*i/100
    ctrl['extension']=max(0,min(1,(math.degrees(math.asin((height-4.212)/2.45))-1)/44))
    ctrl.update_tag();bpy.context.view_layer.update()
    for o in pivots:
     delta=rest[o].inverted()@o.matrix_local
     tracks[o].append([float(delta[r][c]) for c in range(4) for r in range(4)])
   ctrl['extension']=0.;ctrl.update_tag();bpy.context.view_layer.update()
   pantograph_tracks.update({clean(o.name):{'state':'pantograph_'+end.lower(),'times':list(range(0,1001,10)),'transfs':values} for o,values in tracks.items()})
 if key.startswith('vb_'):pantograph_tracks=sample_tracks(bpy,objects,clean)
 if key in FREIGHT_SPECS:pantograph_tracks=freight_tracks(bpy,key,clean)
 markers=[o for o in objects if o.type=='EMPTY' and o.name.startswith(('PAX_','PASSENGER_SEATED_','DRIVER_'))]
 empties=[o for o in objects if o.type=='EMPTY' and not o.name.startswith(('PAX_','PASSENGER_SEATED_','BERTH_','DRIVER_','CAB_EYE_CAMERA_REFERENCE'))]
 mats=[]
 for o in objects:
  if o.type in {'MESH','FONT','CURVE'}:
   for m in o.data.materials:
    if m and m not in mats: mats.append(m)
 assert len(mats)<=64
 material_indices={m.name:i for i,m in enumerate(mats)}
 target=OUT/('vehicle-train+'+key);target.mkdir(parents=True,exist_ok=True)
 image=bpy.data.images.new(key+'_alb',width=128,height=128);pixels=[0.0]*(128*128*4)
 for y in range(128):
  for x in range(128):
   idx=(y//16)*8+x//16;color=tuple(mats[idx].diffuse_color) if idx<len(mats) else (.25,.25,.25,1)
   p=4*(y*128+x);pixels[p:p+4]=list(color[:3])+[1.0]
 image.pixels.foreach_set(pixels);image.filepath_raw=str(target/(key+'_alb.png'));image.file_format='PNG';image.save()
 palette=bpy.data.materials.new(key+'_palette');palette.use_nodes=True
 tex=palette.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
 palette.node_tree.links.new(tex.outputs['Color'],palette.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 palette.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.5
 def bucket(m):
  if not m:return 'palette'
  p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  if p and p.inputs.get('Transmission Weight') and p.inputs['Transmission Weight'].default_value>.5:return 'glass'
  if m.use_nodes and any(n.type=='TEX_IMAGE' and n.image for n in m.node_tree.nodes):return clean(m.name)
  return 'palette'
 dep=bpy.context.evaluated_depsgraph_get();groups={}
 for o in objects:
  if o.type not in {'MESH','FONT','CURVE'}:continue
  parent=o.parent
  while parent and parent not in empties:parent=parent.parent
  for kind in set(bucket(s.material) for s in o.material_slots) or {'palette'}:
   groups.setdefault((parent or root,kind),[]).append(o)
 newcoll=bpy.data.collections.new('TF3_EXPORT');bpy.context.scene.collection.children.link(newcoll);newempties={}
 for e in empties:
  n=bpy.data.objects.new(clean(e.name),None);newcoll.objects.link(n);newempties[e]=n;n.matrix_world=e.matrix_world.copy()
 for e,n in newempties.items():
  if e.parent in newempties:
   world=n.matrix_world.copy();n.parent=newempties[e.parent];n.matrix_world=world
 merged=[]
 for (parent,kind),members in groups.items():
  verts=[];faces=[];uvcoords=[];smooth=[]
  for o in members:
   ev=o.evaluated_get(dep);mesh=ev.to_mesh()
   if mesh is None:continue
   transform=parent.matrix_world.inverted()@o.matrix_world;base=len(verts)
   verts.extend(tuple(transform@v.co) for v in mesh.vertices)
   for poly in mesh.polygons:
    m=mesh.materials[poly.material_index] if len(mesh.materials)>poly.material_index else None
    if bucket(m)!=kind:continue
    faces.append(tuple(base+i for i in poly.vertices))
    # Evaluated materials are separate Blender ID wrappers; match stable names.
    idx=material_indices.get(m.name,0) if m else 0;cx=(idx%8+.5)/8;cy=(idx//8+.5)/8
    coords=[tuple(mesh.uv_layers.active.data[li].uv) for li in poly.loop_indices] if kind not in {'palette','glass'} and mesh.uv_layers.active else [(cx+.035*math.cos(2*math.pi*j/len(poly.vertices)),cy+.035*math.sin(2*math.pi*j/len(poly.vertices))) for j in range(len(poly.vertices))]
    uvcoords.append(coords);smooth.append(poly.use_smooth)
   ev.to_mesh_clear()
  me=bpy.data.meshes.new(key+'_'+clean(parent.name)+'_mesh');me.from_pydata(verts,[],faces);me.update();me.materials.append(palette);uv=me.uv_layers.new(name='UVMap')
  for poly,coords,sm in zip(me.polygons,uvcoords,smooth):
   poly.use_smooth=sm
   for loop,xy in zip(poly.loop_indices,coords):uv.data[loop].uv=xy
  ob=bpy.data.objects.new(clean(parent.name)+'_'+kind+'_visual',me);ob['tf3_material']=kind;newcoll.objects.link(ob);ob.parent=newempties[parent];ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4);merged.append(ob)
 seats=[]
 for mark in sorted(markers,key=lambda o:o.name):
  matrix=mark.matrix_local.copy()
  if key=='icf_sleeper':
   number=int(mark.name.rsplit('_',1)[1]);slot=(number-1)%8
   if slot in (3,4,5,7):matrix=matrix@Matrix.Rotation(math.pi,4,'Z')
  seat={'animation':'driving_upright' if mark.name.startswith('DRIVER_') else 'sitting','group':clean(mark.parent.name),'transf':[float(matrix[r][c]) for c in range(4) for r in range(4)]}
  if mark.name.startswith('DRIVER_'):seat.update(crew=True,forward=not (key=='wag9' and mark.parent.name=='CAB_B'))
  seats.append(seat)
 if key=='wap7':
  for cab in ('CAB_A_INTERIOR','CAB_B_INTERIOR'):
   # The driving_upright character has a ~0.483 m posed hip offset.
   # Cushion top is 2.215 m; 1.80 m root height seats the body on it.
   matrix=Matrix.Translation((8.03,.78,1.80))
   seats.append({'animation':'driving_upright','crew':True,'forward':cab=='CAB_A_INTERIOR','group':clean(cab),'transf':[float(matrix[r][c]) for c in range(4) for r in range(4)]})
 bpy.ops.object.select_all(action='DESELECT')
 for ob in newcoll.objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=merged[0];counts=[]
 for lod,ratio in enumerate((1.0,.24,.055)):
  modifiers=[]
  if lod:
   for ob in merged:
    if len(ob.data.polygons)<100:continue
    mod=ob.modifiers.new('TF3_LOD','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True;modifiers.append((ob,mod))
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  counts.append(sum(sum(len(p.vertices)-2 for p in ob.evaluated_get(dg).data.polygons) for ob in merged))
  bpy.ops.export_scene.fbx(filepath=str(target/(key+f'_lod{lod}.fbx')),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='X',axis_up='Z',apply_unit_scale=True,use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=False)
  for ob,mod in modifiers:ob.modifiers.remove(mod)
 reports.append({'model':key,'mesh_groups':len(merged),'lod_triangles':counts,'palette_materials':len(mats),'pivots':{n.name:list(n.matrix_world.translation) for n in newempties.values()}})
 print('TF3_PREPARED',json.dumps(reports[-1]))
 native_export(ROOT,key,newcoll,merged,mats,image,seats,pantograph_tracks)
OUT.parent.mkdir(parents=True,exist_ok=True)
report_path=OUT.parent/'preparation_report.json'
old=json.loads(report_path.read_text()) if report_path.exists() else []
report_path.write_text(json.dumps([r for r in old if r['model'] not in {n['model'] for n in reports}]+reports,indent=2))
write_formations(ROOT,write_lua)
write_formation(ROOT,write_lua)
