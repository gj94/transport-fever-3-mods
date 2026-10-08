import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
quick='quick' in args;s.cycles.samples=12 if quick else 32;s.render.resolution_x=1000 if quick else 1600;s.render.resolution_y=650 if quick else 1000
names=[a for a in args if a!='quick']
for c in sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:x.name):
 if names and not any(c.name.startswith(a) for a in names):continue
 s.camera=c;s.render.filepath=str(R/'renders'/f'{c.name}.png');bpy.ops.render.render(write_still=True)
