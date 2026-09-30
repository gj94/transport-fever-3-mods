"""Blender 4.3: blender -b -t 2 --python build_pantographs.py -- [source.blend] [output_dir]"""
import bpy,math,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector,Matrix
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
P=Path(args[1]) if len(args)>1 else Path(__file__).resolve().parent
SRC=Path(args[0]) if args else P.parent/'coupling_v03/wap7/WAP7_coupling_v03.blend'
P.mkdir(parents=True,exist_ok=True); bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
REMOVE=('Pantograph lower arm','Pantograph upper arm','Pantograph hinge','Contact shoe','Contact horn')
def snapshot(o):
 d={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[[x for x in row] for row in o.matrix_world],'data':o.data.name if o.data else None}
 if o.type=='MESH':
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('%di'%len(p.vertices),*p.vertices))
  d['geometry_sha256']=h.hexdigest();d['materials']=[m.name if m else None for m in o.data.materials]
 return d
protected={o.name:snapshot(o) for o in bpy.data.objects if not o.name.startswith(REMOVE)}
removed=[o.name for o in bpy.data.objects if o.name.startswith(REMOVE)]
for n in removed:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
body=bpy.data.objects['BODY']; root=bpy.data.objects['WAP7_ROOT']; mats={k:bpy.data.materials[n] for k,n in [('arm','Pantograph ochre'),('dark','Graphite underframe'),('steel','Machined wheel rims')]}
def empty(n,parent,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);sc.collection.objects.link(o);o.parent=parent;o.location=loc;o.empty_display_size=.12;o.empty_display_type='ARROWS';return o
def mesh(n,parent,verts,faces,mat):
 d=bpy.data.meshes.new(n+'_mesh');d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.parent=parent;d.materials.append(mats[mat]);return o
def rods(n,parent,segments,radius,mat='arm'):
 vs=[];fs=[]
 for a,b in segments:
  a,b=Vector(a),Vector(b);w=(b-a).normalized();u=w.cross(Vector((0,0,1)))
  if u.length<.1:u=w.cross(Vector((0,1,0)))
  u.normalize();v=w.cross(u);start=len(vs)
  for c in (a,b):
   for j in range(12):vs.append(tuple(c+radius*(u*math.cos(j*math.tau/12)+v*math.sin(j*math.tau/12))))
  fs += [tuple(start+j for j in range(11,-1,-1)),tuple(start+12+j for j in range(12))]
  for j in range(12):fs.append((start+j,start+(j+1)%12,start+12+(j+1)%12,start+12+j))
 return mesh(n,parent,vs,fs,mat)
