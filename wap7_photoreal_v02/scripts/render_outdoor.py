"""True geometry-grounded outdoor render; builds presentation without saving changes to asset master."""
import bpy,sys,math,json,time,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
view=a[0].upper() if a else 'HERO';samples=int(a[1]) if len(a)>1 else 64;width=int(a[2]) if len(a)>2 else 1280;threads=int(a[3]) if len(a)>3 else 3
master=Path(a[4]).resolve() if len(a)>4 else OUT/'WAP7_detail_v02.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(master));s=bpy.context.scene
import presentation
t=time.time();stage=presentation.apply();print('STAGE_READY',round(time.time()-t,2),flush=True)
p=bpy.data.objects['PANTO_REAR_CTRL'];p['extension']=(math.degrees(math.asin((5.53-4.212)/2.45))-1)/35;p.update_tag();bpy.data.objects['PANTO_FRONT_CTRL']['extension']=0;bpy.data.objects['PANTO_FRONT_CTRL'].update_tag();s.frame_set(1);bpy.context.view_layer.update()
s.render.engine='CYCLES';s.cycles.samples=samples;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.006 if samples>=256 else .015;s.render.threads_mode='FIXED';s.render.threads=threads;s.render.resolution_x=width;s.render.resolution_y=round(width*({'HERO':.58,'FRONT':1.1,'SIDE':.35}.get(view,.67)));s.render.resolution_percentage=100;s.cycles.seed=0;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.film_transparent=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
s.camera=bpy.data.objects['V02_CAM_'+view];s.render.filepath=str(OUT/'previews'/('outdoor_'+view.lower()+'.png'));t=time.time();bpy.ops.render.render(write_still=True)
assert hashlib.sha256(master.read_bytes()).hexdigest()==sha,'Input master changed'
(OUT/'qa'/('outdoor_'+view.lower()+'.json')).write_text(json.dumps({'master_sha256':sha,'master_file_unchanged':True,'render_source_sha256':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),OUT/'components/presentation.py',OUT/'components/depot.py']},'image_sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),'seconds':time.time()-t,'samples':samples,'width':width,'height':s.render.resolution_y,'denoised':False,'threads':threads,'presentation':stage},indent=2))
