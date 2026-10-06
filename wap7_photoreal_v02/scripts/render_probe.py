import bpy,sys,math,json,time,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];a=sys.argv[sys.argv.index('--')+1:]
view=a[0] if a else 'CAB';samples=int(a[1]) if len(a)>1 else 32;width=int(a[2]) if len(a)>2 else 960;threads=int(a[3]) if len(a)>3 else 2
master=Path(a[4]).resolve() if len(a)>4 else OUT/'WAP7_detail_v02.blend'
sha=hashlib.sha256(master.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(master));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=samples;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=32;s.cycles.adaptive_threshold=.015 if samples>=192 else .02;s.render.threads_mode='FIXED';s.render.threads=threads;s.render.resolution_x=width;s.render.resolution_y=round(width*.69);s.render.resolution_percentage=100;s.cycles.seed=0;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.film_transparent=False
if view.upper() in ['ROOF','PANTOGRAPH','HERO']:
 o=bpy.data.objects['PANTO_REAR_CTRL'];o['extension']=.62;o.update_tag();s.frame_set(1);bpy.context.view_layer.update()
s.camera=bpy.data.objects['V02_CAM_'+view.upper()]
if view.upper()=='SIDE':
 s.camera.data.type='ORTHO';s.camera.data.ortho_scale=22.4;s.render.resolution_y=round(width*.28)
s.render.filepath=str(OUT/'previews'/('probe_'+view.lower()+'.png'));t=time.time();bpy.ops.render.render(write_still=True)
assert hashlib.sha256(master.read_bytes()).hexdigest()==sha,'Input master changed'
(OUT/'qa'/('probe_'+view.lower()+'.json')).write_text(json.dumps({'master_sha256':sha,'master_file_unchanged':True,'render_driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),'view':view,'camera_type':s.camera.data.type,'orthographic_span_m':s.camera.data.ortho_scale if s.camera.data.type=='ORTHO' else None,'height':s.render.resolution_y,'seconds':time.time()-t,'samples':samples,'width':width,'denoised':False,'adaptive_sampling':True,'minimum_samples':32,'noise_threshold':s.cycles.adaptive_threshold,'threads':threads},indent=2))
