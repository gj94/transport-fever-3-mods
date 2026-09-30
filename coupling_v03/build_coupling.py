"""Blender 4.3: blender -b -t 2 --python build_coupling.py [-- source_v02_directory]."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
SRC=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else P.parent/'interiors_v02'

def bounds(o):
 b=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)]
def stamp(o):
 d={'parent':o.parent.name if o.parent else None,'matrix_world':[list(r) for r in o.matrix_world],'type':o.type}
 if o.type=='MESH':d['geometry_sha256']=hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
 return d

def build(kind,filename,rootname,plane,beam):
 bpy.ops.wm.open_mainfile(filepath=str(SRC/kind/filename))
 scene=bpy.context.scene;root=bpy.data.objects[rootname];body=bpy.data.objects['BODY'];bpy.context.view_layer.update()
 original={o.name:stamp(o) for o in root.children_recursive+[root]}
 sourcebounds={o.name:bounds(o) for o in root.children_recursive if o.type=='MESH' and (o.name.startswith(('CBC','Draw hook','Screw coupling','Buffer')))}
 coll=bpy.data.collections.new('COUPLING_V03');scene.collection.children.link(coll)
 steel=bpy.data.materials.new('CBC cast steel v03');steel.diffuse_color=(.16,.19,.21,1);steel.use_nodes=True
 bs=steel.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.16,.19,.21,1);bs.inputs['Metallic'].default_value=.72;bs.inputs['Roughness'].default_value=.35
 def finish(o,name,parent,mat=steel):
  o.name=name
  for c in list(o.users_collection):c.objects.unlink(o)
  coll.objects.link(o);o.parent=parent
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(mat)
   be=o.modifiers.new('Small cast edge radius','BEVEL');be.width=.007;be.segments=2
   o.modifiers.new('Weighted cast normals','WEIGHTED_NORMAL')
  return o
 def cube(n,loc,dim,parent):
  bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.location=loc;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,parent)
 def cyl(n,loc,r,depth,parent):
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth);o=bpy.context.object;o.location=loc;return finish(o,n,parent)
 removed=[];modified=[]
 for o in list(root.children_recursive):
  if o.name.startswith(('CBC','Draw hook','Screw coupling')):
   removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
  elif o.name.startswith(('Buffer plate','Buffer head','Buffer housing','Buffer shank')):
   modified.append(o.name);mw=o.matrix_world.copy();pos=mw.translation.copy();pos.y=math.copysign(.978,pos.y);pos.z=1.105;mw.translation=pos;o.matrix_world=mw
   if kind=='icf' and o.name.startswith('Buffer shank'):
    # Original rod terminated before its plate. Extend rod into plate without moving buffer face.
    mw=o.matrix_world.copy();pos=mw.translation.copy();mw=Matrix.Translation(pos)@Matrix.Diagonal((1.25,1,1,1))@Matrix.Translation(-pos)@mw;pos.x=math.copysign(10.81,pos.x);mw.translation=pos;o.matrix_world=mw
 for s,label in [(1,'FRONT'),(-1,'REAR')]:
  a=bpy.data.objects.new('COUPLING_'+label,None);coll.objects.link(a);a.parent=root;a.location=(s*plane,0,1.105);a.rotation_euler.z=0 if s==1 else math.pi;a.empty_display_type='ARROWS';a.empty_display_size=.35
  a['datum']='Artistic paired CBC reference plane; not outermost head tip';a['outward_axis']='+X local';a['up_axis']='+Z local';a['rail_datum_z_m']=0.0
  pivot=bpy.data.objects.new('CBC_'+label+'_PIVOT',None);coll.objects.link(pivot);pivot.parent=root;pivot.location=(s*(beam-.10),0,1.105);pivot.rotation_euler.z=0 if s==1 else math.pi
  # Geometry is authored in outward-facing pivot coordinates, +X toward connection.
  reach=plane-(beam-.10)
  cube('CBC_'+label+'_draft_pocket',(.02,0,0),(.26,.34,.30),pivot)
  cube('CBC_'+label+'_shank',((reach-.22)/2,0,0),(reach-.16,.17,.17),pivot)
  cyl('CBC_'+label+'_draft_pin',(.03,0,0),.055,.33,pivot)
  # Closed knuckle outline. Opposing head rotated 180deg shares a stepped mating
  # boundary x=f(y), f(-y)=-f(y), allowing noses to interleave across the datum.
  poly=[(-.30,-.10),(-.23,-.18),(-.08,-.18),(-.08,-.045),(.08,.045),(.08,.18),(-.15,.18),(-.30,.10)]
  vs=[(reach+x,y,z) for z in [-.115,.115] for x,y in poly];n=len(poly)
  fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  me=bpy.data.meshes.new('Interlocking head casting');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('CBC_'+label+'_closed_knuckle_head',me);coll.objects.link(o);finish(o,o.name,pivot)
  cyl('CBC_'+label+'_knuckle_pin',(reach-.15,.105,0),.028,.255,pivot)
  cube('CBC_'+label+'_lock_lifter',(reach-.18,-.085,.14),(.07,.035,.055),pivot)
  cube('CBC_'+label+'_support_saddle',(reach-.39,0,-.16),(.20,.29,.075),pivot)
 bpy.context.view_layer.update()
 changed=[]
 for n,v in original.items():
  if n not in removed+modified and stamp(bpy.data.objects[n])!=v:changed.append(n)
 assert not changed,changed
 root['coupling_version']='v03 paired CBC visual arrangement';root['length_between_coupling_points_m']=2*plane;root['coupling_height_m']=1.105
 root['original_v02_length_metadata_note']='Original length fields retained for provenance; use length_between_coupling_points_m for v03 anchor span'
 scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 asset=list(root.children_recursive)+[root]
 report={'kind':kind,'root':rootname,'source':str(Path(kind)/filename),'source_original_coupling_bounds':sourcebounds,'removed_coupling_objects':removed,'modified_buffers':modified,'preserved_objects_count':len(original)-len(removed)-len(modified),'unexpected_changes':changed,'unit_scale_length':1.0,'root_world_matrix':[list(r) for r in root.matrix_world], 'rail_datum_z_m':0.0,'rail_datum_basis':'Original source wheel tread reference; flanges extend below z=0','coupling_height_m':1.105,'nominal_reference_heights_m':{'locomotive':1.090,'coach':1.105},'artistic_height_choice':'Common 1.105 m; loco raised 15 mm relative to reference nominal for coincident static anchors','anchor_span_m':2*plane,'anchors':{},'head_bounds':{},'buffer_bounds':{},'protected_rig':{},'interior_object_names':[o.name for o in asset if any(c.name in ['CAB_INTERIORS_V02','ICF_INTERIOR_V02'] for c in o.users_collection)]}
 for o in asset:
  if o.name.startswith('COUPLING_'):report['anchors'][o.name]={'world_location_m':list(o.matrix_world.translation),'world_matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name}
  if o.name.endswith('closed_knuckle_head'):report['head_bounds'][o.name]=bounds(o)
  if o.name.startswith(('Buffer plate','Buffer head','Buffer housing','Buffer shank','Buffer beam')):report['buffer_bounds'][o.name]=bounds(o)
  if o.name.startswith(('BOGIE','AXLE')) or o==root:report['protected_rig'][o.name]=stamp(o)
 report['bounds_non_coupling_structure']={o.name:bounds(o) for o in asset if o.type=='MESH' and o.name.startswith(('Chamfered welded body shell','Coach end wall','Lower blue bodyside','Vestibule bellows','Gangway'))}
 out=P/kind;out.mkdir(exist_ok=True)
 name='WAP7_coupling_v03' if kind=='wap7' else 'ICF_sleeper_CBC_retrofit_v03'
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:
   try:im.pack()
   except:pass
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.object.select_all(action='DESELECT')
 for o in asset:o.hide_set(False);o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH','EMPTY','OTHER'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,path_mode='COPY',embed_textures=True,use_custom_props=True)
 (out/'geometry_validation.json').write_text(json.dumps(report,indent=2))
 print('BUILT',name,len(asset))
for args in [('wap7','WAP7_interiors_v02.blend','WAP7_ROOT',10.20,9.60),('icf','icf_sleeper_interior_v02.blend','ICF_ROOT_metres_X_forward',11.1485,10.48)]:build(*args)
