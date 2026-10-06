"""Render geometry-grounded review images. Example: blender -b -t 8 --python scripts/render_previews.py -- hero 64 1280
Views: hero, side, cab, bogie, roof, front, all. Run finish_package.py afterward to strip PNG machine-path metadata losslessly.
"""
import bpy,sys,math,time,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
view=a[0] if a else 'all';samples=int(a[1]) if len(a)>1 else 256;width=int(a[2]) if len(a)>2 else 1920
master_sha=hashlib.sha256((OUT/'WAP7_photoreal_v01.blend').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(OUT/'WAP7_photoreal_v01.blend'))
exec(compile((OUT/'scripts/restore_stage.py').read_text(),'restore_stage.py','exec'),globals())
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=9;s.cycles.samples=samples;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.005;s.render.resolution_x=width;s.render.resolution_y=round(width*(.5625 if view=='hero' else .625));s.render.resolution_percentage=100
# The trailing collector meets this presentation contact plane. Head-level rig is unchanged.
bpy.data.objects['PANTO_REAR_CTRL']['extension']=(math.degrees(math.asin((5.53-4.212)/2.45))-1)/35
bpy.data.objects['PANTO_FRONT_CTRL']['extension']=0.0
for name in ['PANTO_FRONT_CTRL','PANTO_REAR_CTRL']:bpy.data.objects[name].update_tag()
s.frame_set(s.frame_current)
bpy.context.view_layer.update()
print('REAR_HEAD_Z',bpy.data.objects['PANTO_REAR_HEAD_LEVEL_PIVOT'].matrix_world.translation.z,flush=True)
views={'hero':('CAM_HERO','01_hero_trackside.png'),'side':('CAM_SIDE','02_side_elevation.png'),'cab':('CAM_CAB','03_cab_detail.png'),'bogie':('CAM_BOGIE','04_bogie_detail.png'),'roof':('CAM_ROOF','05_roof_detail.png'),'front':('CAM_FRONT','06_front_portrait.png')}
report={}
for key,(cam,filename) in views.items():
 if view!='all' and key not in view.split(','):continue
 s.render.resolution_y=round(width*({'hero':.5625,'side':.30,'front':1.15}.get(key,.625)))
 saved_hides=[];saved_world=s.world
 if key=='side':
  for o in bpy.data.collections['PRESENTATION_ONLY'].objects:
   if o.type not in ['LIGHT','CAMERA'] and not o.hide_render:saved_hides.append(o);o.hide_render=True
  w=s.world.copy();s.world=w;nt=w.node_tree;out=nt.nodes.get('World Output');old=out.inputs['Surface'].links[0].from_socket;flat=nt.nodes.new('ShaderNodeBackground');flat.inputs[0].default_value=(.40,.425,.43,1);flat.inputs[1].default_value=1;lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(flat.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
  bpy.data.objects['PANTO_REAR_CTRL']['extension']=0;bpy.data.objects['PANTO_REAR_CTRL'].update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
  bpy.data.objects[cam].location.z=2.1
 s.camera=bpy.data.objects[cam];s.render.filepath=str(OUT/'previews'/filename);t=time.time();bpy.ops.render.render(write_still=True);report[key]={'seconds':round(time.time()-t,2),'samples':samples,'width':width,'height':s.render.resolution_y,'camera':cam,'engine':'Cycles CPU','threads':s.render.threads,'denoising':False,'master_sha256':master_sha,'stage_rebuilt':True}
 print('RENDER_TIMING',json.dumps(report[key]),flush=True)
 for o in saved_hides:o.hide_render=False
 s.world=saved_world
 bpy.data.objects['PANTO_REAR_CTRL']['extension']=(math.degrees(math.asin((5.53-4.212)/2.45))-1)/35;bpy.data.objects['PANTO_REAR_CTRL'].update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
(OUT/'qa'/('render_'+view.replace(',','_')+'.json')).write_text(json.dumps(report,indent=2))
