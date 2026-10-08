import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=20;s.render.resolution_x=1200;s.render.resolution_y=750
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for c in sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:x.name):
 if args and not any(c.name.startswith(a) for a in args):continue
 s.camera=c;s.render.filepath=str(P/'renders'/(c.name+'.png'));bpy.ops.render.render(write_still=True)
