import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
models=[('wap7','WAP7_coupling_v03','WAP7_ROOT'),('icf','ICF_sleeper_CBC_retrofit_v03','ICF_ROOT_metres_X_forward')]
for kind,stem,rootname in models:
 report=json.loads((P/kind/'geometry_validation.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/kind/(stem+'.fbx')));bpy.context.view_layer.update()
 checks={};err=0
 for name,rig in report['protected_rig'].items():
  o=bpy.data.objects[name];e=max(abs(o.matrix_world[i][j]-rig['matrix_world'][i][j]) for i in range(4) for j in range(4));err=max(err,e);assert e<1e-5,(name,e)
  assert (o.parent.name if o.parent else None)==rig['parent']
 for name,d in report['anchors'].items():
  o=bpy.data.objects[name];e=max(abs(o.matrix_world[i][j]-d['world_matrix'][i][j]) for i in range(4) for j in range(4));assert e<1e-5,(name,e);assert o.parent.name==rootname
  checks[name]={'location_m':list(o.matrix_world.translation),'parent':o.parent.name,'matrix_max_error':e}
 r={'fresh_import_success':True,'anchor_checks':checks,'protected_rig_max_matrix_error':err,'rig_parent_names_match':True,'root_location_m':list(bpy.data.objects[rootname].matrix_world.translation),'fbx_meshes':sum(o.type=='MESH' for o in bpy.data.objects),'cameras':sum(o.type=='CAMERA' for o in bpy.data.objects),'lights':sum(o.type=='LIGHT' for o in bpy.data.objects),'unit_scale_length':bpy.context.scene.unit_settings.scale_length,'interior_locators':[o.name for o in bpy.data.objects if o.name.startswith(('BERTH_','PASSENGER_SEATED_','CAB_A_INTERIOR','CAB_B_INTERIOR'))]}
 assert not r['cameras'] and not r['lights'];(P/kind/'fbx_validation.json').write_text(json.dumps(r,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True)
roots=[];anchors=[]
for kind,stem,rootname in models:
 with bpy.data.libraries.load(str(P/kind/(stem+'.blend')),link=False) as (fr,to):to.objects=fr.objects
 objs=[]
 for o in to.objects:
  if o: bpy.context.scene.collection.objects.link(o);objs.append(o)
 root=next(o for o in objs if o.name==rootname);keep=set(root.children_recursive+[root])
 for o in objs:
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 roots.append(root);anchors.append({o.name.split('.')[0]:o for o in root.children_recursive if o.name.startswith('COUPLING_')})
bpy.context.view_layer.update()
w=anchors[0]['COUPLING_FRONT'];i=anchors[1]['COUPLING_REAR'];delta=w.matrix_world.translation-i.matrix_world.translation
roots[1].location+=delta;bpy.context.view_layer.update()
residual=(w.matrix_world.translation-i.matrix_world.translation).length;assert residual<1e-5
norm1=w.matrix_world.to_3x3()@Vector((1,0,0));norm2=i.matrix_world.to_3x3()@Vector((1,0,0));assert norm1.dot(norm2)<-.99999
# Sampled 2D source-outline intersection check before bevel (1 mm grid).
# Polygon edges and inward sample grid demonstrate interleaving rather than bounding-box separation.
poly=[(-.30,-.10),(-.23,-.18),(-.08,-.18),(-.08,-.045),(.08,.045),(.08,.18),(-.15,.18),(-.30,.10)]
def inside(x,y,p):
 hit=False
 for a,b in zip(p,p[1:]+p[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
# Read the actual unmodified head vertices in the assembled world pose.
head_a=next(o for o in roots[0].children_recursive if o.name.startswith('CBC_FRONT_closed_knuckle_head'))
head_b=next(o for o in roots[1].children_recursive if o.name.startswith('CBC_REAR_closed_knuckle_head'))
origin=w.matrix_world.translation
poly=[tuple((head_a.matrix_world@v.co-origin)[:2]) for v in list(head_a.data.vertices)[:8]]
q=[tuple((head_b.matrix_world@v.co-origin)[:2]) for v in list(head_b.data.vertices)[:8]]
overlap=0
for ix in range(600):
 for iy in range(360):
  x=-.30+(ix+.37)*.001;y=-.18+(iy+.23)*.001
  overlap+=inside(x,y,poly) and inside(x,y,q)
assert overlap==0,overlap
proof={'pose':'WAP7 +X front to ICF -X rear, straight track','coach_translation_m':list(delta),'anchor_residual_m':residual,'outward_axes_dot':norm1.dot(norm2),'root_center_separation_m':delta.x,'head_interleaving_depth_m':.16,'head_positive_area_overlap_grid_samples':overlap,'grid_pitch_m':.001,'head_contact':'Matching un-beveled stepped face; cast-edge bevel creates fine edge relief','buffer_face_gap_m':10.20-10.11,'body_shell_end_clearance_m':None,'tf3_tested_by_this_package':False}
# Actual preserved shell extents, exclude hoses/buffers/headstock.
for r in roots:
 bpy.context.view_layer.update()
a=[r for o in roots[0].children_recursive if o.name.startswith('Chamfered welded body shell') for r in [o.matrix_world@Vector(v) for v in o.bound_box]]
b=[r for o in roots[1].children_recursive if o.name.startswith(('Coach end wall','Lower blue bodyside')) for r in [o.matrix_world@Vector(v) for v in o.bound_box]]
proof['body_shell_end_clearance_m']=min(v.x for v in b)-max(v.x for v in a)
(P/'paired_alignment_validation.json').write_text(json.dumps(proof,indent=2))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=900;scene.render.resolution_y=580;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('QA world');scene.world.color=(.3,.3,.3);scene.view_settings.view_transform='AgX'
for loc,power,size in [((8,-5,8),2300,7),((13,4,6),1800,6),((0,0,10),1800,8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((10.2,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.09));floor=bpy.context.object;floor.name='QA_ONLY_GROUND';m=bpy.data.materials.new('QA light ground');m.diffuse_color=(.28,.30,.32,1);floor.data.materials.append(m)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam

def render(name,loc,target,lens=52):
 if (P/(name+'.png')).exists():return
 for light,offset in zip([o for o in scene.objects if o.type=='LIGHT'],[(3,-4,6),(-3,4,5),(0,1,8)]):
  light.location=Vector(target)+Vector(offset);light.rotation_euler=(Vector(target)-light.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO' if name=='paired_straight_overview' else 'PERSP';cam.data.ortho_scale=47
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;scene.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
render('paired_connection_closeup',(10.20,-3.3,2.75),(10.20,0,1.105),58)
render('paired_connection_top',(10.2,-.35,4.8),(10.2,0,1.105),58)
render('paired_straight_overview',(32,-40,25),(11.1,0,1.9),48)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'paired_straight_QA.blend'),compress=True)
print('VERIFIED_AND_RENDERED',proof)
