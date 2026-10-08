import bpy,sys,hashlib,json,time
from pathlib import Path
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();mode=sys.argv[sys.argv.index('--')+2];q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));(P/'renders').mkdir(exist_ok=True)
for c in q['cameras']:
 if not c['name'].startswith(mode):continue
 s=bpy.data.scenes[c['scene']];bpy.context.window.scene=s;s.camera=s.objects[c['name']];s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1280;s.render.resolution_y=854;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False
 if hasattr(s,'eevee'):s.eevee.taa_render_samples=48
 f=P/'renders'/(c['name']+'.png');s.render.filepath=str(f);t=time.time();bpy.ops.render.render(write_still=True);r={'file':str(f.relative_to(P)),'camera':c['name'],'scene':s.name,'source_blend_sha256':sha,'image_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'engine':s.render.engine,'render_seconds':round(time.time()-t,2),'samples':48,'denoising':False,'resolution':[1280,854],'historical_unplaced':mode.startswith('H'),'status':'Station closed July2017; historical building study is unplaced, mapped corridor does not establish surviving station remnants.'};(f.with_suffix('.json')).write_text(json.dumps(r,indent=2));print('RENDER_DONE',r,flush=True)
assert sha==hashlib.sha256(src.read_bytes()).hexdigest()