def box(n,parent,c,d,mat='dark'):
 vs=[(c[0]+x*d[0]/2,c[1]+y*d[1]/2,c[2]+z*d[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(n,parent,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
rigs={};L1=1.4;L2=1.05;ZBASE=4.18;A0=math.radians(1);AR=math.radians(36);AMAX=math.radians(45)
for end,px in [('FRONT',5),('REAR',-5)]:
 pre='PANTO_'+end
 r=empty(pre+'_CTRL',body,(px-.75,0,ZBASE));r.matrix_parent_inverse=body.matrix_world.inverted();r['extension']=0.;r.id_properties_ui('extension').update(min=0,max=1,soft_min=0,soft_max=1,description='Independent extension: 0 folded, 1 illustrative raised (36 degrees). Editable; not a TF3 wire binding.')
 r['lower_angle_deg']=1.;r['raised_angle_deg']=36.;r['rail_z_m']=0.;r['contact_top_offset_m']=.032;r['lower_length_m']=L1;r['upper_length_m']=L2
 lo=empty(pre+'_LOWER_PIVOT',r);up=empty(pre+'_ELBOW_PIVOT',lo,(L1,0,0));he=empty(pre+'_HEAD_LEVEL_PIVOT',up,(-L2,0,0))
 # Total rotations: lower=-theta, upper=+theta, head=0. Upper local=-X points back toward the base.
 for o,expr in [(lo,'-a'),(up,'2*a'),(he,'-a')]:
  dr=o.driver_add('rotation_euler',1).driver;dr.type='SCRIPTED'
  v=dr.variables.new();v.name='e';v.targets[0].id=r;v.targets[0].data_path='["extension"]'
  dr.expression=expr.replace('a',f'({A0}+(max(0,min(1,e)))*{AR-A0})')
 rods(pre+'_LOWER_ARMS',lo,[((0,y,0),(L1,y,0)) for y in [-.40,.40]],.021)
 rods(pre+'_LOWER_CROSSBRACE',lo,[((.20,-.40,0),(.20,.40,0)),((.60,-.40,0),(.60,.40,0))],.011)
 rods(pre+'_UPPER_ARMS',up,[((0,y,0),(-L2,y,0)) for y in [-.32,.32]],.016)
 rods(pre+'_UPPER_CROSSBRACE',up,[((-.80,-.32,0),(-.80,.32,0))],.009)
 for y in [-.40,.40]:box(pre+('_BASE_BEARING_L' if y<0 else '_BASE_BEARING_R'),r,(0,y,-.025),(.085,.075,.055),'steel')
 rods(pre+'_BASE_HINGE_SHAFT',r,[((0,-.48,0),(0,.48,0))],.032,'steel')
 rods(pre+'_ELBOW_HINGE_SHAFT',up,[((0,-.45,0),(0,.45,0))],.03,'steel')
 rods(pre+'_HEAD_HINGE_SHAFT',he,[((0,-.37,0),(0,.37,0))],.016,'steel')
 rods(pre+'_HEAD_SUPPORTS',he,[((0,y,0),(-.065,y,.018)) for y in [-.32,.32]]+[((0,y,0),(.065,y,.018)) for y in [-.32,.32]],.008,'steel')
 for i,x in enumerate([-.065,.065]):box(pre+f'_CONTACT_STRIP_{i+1}',he,(x,0,.025),(.045,1.64,.014))
 rods(pre+'_CONTACT_HORNS',he,[((x,s*.82,.025),(x,s*.94,.005)) for x in [-.065,.065] for s in [-1,1]]+[((x,s*.94,.005),(x,s*1.03,-.035)) for x in [-.065,.065] for s in [-1,1]],.009,'dark')
 rigs[end]=(r,lo,up,he)
def pose(a,b):
 for e,x in [('FRONT',a),('REAR',b)]:rigs[e][0]['extension']=x;rigs[e][0].update_tag()
 bpy.context.view_layer.update()
def measure():
 out={}
 for e,(r,lo,up,he) in rigs.items():
  pts=[bpy.data.objects['PANTO_'+e+f'_CONTACT_STRIP_{i}'].matrix_world@v.co for i in [1,2] for v in bpy.data.objects['PANTO_'+e+f'_CONTACT_STRIP_{i}'].data.vertices]
  # Upper four vertices on each rectangular contact strip.
  top=[p.z for i in [1,2] for v in bpy.data.objects['PANTO_'+e+f'_CONTACT_STRIP_{i}'].data.vertices if v.co.z>.025 for p in [bpy.data.objects['PANTO_'+e+f'_CONTACT_STRIP_{i}'].matrix_world@v.co]]
  out[e]={'contact_top_min_m':min(top),'contact_top_max_m':max(top),'head_pivot_height_m':he.matrix_world.translation.z,'head_world_euler_deg':[math.degrees(x) for x in he.matrix_world.to_euler()], 'lower_length_world_m':(up.matrix_world.translation-lo.matrix_world.translation).length,'upper_length_world_m':(he.matrix_world.translation-up.matrix_world.translation).length,'elbow_closure_m':(lo.matrix_world@Vector((L1,0,0))-up.matrix_world.translation).length,'head_closure_m':(up.matrix_world@Vector((-L2,0,0))-he.matrix_world.translation).length}
 return out
qa={'source_file':SRC.name,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'verified_remote_head':'f398592b3908ef205843d1e9b2211cb0189973f4','removed_moving_objects':removed,'rail_z_m':0.,'poses':{}}
for a,b in [(0,0),(.25,.75),(.5,.5),(.75,.25),(1,1),(1,0),(0,1)]:
 pose(a,b);qa['poses'][f'{a}_{b}']=measure()
 for m in qa['poses'][f'{a}_{b}'].values():
  assert abs(m['lower_length_world_m']-L1)<1e-5 and abs(m['upper_length_world_m']-L2)<1e-5
  assert max(abs(x) for x in m['head_world_euler_deg'])<.0001
pose(0,0)
after={n:snapshot(bpy.data.objects[n]) for n in protected};assert protected==after,'Non-pantograph data changed'
qa['preservation']={'protected_objects':len(protected),'exact_equality':True,'root_and_coupling_anchors':{n:protected[n] for n in ['WAP7_ROOT','COUPLING_FRONT','COUPLING_REAR']},'unit_system':sc.unit_settings.system,'unit_scale_length':sc.unit_settings.scale_length}
(P/'protected_source_manifest.json').write_text(json.dumps(protected,indent=2));(P/'rig_validation.json').write_text(json.dumps(qa,indent=2))
sc.frame_start=1;sc.frame_end=161;sc.frame_set(1)
for m in list(sc.timeline_markers):sc.timeline_markers.remove(m)
for n,f in [('BOTH_LOWERED',1),('FRONT_RAISED_REAR_LOWERED',41),('BOTH_RAISED_SAMPLE',81),('FRONT_LOWERED_REAR_RAISED',121),('BOTH_LOWERED_END',161)]:sc.timeline_markers.new(n,frame=f)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'WAP7_pantograph_v04.blend'),compress=True)
def export(name,anim=False):
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.fbx(filepath=str(P/name),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_space_transform=False,add_leaf_bones=False,bake_anim=anim,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,path_mode='AUTO')
export('WAP7_pantograph_v04_lowered.fbx')
pose(1,1);export('WAP7_pantograph_v04_raised_sample.fbx');pose(0,0)
# Drivers are not FBX-portable. Bake rigid local Euler rotation tracks on a separate export representation.
for r,lo,up,he in rigs.values():
 for o in [lo,up,he]:o.driver_remove('rotation_euler',1)
for f in range(1,162):
 front=min(1,max(0,(f-1)/40)) if f<=81 else max(0,1-(f-81)/40)
 rear=max(0,min(1,(f-41)/40)) if f<=121 else max(0,1-(f-121)/40)
 for end,e in [('FRONT',front),('REAR',rear)]:
  r,lo,up,he=rigs[end];a=A0+(AR-A0)*e
  for o,v in [(lo,-a),(up,2*a),(he,-a)]:o.rotation_euler.y=v;o.keyframe_insert(data_path='rotation_euler',frame=f,group=end+'_PANTOGRAPH')
for end,rig in rigs.items():
 for o in rig[1:]:o.animation_data.action.name=o.name+'_INDEPENDENT_MOTION_SAMPLES'
sc.name='WAP7_INDEPENDENT_PANTOGRAPH_SAMPLES';sc.frame_set(1);bpy.context.view_layer.update()
export('WAP7_pantograph_v04_motion_samples.fbx',True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'WAP7_pantograph_v04_baked_samples.blend'),compress=True)
print('BUILD_COMPLETE',json.dumps(qa['poses']))
