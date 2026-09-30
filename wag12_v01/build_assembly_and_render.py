"""Build independent two-section review snapshot, measured formation, studio previews."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'assembly'

def bounds(obs):
 dg=bpy.context.evaluated_depsgraph_get();lo=[1e9]*3;hi=[-1e9]*3
 for o in obs:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh()
  for v in me.vertices:
   w=o.matrix_world@v.co
   for k in range(3):lo[k]=min(lo[k],w[k]);hi[k]=max(hi[k],w[k])
  ev.to_mesh_clear()
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]}

def create_assembly():
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.;sc.render.fps=24;sects=[]
 for sec,x,rz in [('A',9.6,0),('B',-9.6,math.pi)]:
  path=P/'sections'/('WAG12B_'+sec+'.blend')
  with bpy.data.libraries.load(str(path),link=False) as (a,b):b.collections=[n for n in a.collections if n=='WAG12B_SECTION_'+sec]
  c=b.collections[0];sc.collection.children.link(c);r=next(o for o in c.objects if o.name.startswith('WAG12B_'+sec+'_ROOT'));r.location=(x,0,0);r.rotation_euler.z=rz
  sects.append((sec,c,r))
 bpy.context.view_layer.update();joins=[]
 for sec,c,r in sects:
  ctrl=next(o for o in c.objects if o.name.startswith('PANTO_CTRL'));ctrl['extension']=0;ctrl.update_tag()
  rear=next(o for o in c.objects if o.name.startswith('COUPLING_REAR'));front=next(o for o in c.objects if o.name.startswith('COUPLING_FRONT'))
  joins.append({'section':sec,'root_translation_m':list(r.location),'root_rotation_z_rad':rz if sec=='B' else 0,'internal_anchor_m':list(rear.matrix_world.translation),'internal_outward_normal':list((rear.matrix_world.to_3x3()@Vector((1,0,0))).normalized()),'outer_anchor_m':list(front.matrix_world.translation)})
 bpy.context.view_layer.update();bb=bounds([o for sec,c,r in sects for o in c.objects]);(P/'assemblies'/'WAG12B_pair_manifest.json').write_text(json.dumps({'section_pitch_m':19.2,'outer_coupling_span_m':38.4,'sections':joins,'evaluated_lowered_bounds':bb,'coupling_z_m':1.105,'independent_local_section_roots':True,'single_cab_each_outer_end':True,'assembly_is_review_snapshot_not_single_conversion_asset':True},indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'assemblies'/'WAG12B_pair.blend'))

def box(n,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o

def mat(n,color,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def camera(loc,target,lens=50,ortho=0):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name='REVIEW_CAMERA';o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 bpy.context.scene.camera=o;return o

def light(n,loc,power,size,target):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def setup(mode):
 if mode in ('pair','side','coupling','independent'):
  bpy.ops.wm.open_mainfile(filepath=str(P/'assemblies'/'WAG12B_pair.blend'));length=42
 else:bpy.ops.wm.open_mainfile(filepath=str(P/'sections'/'WAG12B_A.blend'));length=23
 sc=bpy.context.scene;sc.world=sc.world or bpy.data.worlds.new('Studio_world');sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.resolution_x=1440;sc.render.resolution_y=810;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.world.color=(.20,.20,.20)
 world=sc.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.31,.39,.48,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
 ground=mat('Studio_ground',(.19,.215,.23),rough=.9);rail=mat('Studio_rail',(.32,.35,.38),.85,.28);sleeper=mat('Studio_sleepers',(.16,.18,.18),.1,.8)
 box('STUDIO_GROUND',(0,0,-.285),(200,200,.18),ground)
 for s in (-1,1):
  box('STUDIO_RAIL',(0,s*.869,-.046),(length,.062,.092),rail);box('STUDIO_RAIL_BASE',(0,s*.869,-.104),(length,.14,.030),rail)
 for i in range(int(length/.62)):
  x=-length/2+.3+i*.62;box('STUDIO_SLEEPER',(x,0,-.161),(.23,2.60,.090),sleeper)
 light('KEY',(8,-12,18),2900,10,(0,0,1.5));light('FILL',(-8,10,12),2200,12,(0,0,2));light('RIM',(-13,-3,8),1800,8,(0,0,2));light('FRONT',(20,3,9),1400,7,(8,0,2))
 if mode=='pair':
  # Exactly one raised panto in service illustration; each section stays independent.
  ctrls=[o for o in bpy.data.objects if o.name.startswith('PANTO_CTRL')];ctrls[1]['extension']=ctrls[1]['normal_wire_extension'];ctrls[1].update_tag();camera((39,-40,19),(.8,0,2.1),49)
 elif mode=='side':camera((0,-51,8),(0,0,2.5),50,42);sc.render.resolution_y=540
 elif mode=='exterior':camera((24,-24,11),(0,0,2.1),52)
 elif mode=='nose':camera((16,-10,6),(7,0,2.15),54)
 elif mode=='cab':
  camera((7.28,0,3.19),(8.58,-.10,2.60),20);light('CAB_FILL',(7.2,0,3.55),55,1.6,(8.35,0,2.1));sc.cycles.samples=48
 elif mode=='driver':
  camera((7.49,-.69,2.94),(15,-.69,2.94),22);light('CAB_FILL',(7.0,0,3.55),35,1.4,(8.35,0,2.1));sc.cycles.samples=32;sc.render.resolution_x=1280;sc.render.resolution_y=720
 elif mode=='bogie':camera((8,-5,2.4),(5.1,0,.9),48)
 elif mode=='coupling':camera((3,-5,3.4),(0,0,2.0),50)
 elif mode=='pantograph':
  c=next(o for o in bpy.data.objects if o.name=='PANTO_CTRL');c['extension']=1;c.update_tag();camera((-8,-9,7),(-5.1,0,5.6),45);sc.render.resolution_x=1000;sc.render.resolution_y=1200
 elif mode=='independent':
  ctrls=[o for o in bpy.data.objects if o.name.startswith('PANTO_CTRL')];ctrls[0]['extension']=1;ctrls[0].update_tag();ctrls[1]['extension']=0;ctrls[1].update_tag();camera((2,-25,8),(0,0,4),50,24)
 bpy.context.view_layer.update();sc.render.filepath=str(P/'renders'/(mode+'.png'));bpy.ops.render.render(write_still=True)

if MODE=='assembly':create_assembly()
else:setup(MODE)
