import bpy,json,math,sys
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
expected=json.loads((P/'rig_validation.json').read_text());protected=json.loads((P/'protected_source_manifest.json').read_text());out={}
for filename,frames in [('WAP7_pantograph_v04_lowered.fbx',[(1,'0_0')]),('WAP7_pantograph_v04_raised_sample.fbx',[(1,'1_1')]),('WAP7_pantograph_v04_motion_samples.fbx',[(1,'0_0'),(41,'1_0'),(81,'1_1'),(121,'0_1'),(161,'0_0')])]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/filename),anim_offset=0);sc=bpy.context.scene
 report={'poses':{},'protected_max_matrix_error_m':0.,'protected_parent_match':True}
 for f,key in frames:
  sc.frame_set(f);bpy.context.view_layer.update();pose={}
  for end in ['FRONT','REAR']:
   head=bpy.data.objects['PANTO_'+end+'_HEAD_LEVEL_PIVOT'];z=[]
   for i in [1,2]:
    o=bpy.data.objects['PANTO_'+end+f'_CONTACT_STRIP_{i}'];zs=[(o.matrix_world@v.co).z for v in o.data.vertices];z+=sorted(zs)[4:]
   err=abs(max(z)-expected['poses'][key][end]['contact_top_max_m']);assert err<2e-5,(filename,f,end,err,max(z))
   tilt=max(abs(math.degrees(x)) for x in head.matrix_world.to_euler());assert tilt<.001,(f,tilt)
   pose[end]={'contact_top_m':max(z),'height_error_m':err,'max_head_tilt_deg':tilt,'parent':head.parent.name}
  for n,d in protected.items():
   if n not in bpy.data.objects:continue
   o=bpy.data.objects[n];err=max(abs(o.matrix_world[i][j]-d['matrix'][i][j]) for i in range(4) for j in range(4));report['protected_max_matrix_error_m']=max(err,report['protected_max_matrix_error_m']);assert err<2e-5,(n,err)
   assert (o.parent.name if o.parent else None)==d['parent'],n
  report['poses'][str(f)]=pose
 report['mesh_count']=sum(o.type=='MESH' for o in bpy.data.objects);report['imported_action_names']=[a.name for a in bpy.data.actions];out[filename]=report
(P/'fbx_validation.json').write_text(json.dumps(out,indent=2))
# Render solely in temporary scene state, without altering delivered asset.
bpy.ops.wm.open_mainfile(filepath=str(P/'WAP7_pantograph_v04.blend'));sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=850;sc.render.resolution_y=470;sc.render.resolution_percentage=100
sc.world.color=(.30,.30,.30);sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
for o in list(bpy.data.objects):
 if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
for loc,pow,size in [((4,-5,10),1800,6),((6,4,8),1300,5),((-6,-2,10),2000,7)]:
 d=bpy.data.lights.new('QA_LIGHT','AREA');d.energy=pow;d.shape='DISK';d.size=size;o=bpy.data.objects.new('QA_LIGHT',d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('QA_CAMERA');cam=bpy.data.objects.new('QA_CAMERA',d);sc.collection.objects.link(cam);sc.camera=cam;d.type='ORTHO'
for name,a,b,loc,target,scale in [('detail_lowered',0,0,(7.6,-7.2,6.2),(4.95,0,4.25),4.8),('detail_raised',1,0,(7.6,-7.2,6.2),(4.95,0,4.85),4.8),('independent_mixed',1,0,(14,-24,14),(0,0,2.7),23.8)]:
 for end,e in [('FRONT',a),('REAR',b)]:r=bpy.data.objects['PANTO_'+end+'_CTRL'];r['extension']=e;r.update_tag()
 bpy.context.view_layer.update();cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;sc.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
print('FBX_QA_AND_RENDER_COMPLETE')
