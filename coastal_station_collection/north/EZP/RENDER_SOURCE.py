import bpy,sys,hashlib,json,time,os,resource
from mathutils import Vector
from pathlib import Path
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();mode=sys.argv[sys.argv.index('--')+2] if len(sys.argv)>sys.argv.index('--')+2 else 'all';src=P/json.load(open(P/'QA_BUILD.json'))['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=854;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=40
s.render.engine='BLENDER_EEVEE_NEXT' if '--cycles' not in sys.argv else 'CYCLES'
if hasattr(s,'eevee'):s.eevee.taa_render_samples=48
if mode=='test':s.render.resolution_x=960;s.render.resolution_y=640
(P/'renders').mkdir(exist_ok=True);manifest=[];cams=sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:x.name)
for c in cams:
 if mode=='test' and not c.name.startswith('02'):continue
 if mode not in ['all','test'] and not c.name.startswith(mode):continue
 override=None
 if c.name.startswith('04'):
  plan=json.load(open(P/'references/plan.json'));b=plan['main_building'];length=b['length'];depth=b['width'];bx,by=b['center'];side=b['public_side']
  if length>24:
   u=-min(length/2-1,10);v=min(depth/2-.9,3.8);c.location=(bx+side*v,by+u,3.1);target=(bx+side*(-.8),by+3.0,2.7);c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=28;override={'reason':'Read-only camera framing makes existing waiting chairs and ticket furniture clearly visible; scene geometry unchanged.','position':list(c.location),'rotation':list(c.rotation_euler),'lens_mm':28}
 s.camera=c;f=P/'renders'/(c.name+'.png');s.render.filepath=str(f);t=time.time();bpy.ops.render.render(write_still=True);r={'file':str(f.relative_to(P)),'camera':c.name,'source_blend_sha256':sha,'image_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'engine':s.render.engine,'render_seconds':round(time.time()-t,2),'samples':s.cycles.samples if s.render.engine=='CYCLES' else 48,'denoising':False,'os_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'renderer_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'camera_override':override,'resolution':[s.render.resolution_x,s.render.resolution_y]};manifest.append(r);(P/'renders'/(c.name+'.json')).write_text(json.dumps(r,indent=2));print('RENDER_DONE',r,flush=True)
print('SOURCE_UNCHANGED',sha==hashlib.sha256(src.read_bytes()).hexdigest(),flush=True)
